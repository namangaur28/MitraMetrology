#!/usr/bin/env bash
# Render build script for backend

set -o errexit

# Install Python dependencies
pip install -r backend/requirements.txt

echo "Build completed successfully"
