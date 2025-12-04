#!/bin/bash

# Telegram Chat Analyzer Bot - Quick Start Script

echo "=========================================="
echo "Telegram Chat Analyzer Bot"
echo "=========================================="
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    echo "Please copy .env.example to .env and configure it:"
    echo "  cp .env.example .env"
    echo "  nano .env"
    exit 1
fi

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate venv
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo "📥 Installing dependencies..."
pip install -q -r requirements.txt

# Run the bot
echo ""
echo "=========================================="
echo "🚀 Starting bot..."
echo "=========================================="
echo ""
python main.py
