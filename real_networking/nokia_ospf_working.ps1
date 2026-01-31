# Nokia NRS OSPF Lab - PowerShell Version (Windows)
# Run this in PowerShell

Write-Host "=========================================" -ForegroundColor Green
Write-Host "NOKIA NRS OSPF LAB - DEBUGGED VERSION" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green
Write-Host ""

# Check if Docker is running
try {
    docker version | Out-Null
} catch {
    Write-Host "ERROR: Docker is not running!" -ForegroundColor Red
    Write-Host "Please start Docker Desktop and wait for it to be ready." -ForegroundColor Yellow
    exit 1
}

Write-Host "[1/5] Cleaning up completely..." -ForegroundColor Yellow
docker stop $(docker ps -aq) 2>$null | Out-Null
docker rm $(docker ps -aq) 2>$null | Out-Null
docker network prune -f | Out-Null
Write-Host "✓ Cleanup complete" -ForegroundColor Green
Write-Host ""

Write-Host "[2/5] Creating fresh network..." -ForegroundColor Yellow
docker network rm ospf-lab 2>$null | Out-Null
Start-Sleep -Seconds 1
docker network create --subnet=172.30.40.0/24 ospf-lab | Out-Null
Write-Host "✓ Network created" -ForegroundColor Green
Write-Host ""

Write-Host "[3/5] Starting routers with unique IPs..." -ForegroundColor Yellow
docker run -d --name R1 --hostname R1 `
  --network ospf-lab --ip 172.30.40.10 `
  --privileged `
  frrouting/frr:latest tail -f /dev/null | Out-Null

docker run -d --name R2 --hostname R2 `
  --network ospf-lab --ip 172.30.40.20 `
  --privileged `
  frrouting/frr:latest tail -f /dev/null | Out-Null

docker run -d --name R3 --hostname R3 `
  --network ospf-lab --ip 172.30.40.30 `
  --privileged `
  frrouting/frr:latest tail -f /dev/null | Out-Null

Write-Host "✓ Routers started" -ForegroundColor Green
Write-Host ""

Write-Host "[4/5] Waiting for containers..." -ForegroundColor Yellow
Start-Sleep -Seconds 8
Write-Host ""

Write-Host "[5/5] Configuring FRR and OSPF..." -ForegroundColor Yellow

# Configure daemons for all routers
foreach ($router in @("R1", "R2", "R3")) {
    Write-Host "  Setting up $router..." -ForegroundColor Cyan
    docker exec $router bash -c "echo 'zebra=yes' > /etc/frr/daemons" 2>$null
    docker exec $router bash -c "echo 'ospfd=yes' >> /etc/frr/daemons" 2>$null
    docker exec $router bash -c "/usr/lib/frr/frrinit.sh start" 2>$null
    Start-Sleep -Seconds 2
}

# Configure R1
Write-Host "  Configuring R1..." -ForegroundColor Cyan
docker exec R1 bash -c @"
vtysh << 'CONFIG'
configure terminal
hostname R1
interface eth0
ip address 172.30.40.10/24
no shutdown
exit
router ospf
ospf router-id 1.1.1.1
network 172.30.40.0/24 area 0.0.0.0
exit
end
copy running-config startup-config
CONFIG
"@ 2>$null

# Configure R2
Write-Host "  Configuring R2..." -ForegroundColor Cyan
docker exec R2 bash -c @"
vtysh << 'CONFIG'
configure terminal
hostname R2
interface eth0
ip address 172.30.40.20/24
no shutdown
exit
router ospf
ospf router-id 2.2.2.2
network 172.30.40.0/24 area 0.0.0.0
exit
end
copy running-config startup-config
CONFIG
"@ 2>$null

# Configure R3 with MTU mismatch
Write-Host "  Configuring R3..." -ForegroundColor Cyan
docker exec R3 bash -c @"
vtysh << 'CONFIG'
configure terminal
hostname R3
interface eth0
ip address 172.30.40.30/24
no shutdown
exit
router ospf
ospf router-id 3.3.3.3
network 172.30.40.0/24 area 0.0.0.0
exit
end
copy running-config startup-config
CONFIG
"@ 2>$null

# Set MTU mismatch on R3
docker exec R3 ip link set eth0 mtu 1400 2>$null

Write-Host "✓ Configuration complete" -ForegroundColor Green
Write-Host ""

Write-Host "=========================================" -ForegroundColor Yellow
Write-Host "WAITING 45 SECONDS FOR OSPF..." -ForegroundColor Yellow
Write-Host "=========================================" -ForegroundColor Yellow
Start-Sleep -Seconds 45

Write-Host ""
Write-Host "=== NOKIA NRS OSPF DEMONSTRATION ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. OSPF NEIGHBOR STATES:" -ForegroundColor Yellow
Write-Host "------------------------" -ForegroundColor Yellow
docker exec R1 vtysh -c "show ip ospf neighbor" 2>$null

Write-Host ""
Write-Host "2. OSPF DATABASE (Type 1 Router LSAs):" -ForegroundColor Yellow
Write-Host "--------------------------------------" -ForegroundColor Yellow
docker exec R1 vtysh -c "show ip ospf database" 2>$null | Select-Object -First 20

Write-Host ""
Write-Host "3. OSPF-LEARNED ROUTES:" -ForegroundColor Yellow
Write-Host "----------------------" -ForegroundColor Yellow
docker exec R1 vtysh -c "show ip route ospf" 2>$null | Select-Object -First 10

Write-Host ""
Write-Host "=========================================" -ForegroundColor Green
Write-Host "MTU MISMATCH TROUBLESHOOTING" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green
Write-Host "Expected: R3 should be in EXSTART state (MTU 1400)" -ForegroundColor White
Write-Host ""
Write-Host "To FIX: docker exec R3 vtysh -c 'conf t' -c 'int eth0' -c 'ip ospf mtu-ignore' -c 'exit' -c 'exit'" -ForegroundColor Cyan
Write-Host ""
Write-Host "After fixing, wait 40 seconds and check:" -ForegroundColor White
Write-Host "  docker exec R1 vtysh -c 'show ip ospf neighbor'" -ForegroundColor Cyan
Write-Host ""
Write-Host "To clean up:" -ForegroundColor Gray
Write-Host "  docker stop R1 R2 R3" -ForegroundColor White
Write-Host "  docker rm R1 R2 R3" -ForegroundColor White
Write-Host "  docker network rm ospf-lab" -ForegroundColor White
Write-Host "=========================================" -ForegroundColor Green

