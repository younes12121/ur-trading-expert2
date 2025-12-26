#!/bin/bash
set -e

echo "🔧 Installing Python dependencies..."
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

echo "✅ Build complete!"

