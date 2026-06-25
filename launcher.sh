#!/bin/bash

# Navigate to the project directory
APP_DIR="$(dirname "$0")/RepairSch_Source"
cd "$APP_DIR"

# 1. Start the app using the venv's python directly
# This avoids the "ModuleNotFoundError"
./venv/bin/python3 app.py &
APP_PID=$!

# 2. Wait for the server to spin up
echo "Starting RepairSch..."
sleep 3

# 3. Open the browser
xdg-open http://localhost:5000

# 4. Keep the window open
wait $APP_PID
