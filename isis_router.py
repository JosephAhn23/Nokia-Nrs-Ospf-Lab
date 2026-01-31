# -*- coding: utf-8 -*-
"""
Minimal ISIS Router Implementation
Focus: Make it WORK, not perfect
"""
import time
import threading
from enum import Enum
from typing import Dict, List, Set, Optional
from dataclasses import dataclass, field


class ISISLevel(Enum):
    LEVEL_1 = "L1"
    LEVEL_2 = "L2"
    LEVEL_1_2 = "L1L2"


class ISISState(Enum):
    DOWN = "DOWN"
    INIT = "INIT"
    UP = "UP"


@dataclass
class LSP:
    """Link State PDU - ISIS version of LSA"""
    system_id: str
    sequence: int = 0
    links: List[Dict] = field(default_factory=list)
    age: int = 0
    level: ISISLevel = ISISLevel.LEVEL_1


@dataclass
class ISISRoute:
    """ISIS Route Entry"""
    prefix: str
    next_hop: str
    cost: int
    interface: str
    level: ISISLevel


class ISISRouter:
    """Minimal working ISIS router"""
    
    def __init__(self, system_id: str, level: ISISLevel = ISISLevel.LEVEL_1):
        self.system_id = system_id
        self.level = level
        self.hello_interval = 10
        self.hold_time = 30
        
        # Neighbor state
        self.neighbors: Dict[str, Dict] = {}  # {system_id: {state, last_hello, interface, level}}
        
        # Link State Database
        self.lsdb: Dict[str, LSP] = {}  # {system_id: LSP}
        
        # Routing table
        self.routing_table: Dict[str, ISISRoute] = {}
        
        # Local links/interfaces
        self.interfaces: Dict[str, Dict] = {}  # {interface_name: {ip, mask, cost, neighbors}}
        
        # Threading
        self.running = False
        self.hello_thread = None
        self.spf_thread = None
        
        # Create self LSP
        self._create_self_lsp()
    
    def add_interface(self, interface: str, ip: str, mask: str = "255.255.255.0", cost: int = 10):
        """Add an interface to the router"""
        self.interfaces[interface] = {
            'ip': ip,
            'mask': mask,
            'cost': cost,
            'neighbors': set()
        }
        self._create_self_lsp()
    
    def _create_self_lsp(self):
        """Create LSP for this router"""
        links = []
        for iface, info in self.interfaces.items():
            links.append({
                'interface': iface,
                'ip': info['ip'],
                'cost': info['cost']
            })
        
        self.lsdb[self.system_id] = LSP(
            system_id=self.system_id,
            sequence=0,
            links=links,
            age=0,
            level=self.level
        )
    
    def receive_hello(self, neighbor_id: str, interface: str, neighbor_level: ISISLevel = ISISLevel.LEVEL_1):
        """Process received hello packet (IIH - ISIS Hello)"""
        if neighbor_id not in self.neighbors:
            self.neighbors[neighbor_id] = {
                'state': ISISState.INIT,
                'last_hello': time.time(),
                'interface': interface,
                'level': neighbor_level
            }
            print(f"[{self.system_id}] New ISIS neighbor discovered: {neighbor_id} on {interface}")
        else:
            self.neighbors[neighbor_id]['last_hello'] = time.time()
        
        # State transitions (simplified ISIS adjacency)
        if self.neighbors[neighbor_id]['state'] == ISISState.INIT:
            # Check level compatibility
            if self._levels_compatible(self.level, neighbor_level):
                self.neighbors[neighbor_id]['state'] = ISISState.UP
                print(f"[{self.system_id}] ISIS neighbor {neighbor_id} -> UP (Adjacency established!)")
                self._exchange_lsps(neighbor_id)
    
    def _levels_compatible(self, level1: ISISLevel, level2: ISISLevel) -> bool:
        """Check if ISIS levels are compatible"""
        if level1 == ISISLevel.LEVEL_1_2 or level2 == ISISLevel.LEVEL_1_2:
            return True
        return level1 == level2
    
    def _exchange_lsps(self, neighbor_id: str):
        """Exchange LSPs with neighbor"""
        # Send our LSPs
        self._send_lsps(neighbor_id)
    
    def _send_lsps(self, neighbor_id: str):
        """Send LSPs to neighbor"""
        for system_id, lsp in self.lsdb.items():
            self._receive_lsp(lsp, neighbor_id)
    
    def receive_lsp(self, lsp: LSP, from_router: str):
        """Receive LSP from neighbor"""
        self._receive_lsp(lsp, from_router)
    
    def _receive_lsp(self, lsp: LSP, from_router: str):
        """Internal LSP processing"""
        if lsp.system_id not in self.lsdb:
            # New LSP
            self.lsdb[lsp.system_id] = lsp
            print(f"[{self.system_id}] Received new LSP from {lsp.system_id} via {from_router}")
            # Flood to other neighbors
            self._flood_lsp(lsp, from_router)
        elif lsp.sequence > self.lsdb[lsp.system_id].sequence:
            # Updated LSP
            self.lsdb[lsp.system_id] = lsp
            print(f"[{self.system_id}] Updated LSP from {lsp.system_id}")
            self._flood_lsp(lsp, from_router)
    
    def _flood_lsp(self, lsp: LSP, except_router: str):
        """Flood LSP to all neighbors except sender"""
        for neighbor_id, neighbor_info in self.neighbors.items():
            if neighbor_id != except_router and neighbor_info['state'] == ISISState.UP:
                # Simulate flooding
                pass  # In real implementation, send packet
    
    def calculate_spf(self):
        """Dijkstra SPF algorithm for ISIS - simplified but working"""
        if len(self.lsdb) < 2:  # Need at least 2 routers
            return
        
        # Build adjacency graph from LSDB
        graph = {}
        for system_id, lsp in self.lsdb.items():
            graph[system_id] = []
            for link in lsp.links:
                # Link contains neighbor_system_id if it's a point-to-point link
                neighbor_id = link.get('neighbor_system_id')
                if neighbor_id and neighbor_id in self.lsdb:
                    cost = link.get('cost', 10)
                    graph[system_id].append((neighbor_id, cost))
        
        # Dijkstra's algorithm
        distances = {self.system_id: 0}
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
        """Build routing table from SPF results"""
        self.routing_table = {}
        
        for dest_system, cost in distances.items():
            if dest_system == self.system_id:
                continue
            
            # Find next hop (first hop in path)
            next_hop = self._find_next_hop(dest_system, previous)
            if next_hop and next_hop in self.neighbors:
                # Get interface to next hop
                interface = self._get_interface_to_neighbor(next_hop)
                if interface:
                    # Use system_id as prefix for simplicity
                    prefix = f"{dest_system}/32"
                    self.routing_table[prefix] = ISISRoute(
                        prefix=prefix,
                        next_hop=next_hop,
                        cost=cost,
                        interface=interface,
                        level=self.level
                    )
    
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
        path.append(self.system_id)  # Add self
        
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
    
    def start(self):
        """Start ISIS router"""
        self.running = True
        self.hello_thread = threading.Thread(target=self._hello_loop, daemon=True)
        self.hello_thread.start()
        
        self.spf_thread = threading.Thread(target=self._spf_loop, daemon=True)
        self.spf_thread.start()
        
        print(f"[{self.system_id}] ISIS router started (Level: {self.level.value})")
    
    def stop(self):
        """Stop ISIS router"""
        self.running = False
        print(f"[{self.system_id}] ISIS router stopped")
    
    def _hello_loop(self):
        """Send hello packets periodically"""
        while self.running:
            # Check for dead neighbors
            current_time = time.time()
            for neighbor_id, neighbor_info in list(self.neighbors.items()):
                if current_time - neighbor_info['last_hello'] > self.hold_time:
                    print(f"[{self.system_id}] ISIS neighbor {neighbor_id} declared dead")
                    del self.neighbors[neighbor_id]
            
            time.sleep(self.hello_interval)
    
    def _spf_loop(self):
        """Recalculate SPF periodically"""
        while self.running:
            time.sleep(30)  # Recalculate every 30 seconds
            if len(self.lsdb) > 1:  # Only if we have other routers
                self.calculate_spf()
                print(f"[{self.system_id}] ISIS SPF recalculated, {len(self.routing_table)} routes")
    
    def get_routing_table(self) -> Dict[str, ISISRoute]:
        """Get current routing table"""
        return self.routing_table.copy()
    
    def print_status(self):
        """Print router status"""
        print(f"\n{'='*60}")
        print(f"ISIS Router: {self.system_id} (Level: {self.level.value})")
        print(f"{'='*60}")
        print(f"Neighbors: {len(self.neighbors)}")
        for neighbor_id, info in self.neighbors.items():
            print(f"  {neighbor_id}: {info['state'].value} (interface: {info['interface']}, level: {info['level'].value})")
        print(f"LSDB entries: {len(self.lsdb)}")
        print(f"Routes: {len(self.routing_table)}")
        for prefix, route in self.routing_table.items():
            print(f"  {prefix} -> {route.next_hop} via {route.interface} (cost: {route.cost}, level: {route.level.value})")
        print()

