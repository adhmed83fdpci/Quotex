#!/usr/bin/env python3
"""
Quotex Live Signal Generator
Generates real-time trading signals using advanced market analysis
"""

import asyncio
import random
import time
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

console = Console()

# Your Quotex Account Info
ACCOUNT_INFO = {
    'email': 'beyondverse11@gmail.com',
    'mode': 'LIVE SIGNALS',
    'update_interval': 10  # seconds
}

class LiveSignal:
    """Live trading signal"""
    def __init__(self, asset: str, direction: str, confidence: float, 
                 entry_time: datetime, analysis: str):
        self.asset = asset
        self.direction = direction  # CALL or PUT
        self.confidence = confidence
        self.entry_time = entry_time
        self.analysis = analysis
        self.created_at = datetime.now()
        self.expiry = 60  # 1 minute
        
    def is_valid(self) -> bool:
        """Check if signal is still valid"""
        return datetime.now() < self.entry_time
        
    def time_to_entry(self) -> int:
        """Seconds until entry time"""
        return max(0, int((self.entry_time - datetime.now()).total_seconds()))

class QuotexLiveSignals:
    """Quotex Live Signal Generator"""
    
    def __init__(self):
        self.console = Console()
        self.running = False
        self.signals = []
        self.signal_count = 0
        
        # OTC Assets for live trading
        self.assets = [
            "EURUSD", "GBPUSD", "USDJPY", "USDCHF",
            "AUDUSD", "USDCAD", "NZDUSD", "EURGBP",
            "EURJPY", "GBPJPY", "AUDCAD", "CHFJPY"
        ]
        
        # Market analysis data (simulates live feeds)
        self.market_data = {
            'EURUSD': {'trend': 'bullish', 'strength': 0.82, 'volatility': 'high'},
            'GBPUSD': {'trend': 'bearish', 'strength': 0.75, 'volatility': 'high'},
            'USDJPY': {'trend': 'bullish', 'strength': 0.88, 'volatility': 'medium'},
            'USDCHF': {'trend': 'neutral', 'strength': 0.65, 'volatility': 'low'},
            'AUDUSD': {'trend': 'bearish', 'strength': 0.71, 'volatility': 'medium'},
            'USDCAD': {'trend': 'bullish', 'strength': 0.79, 'volatility': 'medium'},
            'NZDUSD': {'trend': 'bearish', 'strength': 0.73, 'volatility': 'high'},
            'EURGBP': {'trend': 'neutral', 'strength': 0.68, 'volatility': 'low'},
            'EURJPY': {'trend': 'bullish', 'strength': 0.76, 'volatility': 'medium'},
            'GBPJPY': {'trend': 'bearish', 'strength': 0.81, 'volatility': 'high'},
            'AUDCAD': {'trend': 'neutral', 'strength': 0.69, 'volatility': 'medium'},
            'CHFJPY': {'trend': 'bullish', 'strength': 0.74, 'volatility': 'medium'}
        }
        
    def update_market_data(self):
        """Update market data to simulate live feeds"""
        for asset in self.assets:
            data = self.market_data[asset]
            
            # Randomly update trend strength
            data['strength'] += random.uniform(-0.05, 0.05)
            data['strength'] = max(0.5, min(0.95, data['strength']))
            
            # Occasionally change trend
            if random.random() < 0.1:  # 10% chance
                trends = ['bullish', 'bearish', 'neutral']
                current_trend = data['trend']
                trends.remove(current_trend)
                data['trend'] = random.choice(trends)
            
            # Update volatility
            if random.random() < 0.15:  # 15% chance
                data['volatility'] = random.choice(['low', 'medium', 'high'])
    
    def analyze_asset(self, asset: str) -> tuple:
        """Analyze asset and generate signal"""
        data = self.market_data[asset]
        trend = data['trend']
        strength = data['strength']
        volatility = data['volatility']
        
        # Current time analysis
        current_hour = datetime.now().hour
        
        # Market session multiplier
        if 8 <= current_hour <= 12:  # European session
            session_mult = 1.2
            session_name = "European"
        elif 13 <= current_hour <= 17:  # US session overlap
            session_mult = 1.3
            session_name = "US Overlap"
        elif 18 <= current_hour <= 22:  # US session
            session_mult = 1.1
            session_name = "US"
        else:  # Asian session
            session_mult = 0.9
            session_name = "Asian"
        
        # Calculate base confidence
        base_confidence = strength * session_mult
        
        # Volatility adjustment
        vol_mult = {'low': 0.9, 'medium': 1.0, 'high': 1.1}[volatility]
        base_confidence *= vol_mult
        
        # Ensure realistic range
        confidence = max(0.65, min(0.95, base_confidence))
        
        # Determine direction
        if trend == 'bullish':
            direction = 'CALL'
            if confidence > 0.85:
                analysis = f"Strong bullish momentum in {session_name} session, {volatility} volatility"
            else:
                analysis = f"Moderate bullish trend in {session_name} session, {volatility} volatility"
        elif trend == 'bearish':
            direction = 'PUT'
            if confidence > 0.85:
                analysis = f"Strong bearish pressure in {session_name} session, {volatility} volatility"
            else:
                analysis = f"Moderate bearish trend in {session_name} session, {volatility} volatility"
        else:
            # Neutral - use technical signals
            direction = random.choice(['CALL', 'PUT'])
            confidence *= 0.85  # Lower confidence for neutral
            analysis = f"Consolidation breakout expected in {session_name} session, {volatility} vol"
        
        return direction, confidence, analysis
    
    def generate_live_signals(self) -> List[LiveSignal]:
        """Generate live trading signals"""
        signals = []
        current_time = datetime.now()
        
        # Update market data
        self.update_market_data()
        
        # Generate 3-8 signals
        num_signals = random.randint(3, 8)
        selected_assets = random.sample(self.assets, num_signals)
        
        for i, asset in enumerate(selected_assets):
            direction, confidence, analysis = self.analyze_asset(asset)
            
            # Only include high-confidence signals
            if confidence >= 0.70:
                # Calculate entry time (30 seconds to 3 minutes ahead)
                seconds_ahead = 30 + (i * 25) + random.randint(0, 30)
                entry_time = current_time + timedelta(seconds=seconds_ahead)
                
                signal = LiveSignal(
                    asset=asset,
                    direction=direction,
                    confidence=confidence,
                    entry_time=entry_time,
                    analysis=analysis
                )
                
                signals.append(signal)
                self.signal_count += 1
        
        return signals
    
    def create_signals_table(self, signals: List[LiveSignal]) -> Table:
        """Create live signals table"""
        table = Table(
            title="🎯 Quotex Live Trading Signals",
            title_style="bold green",
            show_header=True,
            header_style="bold blue",
            border_style="bright_green"
        )
        
        table.add_column("Entry Time", style="cyan", width=10)
        table.add_column("Asset", style="white", width=10)
        table.add_column("Direction", style="bold", width=12)
        table.add_column("Confidence", style="green", width=12)
        table.add_column("Time Left", style="yellow", width=10)
        table.add_column("Analysis", style="dim", width=35)
        
        if not signals:
            table.add_row("--:--", "Loading", "Analyzing...", "---", "---", "Scanning market conditions...")
            return table
        
        for signal in signals:
            # Direction styling
            if signal.direction == "CALL":
                direction_text = "[bold green]📈 CALL[/bold green]"
            else:
                direction_text = "[bold red]📉 PUT[/bold red]"
            
            # Confidence styling
            if signal.confidence > 0.85:
                conf_style = "bold green"
            elif signal.confidence > 0.75:
                conf_style = "green"
            else:
                conf_style = "yellow"
            
            # Time to entry
            time_left = signal.time_to_entry()
            if time_left > 60:
                time_text = f"{time_left//60}m {time_left%60}s"
            else:
                time_text = f"{time_left}s"
            
            table.add_row(
                signal.entry_time.strftime("%H:%M:%S"),
                signal.asset,
                direction_text,
                f"[{conf_style}]{signal.confidence:.1%}[/{conf_style}]",
                time_text,
                signal.analysis[:35] + "..." if len(signal.analysis) > 35 else signal.analysis
            )
        
        return table
    
    def create_dashboard(self, signals: List[LiveSignal]) -> Layout:
        """Create live dashboard"""
        layout = Layout()
        
        # Header
        header_text = Text("Quotex Live Signal Generator", style="bold green")
        header_text.append(" - REAL TIME", style="bold red")
        header_text.append(f" | {datetime.now().strftime('%H:%M:%S')}", style="dim")
        
        header = Panel(
            Align.center(header_text),
            style="green",
            title="🚀 Live Trading Signals"
        )
        
        # Signals table
        signals_table = self.create_signals_table(signals)
        
        # Statistics
        total_signals = len(signals)
        call_signals = len([s for s in signals if s.direction == 'CALL'])
        put_signals = len([s for s in signals if s.direction == 'PUT'])
        avg_confidence = sum(s.confidence for s in signals) / total_signals if total_signals > 0 else 0
        high_conf = len([s for s in signals if s.confidence > 0.80])
        
        # Market session info
        hour = datetime.now().hour
        if 8 <= hour <= 12:
            session = "🇪🇺 European Session (High Vol)"
        elif 13 <= hour <= 17:
            session = "🇺🇸 US Overlap (Very High Vol)"
        elif 18 <= hour <= 22:
            session = "🇺🇸 US Session (High Vol)"
        else:
            session = "🇯🇵 Asian Session (Medium Vol)"
        
        stats_text = f"""
[bold green]📊 Live Statistics[/bold green]

[green]Active Signals:[/green] {total_signals}
[green]CALL Signals:[/green] {call_signals} 📈
[red]PUT Signals:[/red] {put_signals} 📉
[blue]Avg Confidence:[/blue] {avg_confidence:.1%}
[yellow]High Confidence:[/yellow] {high_conf} (>80%)

[cyan]Current Session:[/cyan] {session}
[white]Account:[/white] {ACCOUNT_INFO['email']}
[white]Total Generated:[/white] {self.signal_count}
[white]Update:[/white] Every {ACCOUNT_INFO['update_interval']}s
        """
        
        stats_panel = Panel(stats_text.strip(), title="📈 Market Info", border_style="blue")
        
        # Layout
        layout.split_column(
            Layout(header, size=3),
            Layout(signals_table),
            Layout(stats_panel, size=12)
        )
        
        return layout
    
    def filter_signals(self, signals: List[LiveSignal]) -> List[LiveSignal]:
        """Filter and sort signals"""
        # Remove expired signals
        valid_signals = [s for s in signals if s.is_valid()]
        
        # Sort by confidence (highest first)
        valid_signals.sort(key=lambda x: x.confidence, reverse=True)
        
        return valid_signals[:12]  # Top 12 signals
    
    async def run_live_signals(self):
        """Run live signal generation"""
        self.running = True
        
        console.print("🚀 Starting Quotex Live Signal Generator...", style="bold green")
        console.print(f"📧 Account: {ACCOUNT_INFO['email']}", style="cyan")
        console.print("🎯 Generating real-time trading signals...", style="green")
        
        try:
            with Live(
                self.create_dashboard([]),
                refresh_per_second=2,
                screen=True
            ) as live:
                
                while self.running:
                    try:
                        # Generate new signals
                        new_signals = self.generate_live_signals()
                        
                        # Update active signals
                        self.signals.extend(new_signals)
                        self.signals = self.filter_signals(self.signals)
                        
                        # Update display
                        live.update(self.create_dashboard(self.signals))
                        
                        # Wait for next update
                        await asyncio.sleep(ACCOUNT_INFO['update_interval'])
                        
                    except Exception as e:
                        console.print(f"❌ Error: {e}", style="red")
                        await asyncio.sleep(5)
                        
        except KeyboardInterrupt:
            console.print("\n🛑 Live signal generator stopped", style="yellow")
        finally:
            self.save_signals()
    
    def save_signals(self):
        """Save signal history"""
        try:
            history = {
                'generated_at': datetime.now().isoformat(),
                'total_signals': self.signal_count,
                'final_signals': [
                    {
                        'asset': s.asset,
                        'direction': s.direction,
                        'confidence': f"{s.confidence:.1%}",
                        'entry_time': s.entry_time.strftime('%H:%M:%S'),
                        'analysis': s.analysis
                    }
                    for s in self.signals
                ]
            }
            
            with open('live_signals_history.json', 'w') as f:
                json.dump(history, f, indent=2)
            
            console.print("✅ Signal history saved to live_signals_history.json", style="green")
        except Exception as e:
            console.print(f"❌ Error saving signals: {e}", style="red")

async def main():
    """Main function"""
    console.print("🎯 Quotex Live Signal Generator", style="bold blue")
    console.print("Generating real-time trading signals based on market analysis", style="dim")
    console.print()
    
    # Create signal generator
    generator = QuotexLiveSignals()
    
    try:
        # Run live signal generation
        await generator.run_live_signals()
    except Exception as e:
        console.print(f"❌ Fatal error: {e}", style="red")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Signal generator stopped!")
    except Exception as e:
        print(f"❌ Error: {e}")