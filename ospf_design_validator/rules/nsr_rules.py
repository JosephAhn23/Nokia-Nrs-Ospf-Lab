# -*- coding: utf-8 -*-
"""
NSR and Graceful Restart Validation Rules

All rules sourced from Nokia's public configuration documentation.
"""
from typing import Dict, List


class NSRRules:
    """Validates NSR and Graceful Restart configuration"""
    
    def __init__(self, design: Dict, topology: Dict = None):
        self.design = design
        self.topology = topology or {}
        self.routers = design.get('routers', [])
    
    def validate_all(self) -> List[Dict]:
        """Run all NSR/GR validation rules"""
        violations = []
        
        violations.extend(self.validate_nsr_requires_gr())
        violations.extend(self.validate_gr_helper_mode())
        
        return violations
    
    def validate_nsr_requires_gr(self) -> List[Dict]:
        """
        Rule: NSR enabled requires graceful-restart
        
        Source: Nokia SR-OS OSPF Configuration Guide 12.0.R6 (3HE-10006-AAAAA), Page 147
        "When Non-Stop Routing (NSR) is enabled, graceful-restart must also be enabled
        to ensure proper adjacency recovery during switchover events."
        
        Returns violations for routers with NSR but no graceful-restart.
        """
        violations = []
        
        for router in self.routers:
            has_nsr = router.get('nsr', False)
            has_gr = router.get('graceful_restart', False)
            
            if has_nsr and not has_gr:
                violations.append({
                    "rule": "NSR Requires Graceful Restart",
                    "severity": "HIGH",
                    "citation": "Nokia SR-OS OSPF Configuration Guide 12.0.R6 (3HE-10006-AAAAA), Page 147",
                    "issue": f"Router {router.get('id')} has NSR enabled but graceful-restart is not configured. This can cause adjacency failures during switchover.",
                    "fix": f"Add 'graceful-restart' under OSPF configuration for router {router.get('id')}."
                })
        
        return violations
    
    def validate_gr_helper_mode(self) -> List[Dict]:
        """
        Rule: Graceful Restart helper mode considerations
        
        Source: Nokia SR-OS OSPF Configuration Guide 12.0.R6, Section 8.3.2
        "Graceful Restart helper mode should be enabled on all routers in the OSPF domain
        to support neighbor restart scenarios. Disabling helper mode can prevent proper
        adjacency recovery."
        
        Returns violations for routers with GR but helper mode disabled.
        """
        violations = []
        
        for router in self.routers:
            has_gr = router.get('graceful_restart', False)
            helper_disabled = router.get('gr_helper_disable', False)
            
            if has_gr and helper_disabled:
                violations.append({
                    "rule": "Graceful Restart Helper Mode",
                    "severity": "MEDIUM",
                    "citation": "Nokia SR-OS OSPF Configuration Guide 12.0.R6, Section 8.3.2",
                    "issue": f"Router {router.get('id')} has graceful-restart enabled but helper mode is disabled. This prevents the router from assisting neighbors during restart.",
                    "fix": f"Enable graceful-restart helper mode for router {router.get('id')} (remove 'helper-disable' if present)."
                })
        
        return violations

