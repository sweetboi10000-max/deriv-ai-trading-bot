# Quick Start Guide - Deriv AI Trading Bot

## 5-Minute Setup

### Prerequisites
- Python 3.9+
- Deriv API credentials (free account at deriv.com)
- Git installed

### Step 1: Clone & Setup (2 minutes)

```bash
# Clone repository
git clone https://github.com/sweetboi10000-max/deriv-ai-trading-bot.git
cd deriv-ai-trading-bot

# Run setup script
chmod +x setup.sh
./setup.sh
```

### Step 2: Add API Credentials (1 minute)

```bash
# Edit .env file with your Deriv credentials
nano .env
```

Required:
```env
DERIV_API_TOKEN=your_token_here
DERIV_ACCOUNT_ID=your_account_id_here
```

### Step 3: Run Dashboard (2 minutes)

```bash
# Activate virtual environment
source venv/bin/activate

# Start the bot
python main.py --dashboard
```

Open browser: **http://localhost:5000**

## Dashboard Controls

| Button | Action |
|--------|--------|
| ▶ Start Bot | Begin automated trading |
| ⏹ Stop Bot | Stop all trading |
| ⏸ Pause | Pause but keep connection |
| ⏯ Resume | Resume from pause |
| 🔄 Refresh | Manual update |

## Key Metrics Explained

- **Win Rate**: Percentage of profitable trades
- **Loss Streak**: Consecutive losing trades
- **Next Stake (X2)**: Recovery multiplier stake
- **Daily Loss**: Running total for the day

## Configuration Defaults

```
Win Probability: 70-80% (trades only in this range)
Initial Stake: $10
Max Stake: $500
Recovery Multiplier: X2 on losses
Daily Loss Limit: $500
Max Loss Streak: 3 consecutive losses
```

## Testing Strategy

1. **Start Small**
   ```env
   INITIAL_STAKE=1
   MAX_STAKE=10
   ```

2. **Monitor 1 Hour**
   - Watch dashboard
   - Review trades
   - Check accuracy

3. **Increase Gradually**
   - If 70%+ win rate → increase stakes
   - If <70% → review configuration
   - Adjust indicators if needed

## Troubleshooting

### Bot Won't Start
```bash
# Check API token
grep DERIV_API_TOKEN .env

# Check logs
tail -f logs/trading_bot.log
```

### No Trades Executing
- Verify MIN/MAX probability (70-80%)
- Check market data in logs
- Ensure account has balance

### High Losses
- Reduce INITIAL_STAKE
- Increase MIN_WIN_PROBABILITY
- Review market conditions

## CLI Mode (Alternative)

```bash
python main.py --cli

# Commands
start       # Start trading
status      # Check status
stats       # View statistics
trades      # Show recent trades
stop        # Stop bot
exit        # Exit CLI
```

## Docker Alternative

```bash
# Build and run with Docker
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

## Risk Reminders ⚠️

- Start with MINIMAL stakes
- Paper trade first if possible
- Never risk more than 2% per trade
- Set daily loss limits
- Monitor regularly
- AI is probabilistic, not guaranteed

## Support

Check logs for errors:
```bash
tail -f logs/trading_bot.log
```

View recent trades:
```bash
sqlite3 trading_bot.db "SELECT * FROM trades LIMIT 10;"
```

## Next Steps

1. ✅ Setup complete
2. 📖 Read full README.md
3. 🎮 Explore dashboard features
4. 💹 Start with small stakes
5. 📊 Monitor performance
6. 🔧 Optimize configuration

---

**Happy Trading! 🚀**
