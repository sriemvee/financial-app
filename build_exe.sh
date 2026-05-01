#!/bin/bash

echo "🚀 Building Financial App Desktop Executable..."
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install it first."
    exit 1
fi

# Check if pip is available
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not available. Please install Python 3 with pip."
    exit 1
fi

echo "📦 Installing PyInstaller..."
pip3 install pyinstaller

echo ""
echo "🔨 Building executable..."
pyinstaller --onefile --windowed --name "FinancialApp" app_launcher.py

echo ""
echo "✅ Build complete!"
echo "📁 Your executable is in: dist/FinancialApp"
echo ""
echo "To run the app:"
echo "  ./dist/FinancialApp"
