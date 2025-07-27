#!/bin/bash

# Simple wrapper script for the standalone reminder script

# Set the working directory to the EPV folder
cd "$(dirname "$0")"

# Activate virtual environment (if using one)
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Set Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Run the standalone reminder script
python3 send_manager_approval_reminders_standalone.py

# Log the execution
echo "$(date): Standalone manager approval reminder script executed" >> /tmp/epv_reminders.log 