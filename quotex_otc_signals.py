#!/usr/bin/env python3
"""
Quotex OTC Market Signals
Combines pyquotex-master and quotexapi-main to provide comprehensive OTC market signals
"""

import asyncio
import sys
import os
import time
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import signal
from pathlib import Path

# Add library paths
sys.path.append(os.path.join(os.path.dirname(__file__), 'pyquotex-master'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'quotexapi-main'))

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.live import Live
    from rich.text import Text
    from rich.align import Align
    from rich.columns import Columns
    from rich.layout import Layout
    from rich import print as rprint
except ImportError:
    print("Installing required packages...")
    os.system("pip3 install rich")
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.live import Live
    from rich.text import Text
    from rich.align import Align
    from rich.columns import Columns
    from rich.layout import Layout
    from rich import print as rprint

try:
    # Import pyquotex
    from pyquotex.stable_api import Quotex as PyQuotex
    PYQUOTEX_AVAILABLE = True
except ImportError:
    print("Warning: PyQuotex not available")
    PYQUOTEX_AVAILABLE = False

try:
    # Import quotexapi
    from quotexpy import Quotex as QuotexPy
    from quotexpy.utils import asset_parse
    from quotexpy.utils.operation_type import OperationType
    from quotexpy.utils.account_type import AccountType
    QUOTEXAPI_AVAILABLE = True
except ImportError:
    print("Warning: QuotexPy not available")
    QUOTEXAPI_AVAILABLE = False

# Console for rich output
console = Console()

class SignalType:
    """Signal types for OTC markets"""
    CALL = "CALL"
    PUT = "PUT"
    NEUTRAL = "NEUTRAL"
    STRONG_CALL = "STRONG_CALL"
    STRONG_PUT = "STRONG_PUT"

class OTCSignal:
    """Represents an OTC market signal"""
    def __init__(self, asset: str, signal_type: str, confidence: float, 
                 duration: int, source: str, timestamp: datetime = None):
        self.asset = asset
        self.signal_type = signal_type
        self.confidence = confidence
        self.duration = duration
        self.source = source
        self.timestamp = timestamp or datetime.now()
        self.expiry = self.timestamp + timedelta(seconds=duration)
        
    def is_valid(self) -> bool:
        """Check if signal is still valid"""
        return datetime.now() < self.expiry
        
    def to_dict(self) -> Dict:
        """Convert signal to dictionary"""
        return {
            'asset': self.asset,
            'signal_type': self.signal_type,
            'confidence': self.confidence,
            'duration': self.duration,
            'source': self.source,
            'timestamp': self.timestamp.isoformat(),
            'expiry': self.expiry.isoformat(),
            'valid': self.is_valid()
        }

class QuotexOTCSignals:
    """Combined OTC Market Signals System"""
    
    def __init__(self, email: str = None, password: str = None):
        self.console = Console()
        self.email = email
        self.password = password
        self.signals: List[OTCSignal] = []
        self.pyquotex_client = None
        self.quotexpy_client = None
        self.running = False
        self.signal_history = []
        
        # OTC Assets to monitor
        self.otc_assets = [
            "EURUSD_otc", "GBPUSD_otc", "USDJPY_otc", "USDCHF_otc", 
            "AUDUSD_otc", "USDCAD_otc", "NZDUSD_otc", "EURGBP_otc",
            "EURJPY_otc", "GBPJPY_otc", "AUDCAD_otc", "AUDCHF_otc",
            "CADCHF_otc", "CHFJPY_otc", "EURCHF_otc", "EURAUD_otc"
        ]
        
        # Initialize clients
        self._init_clients()
        
    def _init_clients(self):
        """Initialize both clients"""
        if PYQUOTEX_AVAILABLE and self.email and self.password:
            try:
                self.pyquotex_client = PyQuotex(
                    email=self.email,
                    password=self.password,
                    lang="en"
                )
                self.console.print("✅ PyQuotex client initialized", style="green")
            except Exception as e:
                self.console.print(f"❌ PyQuotex client failed: {e}", style="red")
                
        if QUOTEXAPI_AVAILABLE and self.email and self.password:
            try:
                self.quotexpy_client = QuotexPy(
                    email=self.email,
                    password=self.password,
                    headless=True
                )
                self.console.print("✅ QuotexPy client initialized", style="green")
            except Exception as e:
                self.console.print(f"❌ QuotexPy client failed: {e}", style="red")
    
    async def connect_clients(self) -> bool:
        """Connect both clients"""
        pyquotex_connected = False
        quotexpy_connected = False
        
        if self.pyquotex_client:
            try:
                check_connect, message = await self.pyquotex_client.connect()
                if check_connect:
                    pyquotex_connected = True
                    self.console.print("✅ PyQuotex connected", style="green")
                else:
                    self.console.print(f"❌ PyQuotex connection failed: {message}", style="red")
            except Exception as e:
                self.console.print(f"❌ PyQuotex connection error: {e}", style="red")
        
        if self.quotexpy_client:
            try:
                quotexpy_connected = await self.quotexpy_client.connect()
                if quotexpy_connected:
                    self.quotexpy_client.change_account(AccountType.PRACTICE)
                    self.console.print("✅ QuotexPy connected", style="green")
                else:
                    self.console.print("❌ QuotexPy connection failed", style="red")
            except Exception as e:
                self.console.print(f"❌ QuotexPy connection error: {e}", style="red")
        
        return pyquotex_connected or quotexpy_connected
    
    async def get_pyquotex_signals(self) -> List[OTCSignal]:
        """Get signals from PyQuotex"""
        signals = []
        if not self.pyquotex_client:
            return signals
            
        try:
            # Get sentiment data
            for asset in self.otc_assets:
                try:
                    sentiment_data = await self.pyquotex_client.get_realtime_sentiment(asset)
                    if sentiment_data and 'sentiment' in sentiment_data:
                        sentiment = sentiment_data['sentiment']
                        buy_percentage = sentiment.get('buy', 0)
                        sell_percentage = sentiment.get('sell', 0)
                        
                        # Calculate signal strength
                        if buy_percentage > sell_percentage:
                            confidence = (buy_percentage - sell_percentage) / 100
                            if confidence > 0.6:
                                signal_type = SignalType.STRONG_CALL
                            else:
                                signal_type = SignalType.CALL
                        else:
                            confidence = (sell_percentage - buy_percentage) / 100
                            if confidence > 0.6:
                                signal_type = SignalType.STRONG_PUT
                            else:
                                signal_type = SignalType.PUT
                        
                        if confidence > 0.3:  # Only add signals with decent confidence
                            signal = OTCSignal(
                                asset=asset,
                                signal_type=signal_type,
                                confidence=confidence,
                                duration=300,  # 5 minutes
                                source="PyQuotex-Sentiment"
                            )
                            signals.append(signal)
                            
                except Exception as e:
                    continue
                    
            # Get signal data
            signal_data = self.pyquotex_client.get_signal_data()
            if signal_data:
                for asset, asset_signals in signal_data.items():
                    if asset in self.otc_assets:
                        for timestamp, signal_info in asset_signals.items():
                            direction = signal_info.get('dir', '')
                            duration = signal_info.get('duration', 60)
                            
                            signal_type = SignalType.CALL if direction.lower() == 'call' else SignalType.PUT
                            
                            signal = OTCSignal(
                                asset=asset,
                                signal_type=signal_type,
                                confidence=0.7,  # Default confidence for signal data
                                duration=duration,
                                source="PyQuotex-SignalData"
                            )
                            signals.append(signal)
                            
        except Exception as e:
            self.console.print(f"❌ Error getting PyQuotex signals: {e}", style="red")
            
        return signals
    
    async def get_quotexpy_signals(self) -> List[OTCSignal]:
        """Get signals from QuotexPy"""
        signals = []
        if not self.quotexpy_client:
            return signals
            
        try:
            # Get signal data
            signal_data = self.quotexpy_client.get_signal_data()
            if signal_data:
                for asset, asset_signals in signal_data.items():
                    if asset in self.otc_assets:
                        for timestamp, signal_info in asset_signals.items():
                            direction = signal_info.get('dir', '')
                            duration = signal_info.get('duration', 60)
                            
                            signal_type = SignalType.CALL if direction.lower() == 'call' else SignalType.PUT
                            
                            signal = OTCSignal(
                                asset=asset,
                                signal_type=signal_type,
                                confidence=0.8,  # Higher confidence for QuotexPy signals
                                duration=duration,
                                source="QuotexPy-SignalData"
                            )
                            signals.append(signal)
                            
        except Exception as e:
            self.console.print(f"❌ Error getting QuotexPy signals: {e}", style="red")
            
        return signals
    
    def merge_signals(self, pyquotex_signals: List[OTCSignal], 
                     quotexpy_signals: List[OTCSignal]) -> List[OTCSignal]:
        """Merge and deduplicate signals from both sources"""
        merged_signals = []
        signal_map = {}
        
        # Process all signals
        all_signals = pyquotex_signals + quotexpy_signals
        
        for signal in all_signals:
            key = f"{signal.asset}_{signal.signal_type}"
            
            if key not in signal_map:
                signal_map[key] = signal
            else:
                # If we have multiple signals for the same asset/direction, 
                # choose the one with higher confidence
                existing_signal = signal_map[key]
                if signal.confidence > existing_signal.confidence:
                    signal_map[key] = signal
                elif signal.confidence == existing_signal.confidence:
                    # If same confidence, update source to show combined
                    existing_signal.source = f"{existing_signal.source}+{signal.source}"
        
        return list(signal_map.values())
    
    def filter_signals(self, signals: List[OTCSignal]) -> List[OTCSignal]:
        """Filter signals based on quality criteria"""
        filtered = []
        
        for signal in signals:
            # Only include valid signals
            if not signal.is_valid():
                continue
                
            # Minimum confidence threshold
            if signal.confidence < 0.4:
                continue
                
            # Add to filtered list
            filtered.append(signal)
        
        # Sort by confidence
        filtered.sort(key=lambda x: x.confidence, reverse=True)
        
        return filtered
    
    async def get_combined_signals(self) -> List[OTCSignal]:
        """Get combined signals from both sources"""
        # Get signals from both sources
        pyquotex_signals = await self.get_pyquotex_signals()
        quotexpy_signals = await self.get_quotexpy_signals()
        
        # Merge signals
        merged_signals = self.merge_signals(pyquotex_signals, quotexpy_signals)
        
        # Filter signals
        filtered_signals = self.filter_signals(merged_signals)
        
        # Update signal history
        self.signals = filtered_signals
        self.signal_history.append({
            'timestamp': datetime.now(),
            'signals': [signal.to_dict() for signal in filtered_signals]
        })
        
        # Keep only last 100 entries in history
        if len(self.signal_history) > 100:
            self.signal_history = self.signal_history[-100:]
        
        return filtered_signals
    
    def create_signals_table(self, signals: List[OTCSignal]) -> Table:
        """Create a rich table displaying signals"""
        table = Table(
            title="🚀 Quotex OTC Market Signals",
            title_style="bold magenta",
            show_header=True,
            header_style="bold blue"
        )
        
        table.add_column("Asset", style="cyan", width=12)
        table.add_column("Signal", style="bold", width=12)
        table.add_column("Confidence", style="green", width=10)
        table.add_column("Duration", style="yellow", width=8)
        table.add_column("Source", style="dim", width=15)
        table.add_column("Expires", style="magenta", width=10)
        
        for signal in signals:
            # Color code signal type
            if signal.signal_type == SignalType.STRONG_CALL:
                signal_style = "bold green"
                signal_text = "📈 STRONG CALL"
            elif signal.signal_type == SignalType.CALL:
                signal_style = "green"
                signal_text = "📈 CALL"
            elif signal.signal_type == SignalType.STRONG_PUT:
                signal_style = "bold red"
                signal_text = "📉 STRONG PUT"
            elif signal.signal_type == SignalType.PUT:
                signal_style = "red"
                signal_text = "📉 PUT"
            else:
                signal_style = "yellow"
                signal_text = "➡️ NEUTRAL"
            
            # Calculate time to expiry
            time_to_expiry = signal.expiry - datetime.now()
            expires_text = f"{int(time_to_expiry.total_seconds())}s"
            
            table.add_row(
                signal.asset.replace('_otc', ''),
                f"[{signal_style}]{signal_text}[/{signal_style}]",
                f"{signal.confidence:.1%}",
                f"{signal.duration}s",
                signal.source.split('-')[0],  # Shortened source
                expires_text
            )
        
        return table
    
    def create_dashboard(self, signals: List[OTCSignal]) -> Layout:
        """Create a dashboard layout"""
        layout = Layout()
        
        # Create header
        header = Panel(
            Align.center(
                Text("Quotex OTC Market Signals", style="bold magenta") + 
                Text(f" | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", style="dim")
            ),
            style="blue"
        )
        
        # Create signals table
        signals_table = self.create_signals_table(signals)
        
        # Create statistics
        total_signals = len(signals)
        call_signals = len([s for s in signals if 'CALL' in s.signal_type])
        put_signals = len([s for s in signals if 'PUT' in s.signal_type])
        avg_confidence = sum(s.confidence for s in signals) / total_signals if total_signals > 0 else 0
        
        stats = Table(title="📊 Statistics", show_header=False, box=None)
        stats.add_column("Metric", style="cyan")
        stats.add_column("Value", style="green")
        stats.add_row("Total Signals", str(total_signals))
        stats.add_row("Call Signals", str(call_signals))
        stats.add_row("Put Signals", str(put_signals))
        stats.add_row("Avg Confidence", f"{avg_confidence:.1%}")
        
        # Layout structure
        layout.split_column(
            Layout(header, size=3),
            Layout(signals_table),
            Layout(stats, size=6)
        )
        
        return layout
    
    async def run_signal_monitor(self, update_interval: int = 10):
        """Run the signal monitoring system"""
        self.running = True
        
        self.console.print("🚀 Starting Quotex OTC Market Signals Monitor", style="bold green")
        
        # Connect to clients
        if not await self.connect_clients():
            self.console.print("❌ Failed to connect to any client", style="red")
            return
        
        try:
            with Live(
                self.create_dashboard([]), 
                refresh_per_second=1, 
                screen=True
            ) as live:
                while self.running:
                    try:
                        # Get updated signals
                        signals = await self.get_combined_signals()
                        
                        # Update display
                        live.update(self.create_dashboard(signals))
                        
                        # Wait for next update
                        await asyncio.sleep(update_interval)
                        
                    except Exception as e:
                        self.console.print(f"❌ Error in signal monitor: {e}", style="red")
                        await asyncio.sleep(5)
                        
        except KeyboardInterrupt:
            self.console.print("\n🛑 Signal monitor stopped by user", style="yellow")
        finally:
            self.running = False
            await self.cleanup()
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.pyquotex_client:
            try:
                await self.pyquotex_client.close()
            except:
                pass
                
        if self.quotexpy_client:
            try:
                self.quotexpy_client.close()
            except:
                pass
    
    def save_signals_history(self, filename: str = "signals_history.json"):
        """Save signal history to file"""
        try:
            with open(filename, 'w') as f:
                json.dump(self.signal_history, f, indent=2, default=str)
            self.console.print(f"✅ Signal history saved to {filename}", style="green")
        except Exception as e:
            self.console.print(f"❌ Error saving signal history: {e}", style="red")

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    print("\n🛑 Shutting down...")
    sys.exit(0)

async def main():
    """Main function"""
    console.print("🎯 Quotex OTC Market Signals System", style="bold blue")
    console.print("Combining pyquotex-master and quotexapi-main for comprehensive OTC signals", style="dim")
    console.print()
    
    # Get credentials
    email = input("Enter your Quotex email (or press Enter for demo): ").strip()
    if email:
        password = input("Enter your Quotex password: ").strip()
    else:
        email = None
        password = None
        console.print("Running in demo mode (limited functionality)", style="yellow")
    
    # Create signal monitor
    signal_monitor = QuotexOTCSignals(email=email, password=password)
    
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Run the monitor
        await signal_monitor.run_signal_monitor(update_interval=15)
    except Exception as e:
        console.print(f"❌ Fatal error: {e}", style="red")
    finally:
        # Save history
        signal_monitor.save_signals_history()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")