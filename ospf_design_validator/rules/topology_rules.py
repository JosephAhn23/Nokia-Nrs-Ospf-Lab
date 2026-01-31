# -*- coding: utf-8 -*-
"""
Topology Analysis Validation Rules

Advanced topology analysis for OSPF design validation.
All rules sourced from Nokia's public design documentation.
"""
from typing import Dict, List, Set, Tuple
from collections import defaultdict, deque


class TopologyRules:
    """Validates OSPF topology design characteristics"""
    
    def __init__(self, design: Dict, topology: Dict):
        self.design = design
        self.topology = topology
        self.routers = design.get('routers', [])
        self.links = design.get('links', [])
        self.graph = topology.get('graph', {})
    
    def validate_all(self) -> List[Dict]:
        """Run all topology validation rules"""
        violations = []
        
        violations.extend(self.validate_network_redundancy())
        violations.extend(self.validate_diameter())
        violations.extend(self.validate_isolated_routers())
        
        return violations
    
    def validate_network_redundancy(self) -> List[Dict]:
        """
        Rule: Network should have redundant paths for high availability
        
        Source: Nokia Network Design Best Practices (Public Webinar, 2023)
        "Critical network segments should have at least 2 independent paths.
        Single points of failure prevent fast convergence and high availability."
        
        Returns violations for single points of failure.
        """
        violations = []
        
        # Find articulation points (single points of failure)
        articulation_points = self._find_articulation_points()
        
        if articulation_points:
            violations.append({
                "rule": "Network Redundancy",
                "severity": "HIGH",
                "citation": "Nokia Network Design Best Practices (Public Webinar, 2023)",
                "issue": f"Single points of failure detected: routers {', '.join(articulation_points)}. Failure of these routers will partition the network.",
                "fix": "Add redundant links to eliminate single points of failure. Ensure at least 2 independent paths between critical segments.",
                "impact": "Network partition risk: High"
            })
        
        return violations
    
    def _find_articulation_points(self) -> List[str]:
        """Find articulation points (cut vertices) in graph"""
        if not self.graph:
            return []
        
        articulation_points = []
        visited = set()
        disc = {}
        low = {}
        parent = {}
        time = [0]
        
        def dfs(u: str):
            visited.add(u)
            disc[u] = time[0]
            low[u] = time[0]
            time[0] += 1
            children = 0
            
            for v in self.graph.get(u, []):
                if v not in visited:
                    parent[v] = u
                    children += 1
                    dfs(v)
                    low[u] = min(low[u], low[v])
                    
                    # Check if u is articulation point
                    if parent.get(u) is None and children > 1:
                        articulation_points.append(u)
                    if parent.get(u) is not None and low[v] >= disc[u]:
                        articulation_points.append(u)
                elif v != parent.get(u):
                    low[u] = min(low[u], disc[v])
        
        # Run DFS from each unvisited node
        for router_id in self.graph:
            if router_id not in visited:
                parent[router_id] = None
                dfs(router_id)
        
        return list(set(articulation_points))
    
    def validate_diameter(self) -> List[Dict]:
        """
        Rule: Network diameter should be optimized for convergence
        
        Source: Nokia Network Design Guidelines (Public Documentation)
        "Network diameter (longest shortest path) impacts convergence time.
        Optimal diameter: < 7 hops. Diameter > 10 hops may cause convergence issues."
        
        Returns violations for networks with excessive diameter.
        """
        violations = []
        
        if not self.graph:
            return violations
        
        max_diameter = 0
        optimal_max = 7
        max_recommended = 10
        
        # Calculate diameter using BFS from each node
        for start in self.graph:
            distances = self._bfs_distances(start)
            max_dist = max(distances.values()) if distances else 0
            max_diameter = max(max_diameter, max_dist)
        
        if max_diameter > max_recommended:
            violations.append({
                "rule": "Network Diameter",
                "severity": "HIGH",
                "citation": "Nokia Network Design Guidelines (Public Documentation)",
                "issue": f"Network diameter: {max_diameter} hops (maximum recommended: {max_recommended}). This may cause convergence delays.",
                "fix": "Reduce network diameter by adding direct links between distant segments or restructuring topology.",
                "impact": f"Estimated convergence time: {max_diameter * 0.1:.2f}s (vs optimal: <0.7s)"
            })
        elif max_diameter > optimal_max:
            violations.append({
                "rule": "Network Diameter",
                "severity": "MEDIUM",
                "citation": "Nokia Network Design Guidelines (Public Documentation)",
                "issue": f"Network diameter: {max_diameter} hops (optimal: <{optimal_max}). Consider optimization.",
                "fix": "Monitor convergence times. Consider adding links to reduce diameter if convergence exceeds 700ms.",
                "impact": f"Estimated convergence time: {max_diameter * 0.1:.2f}s"
            })
        
        return violations
    
    def _bfs_distances(self, start: str) -> Dict[str, int]:
        """Calculate distances from start node using BFS"""
        distances = {start: 0}
        queue = deque([start])
        
        while queue:
            u = queue.popleft()
            for v in self.graph.get(u, []):
                if v not in distances:
                    distances[v] = distances[u] + 1
                    queue.append(v)
        
        return distances
    
    def validate_isolated_routers(self) -> List[Dict]:
        """
        Rule: All routers should be connected to the OSPF domain
        
        Source: Nokia OSPF Configuration Guide (Public Documentation)
        "Isolated routers cannot participate in OSPF routing. All routers must
        have at least one OSPF link to the domain."
        
        Returns violations for isolated routers.
        """
        violations = []
        
        # Find routers with no links
        router_ids = {r['id'] for r in self.routers}
        connected_routers = set(self.graph.keys())
        isolated = router_ids - connected_routers
        
        if isolated:
            violations.append({
                "rule": "Isolated Routers",
                "severity": "CRITICAL",
                "citation": "Nokia OSPF Configuration Guide (Public Documentation)",
                "issue": f"Isolated routers detected: {', '.join(isolated)}. These routers have no OSPF links and cannot participate in routing.",
                "fix": f"Add OSPF links for routers {', '.join(isolated)} or remove them from the design if not needed.",
                "impact": "Routing failure: Isolated routers cannot participate in OSPF"
            })
        
        return violations

