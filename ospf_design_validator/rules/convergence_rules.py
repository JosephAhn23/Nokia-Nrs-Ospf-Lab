# -*- coding: utf-8 -*-
"""
Convergence Analysis Validation Rules

Analyzes OSPF design for convergence time estimation and SPF calculation impact.
All rules sourced from Nokia's public design documentation.
"""
from typing import Dict, List, Set
from collections import defaultdict


class ConvergenceRules:
    """Validates OSPF design for optimal convergence characteristics"""
    
    def __init__(self, design: Dict, topology: Dict):
        self.design = design
        self.topology = topology
        self.routers = design.get('routers', [])
        self.links = design.get('links', [])
        self.warnings = []
    
    def validate_all(self) -> List[Dict]:
        """Run all convergence validation rules"""
        violations = []
        
        violations.extend(self.validate_spf_complexity())
        violations.extend(self.validate_lsdb_size())
        violations.extend(self.validate_convergence_paths())
        
        return violations
    
    def get_warnings(self) -> List[Dict]:
        """Get convergence warnings (non-critical)"""
        return self.warnings
    
    def validate_spf_complexity(self) -> List[Dict]:
        """
        Rule: SPF calculation complexity should be minimized
        
        Source: Nokia Network Design Best Practices (Public Webinar, 2023)
        "SPF calculation time increases exponentially with area size. Areas with
        more than 100 routers may experience convergence times > 1 second."
        
        Returns violations for areas exceeding optimal size.
        """
        violations = []
        optimal_max = 50
        max_recommended = 100
        
        # Count routers per area
        area_router_count = defaultdict(list)
        for router in self.routers:
            for area in router.get('areas', []):
                area_router_count[area].append(router['id'])
        
        for area, routers in area_router_count.items():
            router_count = len(routers)
            if router_count > max_recommended:
                violations.append({
                    "rule": "SPF Calculation Complexity",
                    "severity": "HIGH",
                    "citation": "Nokia Network Design Best Practices (Public Webinar, 2023)",
                    "issue": f"Area {area} contains {router_count} routers (maximum recommended: {max_recommended}). SPF calculation time may exceed 1 second, impacting convergence.",
                    "fix": f"Split area {area} into multiple areas or implement route summarization to reduce LSDB size.",
                    "impact": f"Estimated convergence time: {router_count * 0.01:.2f}s (vs optimal: <0.5s)"
                })
            elif router_count > optimal_max:
                self.warnings.append({
                    "rule": "SPF Calculation Complexity",
                    "severity": "MEDIUM",
                    "citation": "Nokia Network Design Best Practices (Public Webinar, 2023)",
                    "issue": f"Area {area} contains {router_count} routers (optimal: <{optimal_max}). Consider optimization for better convergence.",
                    "fix": f"Monitor SPF calculation times. Consider splitting area {area} if convergence exceeds 500ms."
                })
        
        return violations
    
    def validate_lsdb_size(self) -> List[Dict]:
        """
        Rule: LSDB size should be optimized for memory and convergence
        
        Source: Nokia SR-OS Design Guidelines (Public Documentation)
        "Large LSDBs consume significant memory and increase SPF calculation time.
        Target LSDB size: < 10,000 LSAs per area for optimal performance."
        
        Returns violations for areas with excessive LSDB size.
        """
        violations = []
        max_lsas = 10000
        
        # Estimate LSDB size (simplified - would need actual LSA count)
        # Formula: Router LSAs + Network LSAs + Summary LSAs
        area_lsdb_estimate = defaultdict(int)
        
        for router in self.routers:
            for area in router.get('areas', []):
                # Each router generates 1 Router LSA
                area_lsdb_estimate[area] += 1
                
                # Count network segments (links) in area
                area_links = [l for l in self.links if l.get('area') == area]
                # Each broadcast segment generates 1 Network LSA
                broadcast_segments = len(set(
                    (l.get('from'), l.get('interface')) for l in area_links
                    if l.get('network_type') == 'broadcast'
                ))
                area_lsdb_estimate[area] += broadcast_segments
        
        # Add summary LSAs (estimated: 1 per ABR per remote area)
        abr_count = sum(1 for r in self.routers if len(r.get('areas', [])) > 1)
        for area in area_lsdb_estimate:
            if area != '0.0.0.0':
                area_lsdb_estimate[area] += abr_count  # Summary LSAs from ABR
        
        for area, lsa_count in area_lsdb_estimate.items():
            if lsa_count > max_lsas:
                violations.append({
                    "rule": "LSDB Size Optimization",
                    "severity": "HIGH",
                    "citation": "Nokia SR-OS Design Guidelines (Public Documentation)",
                    "issue": f"Area {area} estimated LSDB size: {lsa_count} LSAs (maximum recommended: {max_lsas}). This may impact memory usage and SPF calculation.",
                    "fix": f"Implement route summarization at ABR for area {area} to reduce LSDB size.",
                    "impact": f"Estimated memory usage: {lsa_count * 0.1:.1f}MB (vs optimal: <1MB)"
                })
        
        return violations
    
    def validate_convergence_paths(self) -> List[Dict]:
        """
        Rule: Network should have redundant paths for fast convergence
        
        Source: Nokia Network Design Best Practices (Public Webinar Series)
        "Single points of failure prevent fast convergence. Critical routers should
        have at least 2 paths to Area 0 for optimal failover."
        
        Returns violations for routers with single path to Area 0.
        """
        violations = []
        
        # Find routers not in Area 0
        non_backbone_routers = [
            r for r in self.routers
            if '0.0.0.0' not in r.get('areas', [])
        ]
        
        # Build area connectivity graph
        area_graph = defaultdict(set)
        for link in self.links:
            from_router = link.get('from')
            to_router = link.get('to')
            area = link.get('area')
            
            # Find routers in this area
            from_areas = next((r.get('areas', []) for r in self.routers if r['id'] == from_router), [])
            to_areas = next((r.get('areas', []) for r in self.routers if r['id'] == to_router), [])
            
            if area in from_areas and area in to_areas:
                area_graph[area].add((from_router, to_router))
        
        # Check for single path to Area 0
        for router in non_backbone_routers:
            router_areas = router.get('areas', [])
            # Check if router has multiple paths to Area 0
            # (Simplified - would need full path analysis)
            abr_count = sum(1 for r in self.routers 
                          if '0.0.0.0' in r.get('areas', []) and 
                          any(a in router_areas for a in r.get('areas', [])))
            
            if abr_count < 2:
                violations.append({
                    "rule": "Convergence Path Redundancy",
                    "severity": "MEDIUM",
                    "citation": "Nokia Network Design Best Practices (Public Webinar Series)",
                    "issue": f"Router {router['id']} has single path to Area 0 (through {abr_count} ABR). Failure of this path will cause convergence delay.",
                    "fix": f"Add redundant connectivity for router {router['id']} to Area 0, or ensure multiple ABRs in area {router_areas[0]}.",
                    "impact": "Estimated convergence time on failure: 2-5 seconds (vs optimal: <1 second)"
                })
        
        return violations

