#!/usr/bin/env bash
# Build script for Render deployment

set -o errexit  # exit on error

# Install Python dependencies
pip install -r requirements.txt

# Optionally run database migrations here if using Flask-Migrate
# flask db upgrade

echo "Build completed successfully"