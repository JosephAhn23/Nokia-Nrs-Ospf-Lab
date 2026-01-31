# Quick OSPF Setup - PowerShell Commands
# Copy and paste these commands one section at a time

Write-Host "=== Quick OSPF Lab Setup ===" -ForegroundColor Green
Write-Host ""

# Step 1: Clean up
Write-Host "[1/4] Cleaning up..." -ForegroundColor Yellow
docker stop R1 R2 R3 2>$null
docker rm R1 R2 R3 2>$null
docker network rm ospf-lab 2>$null
Start-Sleep -Seconds 2

# Step 2: Create network
Write-Host "[2/4] Creating network..." -ForegroundColor Yellow
docker network create --subnet=172.30.40.0/24 ospf-lab

# Step 3: Start routers
Write-Host "[3/4] Starting routers..." -ForegroundColor Yellow
docker run -d --name R1 --hostname R1 --network ospf-lab --ip 172.30.40.10 --privileged frrouting/frr:latest tail -f /dev/null
docker run -d --name R2 --hostname R2 --network ospf-lab --ip 172.30.40.20 --privileged frrouting/frr:latest tail -f /dev/null
docker run -d --name R3 --hostname R3 --network ospf-lab --ip 172.30.40.30 --privileged frrouting/frr:latest tail -f /dev/null

Write-Host "Waiting 8 seconds..." -ForegroundColor Gray
Start-Sleep -Seconds 8

# Step 4: Configure routers
Write-Host "[4/4] Configuring routers..." -ForegroundColor Yellow

# R1
Write-Host "  Configuring R1..." -ForegroundColor Cyan
docker exec R1 bash -c "echo 'zebra=yes' > /etc/frr/daemons; echo 'ospfd=yes' >> /etc/frr/daemons; /usr/lib/frr/frrinit.sh start"
Start-Sleep -Seconds 2
docker exec R1 vtysh -c "conf t" -c "hostname R1" -c "int eth0" -c "ip add 172.30.40.10/24" -c "no shut" -c "exit" -c "router ospf" -c "router-id 1.1.1.1" -c "network 172.30.40.0/24 area 0.0.0.0" -c "exit" -c "end"

# R2
Write-Host "  Configuring R2..." -ForegroundColor Cyan
docker exec R2 bash -c "echo 'zebra=yes' > /etc/frr/daemons; echo 'ospfd=yes' >> /etc/frr/daemons; /usr/lib/frr/frrinit.sh start"
Start-Sleep -Seconds 2
docker exec R2 vtysh -c "conf t" -c "hostname R2" -c "int eth0" -c "ip add 172.30.40.20/24" -c "no shut" -c "exit" -c "router ospf" -c "router-id 2.2.2.2" -c "network 172.30.40.0/24 area 0.0.0.0" -c "exit" -c "end"

# R3
Write-Host "  Configuring R3..." -ForegroundColor Cyan
docker exec R3 bash -c "echo 'zebra=yes' > /etc/frr/daemons; echo 'ospfd=yes' >> /etc/frr/daemons; /usr/lib/frr/frrinit.sh start"
Start-Sleep -Seconds 2
docker exec R3 vtysh -c "conf t" -c "hostname R3" -c "int eth0" -c "ip add 172.30.40.30/24" -c "no shut" -c "exit" -c "router ospf" -c "router-id 3.3.3.3" -c "network 172.30.40.0/24 area 0.0.0.0" -c "exit" -c "end"

# Set MTU mismatch on R3
docker exec R3 ip link set eth0 mtu 1400

Write-Host "✓ Configuration complete" -ForegroundColor Green
Write-Host ""
Write-Host "Waiting 45 seconds for OSPF adjacencies..." -ForegroundColor Yellow
Start-Sleep -Seconds 45

Write-Host ""
Write-Host "=== OSPF NEIGHBORS ===" -ForegroundColor Cyan
docker exec R1 vtysh -c "show ip ospf neighbor"

Write-Host ""
Write-Host "=== OSPF DATABASE ===" -ForegroundColor Cyan
docker exec R1 vtysh -c "show ip ospf database" | Select-Object -First 15

Write-Host ""
Write-Host "=== OSPF ROUTES ===" -ForegroundColor Cyan
docker exec R1 vtysh -c "show ip route ospf" | Select-Object -First 10

Write-Host ""
Write-Host "=== DONE ===" -ForegroundColor Green

