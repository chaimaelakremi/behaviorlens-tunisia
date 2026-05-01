# Install Visual Studio C++ Build Tools + Scrapy
# This PowerShell script automates the entire process

Write-Host "`n" -ForegroundColor Green
Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   Installing C++ Build Tools + Scrapy + Playwright        ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host "`n" -ForegroundColor Green

# Check if running as Administrator
$isAdmin = [Security.Principal.WindowsIdentity]::GetCurrent().Groups -contains 'S-1-5-32-544'

if (-not $isAdmin) {
    Write-Host "ERROR: This script must run as Administrator!" -ForegroundColor Red
    Write-Host "`nSolution:" -ForegroundColor Yellow
    Write-Host "  1. Right-click PowerShell" -ForegroundColor White
    Write-Host "  2. Select 'Run as Administrator'" -ForegroundColor White
    Write-Host "  3. Run: Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process" -ForegroundColor White
    Write-Host "  4. Then: .\\install_cpp_and_scrapy.ps1" -ForegroundColor White
    exit 1
}

Write-Host "✅ Running as Administrator" -ForegroundColor Green
Write-Host "`nThis will:" -ForegroundColor Cyan
Write-Host "  1. Download Visual Studio Build Tools (~1.5GB)" -ForegroundColor White
Write-Host "  2. Install C++ development tools" -ForegroundColor White
Write-Host "  3. Install Scrapy + Playwright" -ForegroundColor White
Write-Host "`n⏱️  Estimated time: 25-35 minutes" -ForegroundColor Yellow
Write-Host "`nPress Enter to continue..." -ForegroundColor Cyan
Read-Host

# Create temp directory
$tempDir = "$env:TEMP\vs_build_tools"
if (-not (Test-Path $tempDir)) {
    New-Item -ItemType Directory -Path $tempDir -Force | Out-Null
}

$installerPath = "$tempDir\vs_BuildTools.exe"

# Download Visual Studio Build Tools
Write-Host "`n" -ForegroundColor Green
Write-Host "📥 Downloading Visual Studio Build Tools..." -ForegroundColor Cyan
Write-Host "   From: https://aka.ms/vs/17/release/vs_BuildTools.exe" -ForegroundColor Gray
Write-Host "   To: $installerPath" -ForegroundColor Gray
Write-Host "`n   This may take 5-10 minutes..." -ForegroundColor Yellow

try {
    $url = "https://aka.ms/vs/17/release/vs_BuildTools.exe"
    
    # Show progress
    $ProgressPreference = 'Continue'
    Invoke-WebRequest -Uri $url -OutFile $installerPath -UseBasicParsing
    
    Write-Host "`n✅ Download completed!" -ForegroundColor Green
}
catch {
    Write-Host "`n❌ ERROR: Download failed!" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "`nAlternative: Download manually from:" -ForegroundColor Yellow
    Write-Host "   https://visualstudio.microsoft.com/visual-cpp-build-tools/" -ForegroundColor Cyan
    exit 1
}

# Run the installer
Write-Host "`n" -ForegroundColor Green
Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   Starting Visual Studio Build Tools Installer             ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan

Write-Host "`nℹ️  Installer window will open. Please:" -ForegroundColor Cyan
Write-Host "   1. Wait for components to load (1-2 minutes)" -ForegroundColor White
Write-Host "   2. Check: 'Desktop development with C++'" -ForegroundColor White
Write-Host "   3. Click: 'Install'" -ForegroundColor White
Write-Host "   4. Wait: ~10-15 minutes for installation" -ForegroundColor White
Write-Host "`nPress Enter to launch installer..." -ForegroundColor Cyan
Read-Host

Write-Host "`n🔧 Running installer with C++ workload..." -ForegroundColor Green

# Run installer with C++ workload
$installerArgs = @(
    "--add", "Microsoft.VisualStudio.Workload.VCTools",
    "--add", "Microsoft.VisualStudio.Component.VC.Tools.x86.x64",
    "--includeRecommended",
    "--norestart",
    "--passive"
)

& $installerPath $installerArgs

# Wait a moment for installer to complete
Start-Sleep -Seconds 10

Write-Host "`n✅ Build Tools installation complete!" -ForegroundColor Green

# Now install Scrapy
Write-Host "`n" -ForegroundColor Green
Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   Installing Scrapy + Playwright                          ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan

Write-Host "`n📦 Installing Python packages..." -ForegroundColor Cyan

& "C:/Users/aziz/.local/bin/python3.15.exe" -m pip install scrapy scrapy-playwright playwright

# Verify installation
Write-Host "`n" -ForegroundColor Green
Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   Verifying Installation                                   ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan

try {
    $output = & "C:/Users/aziz/.local/bin/python3.15.exe" -c "import scrapy; print('Scrapy', scrapy.__version__)" 2>&1
    
    if ($output -match "Scrapy") {
        Write-Host "`n✅ SUCCESS! Installation complete!" -ForegroundColor Green
        Write-Host "`n$output" -ForegroundColor Green
        Write-Host "`nYou can now use:" -ForegroundColor Cyan
        Write-Host "   • Scrapy web scraping framework" -ForegroundColor White
        Write-Host "   • Playwright for browser automation" -ForegroundColor White
        Write-Host "   • Hybrid collection mode in InsightTN" -ForegroundColor White
        
        Write-Host "`nTest with:" -ForegroundColor Cyan
        Write-Host "   python -m social_media.app --collect --mode hybrid" -ForegroundColor Gray
    }
    else {
        Write-Host "`n⚠️  Installation may have issues:" -ForegroundColor Yellow
        Write-Host $output -ForegroundColor Yellow
    }
}
catch {
    Write-Host "`n⚠️  Verification error:" -ForegroundColor Yellow
    Write-Host $_.Exception.Message -ForegroundColor Yellow
}

Write-Host "`n" -ForegroundColor Green
Write-Host "Press Enter to close..." -ForegroundColor Cyan
Read-Host
