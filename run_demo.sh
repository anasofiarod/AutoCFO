#!/bin/bash

# Check if .venv exists
if [ -d ".venv" ]; then
    echo "[INFO] Using virtual environment..."
    PYTHON_CMD="./.venv/bin/python"
else
    echo "[INFO] Virtual environment not found. Trying system python3..."
    PYTHON_CMD="python3"
fi

# Run the demo
$PYTHON_CMD main.py --demo
