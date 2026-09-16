# Troubleshooting Guide

## Common Issues & Solutions

### Issue 1: Bot Won't Start

**Error:**
```
ConfigurationError: DERIV_API_TOKEN not set
```

**Solutions:**
1. Check `.env` file exists:
   ```bash
   cat .env | grep DERIV_API_TOKEN
   ```

2. Verify token format (should be long string):
   ```bash
   echo $DERIV_API_TOKEN | wc -c  # Should be > 30 chars
   ```

3. Reload environment:
   ```bash
   source venv/bin/activate
   unset DERIV_API_TOKEN
   export DERIV_API_TOKEN="your_token_here"
   python main.py --dashboard
   ```

---

### Issue 2: No API Connection

**Error:**
```
ConnectionError: Failed to connect to Deriv API
```

**Solutions:**
1. Check internet connection:
   ```bash
   ping google.com
   curl https://api.deriv.com/api/v3 -I
   ```

2. Verify Deriv API is up (check status page):
   ```
   https://status.deriv.com
   ```

3. Test API token manually:
   ```bash
   curl -X POST https://ws.derivws.com/websockets/v3 \
     -H "Content-Type: application/json" \
     -d '{"authorize":"YOUR_TOKEN"}'
   ```

4. Check firewall/proxy settings (port 443):
   ```bash
   telnet ws.derivws.com 443
   ```

---

### Issue 3: No Trades Executing

**Symptoms:**
- Bot running but no trades
- Win rate shows 0
- Dashboard shows 0 trades

**Diagnostic Steps:**

1. Check logs:
   ```bash
   tail -50 logs/trading_bot.log | grep -E "SIGNAL|Cannot trade"
   ```

2. Verify probability settings:
   ```bash
   grep "PROBABILITY" .env
   # Should show 70 and 80
   ```

3. Check if prediction signals are generated:
   ```bash
   grep "STRONG" logs/trading_bot.log | tail -10
   ```

4. Test with debug mode:
   ```python
   # Edit main.py, add:
   logging.basicConfig(level=logging.DEBUG)
   ```

**Solutions:**

**Solution A: Relax Entry Conditions**
```env
# Current (too strict?)
MIN_WIN_PROBABILITY=0.70
MAX_WIN_PROBABILITY=0.80

# Try this
MIN_WIN_PROBABILITY=0.65
MAX_WIN_PROBABILITY=0.85
```

**Solution B: Retrain Model**
```bash
# Delete old model
rm models/trading_model*

# Restart bot to retrain
python main.py --auto
```

**Solution C: Increase Trade Frequency**
```env
MIN_TRADES_PER_DAY=1          # Reduce minimum
CANDLE_SIZE=300               # 5-minute candles (faster signals)
```

---

### Issue 4: Consistently Losing Trades

**Symptoms:**
- Win rate < 50%
- Daily losses accumulating
- Balance decreasing

**Root Causes:**
1. Model needs retraining
2. Market conditions changed
3. Configuration too aggressive
4. Symbol not suitable

**Solutions:**

**Step 1: Pause Trading**
```bash
python main.py --cli
> pause
> stats
# Review performance
```

**Step 2: Retrain Model with Fresh Data**
```bash
# Delete old model
rm models/trading_model*

# This forces retraining
python main.py --auto
```

**Step 3: Stricter Entry Conditions**
```env
# More selective entry
MIN_WIN_PROBABILITY=0.75      # Raise from 0.70
MAX_WIN_PROBABILITY=0.78      # Lower from 0.80
MAX_LOSS_STREAK=2             # Stop earlier
```

**Step 4: Test Single Symbol**
```env
# Reduce complexity
SYMBOLS=["EURUSD"]            # Most stable

# Or try
SYMBOLS=["XAUUSD"]            # Gold (less volatile)
```

**Step 5: Reduce Stakes**
```env
INITIAL_STAKE=2               # Smaller size
MAX_STAKE=20                  # Lower ceiling
MAX_DAILY_LOSS=50             # Tighter limit
```

---

### Issue 5: High Memory Usage

**Symptoms:**
```
Memory usage: 500MB+ and increasing
Bot becomes slow
```

**Causes:**
- Memory leak in prediction history
- Large database file
- Too much logging

**Solutions:**

1. Clear old database records:
   ```bash
   python -c "from database import Database; db = Database(); db.clear_old_records(7)"
   ```

2. Reduce prediction history:
   ```python
   # Edit ai_predictor.py line ~200
   self.prediction_history = self.prediction_history[-1000:]  # Keep last 1000
   ```

3. Reduce logging:
   ```env
   LOG_LEVEL=WARNING    # Instead of INFO
   ```

4. Restart bot periodically:
   ```bash
   # Add to cron (daily restart at 1 AM)
   0 1 * * * cd /path/to/bot && python main.py --auto
   ```

---

### Issue 6: Dashboard Not Loading

**Symptoms:**
```
ERR_CONNECTION_REFUSED on localhost:5000
```

**Solutions:**

1. Check if Flask is running:
   ```bash
   netstat -tlnp | grep 5000
   # Or
   lsof -i :5000
   ```

2. Port already in use:
   ```bash
   # Kill process
   kill -9 $(lsof -t -i:5000)
   
   # Or use different port
   export FLASK_PORT=8000
   python main.py --dashboard
   ```

3. Firewall blocking:
   ```bash
   # Linux
   sudo ufw allow 5000
   
   # macOS
   sudo pfctl -f /etc/pf.conf
   ```

4. Check Flask errors:
   ```bash
   python main.py --dashboard 2>&1 | head -50
   ```

---

### Issue 7: Database Corruption

**Error:**
```
SQLiteError: database disk image is malformed
```

**Solutions:**

1. Backup and repair:
   ```bash
   cp trading_bot.db trading_bot.db.bak
   sqlite3 trading_bot.db ".dump" | sqlite3 trading_bot_new.db
   mv trading_bot_new.db trading_bot.db
   ```

2. Or start fresh:
   ```bash
   rm trading_bot.db
   # Restart bot
   python main.py --auto
   ```

3. Regular backups:
   ```bash
   # Add to cron (daily)
   0 2 * * * cp /path/to/trading_bot.db /backup/trading_bot.db.$(date +%Y%m%d)
   ```

---

### Issue 8: Deriv Connection Drops

**Symptoms:**
```
WebSocket connection closed
No trades executing
```

**Solutions:**

1. Auto-reconnect (built-in):
   ```python
   # Already in deriv_api.py
   # Will reconnect automatically
   ```

2. Increase stability:
   ```env
   # Add to deriv_api.py
   RECONNECT_ATTEMPTS=5
   RECONNECT_DELAY=10  # seconds
   ```

3. Monitor connection:
   ```bash
   grep -i "connection\|error" logs/trading_bot.log
   ```

---

### Issue 9: API Rate Limits

**Error:**
```
RateLimitError: Too many requests
```

**Solutions:**

1. Reduce polling frequency:
   ```python
   # In trading_bot.py line ~180
   time.sleep(60)  # Increase from 30
   ```

2. Batch requests:
   ```python
   # Don't fetch each symbol individually
   for symbol in symbols:
       self._fetch_market_data(symbol)  # OK
   ```

3. Check API quota:
   ```bash
   # From Deriv account settings
   # Verify you have sufficient API calls
   ```

---

### Issue 10: Model File Not Found

**Error:**
```
FileNotFoundError: models/trading_model_model.pkl
```

**Solutions:**

1. Create models directory:
   ```bash
   mkdir -p models
   chmod 755 models
   ```

2. Retrain model:
   ```bash
   python -c "from ai_predictor import AIPredictor; p = AIPredictor(); p.save_model('models/trading_model')"
   ```

3. Copy from backup:
   ```bash
   cp backup/trading_model* models/
   ```

---

## Performance Monitoring

### System Resources

```bash
# Check CPU usage
top -p $(pgrep -f "python main.py")

# Check memory
ps aux | grep "python main.py"

# Check disk space
df -h

# Check database size
ls -lh trading_bot.db
```

### Bot Health Check

```bash
#!/bin/bash
# Check if bot is running
pgrep -f "python main.py" > /dev/null || echo "Bot not running!"

# Check recent trades
sqlite3 trading_bot.db "SELECT COUNT(*) FROM trades WHERE datetime(entry_time) > datetime('now', '-1 hour');"

# Check win rate
sqlite3 trading_bot.db "SELECT ROUND(100.0*SUM(CASE WHEN profit_loss > 0 THEN 1 ELSE 0 END)/COUNT(*), 2) FROM trades WHERE status='CLOSED';"
```

## Getting Help

1. **Check Logs First**
   ```bash
   tail -100 logs/trading_bot.log
   ```

2. **Test Configuration**
   ```bash
   python -c "from config import Config; Config.validate(); print('OK')"
   ```

3. **Check Database**
   ```bash
   sqlite3 trading_bot.db ".tables"
   sqlite3 trading_bot.db "SELECT COUNT(*) FROM trades;"
   ```

4. **Review Recent Trades**
   ```bash
   sqlite3 trading_bot.db "SELECT * FROM trades ORDER BY id DESC LIMIT 5;"
   ```

---

**Still having issues?** Check the GitHub Issues page or review the full documentation.
