# Quick MTU Fix Demonstration
# Run this after the lab is set up

Write-Host "=== QUICK MTU FIX DEMO ===" -ForegroundColor Green
Write-Host ""

Write-Host "BEFORE FIX:" -ForegroundColor Yellow
docker exec R1 vtysh -c "show ip ospf neighbor" 2>$null
Write-Host ""

Write-Host "Applying fix..." -ForegroundColor Yellow
docker exec R3 vtysh -c "conf t" -c "interface eth0" -c "ip ospf mtu-ignore" -c "end" -c "copy run start" 2>$null
Write-Host "✓ Fix applied" -ForegroundColor Green
Write-Host ""

Write-Host "Waiting 40 seconds for OSPF reconvergence..." -ForegroundColor Yellow
Start-Sleep -Seconds 40
Write-Host ""

Write-Host "AFTER FIX:" -ForegroundColor Yellow
docker exec R1 vtysh -c "show ip ospf neighbor" 2>$null
Write-Host ""

Write-Host "Complete OSPF Database:" -ForegroundColor Yellow
docker exec R1 vtysh -c "show ip ospf database" 2>$null | Select-Object -First 15
Write-Host ""

Write-Host "OSPF Routes:" -ForegroundColor Yellow
docker exec R1 vtysh -c "show ip route ospf" 2>$null | Select-Object -First 10
Write-Host ""

Write-Host "=== DEMO COMPLETE ===" -ForegroundColor Green

