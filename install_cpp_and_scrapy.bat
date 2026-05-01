@echo off
REM Install Visual Studio C++ Build Tools (required for Scrapy)
REM This script downloads and installs the build tools automatically

echo.
echo ============================================================
echo Installing Visual Studio C++ Build Tools
echo ============================================================
echo.
echo This will download (~1.5GB) and install the tools needed for Scrapy
echo Time required: ~20-30 minutes
echo.

REM Check if running as admin
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: This script must be run as Administrator!
    echo.
    echo Solution: Right-click on Command Prompt and select "Run as Administrator"
    pause
    exit /b 1
)

echo Downloading Visual Studio Build Tools...
echo.

REM Create temp directory for download
if not exist "%TEMP%\vs_build_tools" mkdir "%TEMP%\vs_build_tools"

REM Download the installer (this is the official Visual Studio Build Tools installer)
echo URL: https://aka.ms/vs/17/release/vs_BuildTools.exe
echo Downloading to: %TEMP%\vs_build_tools\vs_BuildTools.exe
echo.

powershell -Command "& {
    $url = 'https://aka.ms/vs/17/release/vs_BuildTools.exe'
    $output = '%TEMP%\vs_build_tools\vs_BuildTools.exe'
    
    Write-Host 'Downloading Visual Studio Build Tools...' -ForegroundColor Green
    Write-Host 'This may take 5-10 minutes depending on internet speed' -ForegroundColor Yellow
    
    try {
        $ProgressPreference = 'SilentlyContinue'
        Invoke-WebRequest -Uri $url -OutFile $output
        Write-Host 'Download completed successfully!' -ForegroundColor Green
    }
    catch {
        Write-Host 'ERROR: Download failed!' -ForegroundColor Red
        Write-Host $_.Exception.Message
        exit 1
    }
}"

if %errorLevel% neq 0 (
    echo.
    echo ERROR: Download failed!
    echo.
    echo Try manually downloading from:
    echo https://visualstudio.microsoft.com/visual-cpp-build-tools/
    echo.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo Running installer...
echo ============================================================
echo.
echo Installer window will open. Please:
echo 1. Wait for components to load
echo 2. Select "Desktop development with C++"
echo 3. Click "Install"
echo 4. Wait for installation to complete (~10-15 minutes)
echo.
pause

REM Run installer with specific workload for C++ development
echo Starting installation...
"%TEMP%\vs_build_tools\vs_BuildTools.exe" ^
    --add Microsoft.VisualStudio.Workload.VCTools ^
    --add Microsoft.VisualStudio.Component.VC.Tools.x86.x64 ^
    --includeRecommended ^
    --norestart ^
    --passive

echo.
echo ============================================================
echo Installation complete!
echo ============================================================
echo.
echo Now installing Scrapy...
echo.

REM Install Scrapy and related packages
C:/Users/aziz/.local/bin/python3.15.exe -m pip install scrapy scrapy-playwright playwright

echo.
echo ============================================================
echo SUCCESS!
echo ============================================================
echo.
echo Scrapy and Playwright are now installed!
echo.
echo Verify installation:
echo C:/Users/aziz/.local/bin/python3.15.exe -c "import scrapy; print('Scrapy', scrapy.__version__)"
echo.
pause
