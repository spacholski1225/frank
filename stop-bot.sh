#!/bin/bash
# Stop background bot

if [ ! -f bot.pid ]; then
    echo "ERROR: bot.pid file not found. Bot may not be running."
    exit 1
fi

PID=$(cat bot.pid)

if ! ps -p $PID > /dev/null 2>&1; then
    echo "ERROR: Bot process (PID: $PID) is not running"
    rm bot.pid
    exit 1
fi

echo "Stopping bot (PID: $PID)..."
kill $PID

# Wait for process to stop
for i in {1..10}; do
    if ! ps -p $PID > /dev/null 2>&1; then
        echo "Bot stopped successfully"
        rm bot.pid
        exit 0
    fi
    sleep 1
done

# If still running, force kill
echo "Bot didn't stop gracefully, forcing..."
kill -9 $PID
rm bot.pid
echo "Bot forcefully stopped"
