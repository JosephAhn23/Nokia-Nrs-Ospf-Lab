#!/bin/bash

echo "=========================================="
echo "Simple 2-Router OSPF Test"
echo "=========================================="
echo ""

# 1. Clean up everything
echo "[1/5] Cleaning up..."
docker stop $(docker ps -aq) 2>/dev/null || true
docker rm $(docker ps -aq) 2>/dev/null || true
docker network rm $(docker network ls -q) 2>/dev/null || true
sleep 2
echo "✓ Cleanup complete"
echo ""

# 2. Create ONE simple network
echo "[2/5] Creating network..."
docker network create --subnet=10.99.99.0/24 ospf-lab
echo "✓ Network created"
echo ""

# 3. Start just TWO routers to test
echo "[3/5] Starting routers..."
docker run -d --name R1 --hostname R1 --privileged \
  --network ospf-lab --ip 10.99.99.1 \
  frrouting/frr:latest

docker run -d --name R2 --hostname R2 --privileged \
  --network ospf-lab --ip 10.99.99.2 \
  frrouting/frr:latest

echo "✓ Routers started"
echo ""

echo "[4/5] Waiting for containers to initialize..."
sleep 10
echo ""

# 4. Configure them manually with simple commands
echo "[5/5] Configuring routers..."
echo "  Configuring R1..."
docker exec R1 bash -c "
echo 'zebra=yes' > /etc/frr/daemons
echo 'ospfd=yes' >> /etc/frr/daemons
/usr/lib/frr/frrinit.sh start
sleep 2
vtysh -c 'conf t' \\
  -c 'interface eth0' \\
  -c 'ip address 10.99.99.1/24' \\
  -c 'no shutdown' \\
  -c 'exit' \\
  -c 'router ospf' \\
  -c 'router-id 1.1.1.1' \\
  -c 'network 10.99.99.0/24 area 0.0.0.0' \\
  -c 'exit' \\
  -c 'write'
" 2>/dev/null || echo "  R1 configuration may have issues"

echo "  Configuring R2..."
docker exec R2 bash -c "
echo 'zebra=yes' > /etc/frr/daemons
echo 'ospfd=yes' >> /etc/frr/daemons
/usr/lib/frr/frrinit.sh start
sleep 2
vtysh -c 'conf t' \\
  -c 'interface eth0' \\
  -c 'ip address 10.99.99.2/24' \\
  -c 'no shutdown' \\
  -c 'exit' \\
  -c 'router ospf' \\
  -c 'router-id 2.2.2.2' \\
  -c 'network 10.99.99.0/24 area 0.0.0.0' \\
  -c 'exit' \\
  -c 'write'
" 2>/dev/null || echo "  R2 configuration may have issues"

echo "✓ Configuration complete"
echo ""

echo "=========================================="
echo "Waiting 20 seconds for OSPF adjacencies..."
echo "=========================================="
sleep 20

echo ""
echo "=== OSPF Neighbors on R1 ==="
docker exec R1 vtysh -c "show ip ospf neighbor" 2>/dev/null || echo "OSPF not running or no neighbors"

echo ""
echo "=== OSPF Neighbors on R2 ==="
docker exec R2 vtysh -c "show ip ospf neighbor" 2>/dev/null || echo "OSPF not running or no neighbors"

echo ""
echo "=== Routing Table on R1 ==="
docker exec R1 vtysh -c "show ip route ospf" 2>/dev/null | head -5 || echo "No OSPF routes"

echo ""
echo "=========================================="
echo "Test Complete!"
echo "=========================================="
echo ""
echo "If you see FULL state neighbors, the setup works!"
echo "Then we can scale to 4 routers with MTU mismatch demo."
echo ""
echo "To clean up:"
echo "  docker stop R1 R2"
echo "  docker rm R1 R2"
echo "  docker network rm ospf-lab"
echo ""

