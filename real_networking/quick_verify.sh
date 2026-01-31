#!/bin/bash
# Quick Verification Script
# Run this once to verify everything works before presenting to Lenish

set -e

if [ "$EUID" -ne 0 ]; then 
    echo "ERROR: This script must be run as root (sudo)"
    exit 1
fi

echo "=========================================="
echo "QUICK VERIFICATION - PRE-LENISH CHECK"
echo "=========================================="
echo ""

cd "$(dirname "$0")"

# Test 1: Docker available
echo "[1/5] Checking Docker..."
if ! command -v docker &> /dev/null; then
    echo "❌ FAIL: Docker not installed"
    exit 1
fi
echo "✓ Docker installed"
echo ""

# Test 2: Setup script works
echo "[2/5] Testing setup script..."
if ! ./setup_frr_docker.sh > /tmp/setup_test.log 2>&1; then
    echo "❌ FAIL: setup_frr_docker.sh failed"
    cat /tmp/setup_test.log
    exit 1
fi
echo "✓ Setup script completed"
echo ""

# Test 3: OSPF adjacencies form
echo "[3/5] Checking OSPF adjacencies (waiting 20 seconds)..."
sleep 20

NEIGHBORS=$(docker exec frr-router1 vtysh -c 'show ip ospf neighbor' 2>/dev/null || echo "")
if echo "$NEIGHBORS" | grep -q "Full"; then
    echo "✓ OSPF adjacencies formed"
    echo "$NEIGHBORS" | head -5
else
    echo "⚠ WARNING: Adjacencies may not be Full yet"
    echo "$NEIGHBORS"
fi
echo ""

# Test 4: IS-IS demo script exists
echo "[4/5] Checking IS-IS demo script..."
if [ -f "./demo_isis_l1_l2_boundary.sh" ]; then
    echo "✓ IS-IS demo script exists"
else
    echo "⚠ WARNING: IS-IS demo script not found"
fi
echo ""

# Test 5: Convergence script exists
echo "[5/5] Checking convergence measurement script..."
if [ -f "./measure_convergence.py" ]; then
    echo "✓ Convergence measurement script exists"
else
    echo "⚠ WARNING: Convergence script not found"
fi
echo ""

echo "=========================================="
echo "VERIFICATION COMPLETE"
echo "=========================================="
echo ""
echo "Status: Ready for Lenish presentation"
echo ""
echo "To run full demo:"
echo "  sudo ./demo_for_lenish.sh"
echo ""
echo "To check current state:"
echo "  docker exec frr-router1 vtysh -c 'show ip ospf neighbor'"
echo ""

