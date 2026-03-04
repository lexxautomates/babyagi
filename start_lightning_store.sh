#!/bin/bash
# Start Agent Lightning Store for BabyAGI
# This should be run before the Telegram bot

cd /root/babyagi
source venv/bin/activate

# Start the Lightning Store in the background
nohup agl store --port 45993 > /var/log/lightning_store.log 2>&1 &

echo "Lightning Store started on port 45993"
echo "Logs: /var/log/lightning_store.log"

# Wait for store to be ready
sleep 3

# Check if it's running
if curl -s http://localhost:45993/health > /dev/null 2>&1; then
    echo "Lightning Store is healthy!"
else
    echo "Warning: Lightning Store may not be fully started yet"
fi