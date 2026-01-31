#!/bin/bash
# Capture real OSPF packets using tcpdump
# OSPF uses IP protocol 89

set -e

if [ "$EUID" -ne 0 ]; then 
    echo "ERROR: This script must be run as root (sudo) for packet capture"
    exit 1
fi

OUTPUT_DIR="./packet_captures"
mkdir -p "$OUTPUT_DIR"

echo "=========================================="
echo "Capturing OSPF Packets"
echo "=========================================="
echo ""
echo "OSPF uses IP protocol 89"
echo "Capturing on all interfaces..."
echo ""
echo "Press Ctrl+C to stop capture"
echo ""

# Capture OSPF packets (IP protocol 89)
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT_FILE="$OUTPUT_DIR/ospf_capture_${TIMESTAMP}.pcap"

echo "Capturing to: $OUTPUT_FILE"
echo ""

# If using Docker FRR setup, capture on docker network
if docker ps | grep -q frr-router; then
    echo "Detected Docker FRR setup, capturing on docker network..."
    tcpdump -i any -w "$OUTPUT_FILE" 'ip proto 89' -v
else
    # If using network namespaces, capture on host
    echo "Capturing on host interfaces..."
    tcpdump -i any -w "$OUTPUT_FILE" 'ip proto 89' -v
fi

echo ""
echo "Capture saved to: $OUTPUT_FILE"
echo ""
echo "To analyze with Wireshark:"
echo "  wireshark $OUTPUT_FILE"
echo ""
echo "To analyze with tcpdump:"
echo "  tcpdump -r $OUTPUT_FILE -v"
echo ""

