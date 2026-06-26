#!/bin/bash

# Navigate to the script's directory
cd "$(dirname "$0")"

# 1. Check if the venv exists, if not, try to run make install
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Running setup..."
    make install
fi

# 2. Inform the user
echo "------------------------------------------"
echo "Starting application..."
echo "Access the app at: http://127.0.0.1:5000"
echo "Press Ctrl+C to stop the server."
echo "------------------------------------------"

# 3. Launch the app using the venv python
./venv/bin/python3 app.py
