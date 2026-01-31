# Nokia NRS OSPF Demo - PowerShell Script
# Run this in PowerShell as Administrator after Docker Desktop is running

Write-Host "=== Nokia NRS Certification Demo ===" -ForegroundColor Green
Write-Host ""

# Check if Docker is running
try {
    docker version | Out-Null
} catch {
    Write-Host "ERROR: Docker is not running!" -ForegroundColor Red
    Write-Host "Please start Docker Desktop and wait for it to be ready." -ForegroundColor Yellow
    Write-Host "Look for the green whale icon in the system tray." -ForegroundColor Yellow
    exit 1
}

Write-Host "✓ Docker is running" -ForegroundColor Green
Write-Host ""

# Clean up
Write-Host "[1/6] Cleaning up..." -ForegroundColor Yellow
docker container prune -f | Out-Null
docker network prune -f | Out-Null
Write-Host "✓ Cleanup complete" -ForegroundColor Green
Write-Host ""

# Create network
Write-Host "[2/6] Creating network..." -ForegroundColor Yellow
docker network create --subnet=10.99.88.0/24 nokia-lab 2>$null
Write-Host "✓ Network created" -ForegroundColor Green
Write-Host ""

# Start router 1
Write-Host "[3/6] Starting routers..." -ForegroundColor Yellow
Write-Host "  Starting R1..." -ForegroundColor Cyan
docker run -d --name R1 --hostname R1 `
  --network nokia-lab --ip 10.99.88.1 `
  --privileged `
  frrouting/frr:latest tail -f /dev/null

# Start router 2
Write-Host "  Starting R2..." -ForegroundColor Cyan
docker run -d --name R2 --hostname R2 `
  --network nokia-lab --ip 10.99.88.2 `
  --privileged `
  frrouting/frr:latest tail -f /dev/null

Write-Host "✓ Routers started" -ForegroundColor Green
Write-Host ""

Write-Host "[4/6] Waiting for containers to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 5
Write-Host ""

Write-Host "[5/6] Configuring FRR..." -ForegroundColor Yellow

# Configure R1
Write-Host "  Configuring R1..." -ForegroundColor Cyan
docker exec R1 bash -c @'
echo "zebra=yes" > /etc/frr/daemons
echo "ospfd=yes" >> /etc/frr/daemons
/usr/lib/frr/frrinit.sh start
sleep 2
vtysh << "VTYSH"
configure terminal
hostname R1
interface eth0
ip address 10.99.88.1/24
no shutdown
exit
router ospf
ospf router-id 1.1.1.1
network 10.99.88.0/24 area 0.0.0.0
exit
write memory
VTYSH
'@ 2>$null

# Configure R2
Write-Host "  Configuring R2..." -ForegroundColor Cyan
docker exec R2 bash -c @'
echo "zebra=yes" > /etc/frr/daemons
echo "ospfd=yes" >> /etc/frr/daemons
/usr/lib/frr/frrinit.sh start
sleep 2
vtysh << "VTYSH"
configure terminal
hostname R2
interface eth0
ip address 10.99.88.2/24
no shutdown
exit
router ospf
ospf router-id 2.2.2.2
network 10.99.88.0/24 area 0.0.0.0
exit
write memory
VTYSH
'@ 2>$null

Write-Host "✓ Configuration complete" -ForegroundColor Green
Write-Host ""

Write-Host "[6/6] Waiting 40 seconds for OSPF convergence..." -ForegroundColor Yellow
Write-Host "(OSPF needs time to form FULL adjacencies)" -ForegroundColor Gray
Start-Sleep -Seconds 40
Write-Host ""

Write-Host "=== OSPF NEIGHBORS ===" -ForegroundColor Cyan
docker exec R1 vtysh -c "show ip ospf neighbor" 2>$null
Write-Host ""

Write-Host "=== OSPF DATABASE ===" -ForegroundColor Cyan
docker exec R1 vtysh -c "show ip ospf database" 2>$null | Select-Object -First 15
Write-Host ""

Write-Host "=== OSPF ROUTES ===" -ForegroundColor Cyan
docker exec R1 vtysh -c "show ip route ospf" 2>$null | Select-Object -First 10
Write-Host ""

Write-Host "=== NOKIA NRS DEMO COMPLETE ===" -ForegroundColor Green
Write-Host ""
Write-Host "Real OSPF protocol demonstration:" -ForegroundColor Yellow
Write-Host "1. Adjacency: DOWN -> INIT -> 2-WAY -> EXSTART -> EXCHANGE -> LOADING -> FULL" -ForegroundColor White
Write-Host "2. Database: Router LSAs (Type 1)" -ForegroundColor White
Write-Host "3. Routes: Installed in kernel routing table" -ForegroundColor White
Write-Host ""
Write-Host "To clean up:" -ForegroundColor Gray
Write-Host "  docker stop R1 R2" -ForegroundColor White
Write-Host "  docker rm R1 R2" -ForegroundColor White
Write-Host "  docker network rm nokia-lab" -ForegroundColor White
Write-Host ""

