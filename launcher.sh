#!/bin/bash
# Path to the directory where the repo was cloned
cd "$(dirname "$0")"

# Start the app using the venv's python directly
./venv/bin/python3 app.py &
APP_PID=$!

# Wait for server to initialize
sleep 3

# Open the browser
xdg-open http://localhost:5000

# Keep the terminal window open
wait $APP_PID
