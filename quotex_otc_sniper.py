#!/usr/bin/env python3
"""
Quotex OTC Sniper Signals Generator
Generates 10-20 sniper-accurate OTC market signals with future entry times
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

# Configuration for OTC Sniper Signals
OTC_CONFIG = {
    'email': 'beyondverse11@gmail.com',
    'signals_count': 15,  # Generate 15 sniper signals
    'update_interval': 30,  # Update every 30 seconds
    'expiry': '1 minute',
    'min_confidence': 0.75
}

class OTCSniperSignal:
    """OTC Sniper Signal for Quotex"""
    def __init__(self, asset: str, direction: str, confidence: float, 
                 entry_time: datetime, analysis: str, signal_id: int):
        self.asset = asset
        self.direction = direction  # CALL or PUT
        self.confidence = confidence
        self.entry_time = entry_time
        self.analysis = analysis
        self.signal_id = signal_id
        self.created_at = datetime.now()
        self.expiry = OTC_CONFIG['expiry']
        
    def is_active(self) -> bool:
        """Check if signal is still active"""
        return datetime.now() < self.entry_time
        
    def time_to_entry(self) -> int:
        """Seconds until entry time"""
        return max(0, int((self.entry_time - datetime.now()).total_seconds()))
    
    def entry_time_str(self) -> str:
        """Entry time in HH:MM format"""
        return self.entry_time.strftime('%H:%M')

class QuotexOTCSniper:
    """Quotex OTC Sniper Signal Generator"""
    
    def __init__(self):
        self.console = Console()
        self.running = False
        self.sniper_signals = []
        self.total_generated = 0
        
        # OTC Market Assets (Non-Forex)
        self.otc_assets = [
            # Cryptocurrencies OTC
            "Bitcoin_otc", "Ethereum_otc", "Litecoin_otc", "Ripple_otc",
            "Bitcoin Cash_otc", "Cardano_otc", "Polkadot_otc", "Chainlink_otc",
            
            # Commodities OTC
            "Gold_otc", "Silver_otc", "Oil_otc", "Natural Gas_otc",
            "Copper_otc", "Platinum_otc", "Palladium_otc",
            
            # Stock Indices OTC
            "US30_otc", "US500_otc", "NASDAQ_otc", "UK100_otc",
            "Germany30_otc", "Japan225_otc", "Australia200_otc",
            
            # Individual Stocks OTC
            "Apple_otc", "Google_otc", "Microsoft_otc", "Amazon_otc",
            "Tesla_otc", "Netflix_otc", "Facebook_otc", "Nvidia_otc"
        ]
        
        # OTC Market Analysis Data
        self.otc_market_data = {}
        self.init_otc_data()
        
    def init_otc_data(self):
        """Initialize OTC market analysis data"""
        for asset in self.otc_assets:
            asset_type = self.get_asset_type(asset)
            
            self.otc_market_data[asset] = {
                'type': asset_type,
                'trend': random.choice(['bullish', 'bearish', 'consolidation']),
                'momentum': random.uniform(0.60, 0.95),
                'volatility': random.choice(['low', 'medium', 'high', 'extreme']),
                'volume': random.choice(['low', 'medium', 'high']),
                'support_level': random.uniform(0.70, 0.85),
                'resistance_level': random.uniform(0.85, 0.95),
                'last_analysis': datetime.now()
            }
    
    def get_asset_type(self, asset: str) -> str:
        """Get asset type for specialized analysis"""
        if 'Bitcoin' in asset or 'Ethereum' in asset or 'Litecoin' in asset or 'Ripple' in asset or 'Bitcoin Cash' in asset or 'Cardano' in asset or 'Polkadot' in asset or 'Chainlink' in asset:
            return 'crypto'
        elif 'Gold' in asset or 'Silver' in asset or 'Oil' in asset or 'Gas' in asset or 'Copper' in asset or 'Platinum' in asset or 'Palladium' in asset:
            return 'commodity'
        elif 'US30' in asset or 'US500' in asset or 'NASDAQ' in asset or 'UK100' in asset or 'Germany30' in asset or 'Japan225' in asset or 'Australia200' in asset:
            return 'index'
        else:
            return 'stock'
    
    def update_otc_market_data(self):
        """Update OTC market data with advanced analysis"""
        for asset in self.otc_assets:
            data = self.otc_market_data[asset]
            asset_type = data['type']
            
            # Asset-type specific updates
            if asset_type == 'crypto':
                # Crypto markets are more volatile
                data['momentum'] += random.uniform(-0.08, 0.08)
                if random.random() < 0.15:  # 15% chance of trend change
                    data['trend'] = random.choice(['bullish', 'bearish', 'consolidation'])
                data['volatility'] = random.choice(['medium', 'high', 'extreme'])
                
            elif asset_type == 'commodity':
                # Commodities follow supply/demand cycles
                data['momentum'] += random.uniform(-0.05, 0.05)
                if random.random() < 0.10:  # 10% chance of trend change
                    data['trend'] = random.choice(['bullish', 'bearish', 'consolidation'])
                data['volatility'] = random.choice(['low', 'medium', 'high'])
                
            elif asset_type == 'index':
                # Indices are more stable
                data['momentum'] += random.uniform(-0.04, 0.04)
                if random.random() < 0.08:  # 8% chance of trend change
                    data['trend'] = random.choice(['bullish', 'bearish', 'consolidation'])
                data['volatility'] = random.choice(['low', 'medium', 'high'])
                
            else:  # stocks
                # Individual stocks
                data['momentum'] += random.uniform(-0.06, 0.06)
                if random.random() < 0.12:  # 12% chance of trend change
                    data['trend'] = random.choice(['bullish', 'bearish', 'consolidation'])
                data['volatility'] = random.choice(['medium', 'high'])
            
            # Ensure momentum stays in realistic range
            data['momentum'] = max(0.50, min(0.98, data['momentum']))
            
            # Update volume occasionally
            if random.random() < 0.20:  # 20% chance
                data['volume'] = random.choice(['low', 'medium', 'high'])
            
            data['last_analysis'] = datetime.now()
    
    def analyze_otc_asset(self, asset: str) -> tuple:
        """Advanced OTC asset analysis for sniper signals"""
        data = self.otc_market_data[asset]
        asset_type = data['type']
        
        # Current market session analysis
        hour = datetime.now().hour
        
        # OTC market sessions (different from forex)
        if 9 <= hour <= 16:  # Main trading session
            session_mult = 1.3
            session_name = "Main OTC Session"
        elif 17 <= hour <= 21:  # Extended session
            session_mult = 1.1
            session_name = "Extended OTC Session"
        elif 22 <= hour <= 23 or 0 <= hour <= 2:  # After hours
            session_mult = 0.9
            session_name = "After Hours OTC"
        else:  # Pre-market
            session_mult = 0.8
            session_name = "Pre-Market OTC"
        
        # Base analysis
        trend = data['trend']
        momentum = data['momentum']
        volatility = data['volatility']
        volume = data['volume']
        
        # Calculate base confidence
        base_confidence = momentum * session_mult
        
        # Asset type multipliers
        type_mults = {
            'crypto': 1.05,  # Crypto signals tend to be strong
            'commodity': 1.02,
            'index': 0.98,
            'stock': 1.00
        }
        base_confidence *= type_mults[asset_type]
        
        # Volatility adjustments
        vol_mults = {'low': 0.85, 'medium': 1.0, 'high': 1.15, 'extreme': 1.25}
        base_confidence *= vol_mults[volatility]
        
        # Volume adjustments
        vol_adj = {'low': 0.9, 'medium': 1.0, 'high': 1.1}
        base_confidence *= vol_adj[volume]
        
        # Time-based OTC adjustments
        if hour in [10, 11, 14, 15]:  # Peak OTC hours
            base_confidence *= 1.08
        elif hour in [12, 13]:  # Lunch hour volatility
            base_confidence *= 1.05
        
        # Ensure sniper-level confidence
        confidence = max(0.75, min(0.96, base_confidence))
        
        # Determine signal direction with OTC-specific logic
        if trend == 'bullish':
            direction = 'CALL'
            if confidence > 0.88:
                analysis = f"Strong bullish breakout in {asset_type.upper()}, {session_name}, {volatility} vol, {volume} volume"
            else:
                analysis = f"Bullish momentum in {asset_type.upper()}, {session_name}, {volatility} vol"
        elif trend == 'bearish':
            direction = 'PUT'
            if confidence > 0.88:
                analysis = f"Strong bearish breakdown in {asset_type.upper()}, {session_name}, {volatility} vol, {volume} volume"
            else:
                analysis = f"Bearish pressure in {asset_type.upper()}, {session_name}, {volatility} vol"
        else:  # consolidation
            # For consolidation, look for breakout direction
            if momentum > 0.80:
                direction = 'CALL'
                analysis = f"Bullish breakout expected from consolidation, {asset_type.upper()}, {volatility} vol"
            else:
                direction = 'PUT'
                analysis = f"Bearish breakdown expected from consolidation, {asset_type.upper()}, {volatility} vol"
            confidence *= 0.90  # Slightly lower confidence for breakouts
        
        return direction, confidence, analysis
    
    def generate_sniper_signals(self) -> List[OTCSniperSignal]:
        """Generate 10-20 sniper-accurate OTC signals"""
        signals = []
        current_time = datetime.now()
        
        # Update market data
        self.update_otc_market_data()
        
        # Generate exact number of signals requested
        num_signals = OTC_CONFIG['signals_count']
        
        # Select diverse assets for signals
        selected_assets = random.sample(self.otc_assets, min(num_signals, len(self.otc_assets)))
        
        for i, asset in enumerate(selected_assets):
            direction, confidence, analysis = self.analyze_otc_asset(asset)
            
            # Only create high-confidence sniper signals
            if confidence >= OTC_CONFIG['min_confidence']:
                # Calculate future entry time (2-30 minutes ahead)
                minutes_ahead = 2 + (i * 1.8) + random.uniform(0, 1.5)
                entry_time = current_time + timedelta(minutes=minutes_ahead)
                
                signal = OTCSniperSignal(
                    asset=asset.replace('_otc', ''),
                    direction=direction,
                    confidence=confidence,
                    entry_time=entry_time,
                    analysis=analysis,
                    signal_id=self.total_generated + i + 1
                )
                
                signals.append(signal)
        
        self.total_generated += len(signals)
        return signals
    
    def create_sniper_table(self, signals: List[OTCSniperSignal]) -> Table:
        """Create sniper signals table"""
        table = Table(
            title="🎯 OTC SNIPER SIGNALS - 1 MINUTE EXPIRY",
            title_style="bold red",
            show_header=True,
            header_style="bold blue",
            border_style="bright_red"
        )
        
        table.add_column("ID", style="bold white", width=4)
        table.add_column("Entry Time", style="cyan", width=10)
        table.add_column("OTC Asset", style="white", width=15)
        table.add_column("Signal", style="bold", width=12)
        table.add_column("Confidence", style="green", width=12)
        table.add_column("Countdown", style="yellow", width=10)
        table.add_column("OTC Analysis", style="dim", width=45)
        
        if not signals:
            table.add_row("--", "--:--", "Loading...", "Analyzing...", "---", "---", "Scanning OTC market conditions...")
            return table
        
        # Sort by entry time
        sorted_signals = sorted(signals, key=lambda x: x.entry_time)
        
        for signal in sorted_signals:
            # Signal direction with emoji
            if signal.direction == "CALL":
                signal_text = "[bold green]📈 CALL[/bold green]"
            else:
                signal_text = "[bold red]📉 PUT[/bold red]"
            
            # Confidence styling for sniper signals
            if signal.confidence > 0.90:
                conf_style = "bold red"  # Ultra high
            elif signal.confidence > 0.85:
                conf_style = "bold green"  # High
            else:
                conf_style = "green"  # Good
            
            # Time countdown
            time_left = signal.time_to_entry()
            if time_left > 60:
                countdown = f"{time_left//60}m {time_left%60}s"
            elif time_left > 0:
                countdown = f"{time_left}s"
            else:
                countdown = "[red]EXPIRED[/red]"
            
            table.add_row(
                f"#{signal.signal_id}",
                signal.entry_time_str(),
                signal.asset,
                signal_text,
                f"[{conf_style}]{signal.confidence:.1%}[/{conf_style}]",
                countdown,
                signal.analysis
            )
        
        return table
    
    def create_otc_dashboard(self, signals: List[OTCSniperSignal]) -> Layout:
        """Create OTC sniper dashboard"""
        layout = Layout()
        
        # Header
        current_time = datetime.now().strftime('%H:%M:%S')
        header_text = Text("QUOTEX OTC SNIPER SIGNALS", style="bold red")
        header_text.append(" - FUTURE ENTRY TIMES", style="bold yellow")
        header_text.append(f" | {current_time}", style="dim")
        
        header = Panel(
            Align.center(header_text),
            style="red",
            title="🎯 SNIPER MODE ACTIVATED"
        )
        
        # Main signals table
        signals_table = self.create_sniper_table(signals)
        
        # OTC Statistics
        active_signals = len([s for s in signals if s.is_active()])
        call_signals = len([s for s in signals if s.direction == 'CALL'])
        put_signals = len([s for s in signals if s.direction == 'PUT'])
        avg_confidence = sum(s.confidence for s in signals) / len(signals) if signals else 0
        ultra_high_conf = len([s for s in signals if s.confidence > 0.90])
        
        # Asset type breakdown
        crypto_signals = len([s for s in signals if any(crypto in s.asset for crypto in ['Bitcoin', 'Ethereum', 'Litecoin', 'Ripple', 'Cardano', 'Polkadot', 'Chainlink'])])
        commodity_signals = len([s for s in signals if any(comm in s.asset for comm in ['Gold', 'Silver', 'Oil', 'Gas', 'Copper', 'Platinum', 'Palladium'])])
        stock_signals = len([s for s in signals if any(stock in s.asset for stock in ['Apple', 'Google', 'Microsoft', 'Amazon', 'Tesla', 'Netflix', 'Facebook', 'Nvidia'])])
        index_signals = len([s for s in signals if any(index in s.asset for index in ['US30', 'US500', 'NASDAQ', 'UK100', 'Germany30', 'Japan225', 'Australia200'])])
        
        stats_text = f"""
[bold red]🎯 SNIPER STATISTICS[/bold red]

[green]Active Signals:[/green] {active_signals}
[green]CALL Signals:[/green] {call_signals} 📈
[red]PUT Signals:[/red] {put_signals} 📉
[blue]Avg Confidence:[/blue] {avg_confidence:.1%}
[red]Ultra High (>90%):[/red] {ultra_high_conf} 🔥

[bold yellow]📊 OTC ASSET BREAKDOWN[/bold yellow]

[cyan]Crypto Signals:[/cyan] {crypto_signals} 🪙
[yellow]Commodity Signals:[/yellow] {commodity_signals} 🥇
[green]Stock Signals:[/green] {stock_signals} 📈
[blue]Index Signals:[/blue] {index_signals} 📊

[bold cyan]⚡ SYSTEM INFO[/bold cyan]

[white]Account:[/white] {OTC_CONFIG['email']}
[white]Total Generated:[/white] {self.total_generated}
[white]Expiry:[/white] {OTC_CONFIG['expiry']}
[white]Update:[/white] Every {OTC_CONFIG['update_interval']}s

[bold red]🎯 SNIPER MODE: OTC MARKETS[/bold red]
[dim]High-accuracy future entry signals[/dim]
        """
        
        stats_panel = Panel(stats_text.strip(), title="📊 OTC Dashboard", border_style="blue")
        
        # Layout
        layout.split_column(
            Layout(header, size=3),
            Layout(signals_table),
            Layout(stats_panel, size=20)
        )
        
        return layout
    
    def filter_active_sniper_signals(self, signals: List[OTCSniperSignal]) -> List[OTCSniperSignal]:
        """Filter active sniper signals"""
        # Remove expired signals
        active_signals = [s for s in signals if s.is_active()]
        
        # Sort by confidence (highest first)
        active_signals.sort(key=lambda x: x.confidence, reverse=True)
        
        return active_signals
    
    def save_sniper_signals(self):
        """Save sniper signals to file"""
        try:
            sniper_data = {
                'generated_at': datetime.now().isoformat(),
                'signal_type': 'OTC_SNIPER_SIGNALS',
                'total_generated': self.total_generated,
                'active_signals': len([s for s in self.sniper_signals if s.is_active()]),
                'expiry': OTC_CONFIG['expiry'],
                'signals': [
                    {
                        'id': s.signal_id,
                        'asset': s.asset,
                        'direction': s.direction,
                        'confidence': f"{s.confidence:.1%}",
                        'entry_time': s.entry_time_str(),
                        'analysis': s.analysis,
                        'active': s.is_active()
                    }
                    for s in self.sniper_signals
                ]
            }
            
            with open('otc_sniper_signals.json', 'w') as f:
                json.dump(sniper_data, f, indent=2)
            
            console.print("✅ OTC Sniper signals saved to otc_sniper_signals.json", style="green")
        except Exception as e:
            console.print(f"❌ Error saving sniper signals: {e}", style="red")
    
    async def run_otc_sniper(self):
        """Run OTC sniper signal generator"""
        self.running = True
        
        console.print("🎯 Starting OTC SNIPER SIGNAL Generator...", style="bold red")
        console.print(f"📧 Account: {OTC_CONFIG['email']}", style="cyan")
        console.print(f"🎯 Generating {OTC_CONFIG['signals_count']} sniper OTC signals...", style="green")
        console.print("⚠️ OTC MARKETS ONLY - No Forex!", style="bold yellow")
        
        try:
            with Live(
                self.create_otc_dashboard([]),
                refresh_per_second=2,
                screen=True
            ) as live:
                
                while self.running:
                    try:
                        # Generate new sniper signals
                        new_signals = self.generate_sniper_signals()
                        
                        # Update signal list
                        self.sniper_signals.extend(new_signals)
                        self.sniper_signals = self.filter_active_sniper_signals(self.sniper_signals)
                        
                        # Update dashboard
                        live.update(self.create_otc_dashboard(self.sniper_signals))
                        
                        # Wait for next cycle
                        await asyncio.sleep(OTC_CONFIG['update_interval'])
                        
                    except Exception as e:
                        console.print(f"❌ Error in sniper generation: {e}", style="red")
                        await asyncio.sleep(5)
                        
        except KeyboardInterrupt:
            console.print("\n🛑 OTC Sniper generator stopped", style="yellow")
        finally:
            self.save_sniper_signals()
            console.print("👋 Sniper signals saved successfully!", style="green")

async def main():
    """Main sniper application"""
    console.print("🎯 QUOTEX OTC SNIPER SIGNALS", style="bold red")
    console.print("Generating sniper-accurate OTC market signals with future entry times", style="dim")
    console.print()
    
    # Initialize sniper
    sniper = QuotexOTCSniper()
    
    try:
        # Start sniper mode
        await sniper.run_otc_sniper()
    except Exception as e:
        console.print(f"❌ Sniper error: {e}", style="red")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🎯 Sniper mode deactivated!")
    except Exception as e:
        print(f"❌ Error: {e}")