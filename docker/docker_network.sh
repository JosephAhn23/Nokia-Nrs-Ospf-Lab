#!/bin/bash
# Docker Network Setup Script
# Creates network namespaces and connects containers

set -e

echo "Setting up Docker networking for OSPF routers..."

# Create bridge network
docker network create --driver bridge --subnet=172.20.0.0/24 ospf_net 2>/dev/null || true

# Start containers
echo "Starting containers..."
docker-compose up -d

# Wait for containers to be ready
sleep 5

# Get container IPs
ROUTER1_IP=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' router1)
ROUTER2_IP=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' router2)
ROUTER3_IP=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' router3)

echo "Router IPs:"
echo "  router1: $ROUTER1_IP"
echo "  router2: $ROUTER2_IP"
echo "  router3: $ROUTER3_IP"

# Enable IP forwarding in containers
echo "Enabling IP forwarding..."
docker exec router1 sh -c "echo 1 > /proc/sys/net/ipv4/ip_forward" || true
docker exec router2 sh -c "echo 1 > /proc/sys/net/ipv4/ip_forward" || true
docker exec router3 sh -c "echo 1 > /proc/sys/net/ipv4/ip_forward" || true

echo "Network setup complete!"
echo ""
echo "Test connectivity:"
echo "  docker exec router1 ping -c 3 $ROUTER2_IP"
echo "  docker exec router2 ping -c 3 $ROUTER3_IP"

