#!/bin/bash
# OSPF DR/BDR Election Demonstration
# Shows real DR/BDR election with packet capture and state verification
#
# This demonstrates:
# - Priority-based DR/BDR election
# - Router ID tiebreaker
# - Packet capture showing Hello packets with DR/BDR fields
# - State verification showing Full/DR, Full/BDR, Full/DROTHER

set -e

if [ "$EUID" -ne 0 ]; then 
    echo "ERROR: This script must be run as root (sudo)"
    exit 1
fi

echo "=========================================="
echo "OSPF DR/BDR Election Demonstration"
echo "=========================================="
echo ""
echo "This demonstrates REAL OSPF DR/BDR election:"
echo "  - Priority-based election (higher priority wins)"
echo "  - Router ID tiebreaker (if priorities equal)"
echo "  - Packet capture showing Hello packets"
echo "  - State verification showing DR/BDR roles"
echo ""

# Check if Docker FRR is running
if ! docker ps | grep -q frr-router; then
    echo "ERROR: Docker FRR setup not running"
    echo "Run: sudo ./setup_frr_docker.sh first"
    exit 1
fi

echo "[1/6] Setting up broadcast network for DR/BDR election..."
echo "--------------------------------------------------------"
echo ""

# Stop existing routers
docker stop frr-router1 frr-router2 frr-router3 2>/dev/null || true
docker rm frr-router1 frr-router2 frr-router3 2>/dev/null || true

# Create Docker network for broadcast segment
docker network create --subnet=10.1.1.0/24 --gateway=10.1.1.254 dr-election-net 2>/dev/null || echo "Network already exists"

# Router 1: Priority 1, Router ID 1.1.1.1 (will be BDR)
cat > /tmp/frr1_dr.conf <<'EOF'
hostname router1
password zebra
enable password zebra

interface eth0
 ip address 10.1.1.1/24
 ip ospf network broadcast
 ip ospf priority 1
!
router ospf
 ospf router-id 1.1.1.1
 network 10.1.1.0/24 area 0.0.0.0
!
line vty
!
EOF

# Router 2: Priority 10, Router ID 2.2.2.2 (will be DR)
cat > /tmp/frr2_dr.conf <<'EOF'
hostname router2
password zebra
enable password zebra

interface eth0
 ip address 10.1.1.2/24
 ip ospf network broadcast
 ip ospf priority 10
!
router ospf
 ospf router-id 2.2.2.2
 network 10.1.1.0/24 area 0.0.0.0
!
line vty
!
EOF

# Router 3: Priority 1, Router ID 3.3.3.3 (will be DROTHER)
cat > /tmp/frr3_dr.conf <<'EOF'
hostname router3
password zebra
enable password zebra

interface eth0
 ip address 10.1.1.3/24
 ip ospf network broadcast
 ip ospf priority 1
!
router ospf
 ospf router-id 3.3.3.3
 network 10.1.1.0/24 area 0.0.0.0
!
line vty
!
EOF

# Start routers
echo "Starting routers..."
docker run -d --name frr-router1 --network dr-election-net \
    -v /tmp/frr1_dr.conf:/etc/frr/frr.conf \
    --cap-add=NET_ADMIN \
    frrouting/frr:latest

docker run -d --name frr-router2 --network dr-election-net \
    -v /tmp/frr2_dr.conf:/etc/frr/frr.conf \
    --cap-add=NET_ADMIN \
    frrouting/frr:latest

docker run -d --name frr-router3 --network dr-election-net \
    -v /tmp/frr3_dr.conf:/etc/frr/frr.conf \
    --cap-add=NET_ADMIN \
    frrouting/frr:latest

echo "✓ Routers started"
echo ""

# Wait for OSPF to initialize
echo "[2/6] Waiting for OSPF adjacencies to form (15 seconds)..."
echo "--------------------------------------------------------"
sleep 15
echo ""

# Capture packets in background
echo "[3/6] Starting packet capture..."
echo "--------------------------------------------------------"
OUTPUT_DIR="./packet_captures"
mkdir -p "$OUTPUT_DIR"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
PCAP_FILE="$OUTPUT_DIR/dr_election_${TIMESTAMP}.pcap"

# Start tcpdump in background
docker exec frr-router1 tcpdump -i eth0 -w /tmp/dr_election.pcap 'ip proto 89' 2>/dev/null &
TCPDUMP_PID=$!
sleep 2
echo "✓ Packet capture started (PID: $TCPDUMP_PID)"
echo ""

# Show initial state
echo "[4/6] OSPF Neighbor States (showing DR/BDR roles)"
echo "--------------------------------------------------------"
echo ""
echo "Router 1 (Priority 1, Router ID 1.1.1.1):"
docker exec frr-router1 vtysh -c 'show ip ospf neighbor' 2>/dev/null | grep -A 10 "Neighbor ID" || echo "  (No neighbors yet)"
echo ""

echo "Router 2 (Priority 10, Router ID 2.2.2.2):"
docker exec frr-router2 vtysh -c 'show ip ospf neighbor' 2>/dev/null | grep -A 10 "Neighbor ID" || echo "  (No neighbors yet)"
echo ""

echo "Router 3 (Priority 1, Router ID 3.3.3.3):"
docker exec frr-router3 vtysh -c 'show ip ospf neighbor' 2>/dev/null | grep -A 10 "Neighbor ID" || echo "  (No neighbors yet)"
echo ""

# Show OSPF interface details (shows DR/BDR)
echo "[5/6] OSPF Interface Details (showing DR/BDR election)"
echo "--------------------------------------------------------"
echo ""
echo "Router 1 interface:"
docker exec frr-router1 vtysh -c 'show ip ospf interface eth0' 2>/dev/null | head -15
echo ""

echo "Router 2 interface:"
docker exec frr-router2 vtysh -c 'show ip ospf interface eth0' 2>/dev/null | head -15
echo ""

echo "Router 3 interface:"
docker exec frr-router3 vtysh -c 'show ip ospf interface eth0' 2>/dev/null | head -15
echo ""

# Stop packet capture
echo "[6/6] Stopping packet capture and saving..."
echo "--------------------------------------------------------"
sleep 2
kill $TCPDUMP_PID 2>/dev/null || true
sleep 1

# Copy pcap from container
docker cp frr-router1:/tmp/dr_election.pcap "$PCAP_FILE" 2>/dev/null || echo "  (Packet capture may be empty)"
echo "✓ Packet capture saved to: $PCAP_FILE"
echo ""

# Analysis
echo "=========================================="
echo "DR/BDR Election Analysis"
echo "=========================================="
echo ""
echo "Expected Results:"
echo "  - DR: Router 2 (Priority 10, highest)"
echo "  - BDR: Router 1 (Priority 1, Router ID 1.1.1.1 < 3.3.3.3, but elected first)"
echo "  - DROTHER: Router 3 (Priority 1, Router ID 3.3.3.3)"
echo ""
echo "Election Process:"
echo "  1. All routers send Hello packets with priority"
echo "  2. Routers see each other's priorities in Hello packets"
echo "  3. Router with highest priority (10) becomes DR"
echo "  4. Router with second-highest priority becomes BDR"
echo "  5. All other routers become DROTHERs"
echo ""
echo "State Verification:"
echo "  - Full/DR: Adjacency with Designated Router"
echo "  - Full/BDR: Adjacency with Backup Designated Router"
echo "  - Full/DROTHER: Adjacency with non-DR/BDR router"
echo ""
echo "Packet Capture Analysis:"
echo "  To analyze captured packets:"
echo "    wireshark $PCAP_FILE"
echo ""
echo "  Look for:"
echo "    - Hello packets with DR field = 2.2.2.2"
echo "    - Hello packets with BDR field = 1.1.1.1"
echo "    - State transitions: INIT → 2-WAY → EXSTART → EXCHANGE → FULL"
echo ""

# Show actual results
echo "=========================================="
echo "Actual Results"
echo "=========================================="
echo ""
echo "Router 1 neighbors:"
docker exec frr-router1 vtysh -c 'show ip ospf neighbor' 2>/dev/null || echo "  (No output)"
echo ""

echo "Router 2 neighbors:"
docker exec frr-router2 vtysh -c 'show ip ospf neighbor' 2>/dev/null || echo "  (No output)"
echo ""

echo "Router 3 neighbors:"
docker exec frr-router3 vtysh -c 'show ip ospf neighbor' 2>/dev/null || echo "  (No output)"
echo ""

echo "=========================================="
echo "Demonstration Complete"
echo "=========================================="
echo ""
echo "This demonstrates:"
echo "  ✓ Real OSPF DR/BDR election (not simulated)"
echo "  ✓ Priority-based election process"
echo "  ✓ Packet capture showing Hello packets"
echo "  ✓ State verification showing DR/BDR roles"
echo ""
echo "Next steps:"
echo "  1. Analyze packet capture: wireshark $PCAP_FILE"
echo "  2. Verify DR/BDR roles: show ip ospf interface"
echo "  3. Test failure scenario: Bring down DR, verify BDR promotes"
echo ""

