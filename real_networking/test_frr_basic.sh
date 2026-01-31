#!/bin/bash

echo "=========================================="
echo "Basic FRR Test - Verify Docker Works"
echo "=========================================="
echo ""

echo "[1/3] Testing FRR container..."
docker run --rm --name test-frr frrouting/frr:latest vtysh -c "show version" 2>/dev/null || {
  echo "❌ FRR container test failed"
  echo "Check Docker Desktop is running"
  exit 1
}

echo "✓ FRR container works"
echo ""

echo "[2/3] Testing FRR daemons..."
docker run --rm --name test-frr-daemon --privileged frrouting/frr:latest bash -c "
echo 'zebra=yes' > /etc/frr/daemons
echo 'ospfd=yes' >> /etc/frr/daemons
/usr/lib/frr/frrinit.sh start
sleep 2
vtysh -c 'show daemons'
" 2>/dev/null || {
  echo "❌ FRR daemon test failed"
  exit 1
}

echo "✓ FRR daemons work"
echo ""

echo "[3/3] Testing OSPF configuration..."
docker run --rm --name test-frr-ospf --privileged frrouting/frr:latest bash -c "
echo 'zebra=yes' > /etc/frr/daemons
echo 'ospfd=yes' >> /etc/frr/daemons
/usr/lib/frr/frrinit.sh start
sleep 2
vtysh -c 'conf t' \\
  -c 'interface lo' \\
  -c 'ip address 1.1.1.1/32' \\
  -c 'no shutdown' \\
  -c 'exit' \\
  -c 'router ospf' \\
  -c 'router-id 1.1.1.1' \\
  -c 'network 1.1.1.1/32 area 0.0.0.0' \\
  -c 'exit' \\
  -c 'write'
sleep 2
vtysh -c 'show ip ospf'
" 2>/dev/null || {
  echo "❌ OSPF configuration test failed"
  exit 1
}

echo "✓ OSPF configuration works"
echo ""

echo "=========================================="
echo "All Tests Passed!"
echo "=========================================="
echo ""
echo "Docker and FRR are working correctly."
echo "You can now run: bash simple_2router_test.sh"
echo ""

