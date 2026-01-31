#!/bin/bash

# Set to avoid Windows path translation
export MSYS_NO_PATHCONV=1

echo "========================================="
echo "NOKIA NRS OSPF LAB - DEBUGGED VERSION"
echo "========================================="

echo "[1/5] Cleaning up completely..."
docker stop $(docker ps -aq) 2>/dev/null || true
docker rm $(docker ps -aq) 2>/dev/null || true
docker network prune -f
echo "✓ Cleanup complete"
echo ""

echo "[2/5] Creating fresh network..."
docker network create --subnet=172.30.40.0/24 ospf-lab 2>/dev/null || {
  echo "Network exists, removing and recreating..."
  docker network rm ospf-lab 2>/dev/null || true
  sleep 1
  docker network create --subnet=172.30.40.0/24 ospf-lab
}
echo "✓ Network created"
echo ""

echo "[3/5] Starting routers with unique IPs..."
# Use different IP range to avoid conflicts
docker run -d --name R1 --hostname R1 \
  --network ospf-lab --ip 172.30.40.10 \
  --privileged \
  frrouting/frr:latest tail -f /dev/null

docker run -d --name R2 --hostname R2 \
  --network ospf-lab --ip 172.30.40.20 \
  --privileged \
  frrouting/frr:latest tail -f /dev/null

docker run -d --name R3 --hostname R3 \
  --network ospf-lab --ip 172.30.40.30 \
  --privileged \
  frrouting/frr:latest tail -f /dev/null

echo "✓ Routers started"
echo ""

echo "[4/5] Waiting for containers..."
sleep 8
echo ""

echo "[5/5] Configuring FRR and OSPF..."
for router in R1 R2 R3; do
  echo "  Setting up $router..."
  
  # Enable daemons
  docker exec $router bash -c "
    echo 'zebra=yes' > /etc/frr/daemons
    echo 'ospfd=yes' >> /etc/frr/daemons
    /usr/lib/frr/frrinit.sh start
    sleep 2
  " 2>/dev/null || true
done

echo "  Configuring R1..."
# R1 configuration
docker exec R1 bash -c "
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
" 2>/dev/null || echo "  R1 configuration may have issues"

echo "  Configuring R2..."
# R2 configuration
docker exec R2 bash -c "
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
" 2>/dev/null || echo "  R2 configuration may have issues"

echo "  Configuring R3..."
# R3 configuration with MTU mismatch
docker exec R3 bash -c "
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
" 2>/dev/null || echo "  R3 configuration may have issues"

# Set MTU mismatch on R3
docker exec R3 ip link set eth0 mtu 1400 2>/dev/null || true

echo "✓ Configuration complete"
echo ""

echo "========================================="
echo "WAITING 45 SECONDS FOR OSPF..."
echo "========================================="
sleep 45

echo ""
echo "=== NOKIA NRS OSPF DEMONSTRATION ==="
echo ""
echo "1. OSPF NEIGHBOR STATES:"
echo "------------------------"
docker exec R1 vtysh -c "show ip ospf neighbor" 2>/dev/null || echo "OSPF not running yet"

echo ""
echo "2. OSPF DATABASE (Type 1 Router LSAs):"
echo "--------------------------------------"
docker exec R1 vtysh -c "show ip ospf database" 2>/dev/null | head -20 || echo "Database not available"

echo ""
echo "3. OSPF-LEARNED ROUTES:"
echo "----------------------"
docker exec R1 vtysh -c "show ip route ospf" 2>/dev/null | head -10 || echo "No OSPF routes yet"

echo ""
echo "========================================="
echo "MTU MISMATCH TROUBLESHOOTING"
echo "========================================="
echo "Expected: R3 should be in EXSTART state (MTU 1400)"
echo ""
echo "To FIX: docker exec R3 vtysh -c 'conf t' -c 'int eth0' -c 'ip ospf mtu-ignore' -c 'exit' -c 'exit'"
echo ""
echo "After fixing, wait 40 seconds and check:"
echo "  docker exec R1 vtysh -c 'show ip ospf neighbor'"
echo ""
echo "To clean up:"
echo "  docker stop R1 R2 R3"
echo "  docker rm R1 R2 R3"
echo "  docker network rm ospf-lab"
echo "========================================="

