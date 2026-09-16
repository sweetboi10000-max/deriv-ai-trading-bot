# Trading Bot Configuration Guide

## Understanding Win Probability (70-80%)

The bot ONLY executes trades when AI confidence is between 70-80%:

```
< 70% = Too uncertain, NO TRADE
70-80% = Sweet spot, EXECUTE TRADE ✓
> 80% = Over-confident, NO TRADE (avoid false signals)
```

## Risk Management Strategy

### Position Sizing

**Initial Configuration:**
```env
INITIAL_STAKE=10              # Start $10 per trade
MAX_STAKE=500                 # Never exceed $500
RISK_PERCENTAGE=2.0           # Risk 2% of balance max
MAX_POSITION_SIZE=1000        # Max single position
```

**For Aggressive Trading:**
```env
INITIAL_STAKE=50
MAX_STAKE=200
RISK_PERCENTAGE=5.0
```

**For Conservative Trading:**
```env
INITIAL_STAKE=5
MAX_STAKE=50
RISK_PERCENTAGE=1.0
```

### Recovery Strategy (X2 Multiplier)

When losses occur, bot automatically doubles stake:

```
Trade 1: Lose $10  → Loss Streak = 1
Trade 2: Stake $20 (X2)  → Loss Streak = 2
Trade 3: Stake $40 (X2)  → Loss Streak = 3 (STOP - max reached)

Once Win → Reset to INITIAL_STAKE
```

**Configuration:**
```env
MAX_LOSS_STREAK=3             # Stop after 3 losses
RECOVERY_MULTIPLIER=2.0       # X2 on each loss
```

### Daily Loss Limits

**Hard Stop at Daily Loss:**
```env
MAX_DAILY_LOSS=500            # No more trades if lost $500 today
```

Reset at midnight:
- Monitor daily P&L on dashboard
- Stops trading when limit hit
- Resumes next day

## Trading Symbols

**Default Configuration:**
```env
SYMBOLS=["EURUSD", "GBPUSD", "XAUUSD", "BTCUSD", "ETHUSD"]
```

**Symbol Details:**
- **EURUSD**: Euro/US Dollar (Forex) - Most liquid
- **GBPUSD**: British Pound/US Dollar (Forex)
- **XAUUSD**: Gold/US Dollar (Commodity)
- **BTCUSD**: Bitcoin/US Dollar (Crypto) - Volatile
- **ETHUSD**: Ethereum/US Dollar (Crypto) - Volatile

**Customize:**
```env
# Only forex
SYMBOLS=["EURUSD", "GBPUSD", "USDJPY"]

# Only crypto
SYMBOLS=["BTCUSD", "ETHUSD"]

# Only gold
SYMBOLS=["XAUUSD"]
```

## AI Model Configuration

### Model Types

**Gradient Boosting (Default - Recommended)**
```env
MODEL_TYPE=gradient_boosting
```
Pros: Better accuracy, handles non-linear patterns
Cons: Slower to train

**Random Forest (Alternative)**
```env
MODEL_TYPE=random_forest
```
Pros: Faster, less overfitting
Cons: Lower accuracy in complex markets

### Technical Indicators

Bot analyzes 20+ features:

```
Momentum:
  - RSI (14 period) - Overbought/Oversold
  - MACD - Trend following
  - Stochastic - Momentum
  - CCI - Commodity Channel Index

Volatility:
  - Bollinger Bands - Support/Resistance
  - ATR - Average True Range
  - Standard Deviation

Trend:
  - ADX - Trend Strength
  - Moving Averages (5, 10, 20, 50)
  - MA Crossovers

Volume:
  - Volume MA
  - Volume Change
```

### Prediction Period

```env
PREDICTION_PERIOD=5           # Uses last 5 candles
CANDLE_SIZE=900               # 15-minute candles
```

Total lookback = 5 × 15 min = 75 minutes

## Trade Timing

**Trade Duration:**
```env
TRADE_DURATION=3600           # 1 hour contracts
```

**Daily Limits:**
```env
MIN_TRADES_PER_DAY=5          # Minimum trades to execute
MAX_TRADES_PER_DAY=50         # Maximum trades per day
```

## Performance Optimization

### For Higher Win Rate

```env
# Stricter entry conditions
MIN_WIN_PROBABILITY=0.75      # Raise from 0.70
MAX_WIN_PROBABILITY=0.79      # Lower from 0.80

# Conservative sizing
INITIAL_STAKE=5
MAX_DAILY_LOSS=200
```

### For More Trades

```env
# More lenient entry
MIN_WIN_PROBABILITY=0.68      # Lower threshold
MAX_WIN_PROBABILITY=0.82      # Higher threshold

# Larger position
INITIAL_STAKE=25
MAX_STAKE=1000
```

### For Safer Trading

```env
# Tight loss control
MAX_LOSS_STREAK=2             # Stop after 2 losses
MAX_DAILY_LOSS=100            # Low daily limit
RECOVERY_MULTIPLIER=1.5       # Smaller recovery multiplier

# Smaller stakes
INITIAL_STAKE=2
RISK_PERCENTAGE=0.5           # Very conservative
```

## Monitoring Performance

### Key Metrics to Watch

1. **Win Rate**
   - Target: 65-75%
   - If <60%: Model needs retraining
   - If >80%: Might be overfitting

2. **Profit Factor**
   - Formula: Total Wins / Total Losses
   - Target: 1.5 or higher
   - <1.0: Losing money

3. **Drawdown**
   - Max peak-to-trough decline
   - Should stay < 20% of account

4. **Recovery Trades Success**
   - Should win 60%+ of recovery trades
   - If lower: Increase MAX_LOSS_STREAK limit

### Daily Review Checklist

- [ ] Win rate ≥ 65%
- [ ] Daily P&L > 0
- [ ] No consecutive limit hits
- [ ] Predictions align with price
- [ ] No unusual errors in logs
- [ ] Backup database if needed

## Troubleshooting Configurations

### Problem: Low Win Rate (<60%)

**Solution 1: Stricter Entry**
```env
MIN_WIN_PROBABILITY=0.73      # Higher threshold
MAX_WIN_PROBABILITY=0.78      # Narrower range
```

**Solution 2: Retrain Model**
```bash
rm models/trading_model*      # Delete old model
python main.py                # Retrain on new data
```

**Solution 3: Change Symbols**
```env
SYMBOLS=["EURUSD"]            # Test one symbol
```

### Problem: Too Few Trades

**Solution: Relax Entry Conditions**
```env
MIN_WIN_PROBABILITY=0.68
MAX_WIN_PROBABILITY=0.82
```

### Problem: Large Losses

**Solution 1: Reduce Stakes**
```env
INITIAL_STAKE=5
MAX_STAKE=100
```

**Solution 2: Tighten Loss Control**
```env
MAX_LOSS_STREAK=2
MAX_DAILY_LOSS=100
RECOVERY_MULTIPLIER=1.5
```

**Solution 3: Pause and Review**
```bash
# Use CLI
python main.py --cli
> pause
# Review configuration
> stop
```

## Advanced Tweaking

### Custom Entry Logic

Edit `trading_bot.py` line ~250:
```python
# Add custom entry filter
if prediction['probability'] > 0.75:
    # Additional confirmation
    if rsi > 50:  # RSI rising
        return True
```

### Multiple Models Ensemble

Train separate models:
```bash
cp ai_predictor.py ai_predictor_v2.py
# Modify feature selection
```

### Time-based Filtering

```python
from datetime import datetime
hour = datetime.now().hour

if 10 <= hour <= 16:  # Only trade 10am-4pm
    return can_trade()
```

## Backtesting Before Live

```bash
# Test configuration on historical data (when available)
python backtest.py --symbol EURUSD --days 30 --config .env.test
```

## Risk Calculator

**Max Risk Per Trade:**
```
Risk = Account Size × Risk % / 100
Example: $1000 × 2% = $20 max loss per trade
```

**Position Size:**
```
Stake = Risk × (100 / Win Rate)
Example: $20 × (100 / 70) = $28.57
```

**Recovery Calculation:**
```
Recovery Amount = Loss × Multiplier
Example: $20 loss × 2.0 = $40 next stake
```

---

**Remember: Test extensively with small stakes before scaling up!**
