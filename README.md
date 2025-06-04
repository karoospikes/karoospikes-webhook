# Karoospikes Professional Webhook Server

Professional trading signal delivery system for MT5 to Telegram integration.

## Features

- 🚀 **Professional Signal Formatting** - Clean, readable Telegram messages
- 🔒 **Comprehensive Security** - Input validation and error handling
- ⚡ **High Performance** - Optimized for real-time trading signals
- 📊 **Real-time Monitoring** - Health checks and status endpoints
- 🌐 **GitHub + Render Deployment** - Professional hosting solution

## Quick Deploy to Render

1. **Fork this repository**
2. **Connect to Render**: https://render.com
3. **Create new Web Service** from GitHub
4. **Auto-deploy is configured** - just click deploy!

## API Endpoints

### POST /signal
Main webhook endpoint for trading signals from MT5.

**Required Fields:**
- `signal_type`: "BUY" or "SELL"
- `symbol`: Trading symbol (e.g., "BOOM500")
- `entry_price`: Entry price (number)
- `tp_price`: Take profit price (number)
- `sl_price`: Stop loss price (number)
- `bot_token`: Telegram bot token

**Optional Fields:**
- `confidence`: Signal confidence percentage (0-100)
- `signal_category`: Signal type (e.g., "PREMIUM SIGNAL")
- `timestamp`: Unix timestamp
- `channel_id`: Telegram channel/chat ID

### GET /health
Health check endpoint for monitoring server status.

### GET /test
Test endpoint for debugging and validation.

### GET /
API documentation and service information.

## Example Signal Format

```json
{
  "signal_type": "BUY",
  "symbol": "BOOM500",
  "entry_price": 4278.44400,
  "tp_price": 4279.44400,
  "sl_price": 4277.94400,
  "confidence": 85,
  "bot_token": "YOUR_BOT_TOKEN",
  "signal_category": "PREMIUM SIGNAL"
}
```

## Telegram Message Output

```
KAROOSPIKES PREMIUM SIGNALS
-----------------------------------

BUY SIGNAL

PREMIUM SIGNAL

BUY BOOM500

Entry: 4278.44400
Take Profit: 4279.44400
Stop Loss: 4277.94400

Confidence: 85%
Time: 2025.06.04 08:51

Professional Trading Signals
Support: @KaroospikesSupport
Risk Warning: Trading involves risk
Powered by Karoospikes
-----------------------------------
```

## MT5 Integration

Use this webhook URL in your MT5 indicator:
```
https://your-app-name.onrender.com/signal
```

## Support

- 📱 Telegram: @KaroospikesSupport
- 🌐 Website: https://www.karoospikes.com
- 📧 Professional trading signals and support

## License

Professional trading system - All rights reserved.
