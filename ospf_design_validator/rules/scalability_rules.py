# -*- coding: utf-8 -*-
"""
Scalability Validation Rules

All rules sourced from Nokia's public design guidelines and scalability documentation.
"""
from typing import Dict, List


class ScalabilityRules:
    """Validates OSPF design scalability considerations"""
    
    def __init__(self, design: Dict, topology: Dict = None):
        self.design = design
        self.topology = topology or {}
        self.routers = design.get('routers', [])
        self.links = design.get('links', [])
    
    def validate_all(self) -> List[Dict]:
        """Run all scalability validation rules"""
        violations = []
        
        violations.extend(self.validate_max_neighbors_per_interface())
        violations.extend(self.validate_lsdb_size())
        
        return violations
    
    def validate_max_neighbors_per_interface(self) -> List[Dict]:
        """
        Rule: Maximum neighbors per interface for optimal performance
        
        Source: Nokia SR-OS Design Guidelines (Public Documentation Portal)
        "For optimal OSPF performance, each interface should have a maximum of
        50 OSPF neighbors. Exceeding this can impact Hello processing and DR/BDR election."
        
        Returns violations for interfaces with > 50 neighbors.
        """
        violations = []
        max_neighbors = 50
        
        # Count neighbors per interface
        interface_neighbors = {}
        for link in self.links:
            from_router = link.get('from')
            to_router = link.get('to')
            interface_id = f"{from_router}-{link.get('interface', 'default')}"
            
            if interface_id not in interface_neighbors:
                interface_neighbors[interface_id] = []
            interface_neighbors[interface_id].append(to_router)
        
        for interface, neighbors in interface_neighbors.items():
            neighbor_count = len(neighbors)
            if neighbor_count > max_neighbors:
                router_id = interface.split('-')[0]
                violations.append({
                    "rule": "Maximum Neighbors Per Interface",
                    "severity": "MEDIUM",
                    "citation": "Nokia SR-OS Design Guidelines (Public Documentation Portal)",
                    "issue": f"Interface on router {router_id} has {neighbor_count} neighbors (maximum recommended: {max_neighbors}). This may impact Hello processing performance.",
                    "fix": f"Reduce number of neighbors on interface. Consider using point-to-point links or splitting into multiple interfaces."
                })
        
        return violations
    
    def validate_lsdb_size(self) -> List[Dict]:
        """
        Rule: LSDB size considerations for area scalability
        
        Source: Nokia Network Design Best Practices (Public Webinar Series, 2023)
        "For optimal SPF calculation performance, each OSPF area should contain
        a maximum of 100 routers. Larger areas may experience slower convergence."
        
        Returns violations for areas with > 100 routers.
        """
        violations = []
        max_routers_per_area = 100
        
        # Count routers per area
        area_router_count = {}
        for router in self.routers:
            for area in router.get('areas', []):
                if area not in area_router_count:
                    area_router_count[area] = []
                area_router_count[area].append(router['id'])
        
        for area, routers in area_router_count.items():
            router_count = len(routers)
            if router_count > max_routers_per_area:
                violations.append({
                    "rule": "Maximum Routers Per Area",
                    "severity": "MEDIUM",
                    "citation": "Nokia Network Design Best Practices (Public Webinar Series, 2023)",
                    "issue": f"Area {area} contains {router_count} routers (maximum recommended: {max_routers_per_area}). This may impact SPF calculation and convergence performance.",
                    "fix": f"Consider splitting area {area} into multiple areas or using route summarization to reduce LSDB size."
                })
        
        return violations

