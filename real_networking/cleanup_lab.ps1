# Cleanup OSPF Lab
# Run this to stop and remove all lab components

Write-Host "=== Cleaning Up OSPF Lab ===" -ForegroundColor Yellow
Write-Host ""

Write-Host "Stopping containers..." -ForegroundColor Cyan
docker stop R1 R2 R3 2>$null | Out-Null
Write-Host "✓ Containers stopped" -ForegroundColor Green

Write-Host "Removing containers..." -ForegroundColor Cyan
docker rm R1 R2 R3 2>$null | Out-Null
Write-Host "✓ Containers removed" -ForegroundColor Green

Write-Host "Removing network..." -ForegroundColor Cyan
docker network rm ospf-lab 2>$null | Out-Null
Write-Host "✓ Network removed" -ForegroundColor Green

Write-Host ""
Write-Host "=== Lab Cleaned Up ===" -ForegroundColor Green
Write-Host ""
Write-Host "To start again, run:" -ForegroundColor Gray
Write-Host "  .\nokia_ospf_working.ps1" -ForegroundColor White
Write-Host ""

