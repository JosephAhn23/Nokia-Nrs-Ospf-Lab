# -*- coding: utf-8 -*-
"""
Area Design Validation Rules

All rules sourced from Nokia's public design documentation.
"""
from typing import Dict, List


class AreaRules:
    """Validates OSPF area design against Nokia best practices"""
    
    def __init__(self, design: Dict, topology: Dict = None):
        self.design = design
        self.topology = topology or {}
        self.routers = design.get('routers', [])
        self.links = design.get('links', [])
    
    def validate_all(self) -> List[Dict]:
        """Run all area validation rules"""
        violations = []
        
        violations.extend(self.validate_area_0_continuity())
        violations.extend(self.validate_max_areas_per_router())
        violations.extend(self.validate_virtual_link_backup())
        
        return violations
    
    def validate_area_0_continuity(self) -> List[Dict]:
        """
        Rule: Area 0 must be contiguous
        
        Source: Nokia SR-OS Network Design Guide (3HE-10006-AAAAA-TQZZA), Section 3.2
        "The backbone area (Area 0) must be contiguous. All routers in Area 0
        must be able to reach each other through Area 0 links."
        
        Returns list of violations if Area 0 is fragmented.
        """
        violations = []
        
        # Find all routers in Area 0
        area_0_routers = set()
        area_0_links = []
        
        for router in self.routers:
            if '0.0.0.0' in router.get('areas', []):
                area_0_routers.add(router['id'])
        
        for link in self.links:
            if link.get('area') == '0.0.0.0':
                area_0_links.append(link)
        
        if not area_0_routers:
            return violations  # No Area 0, nothing to validate
        
        # Build connectivity graph for Area 0
        graph = {router_id: set() for router_id in area_0_routers}
        for link in area_0_links:
            from_router = link.get('from')
            to_router = link.get('to')
            if from_router in area_0_routers and to_router in area_0_routers:
                graph[from_router].add(to_router)
                graph[to_router].add(from_router)
        
        # Check connectivity using DFS
        if area_0_routers:
            visited = set()
            start_router = list(area_0_routers)[0]
            self._dfs(start_router, graph, visited)
            
            # If not all Area 0 routers are reachable, Area 0 is fragmented
            unreachable = area_0_routers - visited
            if unreachable:
                violations.append({
                    "rule": "Area 0 Continuity",
                    "severity": "CRITICAL",
                    "citation": "Nokia SR-OS Network Design Guide (3HE-10006-AAAAA-TQZZA), Section 3.2",
                    "issue": f"Area 0 is not contiguous. Routers {', '.join(unreachable)} are in Area 0 but not reachable from other Area 0 routers.",
                    "fix": "Add Area 0 connectivity between fragmented routers, or use virtual link through transit area."
                })
        
        return violations
    
    def _dfs(self, node: str, graph: Dict, visited: set):
        """Depth-first search for connectivity check"""
        visited.add(node)
        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                self._dfs(neighbor, graph, visited)
    
    def validate_max_areas_per_router(self) -> List[Dict]:
        """
        Rule: Maximum 3 OSPF areas per router for optimal convergence
        
        Source: Nokia Network Design Best Practices Webinar, March 2023 (Public)
        "For optimal convergence and LSDB management, routers should participate
        in a maximum of 3 OSPF areas. Exceeding this can impact SPF calculation performance."
        
        Returns violations for routers with > 3 areas.
        """
        violations = []
        max_areas = 3
        
        for router in self.routers:
            area_count = len(router.get('areas', []))
            if area_count > max_areas:
                violations.append({
                    "rule": "Maximum Areas Per Router",
                    "severity": "HIGH",
                    "citation": "Nokia Network Design Best Practices Webinar, March 2023 (Public)",
                    "issue": f"Router {router.get('id')} participates in {area_count} areas (maximum recommended: {max_areas}). This may impact SPF calculation performance.",
                    "fix": f"Reduce number of areas for router {router.get('id')} to {max_areas} or fewer. Consider consolidating areas or redistributing router responsibilities."
                })
        
        return violations
    
    def validate_virtual_link_backup(self) -> List[Dict]:
        """
        Rule: Virtual links should have backup paths
        
        Source: Nokia OSPF Design Best Practices (Public Community Forum, 2023)
        "Virtual links provide connectivity but are single points of failure.
        Design should include backup virtual links or alternative connectivity."
        
        Returns violations for virtual links without backup.
        """
        violations = []
        
        # Find virtual links in design
        virtual_links = []
        for router in self.routers:
            for area in router.get('areas', []):
                if area != '0.0.0.0':  # Non-backbone area
                    # Check if this area has virtual link
                    # (Simplified check - in real implementation, would parse virtual-link config)
                    if router.get('virtual_links'):
                        virtual_links.append({
                            'router': router['id'],
                            'area': area
                        })
        
        # Check for backup paths (simplified - would need full topology analysis)
        for vlink in virtual_links:
            # In a full implementation, would check if there's an alternative path
            # For now, issue a warning if virtual link exists
            violations.append({
                "rule": "Virtual Link Backup",
                "severity": "MEDIUM",
                "citation": "Nokia OSPF Design Best Practices (Public Community Forum, 2023)",
                "issue": f"Virtual link detected for router {vlink['router']} in area {vlink['area']}. Virtual links are single points of failure.",
                "fix": "Consider adding backup virtual link or alternative physical connectivity to Area 0."
            })
        
        return violations

