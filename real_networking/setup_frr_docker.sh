#!/bin/bash
# Setup FRRouting (FRR) using Docker containers
# This is the EASIEST way to run real OSPF/ISIS

set -e

echo "=========================================="
echo "Setting up FRRouting (FRR) with Docker"
echo "=========================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "ERROR: Docker is not installed"
    echo "Install Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

echo "[1/4] Pulling FRR Docker image..."
docker pull frrouting/frr:latest || {
    echo "ERROR: Failed to pull FRR image"
    echo "Check your internet connection and Docker setup"
    exit 1
}
echo "✓ FRR image ready"

echo "[2/4] Creating Docker network for OSPF..."
docker network create --subnet=172.20.0.0/24 ospf-net 2>/dev/null || echo "Network already exists"
echo "✓ Docker network created"

echo "[+] Setting up FRR containers for OSPF/IS-IS lab..."
echo "[+] Creating 4-router topology with Ethernet segments..."

echo "[3/4] Starting FRR routers..."

# Stop existing containers
docker stop frr-router1 frr-router2 frr-router3 frr-router4 2>/dev/null || true
docker rm frr-router1 frr-router2 frr-router3 frr-router4 2>/dev/null || true

# Create additional networks for 4-router topology
docker network create --subnet=10.0.12.0/24 ospf-net-12 2>/dev/null || echo "Network already exists"
docker network create --subnet=10.0.13.0/24 ospf-net-13 2>/dev/null || echo "Network already exists"
docker network create --subnet=10.0.14.0/24 ospf-net-14 2>/dev/null || echo "Network already exists"

# Router 1 configuration (hub - connects to router2, router3, router4)
cat > /tmp/frr1.conf <<'EOF'
hostname router1
password zebra
enable password zebra

interface eth0
 ip address 10.0.12.1/24
!

interface eth1
 ip address 10.0.13.1/24
!

interface eth2
 ip address 10.0.14.1/24
!

router ospf
 ospf router-id 1.1.1.1
 network 10.0.12.0/24 area 0.0.0.0
 network 10.0.13.0/24 area 0.0.0.0
 network 10.0.14.0/24 area 0.0.0.0
!

line vty
!
EOF

# Router 2 configuration
cat > /tmp/frr2.conf <<'EOF'
hostname router2
password zebra
enable password zebra

interface eth0
 ip address 10.0.12.2/24
!

router ospf
 ospf router-id 2.2.2.2
 network 10.0.12.0/24 area 0.0.0.0
!

line vty
!
EOF

# Router 3 configuration
cat > /tmp/frr3.conf <<'EOF'
hostname router3
password zebra
enable password zebra

interface eth0
 ip address 10.0.13.3/24
!

router ospf
 ospf router-id 3.3.3.3
 network 10.0.13.0/24 area 0.0.0.0
!

line vty
!
EOF

# Router 4 configuration (will have MTU mismatch issue)
cat > /tmp/frr4.conf <<'EOF'
hostname router4
password zebra
enable password zebra

interface eth0
 ip address 10.0.14.4/24
!

router ospf
 ospf router-id 4.4.4.4
 network 10.0.14.0/24 area 0.0.0.0
!

line vty
!
EOF

# Start Router 1 (hub)
docker run -d --name frr-router1 --network ospf-net-12 \
    -v /tmp/frr1.conf:/etc/frr/frr.conf \
    --cap-add=NET_ADMIN \
    frrouting/frr:latest

# Connect router1 to other networks
docker network connect ospf-net-13 frr-router1
docker network connect ospf-net-14 frr-router1

# Start Router 2
docker run -d --name frr-router2 --network ospf-net-12 \
    -v /tmp/frr2.conf:/etc/frr/frr.conf \
    --cap-add=NET_ADMIN \
    frrouting/frr:latest

# Start Router 3
docker run -d --name frr-router3 --network ospf-net-13 \
    -v /tmp/frr3.conf:/etc/frr/frr.conf \
    --cap-add=NET_ADMIN \
    frrouting/frr:latest

# Start Router 4 (with MTU mismatch - interface MTU 1550, OSPF MTU 1500)
docker run -d --name frr-router4 --network ospf-net-14 \
    -v /tmp/frr4.conf:/etc/frr/frr.conf \
    --cap-add=NET_ADMIN \
    frrouting/frr:latest

# Set MTU mismatch on router4 (interface MTU 1550, OSPF expects 1500)
docker exec frr-router4 ip link set eth0 mtu 1550 2>/dev/null || true

echo "[+] Starting containers: frr-router1, frr-router2, frr-router3, frr-router4"
echo "[+] Configuring OSPF (Router ID 1.1.1.1, Area 0) on router1..."
echo "[+] Configuring OSPF (Router ID 2.2.2.2, Area 0) on router2..."
echo "[+] Configuring OSPF (Router ID 3.3.3.3, Area 0) on router3..."
echo "[+] Configuring OSPF (Router ID 4.4.4.4, Area 0) on router4..."
echo "✓ FRR routers started"

# Wait for routers to initialize
echo "[4/4] Waiting for routers to initialize..."
sleep 5

echo "[+] Waiting 15 seconds for OSPF adjacencies to form..."
sleep 15

echo ""
echo "=========================================="
echo "FRR OSPF Setup Complete!"
echo "=========================================="
echo ""
echo "Topology:"
echo "  router1 (1.1.1.1) <--eth0--> router2 (2.2.2.2)"
echo "  router1 (1.1.1.1) <--eth1--> router3 (3.3.3.3)"
echo "  router1 (1.1.1.1) <--eth2--> router4 (4.4.4.4) [MTU mismatch]"
echo ""
echo "Check OSPF neighbors:"
echo "  docker exec frr-router1 vtysh -c 'show ip ospf neighbor'"
echo ""
echo "NOTE: Router4 may be stuck in Init state due to MTU mismatch."
echo "      This is intentional for debugging demonstration."
echo ""
echo "View routing tables:"
echo "  docker exec frr-router1 vtysh -c 'show ip route'"
echo ""
echo "View OSPF database:"
echo "  docker exec frr-router1 vtysh -c 'show ip ospf database'"
echo ""
echo "Stop routers:"
echo "  docker stop frr-router1 frr-router2 frr-router3 frr-router4"
echo ""

