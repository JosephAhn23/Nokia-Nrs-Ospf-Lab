#!/bin/bash
# Manual Step-by-Step Setup Guide
# Copy and paste each section one at a time

echo "========================================="
echo "MANUAL STEP-BY-STEP OSPF SETUP"
echo "========================================="
echo ""
echo "Copy and paste each section below:"
echo ""

cat << 'EOF'

# ============================================
# STEP 1: Clean and create network
# ============================================
docker stop $(docker ps -aq) 2>/dev/null
docker rm $(docker ps -aq) 2>/dev/null
docker network prune -f
docker network create --subnet=10.30.40.0/24 nokia-lab

# ============================================
# STEP 2: Start two routers
# ============================================
docker run -d --name R1 --hostname R1 \
  --network nokia-lab --ip 10.30.40.1 \
  --privileged \
  frrouting/frr:latest tail -f /dev/null

docker run -d --name R2 --hostname R2 \
  --network nokia-lab --ip 10.30.40.2 \
  --privileged \
  frrouting/frr:latest tail -f /dev/null

sleep 5

# ============================================
# STEP 3: Configure R1
# ============================================
docker exec R1 bash -c "
echo 'zebra=yes' > /etc/frr/daemons
echo 'ospfd=yes' >> /etc/frr/daemons
/usr/lib/frr/frrinit.sh start
sleep 2
vtysh << 'EOF'
configure terminal
interface eth0
ip address 10.30.40.1/24
no shutdown
exit
router ospf
ospf router-id 1.1.1.1
network 10.30.40.0/24 area 0.0.0.0
exit
write memory
EOF
"

# ============================================
# STEP 4: Configure R2
# ============================================
docker exec R2 bash -c "
echo 'zebra=yes' > /etc/frr/daemons
echo 'ospfd=yes' >> /etc/frr/daemons
/usr/lib/frr/frrinit.sh start
sleep 2
vtysh << 'EOF'
configure terminal
interface eth0
ip address 10.30.40.2/24
no shutdown
exit
router ospf
ospf router-id 2.2.2.2
network 10.30.40.0/24 area 0.0.0.0
exit
write memory
EOF
"

# ============================================
# STEP 5: Wait and verify
# ============================================
echo "Waiting 40 seconds for OSPF FULL state..."
sleep 40

echo "=== OSPF NEIGHBORS ==="
docker exec R1 vtysh -c "show ip ospf neighbor"
echo ""
echo "=== OSPF ROUTES ==="
docker exec R1 vtysh -c "show ip route ospf"
echo ""
echo "=== OSPF DATABASE ==="
docker exec R1 vtysh -c "show ip ospf database"

EOF

echo ""
echo "========================================="
echo "End of manual setup guide"
echo "========================================="

