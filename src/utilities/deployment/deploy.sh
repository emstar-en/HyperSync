#!/bin/bash
set -e

echo "Starting HyperSync Deployment..."

# 1. Environment Setup
echo "[1/4] Setting up environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "Virtual environment created."
fi
source venv/bin/activate

# 2. Install Dependencies
echo "[2/4] Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# 3. Configuration
echo "[3/4] Loading configuration..."
export HYPERSYNC_ENV=${HYPERSYNC_ENV:-production}
export HYPERSYNC_CONFIG_PATH=${HYPERSYNC_CONFIG_PATH:-./config}

# 4. Start Services
echo "[4/4] Starting services..."
# Start the API server in the background
nohup uvicorn main:app --host 0.0.0.0 --port 8000 > hypersync.log 2>&1 &
PID=$!

echo "HyperSync is running with PID $PID"
echo "Logs available at hypersync.log"
