#!/usr/bin/env powershell
# BehaviorLens - Installation Script for Windows PowerShell

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "🚀 BehaviorLens - Installation Script" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "1️⃣ Installing Graph API Core Dependencies..." -ForegroundColor Yellow
Write-Host "   (feedparser, requests, pandas, python-dotenv)" -ForegroundColor Gray
Write-Host ""

uv pip install feedparser requests pandas python-dotenv

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Graph API core packages installed successfully!" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to install core packages" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "2️⃣ Attempting to install Scrapy (Optional)..." -ForegroundColor Yellow
Write-Host "   Trying pre-built wheels approach..." -ForegroundColor Gray
Write-Host ""

# Try pre-built wheels first
uv pip install scrapy --only-binary :all: 2>$null

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Scrapy installed successfully (pre-built wheels)!" -ForegroundColor Green
    
    Write-Host ""
    Write-Host "3️⃣ Installing Playwright for Scrapy..." -ForegroundColor Yellow
    uv pip install scrapy-playwright playwright
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Playwright installed successfully!" -ForegroundColor Green
        Write-Host ""
        Write-Host "✨ All packages installed! Both Graph API and Scrapy ready!" -ForegroundColor Green
    } else {
        Write-Host "⚠️ Playwright installation failed, but core Scrapy is installed" -ForegroundColor Yellow
    }
} else {
    Write-Host "⚠️ Pre-built Scrapy wheels not available" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "To use Scrapy, choose one of these options:" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Option A: Install Visual C++ Build Tools" -ForegroundColor Gray
    Write-Host "  1) Download: https://visualstudio.microsoft.com/visual-cpp-build-tools/" -ForegroundColor Gray
    Write-Host "  2) Run: uv pip install scrapy scrapy-playwright playwright" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Option B: Use Docker (if available)" -ForegroundColor Gray
    Write-Host "  docker run -it -v $(pwd):/app python:3.11" -ForegroundColor Gray
    Write-Host "  cd /app && pip install scrapy scrapy-playwright playwright" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Graph API will work fine without Scrapy!" -ForegroundColor Green
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Installation Complete!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan

Write-Host ""
Write-Host "📚 Next Steps:" -ForegroundColor Cyan
Write-Host "1. Follow Graph API setup guide: GRAPH_API_SETUP.md" -ForegroundColor Gray
Write-Host "2. Get your access token from developers.facebook.com" -ForegroundColor Gray
Write-Host "3. Set environment: \$env:FACEBOOK_ACCESS_TOKEN='your_token'" -ForegroundColor Gray
Write-Host "4. Run: python -m social_media.app --collect" -ForegroundColor Gray
Write-Host ""
