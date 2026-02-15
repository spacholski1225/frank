#!/bin/bash
# Run bot locally without Docker

echo "Activating virtual environment..."
source ./venv/bin/activate

echo "Checking .env file..."
if [ ! -f ./frank/.env ]; then
    echo "ERROR: .env file not found!"
    exit 1
fi

echo "Starting bot locally..."
cd ./frank
python main.py
