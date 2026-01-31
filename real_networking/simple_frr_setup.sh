#!/bin/bash

echo "=========================================="
echo "Simple FRR Setup for Windows"
echo "=========================================="

# Clean up
docker-compose down 2>/dev/null
rm -rf configs
mkdir -p configs/router1 configs/router2 configs/router3 configs/router4

# Create Docker Compose file
cat > docker-compose.yml << 'EOF'
version: '3.8'
services:
  router1:
    image: frrouting/frr:latest
    container_name: frr-router1
    hostname: router1
    privileged: true
    stdin_open: true
    tty: true
    networks:
      net1:
        ipv4_address: 10.0.12.1
      net2:
        ipv4_address: 10.0.13.1
      net3:
        ipv4_address: 10.0.14.1

  router2:
    image: frrouting/frr:latest
    container_name: frr-router2
    hostname: router2
    privileged: true
    stdin_open: true
    tty: true
    networks:
      net1:
        ipv4_address: 10.0.12.2

  router3:
    image: frrouting/frr:latest
    container_name: frr-router3
    hostname: router3
    privileged: true
    stdin_open: true
    tty: true
    networks:
      net2:
        ipv4_address: 10.0.13.3

  router4:
    image: frrouting/frr:latest
    container_name: frr-router4
    hostname: router4
    privileged: true
    stdin_open: true
    tty: true
    networks:
      net3:
        ipv4_address: 10.0.14.4

networks:
  net1:
    driver: bridge
    ipam:
      config:
        - subnet: 10.0.12.0/24
  net2:
    driver: bridge
    ipam:
      config:
        - subnet: 10.0.13.0/24
  net3:
    driver: bridge
    ipam:
      config:
        - subnet: 10.0.14.0/24
EOF

echo "[1/4] Starting Docker containers..."
docker-compose up -d

echo "[2/4] Waiting for containers to start..."
sleep 10

echo "[3/4] Configuring FRR daemons and interfaces..."
# Configure each router
for i in 1 2 3 4; do
  echo "  Configuring router$i..."
  
  # Enable zebra and ospfd
  docker exec frr-router$i bash -c "echo 'zebra=yes' > /etc/frr/daemons"
  docker exec frr-router$i bash -c "echo 'ospfd=yes' >> /etc/frr/daemons"
  
  # Start FRR
  docker exec frr-router$i /usr/lib/frr/frrinit.sh start 2>/dev/null || true
  
  # Bring up interfaces
  case $i in
    1)
      # Router1 has 3 interfaces
      docker exec frr-router1 vtysh -c "conf t" -c "interface eth0" -c "ip address 10.0.12.1/24" -c "no shutdown" -c "exit" -c "exit" 2>/dev/null || true
      docker exec frr-router1 vtysh -c "conf t" -c "interface eth1" -c "ip address 10.0.13.1/24" -c "no shutdown" -c "exit" -c "exit" 2>/dev/null || true
      docker exec frr-router1 vtysh -c "conf t" -c "interface eth2" -c "ip address 10.0.14.1/24" -c "no shutdown" -c "exit" -c "exit" 2>/dev/null || true
      ;;
    2)
      docker exec frr-router2 vtysh -c "conf t" -c "interface eth0" -c "ip address 10.0.12.2/24" -c "no shutdown" -c "exit" -c "exit" 2>/dev/null || true
      ;;
    3)
      docker exec frr-router3 vtysh -c "conf t" -c "interface eth0" -c "ip address 10.0.13.3/24" -c "no shutdown" -c "exit" -c "exit" 2>/dev/null || true
      ;;
    4)
      docker exec frr-router4 vtysh -c "conf t" -c "interface eth0" -c "ip address 10.0.14.4/24" -c "no shutdown" -c "exit" -c "exit" 2>/dev/null || true
      # Set MTU mismatch
      docker exec frr-router4 ip link set eth0 mtu 1400 2>/dev/null || true
      ;;
  esac
  
  sleep 2
done

echo "[4/4] Configuring OSPF..."
# Configure OSPF
echo "  Configuring router1..."
docker exec frr-router1 vtysh << 'EOF' 2>/dev/null || true
configure terminal
router ospf
ospf router-id 1.1.1.1
network 10.0.12.0/24 area 0.0.0.0
network 10.0.13.0/24 area 0.0.0.0
network 10.0.14.0/24 area 0.0.0.0
exit
exit
EOF

echo "  Configuring router2..."
docker exec frr-router2 vtysh << 'EOF' 2>/dev/null || true
configure terminal
router ospf
ospf router-id 2.2.2.2
network 10.0.12.0/24 area 0.0.0.0
exit
exit
EOF

echo "  Configuring router3..."
docker exec frr-router3 vtysh << 'EOF' 2>/dev/null || true
configure terminal
router ospf
ospf router-id 3.3.3.3
network 10.0.13.0/24 area 0.0.0.0
exit
exit
EOF

echo "  Configuring router4..."
docker exec frr-router4 vtysh << 'EOF' 2>/dev/null || true
configure terminal
router ospf
ospf router-id 4.4.4.4
network 10.0.14.0/24 area 0.0.0.0
exit
exit
EOF

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Waiting 20 seconds for OSPF adjacencies..."
sleep 20

echo ""
echo "=== OSPF Neighbors on Router1 ==="
docker exec frr-router1 vtysh -c "show ip ospf neighbor" 2>/dev/null || echo "OSPF not running yet"

echo ""
echo "=== OSPF Database on Router1 ==="
docker exec frr-router1 vtysh -c "show ip ospf database" 2>/dev/null | head -15 || echo "Database not available"

echo ""
echo "=== Routing Table on Router1 ==="
docker exec frr-router1 vtysh -c "show ip route ospf" 2>/dev/null | head -10 || echo "No OSPF routes yet"

echo ""
echo "=========================================="
echo "MTU Mismatch Demo: Router4 has MTU 1400"
echo "Check for stuck EXSTART state on Router1:"
echo "  docker exec frr-router1 vtysh -c 'show ip ospf neighbor'"
echo "=========================================="

