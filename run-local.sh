#!/bin/bash
# Run bot locally without Docker

echo "Activating virtual environment..."
source /home/spacholski/Sources/frank/venv/bin/activate

echo "Checking .env file..."
if [ ! -f /home/spacholski/Sources/frank/.env ]; then
    echo "ERROR: .env file not found!"
    exit 1
fi

echo "Starting bot locally..."
cd /home/spacholski/Sources/frank
python main.py
