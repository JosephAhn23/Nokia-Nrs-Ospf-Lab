#!/bin/bash
# Complete Real Networking Demonstration
# Shows actual OSPF behavior, routing tables, and packet captures

set -e

echo "=========================================="
echo "REAL NETWORKING DEMONSTRATION"
echo "=========================================="
echo ""
echo "This demonstrates ACTUAL networking, not simulation"
echo ""

# Check if Docker FRR is running
if ! docker ps | grep -q frr-router; then
    echo "ERROR: Docker FRR setup not running"
    echo "Run: sudo ./setup_frr_docker.sh first"
    exit 1
fi

echo "[1/6] Checking OSPF Neighbor Adjacencies"
echo "----------------------------------------"
echo ""
for router in frr-router1 frr-router2 frr-router3; do
    echo "$router:"
    docker exec $router vtysh -c 'show ip ospf neighbor' 2>/dev/null || echo "  (No neighbors yet)"
    echo ""
done

echo "[2/6] Showing Routing Tables"
echo "----------------------------------------"
echo ""
for router in frr-router1 frr-router2 frr-router3; do
    echo "$router routing table:"
    docker exec $router vtysh -c 'show ip route' 2>/dev/null | head -20
    echo ""
done

echo "[3/6] Showing OSPF Database"
echo "----------------------------------------"
echo ""
echo "Router1 OSPF LSDB:"
docker exec frr-router1 vtysh -c 'show ip ospf database' 2>/dev/null | head -15
echo ""

echo "[4/6] Showing OSPF Interface Details"
echo "----------------------------------------"
echo ""
for router in frr-router1 frr-router2 frr-router3; do
    echo "$router interfaces:"
    docker exec $router vtysh -c 'show ip ospf interface' 2>/dev/null | head -10
    echo ""
done

echo "[5/6] Linux Kernel Routing Tables (Real Routes)"
echo "----------------------------------------"
echo ""
for router in frr-router1 frr-router2 frr-router3; do
    echo "$router kernel routes:"
    docker exec $router ip route show 2>/dev/null | head -10
    echo ""
done

echo "[6/6] Packet Capture Instructions"
echo "----------------------------------------"
echo ""
echo "To capture real OSPF packets:"
echo "  sudo ./capture_ospf_packets.sh"
echo ""
echo "To analyze with Wireshark:"
echo "  wireshark packet_captures/ospf_capture_*.pcap"
echo ""
echo "To measure convergence:"
echo "  python3 measure_convergence.py"
echo ""

echo "=========================================="
echo "DEMONSTRATION COMPLETE"
echo "=========================================="
echo ""
echo "This shows:"
echo "  ✓ Real OSPF adjacencies (not simulated)"
echo "  ✓ Real routing tables (actual kernel routes)"
echo "  ✓ Real protocol state (OSPF database)"
echo "  ✓ Real packet capture capability"
echo ""
echo "This is what network engineers actually work with."
echo ""

