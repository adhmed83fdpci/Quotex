#!/usr/bin/env python3
"""
REAL Quotex Signal System Launcher
Connects to your actual Quotex account and generates live trading signals
"""

import os
import sys
import subprocess
import time
from datetime import datetime

def print_banner():
    """Print startup banner"""
    print("=" * 60)
    print("🚀 REAL QUOTEX SIGNAL SYSTEM")
    print("=" * 60)
    print("📧 Account: beyondverse11@gmail.com")
    print("⚠️  MODE: REAL TRADING (NOT DEMO)")
    print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

def install_dependencies():
    """Install required dependencies quickly"""
    deps = ['rich', 'requests', 'asyncio']
    
    for dep in deps:
        try:
            __import__(dep)
        except ImportError:
            print(f"📦 Installing {dep}...")
            subprocess.run([sys.executable, '-m', 'pip', 'install', dep], 
                         capture_output=True)

def check_libraries():
    """Check if required libraries exist"""
    pyquotex_exists = os.path.exists('pyquotex-master')
    quotexapi_exists = os.path.exists('quotexapi-main')
    
    if not pyquotex_exists:
        print("❌ pyquotex-master directory not found!")
        return False
    
    if not quotexapi_exists:
        print("❌ quotexapi-main directory not found!")
        return False
    
    print("✅ Required libraries found")
    return True

def main():
    """Main launcher"""
    print_banner()
    
    print("🔄 Preparing REAL signal system...")
    
    # Install dependencies
    install_dependencies()
    
    # Check libraries
    if not check_libraries():
        print("\n❌ Setup incomplete. Please ensure:")
        print("1. pyquotex-master directory exists")
        print("2. quotexapi-main directory exists")
        input("\nPress Enter to exit...")
        return
    
    print("✅ All checks passed!")
    print("🚀 Starting REAL signal generation...")
    print("⚠️  This will connect to your REAL Quotex account!")
    print("\nPress Ctrl+C to stop the system")
    
    time.sleep(2)
    
    try:
        # Run the real signal system
        os.system("python3 real_quotex_signals.py")
    except KeyboardInterrupt:
        print("\n🛑 Signal system stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()