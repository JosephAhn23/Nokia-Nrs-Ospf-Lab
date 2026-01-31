#!/bin/bash

echo "=========================================="
echo "Testing Single FRR Router"
echo "=========================================="
echo ""

# Clean up
docker rm -f test-router 2>/dev/null

echo "[1/5] Starting test container..."
docker run -d --name test-router --privileged frrouting/frr:latest
sleep 5

echo "[2/5] Checking FRR daemons status..."
docker exec test-router /usr/lib/frr/frrinit.sh status 2>/dev/null || echo "FRR init script not available"

echo ""
echo "[3/5] Enabling OSPF daemon..."
docker exec test-router bash -c "cat > /etc/frr/daemons << 'EOF'
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

echo "[4/5] Restarting FRR..."
docker exec test-router /usr/lib/frr/frrinit.sh restart 2>/dev/null || true
sleep 3

echo ""
echo "[5/5] Testing vtysh..."
echo "=== Checking daemons ==="
docker exec test-router vtysh -c "show daemons" 2>/dev/null || echo "vtysh not working"

echo ""
echo "=== Configuring loopback ==="
docker exec test-router vtysh << 'EOF' 2>/dev/null || true
configure terminal
interface lo
ip address 10.255.255.1/32
no shutdown
exit
router ospf
ospf router-id 10.255.255.1
network 10.255.255.1/32 area 0.0.0.0
exit
exit
EOF

echo ""
echo "=== Checking OSPF ==="
docker exec test-router vtysh -c "show ip ospf" 2>/dev/null | head -10 || echo "OSPF not running"

echo ""
echo "=== Checking Routes ==="
docker exec test-router vtysh -c "show ip route" 2>/dev/null | head -10 || echo "No routes"

echo ""
echo "=========================================="
echo "Test Complete!"
echo "=========================================="
echo ""
echo "If this works, we can scale to multiple routers."
echo "If it fails, check Docker Desktop is running properly."
echo ""
echo "To clean up: docker rm -f test-router"
echo ""

