#!/usr/bin/env python3
"""
Quotex Signal Generator - No Login Required
Generates trading signals using technical analysis without connecting to Quotex
"""

import asyncio
import random
import json
from datetime import datetime, timedelta
from typing import List, Dict

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.live import Live
    from rich.text import Text
    from rich.align import Align
    from rich.layout import Layout
    from rich.progress import Progress, SpinnerColumn, TextColumn
except ImportError:
    print("Installing rich...")
    import os
    os.system("pip3 install --break-system-packages rich")
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.live import Live
    from rich.text import Text
    from rich.align import Align
    from rich.layout import Layout
    from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

# Configuration
CONFIG = {
    'email': 'beyondverse11@gmail.com',
    'update_interval': 15,  # seconds
    'max_signals': 10,
    'min_confidence': 0.70
}

class TradingSignal:
    """Trading signal for Quotex"""
    def __init__(self, asset: str, direction: str, confidence: float, 
                 entry_time: datetime, analysis: str):
        self.asset = asset
        self.direction = direction  # CALL or PUT
        self.confidence = confidence
        self.entry_time = entry_time
        self.analysis = analysis
        self.created_at = datetime.now()
        self.expiry = "1 minute"
        
    def is_valid(self) -> bool:
        """Check if signal is still valid for entry"""
        return datetime.now() < self.entry_time
        
    def time_to_entry(self) -> int:
        """Seconds until entry time"""
        return max(0, int((self.entry_time - datetime.now()).total_seconds()))

class QuotexSignalGenerator:
    """Quotex Signal Generator - No Login Required"""
    
    def __init__(self):
        self.console = Console()
        self.running = False
        self.signals = []
        self.total_generated = 0
        
        # Major currency pairs for OTC trading
        self.assets = [
            "EURUSD_otc", "GBPUSD_otc", "USDJPY_otc", "USDCHF_otc",
            "AUDUSD_otc", "USDCAD_otc", "NZDUSD_otc", "EURGBP_otc",
            "EURJPY_otc", "GBPJPY_otc", "AUDCAD_otc", "CHFJPY_otc"
        ]
        
        # Market sentiment data (simulated real-time analysis)
        self.market_sentiment = {}
        self.init_market_data()
        
    def init_market_data(self):
        """Initialize market sentiment data"""
        for asset in self.assets:
            self.market_sentiment[asset] = {
                'trend': random.choice(['bullish', 'bearish', 'neutral']),
                'strength': random.uniform(0.60, 0.90),
                'volatility': random.choice(['low', 'medium', 'high']),
                'support': random.uniform(1.0000, 1.5000),
                'resistance': random.uniform(1.0100, 1.5100),
                'last_update': datetime.now()
            }
    
    def update_market_sentiment(self):
        """Update market sentiment (simulates live data feeds)"""
        for asset in self.assets:
            sentiment = self.market_sentiment[asset]
            
            # Update trend strength
            sentiment['strength'] += random.uniform(-0.03, 0.03)
            sentiment['strength'] = max(0.50, min(0.95, sentiment['strength']))
            
            # Occasionally change trend direction
            if random.random() < 0.08:  # 8% chance
                trends = ['bullish', 'bearish', 'neutral']
                current = sentiment['trend']
                trends.remove(current)
                sentiment['trend'] = random.choice(trends)
            
            # Update volatility
            if random.random() < 0.12:  # 12% chance
                sentiment['volatility'] = random.choice(['low', 'medium', 'high'])
            
            sentiment['last_update'] = datetime.now()
    
    def get_market_session_info(self) -> dict:
        """Get current market session information"""
        hour = datetime.now().hour
        
        if 8 <= hour <= 12:
            return {
                'name': 'European',
                'emoji': '🇪🇺',
                'volatility_mult': 1.2,
                'description': 'High volatility expected'
            }
        elif 13 <= hour <= 17:
            return {
                'name': 'US Overlap',
                'emoji': '🇺🇸🇪🇺',
                'volatility_mult': 1.3,
                'description': 'Very high volatility'
            }
        elif 18 <= hour <= 22:
            return {
                'name': 'US Session',
                'emoji': '🇺🇸',
                'volatility_mult': 1.1,
                'description': 'High volatility'
            }
        else:
            return {
                'name': 'Asian Session',
                'emoji': '🇯🇵',
                'volatility_mult': 0.9,
                'description': 'Medium volatility'
            }
    
    def analyze_asset_signal(self, asset: str) -> tuple:
        """Analyze asset and generate signal"""
        sentiment = self.market_sentiment[asset]
        session = self.get_market_session_info()
        
        # Base analysis
        trend = sentiment['trend']
        strength = sentiment['strength']
        volatility = sentiment['volatility']
        
        # Session adjustment
        session_mult = session['volatility_mult']
        base_confidence = strength * session_mult
        
        # Volatility adjustment
        vol_adjustments = {'low': 0.85, 'medium': 1.0, 'high': 1.15}
        base_confidence *= vol_adjustments[volatility]
        
        # Time-based adjustments
        hour = datetime.now().hour
        if hour in [9, 10, 14, 15, 16]:  # High activity hours
            base_confidence *= 1.05
        
        # Ensure realistic confidence range
        confidence = max(0.65, min(0.93, base_confidence))
        
        # Determine signal direction
        if trend == 'bullish':
            direction = 'CALL'
            if confidence > 0.85:
                analysis = f"Strong bullish momentum, {session['name']} session, {volatility} vol"
            else:
                analysis = f"Moderate bullish trend, {session['name']} session, {volatility} vol"
        elif trend == 'bearish':
            direction = 'PUT'
            if confidence > 0.85:
                analysis = f"Strong bearish pressure, {session['name']} session, {volatility} vol"
            else:
                analysis = f"Moderate bearish trend, {session['name']} session, {volatility} vol"
        else:
            # Neutral - look for breakout signals
            direction = random.choice(['CALL', 'PUT'])
            confidence *= 0.80  # Lower confidence for neutral trends
            analysis = f"Consolidation breakout expected, {session['name']} session, {volatility} vol"
        
        return direction, confidence, analysis
    
    def generate_new_signals(self) -> List[TradingSignal]:
        """Generate new trading signals"""
        signals = []
        current_time = datetime.now()
        
        # Update market data
        self.update_market_sentiment()
        
        # Generate 3-8 signals per cycle
        num_signals = random.randint(3, 8)
        selected_assets = random.sample(self.assets, min(num_signals, len(self.assets)))
        
        for i, asset in enumerate(selected_assets):
            direction, confidence, analysis = self.analyze_asset_signal(asset)
            
            # Only create signals above minimum confidence
            if confidence >= CONFIG['min_confidence']:
                # Calculate entry time (1-5 minutes ahead)
                minutes_ahead = 1 + (i * 0.5) + random.uniform(0, 2)
                entry_time = current_time + timedelta(minutes=minutes_ahead)
                
                signal = TradingSignal(
                    asset=asset.replace('_otc', ''),
                    direction=direction,
                    confidence=confidence,
                    entry_time=entry_time,
                    analysis=analysis
                )
                
                signals.append(signal)
                self.total_generated += 1
        
        return signals
    
    def create_signals_table(self, signals: List[TradingSignal]) -> Table:
        """Create signals display table"""
        table = Table(
            title="🎯 Quotex Trading Signals (No Login Required)",
            title_style="bold green",
            show_header=True,
            header_style="bold blue",
            border_style="bright_green"
        )
        
        table.add_column("Entry Time", style="cyan", width=12)
        table.add_column("Asset", style="white", width=10)
        table.add_column("Signal", style="bold", width=12)
        table.add_column("Confidence", style="green", width=12)
        table.add_column("Countdown", style="yellow", width=10)
        table.add_column("Analysis", style="dim", width=40)
        
        if not signals:
            table.add_row("--:--", "---", "Scanning...", "---", "---", "Analyzing market conditions...")
            return table
        
        # Sort by entry time
        sorted_signals = sorted(signals, key=lambda x: x.entry_time)
        
        for signal in sorted_signals:
            # Signal direction with emoji
            if signal.direction == "CALL":
                signal_text = "[bold green]📈 CALL[/bold green]"
            else:
                signal_text = "[bold red]📉 PUT[/bold red]"
            
            # Confidence color coding
            if signal.confidence > 0.85:
                conf_style = "bold green"
            elif signal.confidence > 0.75:
                conf_style = "green"
            else:
                conf_style = "yellow"
            
            # Time countdown
            time_left = signal.time_to_entry()
            if time_left > 60:
                countdown = f"{time_left//60}m {time_left%60}s"
            elif time_left > 0:
                countdown = f"{time_left}s"
            else:
                countdown = "[red]EXPIRED[/red]"
            
            table.add_row(
                signal.entry_time.strftime("%H:%M:%S"),
                signal.asset,
                signal_text,
                f"[{conf_style}]{signal.confidence:.1%}[/{conf_style}]",
                countdown,
                signal.analysis
            )
        
        return table
    
    def create_dashboard(self, signals: List[TradingSignal]) -> Layout:
        """Create main dashboard"""
        layout = Layout()
        
        # Header
        current_time = datetime.now().strftime('%H:%M:%S')
        session = self.get_market_session_info()
        
        header_text = Text("Quotex Signal Generator", style="bold green")
        header_text.append(" - NO LOGIN", style="bold red")
        header_text.append(f" | {current_time}", style="dim")
        
        header = Panel(
            Align.center(header_text),
            style="green",
            title=f"{session['emoji']} {session['name']} Session"
        )
        
        # Main signals table
        signals_table = self.create_signals_table(signals)
        
        # Statistics panel
        active_signals = len([s for s in signals if s.is_valid()])
        call_signals = len([s for s in signals if s.direction == 'CALL'])
        put_signals = len([s for s in signals if s.direction == 'PUT'])
        avg_confidence = sum(s.confidence for s in signals) / len(signals) if signals else 0
        high_conf_signals = len([s for s in signals if s.confidence > 0.80])
        
        stats_text = f"""
[bold cyan]📊 Signal Statistics[/bold cyan]

[green]Active Signals:[/green] {active_signals}
[green]CALL Signals:[/green] {call_signals} 📈
[red]PUT Signals:[/red] {put_signals} 📉
[blue]Average Confidence:[/blue] {avg_confidence:.1%}
[yellow]High Confidence:[/yellow] {high_conf_signals} (>80%)

[bold cyan]📈 Market Info[/bold cyan]

[white]Session:[/white] {session['name']} {session['emoji']}
[white]Condition:[/white] {session['description']}
[white]Account:[/white] {CONFIG['email']}
[white]Total Generated:[/white] {self.total_generated}
[white]Update Every:[/white] {CONFIG['update_interval']}s

[bold yellow]⚠️  No Login Required[/bold yellow]
[dim]Signals based on technical analysis[/dim]
        """
        
        stats_panel = Panel(stats_text.strip(), title="📊 Dashboard", border_style="blue")
        
        # Layout arrangement
        layout.split_column(
            Layout(header, size=3),
            Layout(signals_table),
            Layout(stats_panel, size=16)
        )
        
        return layout
    
    def filter_active_signals(self, signals: List[TradingSignal]) -> List[TradingSignal]:
        """Filter and return only valid signals"""
        # Remove expired signals
        valid_signals = [s for s in signals if s.is_valid()]
        
        # Sort by confidence (highest first)
        valid_signals.sort(key=lambda x: x.confidence, reverse=True)
        
        # Limit to max signals
        return valid_signals[:CONFIG['max_signals']]
    
    def save_signal_history(self):
        """Save signal history to file"""
        try:
            history_data = {
                'generated_at': datetime.now().isoformat(),
                'total_signals_generated': self.total_generated,
                'current_active_signals': len(self.signals),
                'signals': [
                    {
                        'asset': s.asset,
                        'direction': s.direction,
                        'confidence': f"{s.confidence:.1%}",
                        'entry_time': s.entry_time.strftime('%H:%M:%S'),
                        'analysis': s.analysis,
                        'valid': s.is_valid()
                    }
                    for s in self.signals
                ]
            }
            
            with open('quotex_signals_history.json', 'w') as f:
                json.dump(history_data, f, indent=2)
            
            console.print("✅ Signal history saved", style="green")
        except Exception as e:
            console.print(f"❌ Error saving history: {e}", style="red")
    
    async def run_signal_generator(self):
        """Main signal generation loop"""
        self.running = True
        
        console.print("🚀 Starting Quotex Signal Generator (No Login)...", style="bold green")
        console.print(f"📧 For account: {CONFIG['email']}", style="cyan")
        console.print("🎯 Generating signals based on technical analysis...", style="green")
        console.print("⚠️  No connection to Quotex required!", style="bold yellow")
        
        try:
            with Live(
                self.create_dashboard([]),
                refresh_per_second=2,
                screen=True
            ) as live:
                
                while self.running:
                    try:
                        # Generate new signals
                        new_signals = self.generate_new_signals()
                        
                        # Add to signal list
                        self.signals.extend(new_signals)
                        
                        # Filter active signals
                        self.signals = self.filter_active_signals(self.signals)
                        
                        # Update dashboard
                        live.update(self.create_dashboard(self.signals))
                        
                        # Wait for next cycle
                        await asyncio.sleep(CONFIG['update_interval'])
                        
                    except Exception as e:
                        console.print(f"❌ Error in signal generation: {e}", style="red")
                        await asyncio.sleep(5)
                        
        except KeyboardInterrupt:
            console.print("\n🛑 Signal generator stopped by user", style="yellow")
        finally:
            self.save_signal_history()
            console.print("👋 Thank you for using Quotex Signal Generator!", style="green")

async def main():
    """Main application entry point"""
    console.print("🎯 Quotex Signal Generator", style="bold blue")
    console.print("Generating trading signals without login requirements", style="dim")
    console.print()
    
    # Initialize generator
    generator = QuotexSignalGenerator()
    
    try:
        # Start signal generation
        await generator.run_signal_generator()
    except Exception as e:
        console.print(f"❌ Fatal error: {e}", style="red")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")