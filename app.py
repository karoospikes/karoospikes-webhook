#!/usr/bin/env python3
"""
Karoospikes Telegram Webhook Server
GitHub + Render Deployment Ready
Professional trading signal delivery system
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
    """Format trading signal for Telegram - Professional Layout"""
    
    signal_type = data.get('signal_type', 'UNKNOWN')
    symbol = data.get('symbol', 'UNKNOWN')
    entry_price = data.get('entry_price', 0)
    tp_price = data.get('tp_price', 0)
    sl_price = data.get('sl_price', 0)
    confidence = data.get('confidence', 0)
    signal_category = data.get('signal_category', 'SIGNAL')
    timestamp = data.get('timestamp', datetime.now().timestamp())
    
    # Convert timestamp to readable format
    if isinstance(timestamp, (int, float)):
        dt = datetime.fromtimestamp(timestamp)
    else:
        dt = datetime.now()
    
    time_str = dt.strftime("%H:%M:%S")
    date_str = dt.strftime("%Y.%m.%d")
    
    # Signal indicator
    signal_indicator = "BUY SIGNAL" if signal_type == "BUY" else "SELL SIGNAL"
    
    # Create professional message format
    message = f"""KAROOSPIKES PREMIUM SIGNALS
{'-' * 35}

{signal_indicator}

{signal_category}

{signal_type} {symbol}

Entry: {entry_price:.5f}
Take Profit: {tp_price:.5f}
Stop Loss: {sl_price:.5f}

Confidence: {confidence}%
Time: {date_str} {time_str}

Professional Trading Signals
Support: @KaroospikesSupport
Risk Warning: Trading involves risk
Powered by Karoospikes

{'-' * 35}"""
    
    return message

def send_to_telegram(bot_token, message, chat_id="@default_channel"):
    """Send message to Telegram with comprehensive error handling"""
    
    url = TELEGRAM_API_URL.format(bot_token)
    
    payload = {
        'chat_id': chat_id,
        'text': message,
        'disable_web_page_preview': True,
        'parse_mode': None  # Use plain text to avoid formatting issues
    }
    
    try:
        response = requests.post(url, json=payload, timeout=15)
        response.raise_for_status()
        
        result = response.json()
        if result.get('ok'):
            logger.info(f"✅ Signal sent successfully to {chat_id}")
            return True, "Success"
        else:
            error_msg = result.get('description', 'Unknown Telegram error')
            logger.error(f"❌ Telegram API error: {error_msg}")
            return False, error_msg
            
    except requests.exceptions.Timeout:
        error_msg = "Request timeout"
        logger.error(f"❌ Timeout error: {error_msg}")
        return False, error_msg
    except requests.exceptions.RequestException as e:
        error_msg = f"Network error: {str(e)}"
        logger.error(f"❌ Network error: {error_msg}")
        return False, error_msg
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(f"❌ Unexpected error: {error_msg}")
        return False, error_msg

@app.route('/signal', methods=['POST'])
def receive_signal():
    """Main webhook endpoint for trading signals from MT5"""
    
    try:
        # Get JSON data from MT5
        data = request.get_json()
        
        if not data:
            logger.warning("⚠️ No JSON data received")
            return jsonify({'status': 'error', 'message': 'No data received'}), 400
        
        logger.info(f"📨 Signal received from MT5: {data.get('signal_type', 'UNKNOWN')} {data.get('symbol', 'UNKNOWN')}")
        
        # Validate required fields
        required_fields = ['signal_type', 'symbol', 'entry_price', 'tp_price', 'sl_price', 'bot_token']
        missing_fields = [field for field in required_fields if field not in data or data[field] is None]
        
        if missing_fields:
            logger.error(f"❌ Missing required fields: {missing_fields}")
            return jsonify({
                'status': 'error', 
                'message': f'Missing required fields: {missing_fields}'
            }), 400
        
        # Validate bot token format
        bot_token = str(data.get('bot_token', '')).strip()
        if not bot_token or len(bot_token) < 10 or ':' not in bot_token:
            logger.error("❌ Invalid bot token format")
            return jsonify({'status': 'error', 'message': 'Invalid bot token format'}), 400
        
        # Validate price data
        try:
            entry_price = float(data.get('entry_price', 0))
            tp_price = float(data.get('tp_price', 0))
            sl_price = float(data.get('sl_price', 0))
            confidence = int(data.get('confidence', 0))
            
            if entry_price <= 0 or tp_price <= 0 or sl_price <= 0:
                raise ValueError("Prices must be positive")
            
            if confidence < 0 or confidence > 100:
                raise ValueError("Confidence must be between 0-100")
                
        except (ValueError, TypeError) as e:
            logger.error(f"❌ Invalid numeric data: {e}")
            return jsonify({'status': 'error', 'message': f'Invalid numeric data: {str(e)}'}), 400
        
        # Format the signal message
        message = format_signal(data)
        
        # Determine chat destination
        chat_id = data.get('channel_id', data.get('chat_id', '@default_channel'))
        
        # Send to Telegram
        success, error_msg = send_to_telegram(bot_token, message, chat_id)
        
        if success:
            logger.info("✅ Signal processing completed successfully")
            return jsonify({
                'status': 'success', 
                'message': 'Signal sent to Telegram successfully',
                'signal_type': data.get('signal_type'),
                'symbol': data.get('symbol'),
                'confidence': confidence
            }), 200
        else:
            logger.error(f"❌ Failed to send signal to Telegram: {error_msg}")
            return jsonify({
                'status': 'error', 
                'message': f'Failed to send signal to Telegram: {error_msg}'
            }), 500
            
    except json.JSONDecodeError:
        logger.error("❌ Invalid JSON data received")
        return jsonify({'status': 'error', 'message': 'Invalid JSON format'}), 400
    except Exception as e:
        logger.error(f"❌ Unexpected server error: {str(e)}")
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for monitoring"""
    return jsonify({
        'status': 'healthy',
        'service': 'Karoospikes Webhook Server',
        'version': '2.0.0',
        'timestamp': datetime.now().isoformat(),
        'uptime': 'Running'
    })

@app.route('/test', methods=['GET', 'POST'])
def test_endpoint():
    """Test endpoint for debugging and validation"""
    if request.method == 'GET':
        return jsonify({
            'status': 'success',
            'message': 'Karoospikes Webhook Server is operational!',
            'endpoints': {
                'POST /signal': 'Main webhook for trading signals',
                'GET /health': 'Health check endpoint',
                'GET /test': 'This test endpoint',
                'GET /': 'API documentation'
            },
            'timestamp': datetime.now().isoformat(),
            'github_deployed': True
        })
    
    # Handle POST request for testing
    try:
        data = request.get_json() or {}
        logger.info(f"🧪 Test signal received: {json.dumps(data, indent=2)}")
        return jsonify({
            'status': 'success',
            'message': 'Test signal received successfully',
            'received_data': data,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Test failed: {str(e)}'
        }), 400

@app.route('/', methods=['GET'])
def api_documentation():
    """API documentation and service information"""
    return jsonify({
        'service': 'Karoospikes Professional Telegram Webhook Server',
        'version': '2.0.0',
        'status': 'operational',
        'description': 'Professional trading signal delivery system for MT5 to Telegram',
        'deployment': 'GitHub + Render',
        'endpoints': {
            'POST /signal': {
                'description': 'Main webhook endpoint for trading signals',
                'content_type': 'application/json',
                'required_fields': [
                    'signal_type (BUY/SELL)',
                    'symbol',
                    'entry_price',
                    'tp_price',
                    'sl_price',
                    'bot_token'
                ],
                'optional_fields': [
                    'confidence',
                    'signal_category',
                    'timestamp',
                    'channel_id'
                ]
            },
            'GET /health': 'Health check endpoint',
            'GET /test': 'Test endpoint for debugging',
            'GET /': 'This documentation'
        },
        'features': [
            'Professional signal formatting',
            'Comprehensive error handling',
            'Auto-retry mechanisms',
            'Real-time monitoring',
            'GitHub deployment ready'
        ],
        'support': {
            'telegram': '@KaroospikesSupport',
            'documentation': 'Available in repository'
        },
        'timestamp': datetime.now().isoformat()
    })

# Error handlers for better user experience
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
    
    print("🚀 Karoospikes Professional Webhook Server Starting...")
    print(f"📡 Server running on port {port}")
    print("🌐 GitHub + Render Deployment")
    print("✅ Ready for professional trading signals!")
    
    # Run the Flask application
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False,  # Production mode
        threaded=True
    )