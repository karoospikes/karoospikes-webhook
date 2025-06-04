#!/usr/bin/env python3
"""
Karoospikes Telegram Webhook Server - Render Deployment
Permanent URL for MT5 trading signals
"""

from flask import Flask, request, jsonify
import requests
import json
import logging
from datetime import datetime
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Telegram API configuration
TELEGRAM_API_URL = "https://api.telegram.org/bot{}/sendMessage"

def format_signal(data):
    """Format trading signal for Telegram - Clean text, no emojis"""
    
    signal_type = data.get('signal_type', 'UNKNOWN')
    symbol = data.get('symbol', 'UNKNOWN')
    entry_price = data.get('entry_price', 0)
    tp_price = data.get('tp_price', 0)
    sl_price = data.get('sl_price', 0)
    confidence = data.get('confidence', 0)
    signal_category = data.get('signal_category', 'SIGNAL')
    timestamp = data.get('timestamp', datetime.now().timestamp())
    
    # Convert timestamp to readable format
    dt = datetime.fromtimestamp(timestamp)
    time_str = dt.strftime("%H:%M:%S")
    date_str = dt.strftime("%Y.%m.%d")
    
    # Clean signal indicator
    signal_indicator = "BUY SIGNAL" if signal_type == "BUY" else "SELL SIGNAL"
    
    # Create clean message format
    message = f"""KAROOSPIKES PREMIUM SIGNALS
{'-' * 35}

{signal_indicator}

PREMIUM SIGNAL

{signal_type} {symbol}

Entry: {entry_price:.5f}
Take Profit: {tp_price:.5f}
Stop Loss: {sl_price:.5f}

Confidence: {confidence}%
Time: {date_str} {time_str}

Type: {signal_category}
Professional Trading Signals
Support: @KaroospikesSupport
Risk Warning: Trading involves risk
Powered by Karoospikes

{'-' * 35}"""
    
    return message

def send_to_telegram(bot_token, message, chat_id="@your_channel"):
    """Send message to Telegram"""
    
    url = TELEGRAM_API_URL.format(bot_token)
    
    payload = {
        'chat_id': chat_id,
        'text': message,
        'disable_web_page_preview': True
    }
    
    try:
        response = requests.post(url, json=payload, timeout=15)
        response.raise_for_status()
        
        result = response.json()
        if result.get('ok'):
            logger.info(f"✅ Signal sent successfully to {chat_id}")
            return True
        else:
            error_msg = result.get('description', 'Unknown error')
            logger.error(f"❌ Telegram API error: {error_msg}")
            return False
            
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Network error: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error: {str(e)}")
        return False

@app.route('/signal', methods=['POST'])
def receive_signal():
    """Main webhook endpoint for MT5 signals"""
    
    try:
        # Get JSON data from MT5
        data = request.get_json()
        
        if not data:
            logger.warning("⚠️ No JSON data received")
            return jsonify({'status': 'error', 'message': 'No data received'}), 400
        
        logger.info(f"📨 Signal received: {json.dumps(data, indent=2)}")
        
        # Validate required fields
        required_fields = ['signal_type', 'symbol', 'entry_price', 'tp_price', 'sl_price', 'bot_token']
        missing_fields = [field for field in required_fields if field not in data or data[field] is None]
        
        if missing_fields:
            logger.error(f"❌ Missing required fields: {missing_fields}")
            return jsonify({
                'status': 'error', 
                'message': f'Missing required fields: {missing_fields}'
            }), 400
        
        # Validate bot token
        bot_token = data.get('bot_token', '').strip()
        if not bot_token or len(bot_token) < 10:
            logger.error("❌ Invalid or missing bot token")
            return jsonify({'status': 'error', 'message': 'Invalid bot token'}), 400
        
        # Validate prices
        try:
            entry_price = float(data.get('entry_price', 0))
            tp_price = float(data.get('tp_price', 0))
            sl_price = float(data.get('sl_price', 0))
            
            if entry_price <= 0 or tp_price <= 0 or sl_price <= 0:
                raise ValueError("Prices must be positive")
                
        except (ValueError, TypeError) as e:
            logger.error(f"❌ Invalid price data: {e}")
            return jsonify({'status': 'error', 'message': 'Invalid price data'}), 400
        
        # Format and send signal
        message = format_signal(data)
        success = send_to_telegram(bot_token, message)
        
        if success:
            logger.info("✅ Signal processing completed successfully")
            return jsonify({
                'status': 'success', 
                'message': 'Signal sent to Telegram successfully'
            }), 200
        else:
            logger.error("❌ Failed to send signal to Telegram")
            return jsonify({
                'status': 'error', 
                'message': 'Failed to send signal to Telegram'
            }), 500
            
    except json.JSONDecodeError:
        logger.error("❌ Invalid JSON data received")
        return jsonify({'status': 'error', 'message': 'Invalid JSON format'}), 400
    except Exception as e:
        logger.error(f"❌ Unexpected server error: {str(e)}")
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Karoospikes Webhook Server',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

@app.route('/test', methods=['GET', 'POST'])
def test_endpoint():
    """Test endpoint for debugging"""
    if request.method == 'GET':
        return jsonify({
            'status': 'success',
            'message': 'Karoospikes Webhook Server is running!',
            'endpoints': {
                'POST /signal': 'Receive trading signals from MT5',
                'GET /health': 'Health check',
                'GET /test': 'Test endpoint'
            },
            'timestamp': datetime.now().isoformat()
        })
    
    # Handle POST request for testing
    try:
        data = request.get_json() or {}
        logger.info(f"🧪 Test signal received: {json.dumps(data, indent=2)}")
        return jsonify({
            'status': 'success',
            'message': 'Test signal received',
            'received_data': data
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Test failed: {str(e)}'
        }), 400

@app.route('/', methods=['GET'])
def home():
    """Home page with API information"""
    return jsonify({
        'service': 'Karoospikes Telegram Webhook Server',
        'status': 'running',
        'version': '1.0.0',
        'description': 'Receives trading signals from MT5 and forwards to Telegram',
        'endpoints': {
            'POST /signal': 'Main webhook endpoint for trading signals',
            'GET /health': 'Health check endpoint',
            'GET /test': 'Test endpoint for debugging',
            'GET /': 'This information page'
        },
        'usage': {
            'content_type': 'application/json',
            'required_fields': [
                'signal_type',
                'symbol', 
                'entry_price',
                'tp_price',
                'sl_price',
                'bot_token'
            ]
        },
        'timestamp': datetime.now().isoformat()
    })

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'status': 'error',
        'message': 'Endpoint not found',
        'available_endpoints': ['/signal', '/health', '/test', '/']
    }), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        'status': 'error',
        'message': 'Method not allowed'
    }), 405

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'status': 'error',
        'message': 'Internal server error'
    }), 500

if __name__ == '__main__':
    # Get port from environment (Render sets this automatically)
    port = int(os.environ.get('PORT', 5000))
    
    print("🚀 Starting Karoospikes Webhook Server...")
    print(f"📡 Server will run on port {port}")
    print("🔗 Available endpoints:")
    print("   POST /signal - Main webhook")
    print("   GET /health - Health check") 
    print("   GET /test - Test endpoint")
    print("   GET / - API information")
    
    # Run the Flask app
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False,  # Set to False for production
        threaded=True
    )