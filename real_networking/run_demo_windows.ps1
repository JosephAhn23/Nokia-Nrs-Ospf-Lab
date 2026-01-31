# PowerShell script to run the demo on Windows
# This is a wrapper that calls the bash script via Git Bash or WSL

Write-Host "=========================================="
Write-Host "NOKIA NRS CERTIFICATION LAB - DEMO"
Write-Host "=========================================="
Write-Host ""

# Check if Docker is available
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: Docker is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Install Docker Desktop: https://www.docker.com/products/docker-desktop"
    exit 1
}

# Check if Docker daemon is running
try {
    docker ps | Out-Null
} catch {
    Write-Host "ERROR: Docker daemon is not running" -ForegroundColor Red
    Write-Host "Start Docker Desktop and try again"
    exit 1
}

Write-Host "✓ Docker is running" -ForegroundColor Green
Write-Host ""

# Try to find bash (Git Bash or WSL)
$bashPath = $null

# Check for Git Bash
$gitBashPaths = @(
    "C:\Program Files\Git\bin\bash.exe",
    "C:\Program Files (x86)\Git\bin\bash.exe",
    "$env:LOCALAPPDATA\Programs\Git\bin\bash.exe"
)

foreach ($path in $gitBashPaths) {
    if (Test-Path $path) {
        $bashPath = $path
        Write-Host "Found Git Bash at: $bashPath" -ForegroundColor Green
        break
    }
}

# Check for WSL
if (-not $bashPath) {
    if (Get-Command wsl -ErrorAction SilentlyContinue) {
        $bashPath = "wsl"
        Write-Host "Found WSL" -ForegroundColor Green
    }
}

if (-not $bashPath) {
    Write-Host "ERROR: Could not find bash (Git Bash or WSL)" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install one of the following:"
    Write-Host "  1. Git for Windows: https://git-scm.com/download/win"
    Write-Host "  2. WSL: wsl --install"
    Write-Host ""
    Write-Host "Or run the commands manually:"
    Write-Host "  cd real_networking"
    Write-Host "  docker exec frr-router1 vtysh -c 'show ip ospf neighbor'"
    exit 1
}

Write-Host ""
Write-Host "Running demo script via bash..." -ForegroundColor Yellow
Write-Host ""

# Get the script directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Run the bash script
if ($bashPath -eq "wsl") {
    wsl bash "$scriptDir/demo_for_lenish.sh"
} else {
    & $bashPath "$scriptDir/demo_for_lenish.sh"
}

