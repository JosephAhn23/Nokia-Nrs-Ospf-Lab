#!/bin/bash
# Cleanup Linux Networking Topology

set -e

if [ "$EUID" -ne 0 ]; then 
    echo "ERROR: This script must be run as root (sudo)"
    exit 1
fi

echo "Cleaning up network namespaces..."

ip netns del router1 2>/dev/null || true
ip netns del router2 2>/dev/null || true
ip netns del router3 2>/dev/null || true
ip link del veth1-router1 2>/dev/null || true
ip link del veth1-router2 2>/dev/null || true
ip link del veth2-router2 2>/dev/null || true
ip link del veth2-router3 2>/dev/null || true

echo "✓ Cleanup complete"

