#!/bin/bash

# Set to avoid path translation issues on Windows
export MSYS_NO_PATHCONV=1

echo "========================================="
echo "NOKIA NRS OSPF LAB - SIMPLE & WORKING"
echo "========================================="

echo "[1/6] Cleaning up..."
docker stop $(docker ps -aq) 2>/dev/null || true
docker rm $(docker ps -aq) 2>/dev/null || true
docker network prune -f

echo "[2/6] Creating network..."
docker network create --subnet=10.20.30.0/24 ospf-net 2>/dev/null || {
  echo "Network already exists, removing and recreating..."
  docker network rm ospf-net 2>/dev/null || true
  sleep 1
  docker network create --subnet=10.20.30.0/24 ospf-net
}
echo "✓ Network created"

echo "[3/6] Starting routers..."
# Start R1
docker run -d --name R1 --hostname R1 \
  --network ospf-net --ip 10.20.30.1 \
  --privileged \
  frrouting/frr:latest tail -f /dev/null

# Start R2
docker run -d --name R2 --hostname R2 \
  --network ospf-net --ip 10.20.30.2 \
  --privileged \
  frrouting/frr:latest tail -f /dev/null

# Start R3 (will have MTU mismatch)
docker run -d --name R3 --hostname R3 \
  --network ospf-net --ip 10.20.30.3 \
  --privileged \
  frrouting/frr:latest tail -f /dev/null

echo "✓ Routers started"

echo "[4/6] Waiting for containers to start..."
sleep 8

echo "[5/6] Configuring FRR daemons..."
for router in R1 R2 R3; do
  echo "  Configuring $router..."
  
  # Enable zebra and ospfd
  docker exec $router bash -c "echo 'zebra=yes' > /etc/frr/daemons"
  docker exec $router bash -c "echo 'ospfd=yes' >> /etc/frr/daemons"
  
  # Start FRR services
  docker exec $router bash -c "/usr/lib/frr/frrinit.sh start" 2>/dev/null || true
  
  sleep 1
done

echo "✓ Daemons configured"

echo "[6/6] Configuring OSPF..."
# Configure R1
echo "  Configuring R1..."
docker exec R1 bash -c "
vtysh << 'CONFIG'
configure terminal
interface eth0
ip address 10.20.30.1/24
no shutdown
exit
router ospf
ospf router-id 1.1.1.1
network 10.20.30.0/24 area 0.0.0.0
exit
write memory
CONFIG
" 2>/dev/null || echo "  R1 configuration may have issues"

# Configure R2
echo "  Configuring R2..."
docker exec R2 bash -c "
vtysh << 'CONFIG'
configure terminal
interface eth0
ip address 10.20.30.2/24
no shutdown
exit
router ospf
ospf router-id 2.2.2.2
network 10.20.30.0/24 area 0.0.0.0
exit
write memory
CONFIG
" 2>/dev/null || echo "  R2 configuration may have issues"

# Configure R3 with MTU mismatch
echo "  Configuring R3..."
docker exec R3 bash -c "
vtysh << 'CONFIG'
configure terminal
interface eth0
ip address 10.20.30.3/24
no shutdown
exit
router ospf
ospf router-id 3.3.3.3
network 10.20.30.0/24 area 0.0.0.0
exit
write memory
CONFIG
" 2>/dev/null || echo "  R3 configuration may have issues"

# Set MTU mismatch on R3
docker exec R3 ip link set eth0 mtu 1400 2>/dev/null || true

echo "✓ Configuration complete"
echo ""

echo "========================================="
echo "WAITING FOR OSPF ADJACENCIES..."
echo "(This takes 30-40 seconds for FULL state)"
echo "========================================="
sleep 40

echo ""
echo "=== NOKIA NRS DEMONSTRATION ==="
echo ""
echo "1. OSPF NEIGHBOR STATES (R1 perspective):"
echo "-----------------------------------------"
docker exec R1 vtysh -c "show ip ospf neighbor" 2>/dev/null || echo "OSPF not running yet"

echo ""
echo "2. OSPF DATABASE (R1):"
echo "----------------------"
docker exec R1 vtysh -c "show ip ospf database" 2>/dev/null | head -20 || echo "Database not available"

echo ""
echo "3. ROUTING TABLE (R1 - OSPF routes only):"
echo "----------------------------------------"
docker exec R1 vtysh -c "show ip route ospf" 2>/dev/null | head -10 || echo "No OSPF routes yet"

echo ""
echo "========================================="
echo "MTU MISMATCH TROUBLESHOOTING"
echo "========================================="
echo "R3 should be stuck in EXSTART due to MTU 1400"
echo ""
echo "To FIX the MTU issue:"
echo "  docker exec R3 vtysh -c 'conf t' -c 'interface eth0' -c 'ip ospf mtu-ignore' -c 'exit' -c 'exit'"
echo ""
echo "After fixing, wait 40 seconds and check again:"
echo "  docker exec R1 vtysh -c 'show ip ospf neighbor'"
echo ""
echo "To clean up:"
echo "  docker stop R1 R2 R3"
echo "  docker rm R1 R2 R3"
echo "  docker network rm ospf-net"
echo "========================================="

