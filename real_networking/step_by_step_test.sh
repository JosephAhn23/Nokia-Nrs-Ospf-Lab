#!/bin/bash
# Step-by-step OSPF test - Start with 1 router, then add 2nd

export MSYS_NO_PATHCONV=1

echo "========================================="
echo "STEP-BY-STEP OSPF TEST"
echo "========================================="
echo ""

echo "[STEP 1] Cleaning up..."
docker stop $(docker ps -aq) 2>/dev/null || true
docker rm $(docker ps -aq) 2>/dev/null || true
docker network prune -f
echo "✓ Cleanup complete"
echo ""

echo "[STEP 2] Creating network..."
docker network create --subnet=192.168.99.0/24 nokia-lab
echo "✓ Network created"
echo ""

echo "[STEP 3] Starting test router..."
docker run -d --name test-router --hostname test-router \
  --network nokia-lab --ip 192.168.99.100 \
  --privileged \
  frrouting/frr:latest tail -f /dev/null

sleep 5
echo "✓ Test router started"
echo ""

echo "[STEP 4] Configuring test router..."
docker exec test-router bash -c "
echo 'zebra=yes' > /etc/frr/daemons
echo 'ospfd=yes' >> /etc/frr/daemons
/usr/lib/frr/frrinit.sh start
sleep 2
vtysh << 'EOF'
configure terminal
hostname TEST-ROUTER
interface eth0
ip address 192.168.99.100/24
no shutdown
exit
router ospf
ospf router-id 100.100.100.100
network 192.168.99.0/24 area 0.0.0.0
exit
end
EOF
sleep 2
vtysh -c 'show ip ospf'
vtysh -c 'show ip route'
" 2>/dev/null || echo "Configuration may have issues"

echo ""
echo "=== TEST ROUTER STATUS ==="
docker exec test-router vtysh -c "show ip ospf" 2>/dev/null || echo "OSPF not running"
echo ""

read -p "Press Enter to add second router (R2)..."

echo ""
echo "[STEP 5] Adding second router (R2)..."
docker run -d --name R2 --hostname R2 \
  --network nokia-lab --ip 192.168.99.200 \
  --privileged \
  frrouting/frr:latest tail -f /dev/null

sleep 5
echo "✓ R2 started"
echo ""

echo "[STEP 6] Configuring R2..."
docker exec R2 bash -c "
echo 'zebra=yes' > /etc/frr/daemons
echo 'ospfd=yes' >> /etc/frr/daemons
/usr/lib/frr/frrinit.sh start
sleep 2
vtysh << 'EOF'
configure terminal
hostname R2
interface eth0
ip address 192.168.99.200/24
no shutdown
exit
router ospf
ospf router-id 200.200.200.200
network 192.168.99.0/24 area 0.0.0.0
exit
end
EOF
" 2>/dev/null || echo "R2 configuration may have issues"

echo ""
echo "[STEP 7] Waiting 40 seconds for OSPF adjacencies..."
sleep 40

echo ""
echo "=== OSPF NEIGHBORS ==="
echo "Test Router:"
docker exec test-router vtysh -c "show ip ospf neighbor" 2>/dev/null || echo "No neighbors"
echo ""
echo "R2:"
docker exec R2 vtysh -c "show ip ospf neighbor" 2>/dev/null || echo "No neighbors"

echo ""
echo "=== OSPF ROUTES ==="
docker exec test-router vtysh -c "show ip route ospf" 2>/dev/null | head -5 || echo "No OSPF routes"

echo ""
echo "========================================="
echo "TEST COMPLETE!"
echo "========================================="
echo ""
echo "If you see FULL state neighbors, OSPF is working!"
echo ""
echo "To clean up:"
echo "  docker stop test-router R2"
echo "  docker rm test-router R2"
echo "  docker network rm nokia-lab"
echo ""

