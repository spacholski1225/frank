#!/bin/bash
# Run bot in background

echo "Activating virtual environment..."
source ./venv/bin/activate

echo "Installing dependencies..."
pip install -q -r requirements.txt

echo "Checking .env file..."
if [ ! -f ./.env ]; then
    echo "ERROR: .env file not found!"
    exit 1
fi

echo "Starting bot in background..."

# Check if bot is already running
if [ -f bot.pid ]; then
    PID=$(cat bot.pid)
    if ps -p $PID > /dev/null 2>&1; then
        echo "ERROR: Bot is already running (PID: $PID)"
        echo "Use ./stop-bot.sh to stop it first"
        exit 1
    else
        # Stale PID file, remove it
        rm bot.pid
    fi
fi

# Run in background with nohup
nohup python main.py > bot.log 2>&1 &
echo $! > bot.pid

echo "Bot started in background (PID: $(cat bot.pid))"
echo "View logs: tail -f bot.log"
echo "Stop bot: ./stop-bot.sh"
