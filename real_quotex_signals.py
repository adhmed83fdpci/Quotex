#!/usr/bin/env python3
"""
REAL Quotex Signal System - Production Mode
Uses actual Quotex API connections to generate live trading signals
"""

import asyncio
import sys
import os
import time
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import traceback

# Add library paths
sys.path.append(os.path.join(os.path.dirname(__file__), 'pyquotex-master'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'quotexapi-main'))

# Install required packages if not present
def install_package(package):
    try:
        __import__(package)
    except ImportError:
        print(f"Installing {package}...")
        os.system(f"pip3 install {package}")

install_package('rich')
install_package('requests')

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.live import Live
from rich.text import Text
from rich.align import Align
from rich.layout import Layout

# REAL CREDENTIALS - NO DEMO
REAL_CONFIG = {
    'QUOTEX_EMAIL': 'beyondverse11@gmail.com',
    'QUOTEX_PASSWORD': 'ahmedtamim94301',
    'MODE': 'REAL',  # REAL MODE - NOT DEMO
    'UPDATE_INTERVAL': 15,  # Faster updates for real signals
    'MIN_CONFIDENCE': 0.70,  # Higher threshold for real trading
}

try:
    from pyquotex.stable_api import Quotex as PyQuotex
    PYQUOTEX_AVAILABLE = True
    print("✅ PyQuotex library loaded successfully")
except ImportError as e:
    print(f"❌ PyQuotex not available: {e}")
    PYQUOTEX_AVAILABLE = False

try:
    from quotexpy import Quotex as QuotexPy
    from quotexpy.utils import asset_parse
    from quotexpy.utils.operation_type import OperationType
    from quotexpy.utils.account_type import AccountType
    QUOTEXAPI_AVAILABLE = True
    print("✅ QuotexPy library loaded successfully")
except ImportError as e:
    print(f"❌ QuotexPy not available: {e}")
    QUOTEXAPI_AVAILABLE = False

# Setup logging for real signals
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('real_quotex_signals.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

console = Console()

class RealSignal:
    """Real trading signal from live Quotex data"""
    def __init__(self, asset: str, direction: str, confidence: float, 
                 entry_time: datetime, source: str, price_data: dict = None):
        self.asset = asset
        self.direction = direction  # CALL or PUT
        self.confidence = confidence
        self.entry_time = entry_time
        self.source = source
        self.price_data = price_data or {}
        self.created_at = datetime.now()
        self.expiry = 60  # 1 minute
        self.id = f"{asset}_{direction}_{entry_time.strftime('%H%M%S')}"
        
    def is_valid(self) -> bool:
        """Check if signal is still valid"""
        return datetime.now() < self.entry_time
        
    def time_to_entry(self) -> int:
        """Seconds until entry time"""
        return max(0, int((self.entry_time - datetime.now()).total_seconds()))
        
    def to_dict(self) -> dict:
        return {
            'asset': self.asset,
            'direction': self.direction,
            'confidence': f"{self.confidence:.1%}",
            'entry_time': self.entry_time.strftime('%H:%M:%S'),
            'source': self.source,
            'time_to_entry': self.time_to_entry(),
            'price_data': self.price_data,
            'created_at': self.created_at.isoformat()
        }

class RealQuotexSignalSystem:
    """REAL Quotex Signal System - Live Trading"""
    
    def __init__(self):
        self.console = Console()
        self.pyquotex_client = None
        self.quotexpy_client = None
        self.running = False
        self.real_signals = []
        self.signal_history = []
        self.connection_status = {'pyquotex': False, 'quotexpy': False}
        
        # Real OTC assets for live trading
        self.live_assets = [
            "EURUSD_otc", "GBPUSD_otc", "USDJPY_otc", "USDCHF_otc",
            "AUDUSD_otc", "USDCAD_otc", "NZDUSD_otc", "EURGBP_otc",
            "EURJPY_otc", "GBPJPY_otc", "AUDCAD_otc", "CHFJPY_otc"
        ]
        
        console.print("🚀 REAL Quotex Signal System Initializing...", style="bold green")
        console.print(f"📧 Account: {REAL_CONFIG['QUOTEX_EMAIL']}", style="cyan")
        console.print("⚠️  REAL MODE - Live Trading Signals", style="bold red")
        
    async def init_real_connections(self) -> bool:
        """Initialize REAL connections to Quotex"""
        console.print("🔗 Connecting to REAL Quotex APIs...", style="yellow")
        
        success_count = 0
        
        # Initialize PyQuotex with REAL credentials
        if PYQUOTEX_AVAILABLE:
            try:
                self.pyquotex_client = PyQuotex(
                    email=REAL_CONFIG['QUOTEX_EMAIL'],
                    password=REAL_CONFIG['QUOTEX_PASSWORD'],
                    lang="en"
                )
                
                console.print("🔄 Connecting PyQuotex to REAL account...", style="yellow")
                check_connect, message = await self.pyquotex_client.connect()
                
                if check_connect:
                    self.connection_status['pyquotex'] = True
                    success_count += 1
                    console.print("✅ PyQuotex REAL connection successful!", style="bold green")
                    
                    # Get account balance to verify real connection
                    try:
                        balance = await self.pyquotex_client.get_balance()
                        console.print(f"💰 Real Account Balance: ${balance}", style="green")
                        logger.info(f"PyQuotex connected - Balance: ${balance}")
                    except Exception as e:
                        console.print(f"⚠️  Balance check failed: {e}", style="yellow")
                else:
                    console.print(f"❌ PyQuotex connection failed: {message}", style="red")
                    logger.error(f"PyQuotex connection failed: {message}")
                    
            except Exception as e:
                console.print(f"❌ PyQuotex error: {e}", style="red")
                logger.error(f"PyQuotex initialization error: {e}")
        
        # Initialize QuotexPy with REAL credentials
        if QUOTEXAPI_AVAILABLE:
            try:
                self.quotexpy_client = QuotexPy(
                    email=REAL_CONFIG['QUOTEX_EMAIL'],
                    password=REAL_CONFIG['QUOTEX_PASSWORD'],
                    headless=True
                )
                
                console.print("🔄 Connecting QuotexPy to REAL account...", style="yellow")
                quotexpy_connected = await self.quotexpy_client.connect()
                
                if quotexpy_connected:
                    # Set to REAL account (not practice)
                    self.quotexpy_client.change_account(AccountType.REAL)
                    self.connection_status['quotexpy'] = True
                    success_count += 1
                    console.print("✅ QuotexPy REAL connection successful!", style="bold green")
                    
                    # Get balance to verify real connection
                    try:
                        balance = await self.quotexpy_client.get_balance()
                        console.print(f"💰 Real Account Balance: ${balance}", style="green")
                        logger.info(f"QuotexPy connected - Balance: ${balance}")
                    except Exception as e:
                        console.print(f"⚠️  Balance check failed: {e}", style="yellow")
                else:
                    console.print("❌ QuotexPy connection failed", style="red")
                    logger.error("QuotexPy connection failed")
                    
            except Exception as e:
                console.print(f"❌ QuotexPy error: {e}", style="red")
                logger.error(f"QuotexPy initialization error: {e}")
        
        if success_count > 0:
            console.print(f"🎯 {success_count}/2 REAL connections established", style="bold green")
            return True
        else:
            console.print("❌ No REAL connections established", style="bold red")
            return False
    
    async def get_real_market_sentiment(self, asset: str) -> Tuple[str, float, dict]:
        """Get REAL market sentiment from live data"""
        try:
            if self.pyquotex_client and self.connection_status['pyquotex']:
                sentiment_data = await self.pyquotex_client.get_realtime_sentiment(asset)
                
                if sentiment_data and 'sentiment' in sentiment_data:
                    sentiment = sentiment_data['sentiment']
                    buy_percentage = sentiment.get('buy', 0)
                    sell_percentage = sentiment.get('sell', 0)
                    
                    # Calculate real signal direction and confidence
                    if buy_percentage > sell_percentage:
                        confidence = (buy_percentage - sell_percentage) / 100
                        direction = "CALL"
                    else:
                        confidence = (sell_percentage - buy_percentage) / 100
                        direction = "PUT"
                    
                    price_data = {
                        'buy_sentiment': buy_percentage,
                        'sell_sentiment': sell_percentage,
                        'timestamp': datetime.now().isoformat()
                    }
                    
                    return direction, min(0.95, max(0.5, confidence)), price_data
                    
        except Exception as e:
            logger.error(f"Error getting real sentiment for {asset}: {e}")
        
        return "CALL", 0.5, {}
    
    async def get_real_signal_data(self) -> dict:
        """Get REAL signal data from both APIs"""
        combined_data = {}
        
        # Get real signals from PyQuotex
        if self.pyquotex_client and self.connection_status['pyquotex']:
            try:
                signal_data = self.pyquotex_client.get_signal_data()
                if signal_data:
                    combined_data.update(signal_data)
                    logger.info(f"Got {len(signal_data)} PyQuotex signals")
            except Exception as e:
                logger.error(f"Error getting PyQuotex real signals: {e}")
        
        # Get real signals from QuotexPy
        if self.quotexpy_client and self.connection_status['quotexpy']:
            try:
                signal_data = self.quotexpy_client.get_signal_data()
                if signal_data:
                    for asset, data in signal_data.items():
                        if asset in combined_data:
                            combined_data[asset].update(data)
                        else:
                            combined_data[asset] = data
                    logger.info(f"Got {len(signal_data)} QuotexPy signals")
            except Exception as e:
                logger.error(f"Error getting QuotexPy real signals: {e}")
        
        return combined_data
    
    async def get_real_asset_prices(self, asset: str) -> dict:
        """Get real-time asset prices"""
        try:
            if self.pyquotex_client and self.connection_status['pyquotex']:
                prices = await self.pyquotex_client.get_realtime_price(asset)
                if prices:
                    latest_price = prices[-1] if isinstance(prices, list) else prices
                    return {
                        'current_price': latest_price.get('price', 0),
                        'timestamp': latest_price.get('timestamp', datetime.now().isoformat()),
                        'source': 'PyQuotex'
                    }
        except Exception as e:
            logger.error(f"Error getting real prices for {asset}: {e}")
        
        return {}
    
    async def generate_real_signals(self) -> List[RealSignal]:
        """Generate REAL trading signals from live market data"""
        real_signals = []
        
        try:
            # Get real signal data from APIs
            signal_data = await self.get_real_signal_data()
            
            # Analyze each live asset
            for asset in self.live_assets:
                try:
                    # Get real sentiment analysis
                    direction, confidence, sentiment_data = await self.get_real_market_sentiment(asset)
                    
                    # Only create signals above confidence threshold
                    if confidence >= REAL_CONFIG['MIN_CONFIDENCE']:
                        # Get real price data
                        price_data = await self.get_real_asset_prices(asset)
                        price_data.update(sentiment_data)
                        
                        # Calculate entry time (30-90 seconds ahead for real trading)
                        seconds_ahead = 30 + int(confidence * 60)  # Higher confidence = later entry
                        entry_time = datetime.now() + timedelta(seconds=seconds_ahead)
                        
                        # Create real signal
                        signal = RealSignal(
                            asset=asset,
                            direction=direction,
                            confidence=confidence,
                            entry_time=entry_time,
                            source="REAL-Live-Analysis",
                            price_data=price_data
                        )
                        
                        real_signals.append(signal)
                        logger.info(f"Generated REAL signal: {asset} {direction} {confidence:.1%}")
                        
                except Exception as e:
                    logger.error(f"Error analyzing real data for {asset}: {e}")
                    continue
            
            # Add signals from API signal data
            for asset, asset_signals in signal_data.items():
                if asset in self.live_assets:
                    for timestamp, signal_info in asset_signals.items():
                        direction = signal_info.get('dir', 'CALL').upper()
                        duration = signal_info.get('duration', 60)
                        
                        # Calculate entry time
                        entry_time = datetime.now() + timedelta(seconds=45)
                        
                        signal = RealSignal(
                            asset=asset,
                            direction=direction,
                            confidence=0.80,  # API signals get high confidence
                            entry_time=entry_time,
                            source="REAL-API-Signals",
                            price_data={'api_signal': True, 'duration': duration}
                        )
                        
                        real_signals.append(signal)
            
        except Exception as e:
            logger.error(f"Error generating real signals: {e}")
        
        return real_signals
    
    def filter_real_signals(self, signals: List[RealSignal]) -> List[RealSignal]:
        """Filter and rank real signals by quality"""
        # Remove invalid signals
        valid_signals = [s for s in signals if s.is_valid()]
        
        # Remove duplicates (same asset)
        unique_signals = {}
        for signal in valid_signals:
            key = signal.asset
            if key not in unique_signals or signal.confidence > unique_signals[key].confidence:
                unique_signals[key] = signal
        
        # Sort by confidence (highest first)
        filtered_signals = sorted(
            unique_signals.values(),
            key=lambda s: s.confidence,
            reverse=True
        )
        
        return filtered_signals[:15]  # Top 15 real signals
    
    def create_real_signals_table(self, signals: List[RealSignal]) -> Table:
        """Create display table for real signals"""
        table = Table(
            title="🎯 REAL Quotex Trading Signals - LIVE",
            title_style="bold red",
            show_header=True,
            header_style="bold blue",
            border_style="bright_red"
        )
        
        table.add_column("Entry Time", style="cyan", width=10)
        table.add_column("Asset", style="white", width=12)
        table.add_column("Direction", style="bold", width=15)
        table.add_column("Confidence", style="green", width=12)
        table.add_column("Time Left", style="yellow", width=10)
        table.add_column("Source", style="dim", width=15)
        
        if not signals:
            table.add_row("--:--", "Loading...", "Analyzing Market", "---", "---", "REAL APIs")
            return table
        
        for signal in signals:
            # Style direction
            if signal.direction == "CALL":
                direction_text = "[bold green]📈 CALL[/bold green]"
            else:
                direction_text = "[bold red]📉 PUT[/bold red]"
            
            # Time to entry
            time_left = signal.time_to_entry()
            if time_left > 60:
                time_text = f"{time_left//60}m {time_left%60}s"
            else:
                time_text = f"{time_left}s"
            
            # Confidence styling
            if signal.confidence > 0.85:
                conf_style = "bold green"
            elif signal.confidence > 0.75:
                conf_style = "green"
            else:
                conf_style = "yellow"
            
            table.add_row(
                signal.entry_time.strftime("%H:%M:%S"),
                signal.asset.replace('_otc', ''),
                direction_text,
                f"[{conf_style}]{signal.confidence:.1%}[/{conf_style}]",
                time_text,
                signal.source.split('-')[0]
            )
        
        return table
    
    def create_real_dashboard(self, signals: List[RealSignal]) -> Layout:
        """Create real trading dashboard"""
        layout = Layout()
        
        # Header
        header_text = Text("REAL Quotex Signal System", style="bold red")
        header_text.append(" - LIVE TRADING", style="bold green")
        header_text.append(f" | {datetime.now().strftime('%H:%M:%S')}", style="dim")
        
        status_text = ""
        if self.connection_status['pyquotex']:
            status_text += "✅ PyQuotex "
        if self.connection_status['quotexpy']:
            status_text += "✅ QuotexPy "
        
        header = Panel(
            Align.center(header_text + Text(f"\n{status_text}", style="green")),
            style="red",
            title="🚀 REAL MODE - Live Account"
        )
        
        # Signals table
        signals_table = self.create_real_signals_table(signals)
        
        # Statistics
        total_signals = len(signals)
        call_signals = len([s for s in signals if s.direction == 'CALL'])
        put_signals = len([s for s in signals if s.direction == 'PUT'])
        avg_confidence = sum(s.confidence for s in signals) / total_signals if total_signals > 0 else 0
        high_conf_signals = len([s for s in signals if s.confidence > 0.80])
        
        stats_text = f"""
[bold red]📊 REAL Trading Stats[/bold red]

[green]Live Signals:[/green] {total_signals}
[green]CALL Signals:[/green] {call_signals} 📈
[red]PUT Signals:[/red] {put_signals} 📉
[blue]Avg Confidence:[/blue] {avg_confidence:.1%}
[yellow]High Confidence:[/yellow] {high_conf_signals} (>80%)

[white]Account:[/white] {REAL_CONFIG['QUOTEX_EMAIL']}
[white]Mode:[/white] REAL TRADING
[white]Update:[/white] Every {REAL_CONFIG['UPDATE_INTERVAL']}s
        """
        
        stats_panel = Panel(stats_text.strip(), title="📈 Live Stats", border_style="green")
        
        # Layout
        layout.split_column(
            Layout(header, size=4),
            Layout(signals_table),
            Layout(stats_panel, size=10)
        )
        
        return layout
    
    async def monitor_real_signals(self):
        """Monitor and display real signals continuously"""
        self.running = True
        
        console.print("🚀 Starting REAL signal monitoring...", style="bold green")
        
        # Connect to real APIs
        if not await self.init_real_connections():
            console.print("❌ Failed to establish REAL connections. Exiting.", style="bold red")
            return
        
        console.print("🎯 REAL signal generation started!", style="bold green")
        
        try:
            with Live(
                self.create_real_dashboard([]),
                refresh_per_second=2,
                screen=True
            ) as live:
                
                while self.running:
                    try:
                        # Generate real signals from live data
                        new_signals = await self.generate_real_signals()
                        
                        # Filter and update active signals
                        self.real_signals = self.filter_real_signals(new_signals)
                        
                        # Update display
                        live.update(self.create_real_dashboard(self.real_signals))
                        
                        # Save real signal history
                        self.signal_history.append({
                            'timestamp': datetime.now().isoformat(),
                            'signals': [s.to_dict() for s in self.real_signals],
                            'connections': self.connection_status
                        })
                        
                        # Log real signals
                        if self.real_signals:
                            logger.info(f"Generated {len(self.real_signals)} REAL signals")
                            for signal in self.real_signals[:3]:  # Log top 3
                                logger.info(f"REAL SIGNAL: {signal.asset} {signal.direction} {signal.confidence:.1%} at {signal.entry_time.strftime('%H:%M:%S')}")
                        
                        # Wait for next update
                        await asyncio.sleep(REAL_CONFIG['UPDATE_INTERVAL'])
                        
                    except Exception as e:
                        error_msg = f"Error in real signal monitoring: {e}"
                        console.print(f"❌ {error_msg}", style="red")
                        logger.error(f"{error_msg}\n{traceback.format_exc()}")
                        await asyncio.sleep(5)
                        
        except KeyboardInterrupt:
            console.print("\n🛑 REAL signal monitoring stopped", style="yellow")
        finally:
            await self.cleanup()
    
    def save_real_signals(self):
        """Save real signal history"""
        try:
            with open('real_signals_history.json', 'w') as f:
                json.dump(self.signal_history, f, indent=2, default=str)
            console.print("✅ REAL signal history saved", style="green")
        except Exception as e:
            console.print(f"❌ Error saving real signals: {e}", style="red")
    
    async def cleanup(self):
        """Cleanup real connections"""
        console.print("🔄 Closing REAL connections...", style="yellow")
        
        if self.pyquotex_client:
            try:
                await self.pyquotex_client.close()
                console.print("✅ PyQuotex connection closed", style="green")
            except:
                pass
        
        if self.quotexpy_client:
            try:
                self.quotexpy_client.close()
                console.print("✅ QuotexPy connection closed", style="green")
            except:
                pass
        
        self.save_real_signals()

async def main():
    """Main entry point for REAL signal system"""
    console.print("🎯 REAL Quotex Signal System Starting...", style="bold blue")
    console.print("⚠️  WARNING: This connects to your REAL trading account!", style="bold red")
    console.print(f"📧 Account: {REAL_CONFIG['QUOTEX_EMAIL']}", style="cyan")
    console.print()
    
    # Create real signal system
    real_system = RealQuotexSignalSystem()
    
    try:
        # Start real signal monitoring
        await real_system.monitor_real_signals()
    except Exception as e:
        console.print(f"❌ Fatal error: {e}", style="bold red")
        logger.error(f"Fatal error: {e}\n{traceback.format_exc()}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 REAL signal system stopped!")
    except Exception as e:
        print(f"❌ Error: {e}")