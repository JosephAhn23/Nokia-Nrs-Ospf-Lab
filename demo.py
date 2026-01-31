# -*- coding: utf-8 -*-
"""
OSPF Demo - Working demonstration
Shows adjacency formation, LSA exchange, SPF calculation
"""
import time
from ospf_network import OSPFNetwork


def main():
    print("="*60)
    print("OSPF Network Demo - Working Implementation")
    print("="*60)
    print()
    
    # Create network
    network = OSPFNetwork()
    
    # Add 3 routers
    print("Creating 3 routers...")
    router1 = network.add_router("1.1.1.1", "0.0.0.0")
    router2 = network.add_router("2.2.2.2", "0.0.0.0")
    router3 = network.add_router("3.3.3.3", "0.0.0.0")
    
    # Connect routers in triangle topology
    print("\nConnecting routers...")
    network.connect_routers("1.1.1.1", "2.2.2.2", "eth0", "eth0", "10.1.12.1", "10.1.12.2")
    network.connect_routers("2.2.2.2", "3.3.3.3", "eth1", "eth0", "10.1.23.2", "10.1.23.3")
    network.connect_routers("1.1.1.1", "3.3.3.3", "eth1", "eth1", "10.1.13.1", "10.1.13.3")
    
    # Start all routers
    print("\nStarting OSPF routers...")
    network.start_all()
    
    # Wait for adjacencies
    print("\nWaiting for adjacencies to form...")
    time.sleep(2)
    
    # Exchange LSAs
    print("\nExchanging LSAs...")
    for router_id, router in network.routers.items():
        for neighbor_id in router.neighbors.keys():
            if neighbor_id in network.routers:
                neighbor_router = network.routers[neighbor_id]
                # Exchange LSAs
                for lsa_router_id, lsa in neighbor_router.lsdb.items():
                    router.receive_lsa(lsa, neighbor_id)
    
    # Calculate SPF
    print("\nCalculating SPF...")
    for router in network.routers.values():
        router.calculate_spf()
    
    # Show status
    print("\n" + "="*60)
    print("NETWORK STATUS")
    print("="*60)
    network.print_network_status()
    
    # Demo: Link failure
    print("\n" + "="*60)
    print("DEMO: Simulating link failure between 1.1.1.1 and 2.2.2.2")
    print("="*60)
    time.sleep(1)
    network.simulate_link_failure("1.1.1.1", "2.2.2.2")
    
    # Recalculate SPF
    print("\nRecalculating SPF after link failure...")
    time.sleep(1)
    for router in network.routers.values():
        router.calculate_spf()
    
    print("\n" + "="*60)
    print("NETWORK STATUS AFTER LINK FAILURE")
    print("="*60)
    network.print_network_status()
    
    # Stop
    network.stop_all()
    print("\nDemo complete!")


if __name__ == "__main__":
    main()

