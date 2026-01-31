# -*- coding: utf-8 -*-
"""
OSPF Network Simulator
Connects multiple routers and simulates network
"""
import time
from typing import Dict, List
from ospf_router import OSPFRouter, OSPFState


class OSPFNetwork:
    """Network containing multiple OSPF routers"""
    
    def __init__(self):
        self.routers: Dict[str, OSPFRouter] = {}
        self.links: List[tuple] = []  # [(router1, router2, interface1, interface2)]
    
    def add_router(self, router_id: str, area_id: str = "0.0.0.0") -> OSPFRouter:
        """Add router to network"""
        router = OSPFRouter(router_id, area_id)
        self.routers[router_id] = router
        return router
    
    def connect_routers(self, router1_id: str, router2_id: str, 
                       interface1: str, interface2: str,
                       ip1: str, ip2: str, cost: int = 10):
        """Connect two routers"""
        if router1_id not in self.routers or router2_id not in self.routers:
            raise ValueError("Both routers must exist")
        
        router1 = self.routers[router1_id]
        router2 = self.routers[router2_id]
        
        # Add interfaces
        router1.add_interface(interface1, ip1, cost=cost)
        router2.add_interface(interface2, ip2, cost=cost)
        
        # Record link
        self.links.append((router1_id, router2_id, interface1, interface2))
        
        # Update LSAs with neighbor connections
        router1.lsdb[router1.router_id].links.append({
            'interface': interface1,
            'ip': ip1,
            'cost': cost,
            'neighbor_router_id': router2_id
        })
        router2.lsdb[router2.router_id].links.append({
            'interface': interface2,
            'ip': ip2,
            'cost': cost,
            'neighbor_router_id': router1_id
        })
        
        # Establish adjacency
        router1.neighbors[router2_id] = {
            'state': OSPFState.INIT,
            'last_hello': time.time(),
            'interface': interface1
        }
        router1.interfaces[interface1]['neighbors'].add(router2_id)
        
        router2.neighbors[router1_id] = {
            'state': OSPFState.INIT,
            'last_hello': time.time(),
            'interface': interface2
        }
        router2.interfaces[interface2]['neighbors'].add(router1_id)
        
        # Exchange hellos
        router1.receive_hello(router2_id, interface1)
        router2.receive_hello(router1_id, interface2)
        
        print(f"Connected {router1_id} <-> {router2_id}")
    
    def start_all(self):
        """Start all routers"""
        for router in self.routers.values():
            router.start()
    
    def stop_all(self):
        """Stop all routers"""
        for router in self.routers.values():
            router.stop()
    
    def simulate_link_failure(self, router1_id: str, router2_id: str):
        """Simulate link failure between two routers"""
        if router1_id in self.routers and router2_id in self.routers:
            router1 = self.routers[router1_id]
            router2 = self.routers[router2_id]
            
            # Remove neighbors
            if router2_id in router1.neighbors:
                del router1.neighbors[router2_id]
            if router1_id in router2.neighbors:
                del router2.neighbors[router1_id]
            
            # Remove from interfaces
            for iface in router1.interfaces.values():
                iface['neighbors'].discard(router2_id)
            for iface in router2.interfaces.values():
                iface['neighbors'].discard(router1_id)
            
            print(f"Link failure: {router1_id} <-> {router2_id}")
            print("Routers will reconverge via SPF...")
    
    def print_network_status(self):
        """Print status of all routers"""
        for router in self.routers.values():
            router.print_status()

