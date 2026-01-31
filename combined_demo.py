# -*- coding: utf-8 -*-
"""
Combined OSPF/ISIS Demo
Shows both protocols working together
"""
import time
from ospf_network import OSPFNetwork
from isis_network import ISISNetwork
from isis_router import ISISLevel


def main():
    print("="*60)
    print("OSPF/ISIS Combined Demo")
    print("="*60)
    print()
    
    # OSPF Network
    print("="*60)
    print("PART 1: OSPF Network")
    print("="*60)
    ospf_net = OSPFNetwork()
    
    router1 = ospf_net.add_router("1.1.1.1")
    router2 = ospf_net.add_router("2.2.2.2")
    router3 = ospf_net.add_router("3.3.3.3")
    
    ospf_net.connect_routers("1.1.1.1", "2.2.2.2", "eth0", "eth0", "10.1.12.1", "10.1.12.2")
    ospf_net.connect_routers("2.2.2.2", "3.3.3.3", "eth1", "eth0", "10.1.23.2", "10.1.23.3")
    
    ospf_net.start_all()
    time.sleep(1)
    
    # Exchange LSAs
    for router_id, router in ospf_net.routers.items():
        for neighbor_id in router.neighbors.keys():
            if neighbor_id in ospf_net.routers:
                neighbor_router = ospf_net.routers[neighbor_id]
                for lsa_router_id, lsa in neighbor_router.lsdb.items():
                    router.receive_lsa(lsa, neighbor_id)
    
    for router in ospf_net.routers.values():
        router.calculate_spf()
    
    print("\nOSPF Network Status:")
    ospf_net.print_network_status()
    
    ospf_net.stop_all()
    
    # ISIS Network
    print("\n" + "="*60)
    print("PART 2: ISIS Network")
    print("="*60)
    isis_net = ISISNetwork()
    
    isis_r1 = isis_net.add_router("0000.0000.0001", ISISLevel.LEVEL_1)
    isis_r2 = isis_net.add_router("0000.0000.0002", ISISLevel.LEVEL_1)
    isis_r3 = isis_net.add_router("0000.0000.0003", ISISLevel.LEVEL_1)
    
    isis_net.connect_routers("0000.0000.0001", "0000.0000.0002", "eth0", "eth0", "10.2.12.1", "10.2.12.2")
    isis_net.connect_routers("0000.0000.0002", "0000.0000.0003", "eth1", "eth0", "10.2.23.2", "10.2.23.3")
    
    isis_net.start_all()
    time.sleep(1)
    
    # Exchange LSPs
    for router_id, router in isis_net.routers.items():
        for neighbor_id in router.neighbors.keys():
            if neighbor_id in isis_net.routers:
                neighbor_router = isis_net.routers[neighbor_id]
                for lsp_router_id, lsp in neighbor_router.lsdb.items():
                    router.receive_lsp(lsp, neighbor_id)
    
    for router in isis_net.routers.values():
        router.calculate_spf()
    
    print("\nISIS Network Status:")
    isis_net.print_network_status()
    
    isis_net.stop_all()
    
    print("\n" + "="*60)
    print("DEMO COMPLETE")
    print("="*60)
    print("[OK] OSPF: Adjacency formation, LSA exchange, SPF calculation")
    print("[OK] ISIS: Adjacency formation, LSP exchange, SPF calculation")
    print("="*60)


if __name__ == "__main__":
    main()

