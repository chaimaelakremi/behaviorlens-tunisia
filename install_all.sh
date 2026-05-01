#!/bin/bash
# BehaviorLens - Complete Installation Script

echo "=========================================="
echo "🚀 BehaviorLens - Installation Script"
echo "=========================================="

echo ""
echo "1️⃣ Installing Graph API Core Dependencies..."
echo "   (feedparser, requests, pandas, python-dotenv)"
echo ""

uv pip install feedparser requests pandas python-dotenv

if [ $? -eq 0 ]; then
    echo "✅ Graph API core packages installed successfully!"
else
    echo "❌ Failed to install core packages"
    exit 1
fi

echo ""
echo "2️⃣ Attempting to install Scrapy (Optional)..."
echo "   Trying pre-built wheels approach..."
echo ""

# Try pre-built wheels first
uv pip install scrapy --only-binary :all: 2>/dev/null

if [ $? -eq 0 ]; then
    echo "✅ Scrapy installed successfully (pre-built wheels)!"
    
    echo ""
    echo "3️⃣ Installing Playwright for Scrapy..."
    uv pip install scrapy-playwright playwright
    
    if [ $? -eq 0 ]; then
        echo "✅ Playwright installed successfully!"
        echo ""
        echo "✨ All packages installed! Both Graph API and Scrapy ready!"
    else
        echo "⚠️ Playwright installation failed, but core Scrapy is installed"
    fi
else
    echo "⚠️ Pre-built Scrapy wheels not available"
    echo ""
    echo "To use Scrapy, choose one of these options:"
    echo ""
    echo "Option A: Install Visual C++ Build Tools"
    echo "  1) Download: https://visualstudio.microsoft.com/visual-cpp-build-tools/"
    echo "  2) Run: uv pip install scrapy scrapy-playwright playwright"
    echo ""
    echo "Option B: Use Docker"
    echo "  docker run -it -v \$(pwd):/app python:3.11 bash"
    echo "  cd /app && pip install scrapy scrapy-playwright playwright"
    echo ""
    echo "Graph API will work fine without Scrapy!"
fi

echo ""
echo "=========================================="
echo "Installation Complete!"
echo "=========================================="
