#!/usr/bin/env python3
"""
Deriv AI Trading Bot - Main Entry Point
Crypto, Forex, and Gold Trading with 70-80% Win Probability
"""

import sys
import argparse
import logging
from config import Config
from trading_bot import TradingBot

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/trading_bot.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def print_banner():
    """Print ASCII art banner"""
    banner = """
    ╔═══════════════════════════════════════════════════╗
    ║                                                   ║
    ║       DERIV AI TRADING BOT - EZE AI DESIGN       ║
    ║                                                   ║
    ║   Crypto | Forex | Gold Trading                 ║
    ║   AI Prediction | 70-80% Win Probability        ║
    ║   Low Risk Management | Recovery X2             ║
    ║                                                   ║
    ╚═══════════════════════════════════════════════════╝
    """
    print(banner)

def run_cli_mode(bot):
    """Run bot in CLI interactive mode"""
    print("\n" + "="*50)
    print("TRADING BOT CLI MODE")
    print("="*50)
    print("\nCommands:")
    print("  start     - Start the trading bot")
    print("  stop      - Stop the trading bot")
    print("  pause     - Pause trading")
    print("  resume    - Resume trading")
    print("  status    - Show bot status")
    print("  stats     - Show statistics")
    print("  summary   - Show performance summary")
    print("  trades    - Show recent trades")
    print("  help      - Show this help")
    print("  exit      - Exit CLI\n")
    
    while True:
        try:
            cmd = input("bot> ").strip().lower()
            
            if cmd == 'start':
                print("Starting bot...")
                if bot.start():
                    print("✓ Bot started successfully")
                else:
                    print("✗ Failed to start bot")
            
            elif cmd == 'stop':
                print("Stopping bot...")
                if bot.stop():
                    print("✓ Bot stopped successfully")
                else:
                    print("✗ Failed to stop bot")
            
            elif cmd == 'pause':
                if bot.running:
                    bot.pause()
                    print("✓ Bot paused")
                else:
                    print("✗ Bot is not running")
            
            elif cmd == 'resume':
                if bot.running:
                    bot.resume()
                    print("✓ Bot resumed")
                else:
                    print("✗ Bot is not running")
            
            elif cmd == 'status':
                if bot.running:
                    status = bot.get_status()
                    print("\n" + str(status) + "\n")
                else:
                    print("✗ Bot is not running")
            
            elif cmd == 'stats':
                if bot.risk_manager:
                    print(bot.risk_manager.get_risk_summary())
                else:
                    print("✗ Bot is not running")
            
            elif cmd == 'summary':
                if bot.running:
                    print(bot.get_performance_summary())
                else:
                    print("✗ Bot is not running")
            
            elif cmd == 'trades':
                if bot.database:
                    trades = bot.database.get_trade_history(limit=10)
                    if trades:
                        print("\nRecent Trades:")
                        for trade in trades:
                            print(f"  {trade['trade_id']}: {trade['symbol']} {trade['contract_type']} - ${trade['stake']:.2f} - {trade['status']}")
                    else:
                        print("No trades recorded")
                else:
                    print("✗ Bot is not running")
            
            elif cmd == 'help':
                print("\nCommands:")
                print("  start     - Start the trading bot")
                print("  stop      - Stop the trading bot")
                print("  pause     - Pause trading")
                print("  resume    - Resume trading")
                print("  status    - Show bot status")
                print("  stats     - Show statistics")
                print("  summary   - Show performance summary")
                print("  trades    - Show recent trades")
                print("  help      - Show this help")
                print("  exit      - Exit CLI\n")
            
            elif cmd == 'exit':
                print("Exiting...")
                if bot.running:
                    bot.stop()
                break
            
            else:
                print("Unknown command. Type 'help' for available commands.")
        
        except KeyboardInterrupt:
            print("\n\nExiting...")
            if bot.running:
                bot.stop()
            break
        except Exception as e:
            logger.error(f"CLI error: {e}")
            print(f"Error: {e}")

def main():
    """Main entry point"""
    print_banner()
    
    parser = argparse.ArgumentParser(
        description='Deriv AI Trading Bot',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --cli                # Run in CLI mode
  python main.py --dashboard          # Run web dashboard
  python main.py --auto               # Run in automatic mode
        """
    )
    
    parser.add_argument(
        '--mode',
        choices=['cli', 'dashboard', 'auto'],
        default='dashboard',
        help='Execution mode (default: dashboard)'
    )
    
    parser.add_argument(
        '--cli',
        action='store_true',
        help='Run in CLI interactive mode'
    )
    
    parser.add_argument(
        '--dashboard',
        action='store_true',
        help='Run web dashboard'
    )
    
    parser.add_argument(
        '--auto',
        action='store_true',
        help='Run in automatic mode (no dashboard)'
    )
    
    parser.add_argument(
        '--config',
        help='Path to config file'
    )
    
    args = parser.parse_args()
    
    # Validate configuration
    try:
        Config.validate()
        logger.info("Configuration validated successfully")
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        print(f"❌ Configuration Error: {e}")
        sys.exit(1)
    
    # Create bot instance
    bot = TradingBot()
    
    # Determine mode
    if args.cli or args.mode == 'cli':
        logger.info("Running in CLI mode")
        run_cli_mode(bot)
    
    elif args.dashboard or args.mode == 'dashboard':
        logger.info("Running in Dashboard mode")
        print("Starting web dashboard on http://localhost:5000")
        print("Press Ctrl+C to stop\n")
        try:
            from dashboard import app, Config as DashConfig
            app.run(
                host='0.0.0.0',
                port=DashConfig.FLASK_PORT,
                debug=DashConfig.FLASK_DEBUG
            )
        except KeyboardInterrupt:
            print("\n\nShutting down...")
            if bot.running:
                bot.stop()
    
    elif args.auto or args.mode == 'auto':
        logger.info("Running in Automatic mode")
        print("Starting bot in automatic mode...")
        if bot.start():
            print("✓ Bot started successfully")
            print("Bot is running. Press Ctrl+C to stop\n")
            try:
                import time
                while bot.running:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n\nStopping bot...")
                bot.stop()
                print("✓ Bot stopped")
        else:
            print("✗ Failed to start bot")
            sys.exit(1)

if __name__ == '__main__':
    main()
