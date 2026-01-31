#!/bin/bash
# Debug FRR Setup - Check what's running and diagnose issues

echo "=========================================="
echo "FRR Debug Information"
echo "=========================================="
echo ""

# Check what's running in each container
for router in frr-router1 frr-router2 frr-router3 frr-router4; do
  if docker ps --format "{{.Names}}" | grep -q "^${router}$"; then
    echo "=== $router ==="
    echo "Processes:"
    docker exec $router ps aux | grep -E "(zebra|ospf|bgp|frr|watch)" | head -5 || echo "  No FRR processes found"
    echo ""
    echo "FRR Status:"
    docker exec $router /usr/lib/frr/frrinit.sh status 2>/dev/null || echo "  FRR init script not available"
    echo ""
    echo "Daemons config:"
    docker exec $router cat /etc/frr/daemons | grep -E "(zebra|ospfd)" || echo "  Cannot read daemons file"
    echo ""
  else
    echo "=== $router ==="
    echo "  Container not running"
    echo ""
  fi
done

echo "=== Network Connectivity ==="
echo "Router1 interfaces:"
docker exec frr-router1 ip addr show 2>/dev/null | grep -E "(eth|inet )" | head -10 || echo "  Cannot check interfaces"
echo ""

echo "=== OSPF Status (if running) ==="
docker exec frr-router1 vtysh -c "show ip ospf neighbor" 2>/dev/null || echo "  OSPF not running or not configured"
echo ""

