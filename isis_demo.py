# -*- coding: utf-8 -*-
"""
ISIS Demo - Working demonstration
Shows adjacency formation, LSP exchange, SPF calculation
"""
import time
from isis_network import ISISNetwork
from isis_router import ISISLevel


def main():
    print("="*60)
    print("ISIS Network Demo - Working Implementation")
    print("="*60)
    print()
    
    # Create network
    network = ISISNetwork()
    
    # Add 3 routers
    print("Creating 3 ISIS routers...")
    router1 = network.add_router("0000.0000.0001", ISISLevel.LEVEL_1)
    router2 = network.add_router("0000.0000.0002", ISISLevel.LEVEL_1)
    router3 = network.add_router("0000.0000.0003", ISISLevel.LEVEL_1)
    
    # Connect routers in triangle topology
    print("\nConnecting routers...")
    network.connect_routers("0000.0000.0001", "0000.0000.0002", "eth0", "eth0", "10.1.12.1", "10.1.12.2")
    network.connect_routers("0000.0000.0002", "0000.0000.0003", "eth1", "eth0", "10.1.23.2", "10.1.23.3")
    network.connect_routers("0000.0000.0001", "0000.0000.0003", "eth1", "eth1", "10.1.13.1", "10.1.13.3")
    
    # Start all routers
    print("\nStarting ISIS routers...")
    network.start_all()
    
    # Wait for adjacencies
    print("\nWaiting for adjacencies to form...")
    time.sleep(2)
    
    # Exchange LSPs
    print("\nExchanging LSPs...")
    for router_id, router in network.routers.items():
        for neighbor_id in router.neighbors.keys():
            if neighbor_id in network.routers:
                neighbor_router = network.routers[neighbor_id]
                # Exchange LSPs
                for lsp_router_id, lsp in neighbor_router.lsdb.items():
                    router.receive_lsp(lsp, neighbor_id)
    
    # Calculate SPF
    print("\nCalculating SPF...")
    for router in network.routers.values():
        router.calculate_spf()
    
    # Show status
    print("\n" + "="*60)
    print("ISIS NETWORK STATUS")
    print("="*60)
    network.print_network_status()
    
    # Demo: Link failure
    print("\n" + "="*60)
    print("DEMO: Simulating link failure between 0000.0000.0001 and 0000.0000.0002")
    print("="*60)
    time.sleep(1)
    network.simulate_link_failure("0000.0000.0001", "0000.0000.0002")
    
    # Recalculate SPF
    print("\nRecalculating SPF after link failure...")
    time.sleep(1)
    for router in network.routers.values():
        router.calculate_spf()
    
    print("\n" + "="*60)
    print("ISIS NETWORK STATUS AFTER LINK FAILURE")
    print("="*60)
    network.print_network_status()
    
    # Stop
    network.stop_all()
    print("\nISIS Demo complete!")


if __name__ == "__main__":
    main()

