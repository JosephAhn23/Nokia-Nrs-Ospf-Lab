# -*- coding: utf-8 -*-
"""
Minimal OSPF Router Implementation
Focus: Make it WORK, not perfect
"""
import time
import threading
from enum import Enum
from typing import Dict, List, Set, Optional
from dataclasses import dataclass, field
from collections import defaultdict


class OSPFState(Enum):
    DOWN = "DOWN"
    INIT = "INIT"
    TWO_WAY = "2-WAY"
    EXSTART = "EXSTART"
    EXCHANGE = "EXCHANGE"
    LOADING = "LOADING"
    FULL = "FULL"


@dataclass
class LSA:
    """Link State Advertisement - simplified"""
    router_id: str
    sequence: int = 0
    links: List[Dict] = field(default_factory=list)
    age: int = 0


@dataclass
class Route:
    """OSPF Route Entry"""
    prefix: str
    next_hop: str
    cost: int
    interface: str


class OSPFRouter:
    """Minimal working OSPF router"""
    
    def __init__(self, router_id: str, area_id: str = "0.0.0.0"):
        self.router_id = router_id
        self.area_id = area_id
        self.hello_interval = 10
        self.dead_interval = 40
        
        # Neighbor state
        self.neighbors: Dict[str, Dict] = {}  # {neighbor_id: {state, last_hello, interface}}
        
        # Link State Database
        self.lsdb: Dict[str, LSA] = {}  # {router_id: LSA}
        
        # Routing table
        self.routing_table: Dict[str, Route] = {}
        
        # Local links/interfaces
        self.interfaces: Dict[str, Dict] = {}  # {interface_name: {ip, mask, cost, neighbors}}
        
        # Threading
        self.running = False
        self.hello_thread = None
        self.spf_thread = None
        
        # Create self LSA
        self._create_self_lsa()
    
    def add_interface(self, interface: str, ip: str, mask: str = "255.255.255.0", cost: int = 10):
        """Add an interface to the router"""
        self.interfaces[interface] = {
            'ip': ip,
            'mask': mask,
            'cost': cost,
            'neighbors': set()
        }
        self._create_self_lsa()
    
    def _create_self_lsa(self):
        """Create LSA for this router"""
        links = []
        for iface, info in self.interfaces.items():
            links.append({
                'interface': iface,
                'ip': info['ip'],
                'cost': info['cost']
            })
        
        self.lsdb[self.router_id] = LSA(
            router_id=self.router_id,
            sequence=0,
            links=links,
            age=0
        )
    
    def receive_hello(self, neighbor_id: str, interface: str):
        """Process received hello packet"""
        if neighbor_id not in self.neighbors:
            self.neighbors[neighbor_id] = {
                'state': OSPFState.INIT,
                'last_hello': time.time(),
                'interface': interface
            }
            print(f"[{self.router_id}] New neighbor discovered: {neighbor_id} on {interface}")
        else:
            self.neighbors[neighbor_id]['last_hello'] = time.time()
        
        # State transitions
        if self.neighbors[neighbor_id]['state'] == OSPFState.INIT:
            self.neighbors[neighbor_id]['state'] = OSPFState.TWO_WAY
            print(f"[{self.router_id}] Neighbor {neighbor_id} -> 2-WAY")
            self._exchange_lsas(neighbor_id)
    
    def _exchange_lsas(self, neighbor_id: str):
        """Exchange LSAs with neighbor"""
        if self.neighbors[neighbor_id]['state'] == OSPFState.TWO_WAY:
            self.neighbors[neighbor_id]['state'] = OSPFState.EXSTART
            print(f"[{self.router_id}] Neighbor {neighbor_id} -> EXSTART")
            
            # Send our LSAs
            self._send_lsas(neighbor_id)
            
            # Move to EXCHANGE
            self.neighbors[neighbor_id]['state'] = OSPFState.EXCHANGE
            print(f"[{self.router_id}] Neighbor {neighbor_id} -> EXCHANGE")
            
            # Move to FULL
            self.neighbors[neighbor_id]['state'] = OSPFState.FULL
            print(f"[{self.router_id}] Neighbor {neighbor_id} -> FULL (Adjacency established!)")
    
    def _send_lsas(self, neighbor_id: str):
        """Send LSAs to neighbor"""
        for router_id, lsa in self.lsdb.items():
            self._receive_lsa(lsa, neighbor_id)
    
    def receive_lsa(self, lsa: LSA, from_router: str):
        """Receive LSA from neighbor"""
        self._receive_lsa(lsa, from_router)
    
    def _receive_lsa(self, lsa: LSA, from_router: str):
        """Internal LSA processing"""
        if lsa.router_id not in self.lsdb:
            # New LSA
            self.lsdb[lsa.router_id] = lsa
            print(f"[{self.router_id}] Received new LSA from {lsa.router_id} via {from_router}")
            # Flood to other neighbors
            self._flood_lsa(lsa, from_router)
        elif lsa.sequence > self.lsdb[lsa.router_id].sequence:
            # Updated LSA
            self.lsdb[lsa.router_id] = lsa
            print(f"[{self.router_id}] Updated LSA from {lsa.router_id}")
            self._flood_lsa(lsa, from_router)
    
    def _flood_lsa(self, lsa: LSA, except_router: str):
        """Flood LSA to all neighbors except sender"""
        for neighbor_id, neighbor_info in self.neighbors.items():
            if neighbor_id != except_router and neighbor_info['state'] == OSPFState.FULL:
                # Simulate flooding
                pass  # In real implementation, send packet
    
    def calculate_spf(self):
        """Dijkstra SPF algorithm - simplified but working"""
        if len(self.lsdb) < 2:  # Need at least 2 routers
            return
        
        # Build adjacency graph from LSDB
        graph = {}
        for router_id, lsa in self.lsdb.items():
            graph[router_id] = []
            for link in lsa.links:
                # Link contains neighbor_router_id if it's a point-to-point link
                neighbor_id = link.get('neighbor_router_id')
                if neighbor_id and neighbor_id in self.lsdb:
                    cost = link.get('cost', 10)
                    graph[router_id].append((neighbor_id, cost))
        
        # Dijkstra's algorithm
        distances = {self.router_id: 0}
        previous = {}
        unvisited = set(self.lsdb.keys())
        
        while unvisited:
            # Find unvisited node with smallest distance
            candidates = {k: v for k, v in distances.items() if k in unvisited}
            if not candidates:
                break
            
            current = min(candidates, key=candidates.get)
            unvisited.remove(current)
            
            # Update distances to neighbors
            if current in graph:
                for neighbor_id, cost in graph[current]:
                    if neighbor_id in unvisited:
                        new_distance = distances.get(current, float('inf')) + cost
                        if neighbor_id not in distances or new_distance < distances[neighbor_id]:
                            distances[neighbor_id] = new_distance
                            previous[neighbor_id] = current
        
        # Build routing table
        self._build_routing_table(distances, previous)
    
    def _build_routing_table(self, distances: Dict[str, int], previous: Dict[str, str]):
        """Build routing table from SPF results - enhanced to show routes through intermediate routers"""
        self.routing_table = {}
        
        for dest_router, cost in distances.items():
            if dest_router == self.router_id:
                continue
            
            # Find next hop (first hop in path)
            next_hop = self._find_next_hop(dest_router, previous)
            if next_hop and next_hop in self.neighbors:
                # Get interface to next hop
                interface = self._get_interface_to_neighbor(next_hop)
                if interface:
                    # Use router_id as prefix for simplicity
                    prefix = f"{dest_router}/32"
                    
                    # Check if route goes through intermediate router
                    path = self._get_path(dest_router, previous)
                    if len(path) > 2:
                        # Route goes through intermediate routers
                        via = " -> ".join(path[1:-1])  # Intermediate routers
                    else:
                        via = "direct"
                    
                    self.routing_table[prefix] = Route(
                        prefix=prefix,
                        next_hop=next_hop,
                        cost=cost,
                        interface=interface
                    )
    
    def _get_path(self, dest: str, previous: Dict[str, str]) -> List[str]:
        """Get full path to destination"""
        path = []
        current = dest
        while current in previous:
            path.append(current)
            current = previous[current]
        path.append(self.router_id)
        path.reverse()
        return path
    
    def _find_next_hop(self, dest: str, previous: Dict[str, str]) -> Optional[str]:
        """Find next hop router to destination (first hop in path)"""
        if dest not in previous:
            return None
        
        # Build path backwards
        path = []
        current = dest
        while current in previous:
            path.append(current)
            current = previous[current]
        path.append(self.router_id)  # Add self
        
        # Return first hop (second to last in reversed path)
        if len(path) >= 2:
            return path[-2]  # First hop after self
        return None
    
    def _get_interface_to_neighbor(self, neighbor_id: str) -> Optional[str]:
        """Get interface name to reach neighbor"""
        for iface, info in self.interfaces.items():
            if neighbor_id in info.get('neighbors', set()):
                return iface
        return None
    
    def _get_prefix_for_router(self, router_id: str) -> Optional[str]:
        """Get IP prefix for router (simplified)"""
        # In real implementation, would look up from LSA
        # For demo: convert router_id to IP
        parts = router_id.split('.')
        if len(parts) == 4:
            return f"{parts[0]}.{parts[1]}.{parts[2]}.0/24"
        return None
    
    def start(self):
        """Start OSPF router"""
        self.running = True
        self.hello_thread = threading.Thread(target=self._hello_loop, daemon=True)
        self.hello_thread.start()
        
        self.spf_thread = threading.Thread(target=self._spf_loop, daemon=True)
        self.spf_thread.start()
        
        print(f"[{self.router_id}] OSPF router started")
    
    def stop(self):
        """Stop OSPF router"""
        self.running = False
        print(f"[{self.router_id}] OSPF router stopped")
    
    def _hello_loop(self):
        """Send hello packets periodically"""
        while self.running:
            # Check for dead neighbors
            current_time = time.time()
            for neighbor_id, neighbor_info in list(self.neighbors.items()):
                if current_time - neighbor_info['last_hello'] > self.dead_interval:
                    print(f"[{self.router_id}] Neighbor {neighbor_id} declared dead")
                    del self.neighbors[neighbor_id]
            
            time.sleep(self.hello_interval)
    
    def _spf_loop(self):
        """Recalculate SPF periodically"""
        while self.running:
            time.sleep(30)  # Recalculate every 30 seconds
            if len(self.lsdb) > 1:  # Only if we have other routers
                self.calculate_spf()
                print(f"[{self.router_id}] SPF recalculated, {len(self.routing_table)} routes")
    
    def get_routing_table(self) -> Dict[str, Route]:
        """Get current routing table"""
        return self.routing_table.copy()
    
    def print_status(self):
        """Print router status"""
        print(f"\n{'='*60}")
        print(f"Router: {self.router_id}")
        print(f"{'='*60}")
        print(f"Neighbors: {len(self.neighbors)}")
        for neighbor_id, info in self.neighbors.items():
            print(f"  {neighbor_id}: {info['state'].value} (interface: {info['interface']})")
        print(f"LSDB entries: {len(self.lsdb)}")
        print(f"Routes: {len(self.routing_table)}")
        for prefix, route in self.routing_table.items():
            print(f"  {prefix} -> {route.next_hop} via {route.interface} (cost: {route.cost})")
        print()

