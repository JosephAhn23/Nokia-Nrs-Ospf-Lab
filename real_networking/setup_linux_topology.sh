#!/bin/bash
# Real Linux Networking Topology Setup
# Creates network namespaces and veth pairs for real routing protocols

set -e

echo "=========================================="
echo "Setting up REAL Linux Networking Topology"
echo "=========================================="
echo ""

# Check if running as root (required for network namespaces)
if [ "$EUID" -ne 0 ]; then 
    echo "ERROR: This script must be run as root (sudo)"
    echo "Network namespaces require root privileges"
    exit 1
fi

# Clean up any existing setup
echo "[1/6] Cleaning up any existing namespaces..."
ip netns del router1 2>/dev/null || true
ip netns del router2 2>/dev/null || true
ip netns del router3 2>/dev/null || true
ip link del veth1-router1 2>/dev/null || true
ip link del veth1-router2 2>/dev/null || true
ip link del veth2-router2 2>/dev/null || true
ip link del veth2-router3 2>/dev/null || true

# Create network namespaces (isolated routers)
echo "[2/6] Creating network namespaces..."
ip netns add router1
ip netns add router2
ip netns add router3
echo "✓ Created 3 network namespaces"

# Create veth pairs (virtual ethernet cables)
echo "[3/6] Creating veth pairs..."
ip link add veth1-router1 type veth peer name veth1-router2
ip link add veth2-router2 type veth peer name veth2-router3
echo "✓ Created veth pairs"

# Move interfaces into namespaces
echo "[4/6] Moving interfaces into namespaces..."
ip link set veth1-router1 netns router1
ip link set veth1-router2 netns router2
ip link set veth2-router2 netns router2
ip link set veth2-router3 netns router3
echo "✓ Interfaces moved to namespaces"

# Configure IP addresses
echo "[5/6] Configuring IP addresses..."
ip netns exec router1 ip addr add 10.1.1.1/24 dev veth1-router1
ip netns exec router1 ip link set veth1-router1 up
ip netns exec router1 ip link set lo up

ip netns exec router2 ip addr add 10.1.1.2/24 dev veth1-router2
ip netns exec router2 ip link set veth1-router2 up
ip netns exec router2 ip addr add 10.1.2.1/24 dev veth2-router2
ip netns exec router2 ip link set veth2-router2 up
ip netns exec router2 ip link set lo up

ip netns exec router3 ip addr add 10.1.2.2/24 dev veth2-router3
ip netns exec router3 ip link set veth2-router3 up
ip netns exec router3 ip link set lo up
echo "✓ IP addresses configured"

# Enable IP forwarding in each namespace
echo "[6/6] Enabling IP forwarding..."
ip netns exec router1 sysctl -w net.ipv4.ip_forward=1 > /dev/null
ip netns exec router2 sysctl -w net.ipv4.ip_forward=1 > /dev/null
ip netns exec router3 sysctl -w net.ipv4.ip_forward=1 > /dev/null
echo "✓ IP forwarding enabled"

echo ""
echo "=========================================="
echo "Topology Setup Complete!"
echo "=========================================="
echo ""
echo "Topology:"
echo "  router1 (10.1.1.1) <---> router2 (10.1.1.2, 10.1.2.1) <---> router3 (10.1.2.2)"
echo ""
echo "Test connectivity:"
echo "  sudo ip netns exec router1 ping -c 3 10.1.1.2"
echo "  sudo ip netns exec router2 ping -c 3 10.1.1.1"
echo "  sudo ip netns exec router2 ping -c 3 10.1.2.2"
echo "  sudo ip netns exec router3 ping -c 3 10.1.2.1"
echo ""
echo "View routing tables:"
echo "  sudo ip netns exec router1 ip route"
echo "  sudo ip netns exec router2 ip route"
echo "  sudo ip netns exec router3 ip route"
echo ""
echo "Cleanup:"
echo "  sudo ./cleanup_linux_topology.sh"
echo ""

