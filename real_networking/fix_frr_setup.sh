#!/bin/bash
# Fix FRR Setup - Properly configure and start FRR daemons
# This script fixes the daemon startup issues

set -e

echo "=========================================="
echo "Fixing FRR Setup - Starting Daemons"
echo "=========================================="
echo ""

# Stop and remove existing containers
echo "[1/8] Cleaning up existing containers..."
docker stop frr-router1 frr-router2 frr-router3 frr-router4 2>/dev/null || true
docker rm frr-router1 frr-router2 frr-router3 frr-router4 2>/dev/null || true
echo "✓ Cleanup complete"
echo ""

# Create network bridges (remove existing first if they exist)
echo "[2/8] Creating Docker networks..."
docker network rm net1 net2 net3 2>/dev/null || true
sleep 2
docker network create --subnet=10.0.12.0/24 net1 || {
  echo "Warning: Failed to create net1, trying to use existing..."
  docker network inspect net1 >/dev/null 2>&1 || exit 1
}
docker network create --subnet=10.0.13.0/24 net2 || {
  echo "Warning: Failed to create net2, trying to use existing..."
  docker network inspect net2 >/dev/null 2>&1 || exit 1
}
docker network create --subnet=10.0.14.0/24 net3 || {
  echo "Warning: Failed to create net3, trying to use existing..."
  docker network inspect net3 >/dev/null 2>&1 || exit 1
}
echo "✓ Networks ready"
echo ""

# Start router1 (central router)
echo "[3/8] Starting routers..."
docker run -d --name frr-router1 --hostname router1 \
  --cap-add=NET_ADMIN --cap-add=SYS_ADMIN --cap-add=NET_RAW \
  --network net1 \
  frrouting/frr:latest

# Wait a moment for container to start
sleep 2

# Connect router1 to other networks
docker network connect net2 frr-router1
docker network connect net3 frr-router1

# Start router2
docker run -d --name frr-router2 --hostname router2 \
  --cap-add=NET_ADMIN --cap-add=SYS_ADMIN --cap-add=NET_RAW \
  --network net1 \
  frrouting/frr:latest

# Start router3
docker run -d --name frr-router3 --hostname router3 \
  --cap-add=NET_ADMIN --cap-add=SYS_ADMIN --cap-add=NET_RAW \
  --network net2 \
  frrouting/frr:latest

# Start router4 (will have MTU mismatch)
docker run -d --name frr-router4 --hostname router4 \
  --cap-add=NET_ADMIN --cap-add=SYS_ADMIN --cap-add=NET_RAW \
  --network net3 \
  frrouting/frr:latest

echo "✓ All routers started"
echo ""

# Wait for containers to start
echo "[4/8] Waiting for containers to initialize..."
sleep 5
echo ""

# Enable OSPF in daemon config (properly inside containers)
echo "[5/8] Configuring FRR daemons..."
for router in frr-router1 frr-router2 frr-router3 frr-router4; do
  echo "  Configuring $router..."
  
  # Enable zebra and ospfd
  docker exec $router bash -c "cat > /etc/frr/daemons << 'EOF'
# This file tells the frr package which daemons to start.
#
# Entries are in the format: <daemon>=(yes|no|priority)
# valid daemons are: bgpd, eigrpd, fabricd, isisd, ldpd, nhrpd, ospf6d, ospfd,
#                    pbrd, pimd, ripd, ripngd, staticd, vrrpd, vrrpgrpd,
#                    watcherd, zebra
#
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
vrrpgrpd=no
pathd=no
EOF"
  
  # Restart FRR services inside container
  docker exec $router /usr/lib/frr/frrinit.sh restart 2>/dev/null || true
  sleep 2
done

echo "✓ Daemons configured"
echo ""

echo "[6/8] Waiting for FRR daemons to start..."
sleep 10
echo ""

# Configure router1
echo "[7/8] Configuring OSPF on routers..."
echo "  Configuring router1..."
docker exec frr-router1 vtysh << 'EOF' 2>/dev/null || true
configure terminal
hostname router1
interface eth0
ip address 10.0.12.1/24
no shutdown
exit
interface eth1
ip address 10.0.13.1/24
no shutdown
exit
interface eth2
ip address 10.0.14.1/24
no shutdown
exit
router ospf
ospf router-id 1.1.1.1
network 10.0.12.0/24 area 0.0.0.0
network 10.0.13.0/24 area 0.0.0.0
network 10.0.14.0/24 area 0.0.0.0
exit
exit
EOF

# Configure router2
echo "  Configuring router2..."
docker exec frr-router2 vtysh << 'EOF' 2>/dev/null || true
configure terminal
hostname router2
interface eth0
ip address 10.0.12.2/24
no shutdown
exit
router ospf
ospf router-id 2.2.2.2
network 10.0.12.0/24 area 0.0.0.0
exit
exit
EOF

# Configure router3
echo "  Configuring router3..."
docker exec frr-router3 vtysh << 'EOF' 2>/dev/null || true
configure terminal
hostname router3
interface eth0
ip address 10.0.13.3/24
no shutdown
exit
router ospf
ospf router-id 3.3.3.3
network 10.0.13.0/24 area 0.0.0.0
exit
exit
EOF

# Configure router4 (with MTU mismatch)
echo "  Configuring router4..."
docker exec frr-router4 vtysh << 'EOF' 2>/dev/null || true
configure terminal
hostname router4
interface eth0
ip address 10.0.14.4/24
no shutdown
exit
router ospf
ospf router-id 4.4.4.4
network 10.0.14.0/24 area 0.0.0.0
exit
exit
EOF

# Set MTU mismatch on router4
docker exec frr-router4 ip link set eth0 mtu 1400 2>/dev/null || true

echo "✓ Configuration complete"
echo ""

echo "[8/8] Waiting 20 seconds for OSPF adjacencies to form..."
sleep 20
echo ""

echo "=========================================="
echo "OSPF Setup Complete!"
echo "=========================================="
echo ""

echo "=== OSPF Neighbor Status ==="
docker exec frr-router1 vtysh -c "show ip ospf neighbor" 2>/dev/null || echo "OSPF not running yet"
echo ""

echo "=== OSPF Routes ==="
docker exec frr-router1 vtysh -c "show ip route ospf" 2>/dev/null | head -10 || echo "No OSPF routes yet"
echo ""

echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "NOTE: Router4 should show Init state due to MTU mismatch (1400 vs 1500)"
echo "This is intentional for debugging demonstration."
echo ""
echo "To fix router4 MTU issue:"
echo "  docker exec frr-router4 vtysh -c 'configure terminal' -c 'interface eth0' -c 'ip ospf mtu-ignore' -c 'exit' -c 'exit'"
echo ""

