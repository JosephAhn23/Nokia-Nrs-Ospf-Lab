# Manual Commands - Copy and paste these one by one
# These are the exact commands to run in PowerShell

Write-Host "=== MANUAL OSPF SETUP COMMANDS ===" -ForegroundColor Cyan
Write-Host "Copy and paste each section below:" -ForegroundColor Yellow
Write-Host ""

Write-Host "--- SECTION 1: Clean up ---" -ForegroundColor Green
@"
docker stop `$(docker ps -q) 2>`$null
docker rm `$(docker ps -aq) 2>`$null
docker network prune -f
"@

Write-Host "`n--- SECTION 2: Create network ---" -ForegroundColor Green
@"
docker network create --subnet=192.168.88.0/24 nokia-lab
"@

Write-Host "`n--- SECTION 3: Start routers ---" -ForegroundColor Green
@"
docker run -d --name R1 --hostname R1 --network nokia-lab --ip 192.168.88.10 --privileged frrouting/frr:latest tail -f /dev/null
docker run -d --name R2 --hostname R2 --network nokia-lab --ip 192.168.88.20 --privileged frrouting/frr:latest tail -f /dev/null
docker run -d --name R3 --hostname R3 --network nokia-lab --ip 192.168.88.30 --privileged frrouting/frr:latest tail -f /dev/null
Start-Sleep -Seconds 8
"@

Write-Host "`n--- SECTION 4: Configure R1 ---" -ForegroundColor Green
@"
docker exec R1 bash -c "echo 'zebra=yes' > /etc/frr/daemons"
docker exec R1 bash -c "echo 'ospfd=yes' >> /etc/frr/daemons"
docker exec R1 /usr/lib/frr/frrinit.sh start
Start-Sleep -Seconds 2
docker exec R1 vtysh -c "conf t" -c "int eth0" -c "ip add 192.168.88.10/24" -c "no shut" -c "exit" -c "router ospf" -c "router-id 1.1.1.1" -c "network 192.168.88.0/24 area 0" -c "end" -c "copy run start"
"@

Write-Host "`n--- SECTION 5: Configure R2 ---" -ForegroundColor Green
@"
docker exec R2 bash -c "echo 'zebra=yes' > /etc/frr/daemons"
docker exec R2 bash -c "echo 'ospfd=yes' >> /etc/frr/daemons"
docker exec R2 /usr/lib/frr/frrinit.sh start
Start-Sleep -Seconds 2
docker exec R2 vtysh -c "conf t" -c "int eth0" -c "ip add 192.168.88.20/24" -c "no shut" -c "exit" -c "router ospf" -c "router-id 2.2.2.2" -c "network 192.168.88.0/24 area 0" -c "end" -c "copy run start"
"@

Write-Host "`n--- SECTION 6: Configure R3 (with MTU mismatch) ---" -ForegroundColor Green
@"
docker exec R3 bash -c "echo 'zebra=yes' > /etc/frr/daemons"
docker exec R3 bash -c "echo 'ospfd=yes' >> /etc/frr/daemons"
docker exec R3 /usr/lib/frr/frrinit.sh start
Start-Sleep -Seconds 2
docker exec R3 vtysh -c "conf t" -c "int eth0" -c "ip add 192.168.88.30/24" -c "no shut" -c "exit" -c "router ospf" -c "router-id 3.3.3.3" -c "network 192.168.88.0/24 area 0" -c "end" -c "copy run start"
docker exec R3 ip link set eth0 mtu 1400
"@

Write-Host "`n--- SECTION 7: Wait and check results ---" -ForegroundColor Green
@"
Write-Host "Waiting 45 seconds for OSPF..." -ForegroundColor Yellow
Start-Sleep -Seconds 45
Write-Host "=== OSPF NEIGHBORS ===" -ForegroundColor Green
docker exec R1 vtysh -c "show ip ospf neighbor"
"@

Write-Host "`n=== END OF MANUAL COMMANDS ===" -ForegroundColor Cyan

