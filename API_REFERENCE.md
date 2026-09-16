# REST API Reference

## Base URL
```
http://localhost:5000/api
```

## Authentication
No authentication required (local access). For remote access, use:
```bash
# SSH Tunnel
ssh -L 5000:localhost:5000 user@server
```

---

## Bot Control Endpoints

### Start Bot
**POST** `/bot/start`

Start the trading bot.

**Response:**
```json
{
  "status": "success",
  "message": "Bot started successfully",
  "bot_status": {
    "status": "RUNNING",
    "active_trades": 0
  }
}
```

**Status Codes:**
- 200: Success
- 400: Bot already running
- 500: Start failed

### Stop Bot
**POST** `/bot/stop`

Stop the trading bot.

**Response:**
```json
{
  "status": "success",
  "message": "Bot stopped successfully"
}
```

### Pause Bot
**POST** `/bot/pause`

Pause trading (maintains connection).

**Response:**
```json
{
  "status": "success",
  "message": "Bot paused",
  "bot_status": {"paused": true}
}
```

### Resume Bot
**POST** `/bot/resume`

Resume trading after pause.

**Response:**
```json
{
  "status": "success",
  "message": "Bot resumed"
}
```

---

## Status Endpoints

### Get Bot Status
**GET** `/bot/status`

Get current bot status and session info.

**Response:**
```json
{
  "status": "RUNNING",
  "paused": false,
  "session_start": "2024-01-15T10:30:00",
  "active_trades": 2,
  "last_update": "2024-01-15T10:45:30"
}
```

### Get Statistics
**GET** `/bot/statistics`

Get bot performance statistics.

**Response:**
```json
{
  "status": "success",
  "statistics": {
    "initial_balance": 1000.00,
    "current_balance": 1250.00,
    "balance_change": 250.00,
    "balance_change_percent": 25.00,
    "total_trades": 50,
    "winning_trades": 35,
    "losing_trades": 15,
    "win_rate_percent": 70.00,
    "loss_streak": 0,
    "win_streak": 3,
    "recovery_trades": 8,
    "daily_loss": 50.00,
    "current_stake": 10.00,
    "next_stake": 10.00
  }
}
```

---

## Trade Endpoints

### Get Trade History
**GET** `/trades/history`

Get recent trade history.

**Query Parameters:**
- `limit` (int): Number of trades to return (default: 50, max: 500)

**Example:**
```
GET /trades/history?limit=10
```

**Response:**
```json
{
  "status": "success",
  "trades": [
    {
      "id": 1,
      "trade_id": "EURUSD_1705316400",
      "symbol": "EURUSD",
      "contract_type": "CALL",
      "entry_time": "2024-01-15T10:30:00",
      "exit_time": "2024-01-15T11:30:00",
      "stake": 10.00,
      "profit_loss": 9.00,
      "status": "CLOSED",
      "win_probability": 0.75,
      "signal": "STRONG_UP"
    }
  ],
  "total": 50
}
```

---

## Performance Endpoints

### Get Performance Summary
**GET** `/performance/summary`

Get comprehensive performance summary.

**Response:**
```json
{
  "status": "success",
  "summary": "Performance report text...",
  "statistics": {
    "total_trades": 50,
    "winning_trades": 35,
    "win_rate_percent": 70.00
  }
}
```

### Get Latest Predictions
**GET** `/predictions/latest`

Get recent AI predictions.

**Response:**
```json
{
  "status": "success",
  "predictions": [
    {
      "direction": "UP",
      "probability": 0.75,
      "confidence": 0.75,
      "signal": "STRONG_UP",
      "timestamp": "2024-01-15T10:45:00",
      "symbol": "EURUSD"
    }
  ],
  "total": 157
}
```

---

## Configuration Endpoints

### Get Configuration
**GET** `/config`

Get bot configuration.

**Response:**
```json
{
  "status": "success",
  "config": {
    "MIN_WIN_PROBABILITY": 0.70,
    "MAX_WIN_PROBABILITY": 0.80,
    "INITIAL_STAKE": 10,
    "MAX_STAKE": 500,
    "RECOVERY_MULTIPLIER": 2.0,
    "MAX_LOSS_STREAK": 3,
    "MAX_DAILY_LOSS": 500,
    "SYMBOLS": ["EURUSD", "GBPUSD", "XAUUSD", "BTCUSD", "ETHUSD"]
  }
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "status": "error",
  "message": "Bot not running"
}
```

### 404 Not Found
```json
{
  "status": "error",
  "message": "Endpoint not found"
}
```

### 500 Internal Server Error
```json
{
  "status": "error",
  "message": "Internal server error"
}
```

---

## Example Requests

### Using cURL

**Start bot:**
```bash
curl -X POST http://localhost:5000/api/bot/start
```

**Get status:**
```bash
curl http://localhost:5000/api/bot/status
```

**Get trades (last 10):**
```bash
curl http://localhost:5000/api/trades/history?limit=10
```

### Using Python

```python
import requests

BASE_URL = "http://localhost:5000/api"

# Start bot
response = requests.post(f"{BASE_URL}/bot/start")
print(response.json())

# Get status
status = requests.get(f"{BASE_URL}/bot/status").json()
print(f"Bot Status: {status['status']}")

# Get trades
trades = requests.get(f"{BASE_URL}/trades/history?limit=5").json()
for trade in trades['trades']:
    print(f"{trade['trade_id']}: {trade['profit_loss']}")
```

### Using JavaScript

```javascript
const BASE_URL = 'http://localhost:5000/api';

// Start bot
fetch(`${BASE_URL}/bot/start`, {method: 'POST'})
  .then(r => r.json())
  .then(d => console.log(d));

// Get status
fetch(`${BASE_URL}/bot/status`)
  .then(r => r.json())
  .then(d => console.log('Bot:', d.status));

// Get trades
fetch(`${BASE_URL}/trades/history?limit=10`)
  .then(r => r.json())
  .then(d => console.log('Trades:', d.total));
```

---

## Rate Limits

No explicit rate limits on local API. For remote access:
- Recommended: 1 request per second
- Status checks: Every 5 seconds OK
- Avoid polling predictions more than every 10 seconds

## WebSocket (Future)

Real-time updates via WebSocket (planned feature):
```javascript
const ws = new WebSocket('ws://localhost:5000/ws');
ws.onmessage = (event) => {
  console.log('Bot update:', event.data);
};
```

---

**Last Updated:** 2024-01-15
