# -*- coding: utf-8 -*-
"""
Route Loop Demonstration
Shows how routing loops can occur and how to troubleshoot
"""
import time
from ospf_network import OSPFNetwork


def create_route_loop_scenario():
    """Create a network topology that can cause routing loops"""
    network = OSPFNetwork()
    
    # Create 4 routers in a square (potential loop)
    router1 = network.add_router("1.1.1.1")
    router2 = network.add_router("2.2.2.2")
    router3 = network.add_router("3.3.3.3")
    router4 = network.add_router("4.4.4.4")
    
    # Connect in square: 1-2-3-4-1
    network.connect_routers("1.1.1.1", "2.2.2.2", "eth0", "eth0", "10.1.12.1", "10.1.12.2", cost=10)
    network.connect_routers("2.2.2.2", "3.3.3.3", "eth1", "eth0", "10.1.23.2", "10.1.23.3", cost=10)
    network.connect_routers("3.3.3.3", "4.4.4.4", "eth1", "eth0", "10.1.34.3", "10.1.34.4", cost=10)
    network.connect_routers("4.4.4.4", "1.1.1.1", "eth1", "eth1", "10.1.41.4", "10.1.41.1", cost=100)  # High cost link
    
    return network


def demonstrate_route_loop():
    """Demonstrate routing loop scenario"""
    print("="*60)
    print("ROUTE LOOP DEMONSTRATION")
    print("="*60)
    print()
    
    network = create_route_loop_scenario()
    
    # Start network
    network.start_all()
    time.sleep(2)
    
    # Exchange LSAs
    print("\nExchanging LSAs...")
    for router_id, router in network.routers.items():
        for neighbor_id in router.neighbors.keys():
            if neighbor_id in network.routers:
                neighbor_router = network.routers[neighbor_id]
                for lsa_router_id, lsa in neighbor_router.lsdb.items():
                    router.receive_lsa(lsa, neighbor_id)
    
    # Calculate SPF
    print("\nCalculating SPF...")
    for router in network.routers.values():
        router.calculate_spf()
    
    # Show routing tables
    print("\n" + "="*60)
    print("ROUTING TABLES (Before link failure)")
    print("="*60)
    network.print_network_status()
    
    # Simulate high-cost link failure
    print("\n" + "="*60)
    print("SIMULATING HIGH-COST LINK FAILURE: 4.4.4.4 <-> 1.1.1.1")
    print("This creates a potential routing loop scenario")
    print("="*60)
    time.sleep(1)
    
    network.simulate_link_failure("4.4.4.4", "1.1.1.1")
    
    # Recalculate
    print("\nRecalculating SPF...")
    time.sleep(1)
    for router in network.routers.values():
        router.calculate_spf()
    
    print("\n" + "="*60)
    print("ROUTING TABLES (After link failure)")
    print("="*60)
    print("Note: OSPF SPF prevents loops by calculating shortest path")
    print("All routers should converge to use path: 1->2->3->4")
    print("="*60)
    network.print_network_status()
    
    # Troubleshooting tips
    print("\n" + "="*60)
    print("TROUBLESHOOTING ROUTING LOOPS")
    print("="*60)
    print("1. Check OSPF adjacencies: Are all neighbors in FULL state?")
    print("2. Verify LSDB: Do all routers have same LSDB?")
    print("3. Check SPF calculation: Are routes using shortest path?")
    print("4. Verify link costs: Are costs consistent?")
    print("5. Check for duplicate router IDs")
    print("="*60)
    
    network.stop_all()


if __name__ == "__main__":
    demonstrate_route_loop()

