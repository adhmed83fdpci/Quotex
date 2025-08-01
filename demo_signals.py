#!/usr/bin/env python3
"""
Demo Signal Generator for Quotex OTC Market Signals
This demonstrates the system functionality without requiring actual API credentials
"""

import asyncio
import random
import time
from datetime import datetime, timedelta
from typing import List
import json

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.live import Live
    from rich.text import Text
    from rich.align import Align
    from rich.layout import Layout
except ImportError:
    print("Installing rich...")
    import os
    os.system("pip3 install rich")
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.live import Live
    from rich.text import Text
    from rich.align import Align
    from rich.layout import Layout

console = Console()

class SignalType:
    """Signal types for OTC markets"""
    CALL = "CALL"
    PUT = "PUT"
    NEUTRAL = "NEUTRAL"
    STRONG_CALL = "STRONG_CALL"
    STRONG_PUT = "STRONG_PUT"

class DemoOTCSignal:
    """Demo OTC Signal"""
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
        
    def to_dict(self) -> dict:
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

class DemoSignalGenerator:
    """Demo signal generator for OTC markets"""
    
    def __init__(self):
        self.console = Console()
        self.signals: List[DemoOTCSignal] = []
        self.running = False
        self.signal_history = []
        
        # OTC Assets to monitor
        self.otc_assets = [
            "EURUSD_otc", "GBPUSD_otc", "USDJPY_otc", "USDCHF_otc", 
            "AUDUSD_otc", "USDCAD_otc", "NZDUSD_otc", "EURGBP_otc",
            "EURJPY_otc", "GBPJPY_otc", "AUDCAD_otc", "AUDCHF_otc",
            "CADCHF_otc", "CHFJPY_otc", "EURCHF_otc", "EURAUD_otc"
        ]
        
        # Market conditions simulation
        self.market_trend = {asset: "neutral" for asset in self.otc_assets}
        self.volatility = {asset: 0.5 for asset in self.otc_assets}
        
    def generate_demo_signals(self) -> List[DemoOTCSignal]:
        """Generate realistic demo signals"""
        signals = []
        
        # Simulate different signal sources
        sources = [
            ("PyQuotex-Sentiment", 0.7),
            ("PyQuotex-SignalData", 0.8),
            ("QuotexPy-SignalData", 0.85),
            ("TechnicalAnalysis", 0.75),
            ("MarketMood", 0.6)
        ]
        
        # Generate signals for random assets
        num_signals = random.randint(3, 8)
        selected_assets = random.sample(self.otc_assets, num_signals)
        
        for asset in selected_assets:
            # Simulate market analysis
            market_sentiment = random.uniform(0.3, 0.9)
            trend_strength = self.volatility[asset] * random.uniform(0.5, 1.5)
            
            # Determine signal direction
            if market_sentiment > 0.6:
                if trend_strength > 0.8:
                    signal_type = SignalType.STRONG_CALL
                else:
                    signal_type = SignalType.CALL
                confidence = market_sentiment * trend_strength
            else:
                if trend_strength > 0.8:
                    signal_type = SignalType.STRONG_PUT
                else:
                    signal_type = SignalType.PUT
                confidence = (1 - market_sentiment) * trend_strength
            
            # Adjust confidence to realistic ranges
            confidence = max(0.4, min(0.95, confidence))
            
            # Random duration between 1-10 minutes
            duration = random.choice([60, 120, 180, 300, 420, 600])
            
            # Random source
            source, source_confidence = random.choice(sources)
            final_confidence = (confidence + source_confidence) / 2
            
            signal = DemoOTCSignal(
                asset=asset,
                signal_type=signal_type,
                confidence=final_confidence,
                duration=duration,
                source=source
            )
            
            signals.append(signal)
            
        return signals
    
    def update_market_conditions(self):
        """Simulate changing market conditions"""
        for asset in self.otc_assets:
            # Gradually change volatility
            self.volatility[asset] += random.uniform(-0.1, 0.1)
            self.volatility[asset] = max(0.2, min(1.0, self.volatility[asset]))
            
            # Occasionally change market trend
            if random.random() < 0.1:  # 10% chance
                trends = ["bullish", "bearish", "neutral"]
                self.market_trend[asset] = random.choice(trends)
    
    def create_signals_table(self, signals: List[DemoOTCSignal]) -> Table:
        """Create a rich table displaying signals"""
        table = Table(
            title="🚀 Quotex OTC Market Signals (DEMO)",
            title_style="bold magenta",
            show_header=True,
            header_style="bold blue",
            border_style="bright_blue"
        )
        
        table.add_column("Asset", style="cyan", width=12)
        table.add_column("Signal", style="bold", width=15)
        table.add_column("Confidence", style="green", width=12)
        table.add_column("Duration", style="yellow", width=10)
        table.add_column("Source", style="dim", width=18)
        table.add_column("Expires In", style="magenta", width=12)
        
        if not signals:
            table.add_row(
                "---", "No Active Signals", "---", "---", "---", "---"
            )
            return table
        
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
            if time_to_expiry.total_seconds() > 0:
                expires_text = f"{int(time_to_expiry.total_seconds())}s"
                expires_style = "magenta"
            else:
                expires_text = "EXPIRED"
                expires_style = "red"
            
            table.add_row(
                signal.asset.replace('_otc', ''),
                f"[{signal_style}]{signal_text}[/{signal_style}]",
                f"{signal.confidence:.1%}",
                f"{signal.duration}s",
                signal.source,
                f"[{expires_style}]{expires_text}[/{expires_style}]"
            )
        
        return table
    
    def create_market_status_table(self) -> Table:
        """Create market status overview"""
        table = Table(
            title="📊 Market Overview",
            show_header=True,
            header_style="bold cyan",
            border_style="cyan"
        )
        
        table.add_column("Asset", style="white")
        table.add_column("Trend", style="bold")
        table.add_column("Volatility", style="yellow")
        table.add_column("Status", style="green")
        
        for i, asset in enumerate(self.otc_assets[:8]):  # Show first 8 assets
            trend = self.market_trend[asset]
            volatility = self.volatility[asset]
            
            # Style trend
            if trend == "bullish":
                trend_text = "[green]📈 Bullish[/green]"
            elif trend == "bearish":
                trend_text = "[red]📉 Bearish[/red]"
            else:
                trend_text = "[yellow]➡️ Neutral[/yellow]"
            
            # Style volatility
            if volatility > 0.7:
                vol_text = "[red]High[/red]"
            elif volatility > 0.4:
                vol_text = "[yellow]Medium[/yellow]"
            else:
                vol_text = "[green]Low[/green]"
            
            table.add_row(
                asset.replace('_otc', ''),
                trend_text,
                vol_text,
                "[green]🟢 Active[/green]"
            )
        
        return table
    
    def create_statistics_panel(self, signals: List[DemoOTCSignal]) -> Panel:
        """Create statistics panel"""
        total_signals = len(signals)
        call_signals = len([s for s in signals if 'CALL' in s.signal_type])
        put_signals = len([s for s in signals if 'PUT' in s.signal_type])
        strong_signals = len([s for s in signals if 'STRONG' in s.signal_type])
        avg_confidence = sum(s.confidence for s in signals) / total_signals if total_signals > 0 else 0
        
        stats_text = f"""
[bold cyan]📊 Signal Statistics[/bold cyan]

[green]Total Active Signals:[/green] {total_signals}
[green]Call Signals:[/green] {call_signals} 📈
[red]Put Signals:[/red] {put_signals} 📉
[yellow]Strong Signals:[/yellow] {strong_signals} ⚡
[blue]Average Confidence:[/blue] {avg_confidence:.1%}

[dim]Last Update: {datetime.now().strftime('%H:%M:%S')}[/dim]
        """
        
        return Panel(
            stats_text.strip(),
            title="📈 Statistics",
            border_style="green"
        )
    
    def create_dashboard(self, signals: List[DemoOTCSignal]) -> Layout:
        """Create a comprehensive dashboard"""
        layout = Layout()
        
        # Create header
        header_text = Text("Quotex OTC Market Signals", style="bold magenta")
        header_text.append(" - DEMO MODE", style="bold red")
        header_text.append(f" | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", style="dim")
        
        header = Panel(
            Align.center(header_text),
            style="blue",
            title="🎯 Trading Dashboard"
        )
        
        # Create main content
        signals_table = self.create_signals_table(signals)
        market_table = self.create_market_status_table()
        stats_panel = self.create_statistics_panel(signals)
        
        # Layout structure
        layout.split_column(
            Layout(header, size=3),
            Layout(signals_table, name="signals"),
            Layout.split_row(
                Layout(market_table, name="market"),
                Layout(stats_panel, name="stats")
            )
        )
        
        return layout
    
    def filter_valid_signals(self, signals: List[DemoOTCSignal]) -> List[DemoOTCSignal]:
        """Filter out expired signals"""
        valid_signals = [s for s in signals if s.is_valid()]
        return sorted(valid_signals, key=lambda x: x.confidence, reverse=True)
    
    async def run_demo(self, update_interval: int = 10):
        """Run the demo signal system"""
        self.running = True
        
        self.console.print("🚀 Starting Quotex OTC Market Signals Demo", style="bold green")
        self.console.print("This is a demonstration - signals are simulated!", style="yellow")
        self.console.print()
        
        try:
            with Live(
                self.create_dashboard([]), 
                refresh_per_second=1, 
                screen=True
            ) as live:
                while self.running:
                    try:
                        # Update market conditions
                        self.update_market_conditions()
                        
                        # Generate new signals occasionally
                        if random.random() < 0.3:  # 30% chance each update
                            new_signals = self.generate_demo_signals()
                            self.signals.extend(new_signals)
                        
                        # Filter valid signals
                        self.signals = self.filter_valid_signals(self.signals)
                        
                        # Keep only top 10 signals
                        if len(self.signals) > 10:
                            self.signals = self.signals[:10]
                        
                        # Update display
                        live.update(self.create_dashboard(self.signals))
                        
                        # Save to history
                        self.signal_history.append({
                            'timestamp': datetime.now().isoformat(),
                            'signals': [s.to_dict() for s in self.signals]
                        })
                        
                        # Keep only last 100 entries
                        if len(self.signal_history) > 100:
                            self.signal_history = self.signal_history[-100:]
                        
                        # Wait for next update
                        await asyncio.sleep(update_interval)
                        
                    except Exception as e:
                        self.console.print(f"❌ Error in demo: {e}", style="red")
                        await asyncio.sleep(5)
                        
        except KeyboardInterrupt:
            self.console.print("\n🛑 Demo stopped by user", style="yellow")
        finally:
            self.running = False
            self.save_demo_history()
    
    def save_demo_history(self):
        """Save demo signal history"""
        try:
            with open('demo_signals_history.json', 'w') as f:
                json.dump(self.signal_history, f, indent=2)
            self.console.print("✅ Demo history saved to demo_signals_history.json", style="green")
        except Exception as e:
            self.console.print(f"❌ Error saving demo history: {e}", style="red")

async def main():
    """Main demo function"""
    console.print("🎯 Quotex OTC Market Signals - DEMO MODE", style="bold blue")
    console.print("This demonstration shows how the real system would work", style="dim")
    console.print("Press Ctrl+C to stop the demo", style="yellow")
    console.print()
    
    # Create demo generator
    demo = DemoSignalGenerator()
    
    try:
        # Run the demo
        await demo.run_demo(update_interval=8)  # Faster updates for demo
    except Exception as e:
        console.print(f"❌ Demo error: {e}", style="red")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Demo ended!")
    except Exception as e:
        print(f"❌ Error: {e}")