# PowerShell script to setup OSPF topology on Windows
# This runs the setup script via Git Bash or WSL

Write-Host "Setting up FRR OSPF topology..." -ForegroundColor Cyan

# Check if Docker is available
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: Docker is not installed" -ForegroundColor Red
    exit 1
}

# Try to find bash
$bashPath = $null
$gitBashPaths = @(
    "C:\Program Files\Git\bin\bash.exe",
    "C:\Program Files (x86)\Git\bin\bash.exe",
    "$env:LOCALAPPDATA\Programs\Git\bin\bash.exe"
)

foreach ($path in $gitBashPaths) {
    if (Test-Path $path) {
        $bashPath = $path
        break
    }
}

if (-not $bashPath) {
    if (Get-Command wsl -ErrorAction SilentlyContinue) {
        $bashPath = "wsl"
    }
}

if (-not $bashPath) {
    Write-Host "ERROR: Need Git Bash or WSL to run bash scripts" -ForegroundColor Red
    Write-Host "Install Git: https://git-scm.com/download/win"
    exit 1
}

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

if ($bashPath -eq "wsl") {
    wsl bash "$scriptDir/setup_frr_docker.sh"
} else {
    & $bashPath "$scriptDir/setup_frr_docker.sh"
}

