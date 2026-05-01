@echo off
REM BehaviorLens Tunisia - Quick Start Script
REM This script sets up and runs the complete pipeline

echo.
echo ========================================
echo BehaviorLens Tunisia - Quick Start
echo ========================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.8+
    pause
    exit /b 1
)

echo [1/4] Checking Python version...
python --version

echo.
echo [2/4] Installing dependencies...
pip install -q scrapy scrapy-playwright playwright fastapi uvicorn aiofiles 2>nul
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    echo Run manually: pip install scrapy scrapy-playwright playwright fastapi uvicorn
    pause
    exit /b 1
)

echo.
echo [3/4] Installing Playwright browsers...
python -m playwright install chromium 2>nul

echo.
echo [4/4] Creating directories...
if not exist "sessions" mkdir sessions
if not exist "data" mkdir data

echo.
echo ========================================
echo ✅ Setup Complete!
echo ========================================
echo.
echo Choose what to do:
echo.
echo   Option 1: python behaviorlens_social.py
echo            [Collect data from all platforms]
echo.
echo   Option 2: python behaviorlens_social.py --api
echo            [Start API server on http://localhost:8000]
echo.
echo   Option 3: python simple_web_scraper.py
echo            [Collect news posts only (fast)]
echo.
echo For more info:
echo   - Read BEHAVIORLENS_README.md
echo   - Read PROJECT_INDEX.md
echo.
echo Recommended: Option 1 (takes 20-40 minutes to collect data)
echo.
pause
