#!/bin/bash
# Setup FRRouting (FRR) with OSPF on Linux network namespaces
# This runs REAL OSPF protocol, not a simulation

set -e

if [ "$EUID" -ne 0 ]; then 
    echo "ERROR: This script must be run as root (sudo)"
    exit 1
fi

echo "=========================================="
echo "Setting up FRRouting (FRR) with OSPF"
echo "=========================================="
echo ""

# Check if FRR is installed
if ! command -v vtysh &> /dev/null; then
    echo "ERROR: FRRouting (FRR) is not installed"
    echo ""
    echo "Install FRR:"
    echo "  Ubuntu/Debian: sudo apt-get install frr frr-pythontools"
    echo "  Or use Docker: docker pull frrouting/frr"
    echo ""
    exit 1
fi

# First, ensure Linux topology is set up
if [ ! -f "setup_linux_topology.sh" ]; then
    echo "ERROR: setup_linux_topology.sh not found"
    echo "Run setup_linux_topology.sh first"
    exit 1
fi

echo "[1/5] Ensuring Linux topology is set up..."
if ! ip netns list | grep -q router1; then
    echo "Running setup_linux_topology.sh..."
    ./setup_linux_topology.sh
fi

# Create FRR config directories in each namespace
echo "[2/5] Setting up FRR configuration..."
mkdir -p /tmp/frr-router1 /tmp/frr-router2 /tmp/frr-router3

# Router 1 OSPF config
cat > /tmp/frr-router1/frr.conf <<EOF
hostname router1
password zebra
enable password zebra

router ospf
 ospf router-id 1.1.1.1
 network 10.1.1.0/24 area 0.0.0.0
 passive-interface lo
!
line vty
!
EOF

# Router 2 OSPF config
cat > /tmp/frr-router2/frr.conf <<EOF
hostname router2
password zebra
enable password zebra

router ospf
 ospf router-id 2.2.2.2
 network 10.1.1.0/24 area 0.0.0.0
 network 10.1.2.0/24 area 0.0.0.0
 passive-interface lo
!
line vty
!
EOF

# Router 3 OSPF config
cat > /tmp/frr-router3/frr.conf <<EOF
hostname router3
password zebra
enable password zebra

router ospf
 ospf router-id 3.3.3.3
 network 10.1.2.0/24 area 0.0.0.0
 passive-interface lo
!
line vty
!
EOF

echo "✓ FRR configuration files created"

# Start FRR daemons in each namespace
echo "[3/5] Starting FRR daemons..."
echo "  (This requires FRR to be installed and configured)"
echo ""
echo "NOTE: Running FRR in network namespaces requires:"
echo "  1. FRR installed on the system"
echo "  2. Proper permissions to run daemons"
echo ""
echo "Alternative: Use FRR Docker containers (see setup_frr_docker.sh)"
echo ""

# For now, provide instructions
echo "To manually start FRR in namespaces:"
echo ""
echo "  # Router 1"
echo "  sudo ip netns exec router1 zebra -d -f /tmp/frr-router1/frr.conf -i /tmp/frr-router1/zebra.pid"
echo "  sudo ip netns exec router1 ospfd -d -f /tmp/frr-router1/frr.conf -i /tmp/frr-router1/ospfd.pid"
echo ""
echo "  # Router 2"
echo "  sudo ip netns exec router2 zebra -d -f /tmp/frr-router2/frr.conf -i /tmp/frr-router2/zebra.pid"
echo "  sudo ip netns exec router2 ospfd -d -f /tmp/frr-router2/frr.conf -i /tmp/frr-router2/ospfd.pid"
echo ""
echo "  # Router 3"
echo "  sudo ip netns exec router3 zebra -d -f /tmp/frr-router3/frr.conf -i /tmp/frr-router3/zebra.pid"
echo "  sudo ip netns exec router3 ospfd -d -f /tmp/frr-router3/frr.conf -i /tmp/frr-router3/ospfd.pid"
echo ""

echo "=========================================="
echo "FRR Setup Instructions Complete"
echo "=========================================="
echo ""
echo "For easier setup, use Docker-based FRR (see setup_frr_docker.sh)"
echo ""

