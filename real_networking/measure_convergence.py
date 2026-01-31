#!/usr/bin/env python3
"""
Real OSPF Convergence Measurement Tool
Measures actual convergence time after link failure

This script:
1. Monitors OSPF neighbor state
2. Simulates link failure
3. Measures time until reconvergence
4. Shows actual routing table changes
"""

import subprocess
import time
import sys
import json
from datetime import datetime

def run_command(cmd, check=True):
    """Run shell command and return output"""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, check=check
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {cmd}")
        print(f"Error: {e.stderr}")
        return None

def check_docker_setup():
    """Check if Docker FRR setup is running"""
    result = run_command("docker ps --format '{{.Names}}' | grep frr-router", check=False)
    return bool(result and "frr-router" in result)

def get_ospf_neighbors(router_name):
    """Get OSPF neighbor status from FRR router"""
    cmd = f"docker exec {router_name} vtysh -c 'show ip ospf neighbor json'"
    output = run_command(cmd, check=False)
    if output:
        try:
            return json.loads(output)
        except:
            pass
    return None

def get_routing_table(router_name):
    """Get routing table from FRR router"""
    cmd = f"docker exec {router_name} vtysh -c 'show ip route json'"
    output = run_command(cmd, check=False)
    if output:
        try:
            return json.loads(output)
        except:
            pass
    return None

def simulate_link_failure(router_name, interface):
    """Simulate link failure by bringing interface down"""
    print(f"\n[CONVERGENCE TEST] Bringing down {interface} on {router_name}...")
    cmd = f"docker exec {router_name} ip link set {interface} down"
    run_command(cmd)
    print(f"✓ Interface {interface} is now DOWN")

def restore_link(router_name, interface):
    """Restore link by bringing interface up"""
    print(f"\n[RESTORE] Bringing up {interface} on {router_name}...")
    cmd = f"docker exec {router_name} ip link set {interface} up"
    run_command(cmd)
    print(f"✓ Interface {interface} is now UP")

def measure_convergence(router_name, target_prefix, max_wait=30):
    """
    Measure convergence time after link failure
    
    Returns:
        convergence_time: Time in seconds until route is removed/updated
        success: Whether convergence was detected
    """
    print(f"\n[MEASUREMENT] Monitoring route to {target_prefix}...")
    
    start_time = time.time()
    initial_routes = get_routing_table(router_name)
    
    # Check if route exists initially
    route_exists = False
    if initial_routes:
        for route_key, route_data in initial_routes.items():
            if isinstance(route_data, dict) and target_prefix in str(route_data):
                route_exists = True
                print(f"✓ Route to {target_prefix} exists initially")
                break
    
    if not route_exists:
        print(f"⚠ Route to {target_prefix} not found initially")
        print("This might be expected if testing link failure")
    
    # Monitor for convergence
    check_interval = 0.5  # Check every 500ms
    elapsed = 0
    
    while elapsed < max_wait:
        time.sleep(check_interval)
        elapsed = time.time() - start_time
        
        current_routes = get_routing_table(router_name)
        route_still_exists = False
        
        if current_routes:
            for route_key, route_data in current_routes.items():
                if isinstance(route_data, dict) and target_prefix in str(route_data):
                    route_still_exists = True
                    break
        
        # If route disappeared or changed, convergence occurred
        if route_exists and not route_still_exists:
            convergence_time = time.time() - start_time
            print(f"\n✓ CONVERGENCE DETECTED!")
            print(f"  Time: {convergence_time:.3f} seconds")
            return convergence_time, True
        
        # If route appeared (after restore), convergence occurred
        if not route_exists and route_still_exists:
            convergence_time = time.time() - start_time
            print(f"\n✓ CONVERGENCE DETECTED (route restored)!")
            print(f"  Time: {convergence_time:.3f} seconds")
            return convergence_time, True
        
        if elapsed % 2 < check_interval:  # Print every 2 seconds
            print(f"  [{elapsed:.1f}s] Monitoring...", end='\r')
    
    print(f"\n⚠ No convergence detected within {max_wait} seconds")
    return max_wait, False

def main():
    print("=" * 60)
    print("OSPF Convergence Measurement Tool")
    print("=" * 60)
    print()
    
    if not check_docker_setup():
        print("ERROR: Docker FRR setup not detected")
        print("Run: ./setup_frr_docker.sh first")
        sys.exit(1)
    
    print("✓ Docker FRR setup detected")
    print()
    
    # Show initial state
    print("[INITIAL STATE]")
    print("-" * 60)
    
    for router in ["frr-router1", "frr-router2", "frr-router3"]:
        neighbors = get_ospf_neighbors(router)
        if neighbors:
            print(f"\n{router} OSPF Neighbors:")
            for neighbor_id, neighbor_data in neighbors.items():
                if isinstance(neighbor_data, dict):
                    state = neighbor_data.get('state', 'UNKNOWN')
                    print(f"  Neighbor: {neighbor_id}, State: {state}")
    
    print()
    print("-" * 60)
    
    # Test: Simulate link failure between router2 and router3
    print("\n[TEST 1: Link Failure]")
    print("=" * 60)
    print("Simulating failure of link between router2 and router3")
    
    # Bring down interface on router2
    simulate_link_failure("frr-router2", "eth1")
    
    # Measure convergence on router1 (should lose route to router3)
    convergence_time, success = measure_convergence(
        "frr-router1",
        "10.1.2.0/24",  # Network behind router3
        max_wait=30
    )
    
    if success:
        print(f"\n✓ Convergence time: {convergence_time:.3f} seconds")
    else:
        print(f"\n⚠ Convergence not detected within timeout")
    
    # Wait a bit
    time.sleep(5)
    
    # Restore link
    print("\n[TEST 2: Link Restoration]")
    print("=" * 60)
    restore_link("frr-router2", "eth1")
    
    # Measure convergence after restore
    convergence_time, success = measure_convergence(
        "frr-router1",
        "10.1.2.0/24",
        max_wait=30
    )
    
    if success:
        print(f"\n✓ Restoration convergence time: {convergence_time:.3f} seconds")
    
    # Final state
    print("\n[FINAL STATE]")
    print("-" * 60)
    for router in ["frr-router1", "frr-router2", "frr-router3"]:
        neighbors = get_ospf_neighbors(router)
        if neighbors:
            print(f"\n{router} OSPF Neighbors:")
            for neighbor_id, neighbor_data in neighbors.items():
                if isinstance(neighbor_data, dict):
                    state = neighbor_data.get('state', 'UNKNOWN')
                    print(f"  Neighbor: {neighbor_id}, State: {state}")
    
    print()
    print("=" * 60)
    print("Measurement Complete")
    print("=" * 60)

if __name__ == "__main__":
    main()

