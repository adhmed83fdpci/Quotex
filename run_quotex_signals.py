#!/usr/bin/env python3
"""
Quotex Signal Bot Launcher
Installs dependencies and runs the signal bot
"""

import os
import sys
import subprocess
import time

def install_dependencies():
    """Install required dependencies"""
    print("🔄 Installing dependencies...")
    
    dependencies = [
        'rich',
        'requests', 
        'asyncio',
        'websockets',
        'beautifulsoup4',
        'numpy'
    ]
    
    for dep in dependencies:
        try:
            print(f"Installing {dep}...")
            result = subprocess.run([sys.executable, '-m', 'pip', 'install', dep], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ {dep} installed successfully")
            else:
                print(f"❌ Failed to install {dep}: {result.stderr}")
        except Exception as e:
            print(f"❌ Error installing {dep}: {e}")

def check_libraries():
    """Check if the required libraries are present"""
    pyquotex_path = os.path.join(os.getcwd(), 'pyquotex-master')
    quotexapi_path = os.path.join(os.getcwd(), 'quotexapi-main')
    
    if not os.path.exists(pyquotex_path):
        print("❌ pyquotex-master directory not found!")
        return False
        
    if not os.path.exists(quotexapi_path):
        print("❌ quotexapi-main directory not found!")
        return False
    
    print("✅ Required libraries found")
    return True

def run_signal_bot():
    """Run the main signal bot"""
    print("🚀 Starting Quotex Signal Bot...")
    
    try:
        # Run the signal bot
        os.system("python3 quotex_signal_bot.py")
    except KeyboardInterrupt:
        print("\n🛑 Signal bot stopped by user")
    except Exception as e:
        print(f"❌ Error running signal bot: {e}")

def main():
    """Main launcher function"""
    print("🎯 Quotex Signal Bot Launcher")
    print("=" * 50)
    
    # Install dependencies
    install_dependencies()
    
    # Check if libraries are present
    if not check_libraries():
        print("\n❌ Required libraries not found. Please ensure:")
        print("1. pyquotex-master directory exists")
        print("2. quotexapi-main directory exists")
        return
    
    print("\n✅ All checks passed!")
    print("⏰ Starting signal bot in 3 seconds...")
    time.sleep(3)
    
    # Run the signal bot
    run_signal_bot()

if __name__ == "__main__":
    main()