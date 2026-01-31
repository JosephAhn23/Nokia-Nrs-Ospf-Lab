#!/bin/bash

echo "=========================================="
echo "Nokia NRS OSPF Lab Setup"
echo "=========================================="

# Remove ALL existing networks
echo "[0/4] Cleaning up existing networks..."
docker network rm net1 net2 net3 ospf-net ospf-net-12 ospf-net-13 ospf-net-14 2>/dev/null || true
sleep 2

# Create fresh networks with unique subnets
echo "[0/4] Creating networks..."
docker network create --subnet=172.20.12.0/24 net1
docker network create --subnet=172.20.13.0/24 net2
docker network create --subnet=172.20.14.0/24 net3
echo "✓ Networks created"
echo ""

# Stop and remove existing containers
echo "[1/4] Cleaning up existing containers..."
docker stop frr-router1 frr-router2 frr-router3 frr-router4 2>/dev/null || true
docker rm frr-router1 frr-router2 frr-router3 frr-router4 2>/dev/null || true
echo "✓ Cleanup complete"
echo ""

echo "[2/4] Starting routers..."
# Router 1 (central router)
docker run -d --name frr-router1 --hostname router1 \
  --privileged \
  --network net1 --ip 172.20.12.1 \
  frrouting/frr:latest

# Connect router1 to other networks
docker network connect net2 --ip 172.20.13.1 frr-router1
docker network connect net3 --ip 172.20.14.1 frr-router1

# Router 2
docker run -d --name frr-router2 --hostname router2 \
  --privileged \
  --network net1 --ip 172.20.12.2 \
  frrouting/frr:latest

# Router 3
docker run -d --name frr-router3 --hostname router3 \
  --privileged \
  --network net2 --ip 172.20.13.3 \
  frrouting/frr:latest

# Router 4 (with MTU mismatch)
docker run -d --name frr-router4 --hostname router4 \
  --privileged \
  --network net3 --ip 172.20.14.4 \
  frrouting/frr:latest

echo "✓ All routers started"
echo ""

echo "[3/4] Waiting for containers to start..."
sleep 8

echo "[4/4] Configuring FRR daemons..."
# Enable zebra and ospfd in each router
for router in frr-router1 frr-router2 frr-router3 frr-router4; do
  echo "  Configuring $router..."
  
  # Create daemons file
  docker exec $router bash -c "cat > /etc/frr/daemons << 'DAEMONS'
zebra=yes
ospfd=yes
ospf6d=no
ripd=no
ripngd=no
isisd=no
pimd=no
ldpd=no
nhrpd=no
eigrpd=no
babeld=no
sharpd=no
pbrd=no
staticd=no
bfdd=no
fabricd=no
vrrpd=no
DAEMONS"
  
  # Start FRR
  docker exec $router /usr/lib/frr/frrinit.sh start 2>/dev/null || true
  sleep 1
done

echo "✓ Daemons configured"
echo ""

echo "[5/4] Configuring interfaces and OSPF..."
# Configure router1 interfaces
echo "  Configuring router1..."
docker exec frr-router1 vtysh << 'ROUTER1' 2>/dev/null || true
configure terminal
hostname router1
interface eth0
ip address 172.20.12.1/24
no shutdown
exit
interface eth1
ip address 172.20.13.1/24
no shutdown
exit
interface eth2
ip address 172.20.14.1/24
no shutdown
exit
router ospf
ospf router-id 1.1.1.1
network 172.20.12.0/24 area 0.0.0.0
network 172.20.13.0/24 area 0.0.0.0
network 172.20.14.0/24 area 0.0.0.0
exit
write memory
ROUTER1

# Configure router2
echo "  Configuring router2..."
docker exec frr-router2 vtysh << 'ROUTER2' 2>/dev/null || true
configure terminal
hostname router2
interface eth0
ip address 172.20.12.2/24
no shutdown
exit
router ospf
ospf router-id 2.2.2.2
network 172.20.12.0/24 area 0.0.0.0
exit
write memory
ROUTER2

# Configure router3
echo "  Configuring router3..."
docker exec frr-router3 vtysh << 'ROUTER3' 2>/dev/null || true
configure terminal
hostname router3
interface eth0
ip address 172.20.13.3/24
no shutdown
exit
router ospf
ospf router-id 3.3.3.3
network 172.20.13.0/24 area 0.0.0.0
exit
write memory
ROUTER3

# Configure router4 with MTU mismatch
echo "  Configuring router4..."
docker exec frr-router4 vtysh << 'ROUTER4' 2>/dev/null || true
configure terminal
hostname router4
interface eth0
ip address 172.20.14.4/24
no shutdown
exit
router ospf
ospf router-id 4.4.4.4
network 172.20.14.0/24 area 0.0.0.0
exit
write memory
ROUTER4

# Set MTU mismatch on router4
docker exec frr-router4 ip link set eth0 mtu 1400 2>/dev/null || true

echo "✓ Configuration complete"
echo ""

echo "=========================================="
echo "Setup Complete!"
echo "Waiting 20 seconds for OSPF adjacencies..."
echo "=========================================="
sleep 20

echo ""
echo "=== CRITICAL: OSPF Neighbor States ==="
echo "Router1 should see FULL with router2 and router3"
echo "Router1 should see EXSTART with router4 (MTU mismatch)"
echo ""
docker exec frr-router1 vtysh -c "show ip ospf neighbor" 2>/dev/null || echo "OSPF not running yet"

echo ""
echo "=== OSPF Database Summary ==="
docker exec frr-router1 vtysh -c "show ip ospf database" 2>/dev/null | head -20 || echo "Database not available"

echo ""
echo "=== OSPF Routes ==="
docker exec frr-router1 vtysh -c "show ip route ospf" 2>/dev/null | head -10 || echo "No OSPF routes yet"

echo ""
echo "=========================================="
echo "Nokia NRS Demonstration Ready!"
echo "=========================================="
echo "1. MTU Mismatch Failure: router4 stuck in EXSTART"
echo "2. Working adjacencies: router2 and router3 in FULL state"
echo "3. Real OSPF protocol behavior"
echo ""
echo "Test commands:"
echo "  docker exec frr-router1 vtysh -c 'show ip ospf neighbor'"
echo "  docker exec frr-router1 vtysh -c 'show ip route ospf'"
echo "  docker exec frr-router1 vtysh -c 'show ip ospf database'"
echo ""
echo "Fix router4 MTU issue:"
echo "  docker exec frr-router4 vtysh -c 'conf t' -c 'interface eth0' -c 'ip ospf mtu-ignore' -c 'exit' -c 'exit'"
echo "=========================================="

