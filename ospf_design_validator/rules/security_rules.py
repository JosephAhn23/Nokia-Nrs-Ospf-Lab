# -*- coding: utf-8 -*-
"""
Security Validation Rules

Validates OSPF design for security best practices.
All rules sourced from Nokia's public security documentation.
"""
from typing import Dict, List


class SecurityRules:
    """Validates OSPF design security configuration"""
    
    def __init__(self, design: Dict, topology: Dict):
        self.design = design
        self.topology = topology
        self.routers = design.get('routers', [])
        self.links = design.get('links', [])
    
    def validate_all(self) -> List[Dict]:
        """Run all security validation rules"""
        violations = []
        
        violations.extend(self.validate_authentication())
        violations.extend(self.validate_interface_security())
        violations.extend(self.validate_route_filtering())
        
        return violations
    
    def validate_authentication(self) -> List[Dict]:
        """
        Rule: OSPF authentication should be enabled in production
        
        Source: Nokia SR-OS Security Guide (Public Documentation)
        "OSPF authentication prevents unauthorized routers from joining the OSPF domain.
        All production OSPF interfaces should have authentication configured."
        
        Returns violations for routers without authentication.
        """
        violations = []
        
        routers_without_auth = []
        for router in self.routers:
            if not router.get('authentication', {}).get('enabled', False):
                routers_without_auth.append(router['id'])
        
        if routers_without_auth:
            violations.append({
                "rule": "OSPF Authentication",
                "severity": "HIGH",
                "citation": "Nokia SR-OS Security Guide (Public Documentation)",
                "issue": f"Routers {', '.join(routers_without_auth)} do not have OSPF authentication enabled. This allows unauthorized routers to join the OSPF domain.",
                "fix": "Enable OSPF authentication on all interfaces. Use MD5 or SHA-256 authentication keys.",
                "impact": "Security risk: Unauthorized router injection possible"
            })
        
        return violations
    
    def validate_interface_security(self) -> List[Dict]:
        """
        Rule: OSPF should not run on untrusted interfaces
        
        Source: Nokia Security Best Practices (Public Forum, 2023)
        "OSPF should only be enabled on trusted, internal interfaces. External-facing
        interfaces should use BGP or static routes with proper filtering."
        
        Returns violations for potentially insecure interface configurations.
        """
        violations = []
        
        # Check for OSPF on external interfaces (simplified check)
        for router in self.routers:
            external_interfaces = router.get('external_interfaces', [])
            ospf_on_external = [
                iface for iface in external_interfaces
                if any(link.get('from') == router['id'] or link.get('to') == router['id']
                      for link in self.links)
            ]
            
            if ospf_on_external:
                violations.append({
                    "rule": "Interface Security",
                    "severity": "MEDIUM",
                    "citation": "Nokia Security Best Practices (Public Forum, 2023)",
                    "issue": f"Router {router['id']} has OSPF enabled on potentially external interfaces: {', '.join(ospf_on_external)}. This exposes OSPF to untrusted networks.",
                    "fix": f"Disable OSPF on external interfaces for router {router['id']}. Use BGP or static routes with proper filtering instead.",
                    "impact": "Security risk: OSPF domain exposure to external networks"
                })
        
        return violations
    
    def validate_route_filtering(self) -> List[Dict]:
        """
        Rule: Route filtering should be implemented at area boundaries
        
        Source: Nokia SR-OS Design Guide (Public Documentation)
        "Route filtering at ABR prevents unwanted routes from propagating between areas.
        This improves security and reduces LSDB size."
        
        Returns violations for ABRs without route filtering.
        """
        violations = []
        
        # Find ABRs
        abrs = [r for r in self.routers if len(r.get('areas', [])) > 1]
        
        abrs_without_filtering = []
        for abr in abrs:
            if not abr.get('route_filtering', {}).get('enabled', False):
                abrs_without_filtering.append(abr['id'])
        
        if abrs_without_filtering:
            violations.append({
                "rule": "Route Filtering at ABR",
                "severity": "MEDIUM",
                "citation": "Nokia SR-OS Design Guide (Public Documentation)",
                "issue": f"ABRs {', '.join(abrs_without_filtering)} do not have route filtering configured. All routes will propagate between areas.",
                "fix": "Configure route filtering policies at ABRs to control route propagation between areas.",
                "impact": "Security and scalability: Uncontrolled route propagation"
            })
        
        return violations

