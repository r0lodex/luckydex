#!/bin/bash

# Load environment variables from .env file and run Chalice locally
# This script makes it easier to test locally with your Google Sheets configuration

if [ -f .env ]; then
    echo "Loading environment variables from .env file..."
    export $(grep -v '^#' .env | xargs)
else
    echo "Warning: .env file not found"
fi

echo "Starting Chalice local server..."
echo "Visit http://localhost:8000/home to test the app"
chalice local
