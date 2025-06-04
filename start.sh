#!/bin/bash
echo "🚀 Starting Karoospikes Webhook Server on Render..."
echo "📡 Port: $PORT"
echo "🌐 Starting gunicorn server..."

# Start the Flask app with gunicorn
exec gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 30 --keep-alive 2 --max-requests 1000 app:app