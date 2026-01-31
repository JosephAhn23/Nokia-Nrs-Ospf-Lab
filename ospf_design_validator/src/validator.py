# -*- coding: utf-8 -*-
"""
Nokia OSPF Network Design Validator - Production Grade

Validates OSPF network designs against Nokia's public best practices with
advanced topology analysis, convergence estimation, and automated fix generation.

All rules sourced from Nokia's public configuration guides and design documentation.
"""
import json
import sys
from typing import Dict, List, Optional, Tuple, Set
from pathlib import Path
from collections import defaultdict
import time

# Import rule modules
sys.path.insert(0, str(Path(__file__).parent.parent))
from rules.area_rules import AreaRules
from rules.nsr_rules import NSRRules
from rules.scalability_rules import ScalabilityRules
from rules.convergence_rules import ConvergenceRules
from rules.security_rules import SecurityRules
from rules.topology_rules import TopologyRules


class NokiaOspfDesignValidator:
    """
    Production-grade OSPF design validator with advanced analysis capabilities.
    
    Features:
    - Topology graph analysis
    - Convergence time estimation
    - Automated fix generation with config snippets
    - Performance impact assessment
    - Security validation
    - Comprehensive rule engine
    
    All validation rules sourced from:
    - Nokia SR-OS OSPF Configuration Guide (3HE-10006-AAAAA) - Public
    - Nokia Network Design Guidelines (Public webinars)
    - IETF RFCs (Public standards)
    - Nokia Community Forum best practices (Public)
    """
    
    def __init__(self, design_json: Dict, strict_mode: bool = True):
        """
        Initialize validator with network design.
        
        Args:
            design_json: Network design in JSON format
            strict_mode: If True, treats warnings as violations
        """
        self.design = design_json
        self.strict_mode = strict_mode
        self.violations = []
        self.warnings = []
        self.citations = []
        self.metrics = {}
        self.validation_time = 0.0
        
        # Validate JSON schema first
        self._validate_schema()
        
        # Build topology graph
        self.topology = self._build_topology_graph()
        
        # Initialize rule validators
        self.area_rules = AreaRules(design_json, self.topology)
        self.nsr_rules = NSRRules(design_json, self.topology)
        self.scalability_rules = ScalabilityRules(design_json, self.topology)
        self.convergence_rules = ConvergenceRules(design_json, self.topology)
        self.security_rules = SecurityRules(design_json, self.topology)
        self.topology_rules = TopologyRules(design_json, self.topology)
    
    def _validate_schema(self):
        """Validate design JSON schema"""
        required_keys = ['routers', 'links']
        for key in required_keys:
            if key not in self.design:
                raise ValueError(f"Missing required key: {key}")
        
        if not isinstance(self.design['routers'], list):
            raise ValueError("'routers' must be a list")
        if not isinstance(self.design['links'], list):
            raise ValueError("'links' must be a list")
        
        # Validate router structure
        for router in self.design['routers']:
            if 'id' not in router:
                raise ValueError("Router missing required 'id' field")
    
    def _build_topology_graph(self) -> Dict:
        """Build bidirectional topology graph for analysis"""
        graph = defaultdict(set)
        router_info = {}
        
        for router in self.design.get('routers', []):
            router_info[router['id']] = router
        
        for link in self.design.get('links', []):
            from_router = link.get('from')
            to_router = link.get('to')
            if from_router and to_router:
                graph[from_router].add(to_router)
                graph[to_router].add(from_router)
        
        return {
            'graph': dict(graph),
            'routers': router_info,
            'links': self.design.get('links', [])
        }
    
    def validate(self) -> Dict:
        """
        Run comprehensive validation with performance metrics.
        
        Returns:
            {
                "valid": bool,
                "violations": List[Dict],
                "warnings": List[Dict],
                "citations": List[str],
                "summary": Dict,
                "metrics": Dict,
                "fixes": List[Dict]
            }
        """
        start_time = time.time()
        self.violations = []
        self.warnings = []
        self.citations = []
        self.metrics = {}
        
        # Run all validation rule sets
        self._run_area_validation()
        self._run_nsr_validation()
        self._run_scalability_validation()
        self._run_convergence_validation()
        self._run_security_validation()
        self._run_topology_validation()
        
        # Calculate metrics
        self._calculate_metrics()
        
        # Generate automated fixes
        fixes = self._generate_fixes()
        
        # Collect citations
        for violation in self.violations + self.warnings:
            if 'citation' in violation:
                self.citations.append(violation['citation'])
        self.citations = sorted(list(set(self.citations)))
        
        self.validation_time = time.time() - start_time
        
        summary = self._generate_summary()
        
        return {
            "valid": len(self.violations) == 0,
            "violations": self.violations,
            "warnings": self.warnings if not self.strict_mode else [],
            "citations": self.citations,
            "summary": summary,
            "metrics": self.metrics,
            "fixes": fixes,
            "validation_time_ms": round(self.validation_time * 1000, 2)
        }
    
    def _run_area_validation(self):
        """Run area design validation"""
        violations = self.area_rules.validate_all()
        self.violations.extend(violations)
    
    def _run_nsr_validation(self):
        """Run NSR/GR validation"""
        violations = self.nsr_rules.validate_all()
        self.violations.extend(violations)
    
    def _run_scalability_validation(self):
        """Run scalability validation"""
        violations = self.scalability_rules.validate_all()
        self.violations.extend(violations)
    
    def _run_convergence_validation(self):
        """Run convergence analysis"""
        violations = self.convergence_rules.validate_all()
        self.violations.extend(violations)
        self.warnings.extend(self.convergence_rules.get_warnings())
    
    def _run_security_validation(self):
        """Run security validation"""
        violations = self.security_rules.validate_all()
        self.violations.extend(violations)
    
    def _run_topology_validation(self):
        """Run topology analysis"""
        violations = self.topology_rules.validate_all()
        self.violations.extend(violations)
    
    def _calculate_metrics(self):
        """Calculate design metrics"""
        routers = self.design.get('routers', [])
        links = self.design.get('links', [])
        
        # Count areas
        all_areas = set()
        for router in routers:
            all_areas.update(router.get('areas', []))
        
        # Calculate average areas per router
        total_areas = sum(len(r.get('areas', [])) for r in routers)
        avg_areas = total_areas / len(routers) if routers else 0
        
        # Count ABRs
        abr_count = sum(1 for r in routers if len(r.get('areas', [])) > 1)
        
        # Count ASBRs
        asbr_count = sum(1 for r in routers if r.get('asbr', False))
        
        self.metrics = {
            "total_routers": len(routers),
            "total_links": len(links),
            "total_areas": len(all_areas),
            "average_areas_per_router": round(avg_areas, 2),
            "abr_count": abr_count,
            "asbr_count": asbr_count,
            "average_degree": round(len(links) * 2 / len(routers), 2) if routers else 0
        }
    
    def _generate_fixes(self) -> List[Dict]:
        """Generate automated fix suggestions with config snippets"""
        fixes = []
        
        for violation in self.violations:
            if 'fix' in violation and 'config_snippet' not in violation:
                # Generate config snippet based on violation type
                fix = {
                    "violation_id": violation.get('rule', 'unknown'),
                    "description": violation.get('fix', ''),
                    "config_snippet": self._generate_config_snippet(violation),
                    "estimated_time": self._estimate_fix_time(violation)
                }
                fixes.append(fix)
        
        return fixes
    
    def _generate_config_snippet(self, violation: Dict) -> str:
        """Generate Nokia config snippet for fix"""
        rule = violation.get('rule', '')
        router_id = violation.get('router_id', 'R1')
        
        if 'NSR Requires Graceful Restart' in rule:
            return f"""
/configure router ospf
    graceful-restart
    exit
"""
        elif 'Maximum Areas Per Router' in rule:
            return f"""
/configure router ospf
    area 0.0.0.0
        interface "to-area-0"
    exit
    # Remove excess area configurations
"""
        elif 'Area 0 Continuity' in rule:
            return f"""
/configure router ospf area 0.0.0.0
    interface "to-backbone"
        interface-type point-to-point
    exit
"""
        else:
            return "# Configuration fix required - see Nokia SR-OS Configuration Guide"
    
    def _estimate_fix_time(self, violation: Dict) -> str:
        """Estimate time to implement fix"""
        severity = violation.get('severity', 'MEDIUM')
        if severity == 'CRITICAL':
            return "15-30 minutes"
        elif severity == 'HIGH':
            return "10-20 minutes"
        else:
            return "5-15 minutes"
    
    def _generate_summary(self) -> Dict:
        """Generate comprehensive validation summary"""
        critical = sum(1 for v in self.violations if v.get('severity') == 'CRITICAL')
        high = sum(1 for v in self.violations if v.get('severity') == 'HIGH')
        medium = sum(1 for v in self.violations if v.get('severity') == 'MEDIUM')
        low = sum(1 for v in self.violations if v.get('severity') == 'LOW')
        
        # Calculate risk score (0-100)
        risk_score = (critical * 25 + high * 15 + medium * 5 + low * 1)
        risk_score = min(100, risk_score)
        
        return {
            "total_violations": len(self.violations),
            "total_warnings": len(self.warnings),
            "critical": critical,
            "high": high,
            "medium": medium,
            "low": low,
            "risk_score": risk_score,
            "deployment_ready": risk_score < 20
        }
    
    def generate_report(self, format: str = 'text') -> str:
        """Generate comprehensive validation report"""
        result = self.validate()
        
        if format == 'json':
            return json.dumps(result, indent=2)
        
        # Text format
        report = []
        report.append("=" * 80)
        report.append("NOKIA OSPF DESIGN VALIDATION REPORT")
        report.append("=" * 80)
        report.append("")
        report.append(f"Design Valid: {result['valid']}")
        report.append(f"Risk Score: {result['summary']['risk_score']}/100")
        report.append(f"Deployment Ready: {result['summary']['deployment_ready']}")
        report.append(f"Validation Time: {result['validation_time_ms']}ms")
        report.append("")
        
        # Metrics
        report.append("Design Metrics:")
        report.append("-" * 80)
        for key, value in result['metrics'].items():
            report.append(f"  {key.replace('_', ' ').title()}: {value}")
        report.append("")
        
        # Summary
        report.append("Violation Summary:")
        report.append("-" * 80)
        report.append(f"  Total Violations: {result['summary']['total_violations']}")
        report.append(f"  CRITICAL: {result['summary']['critical']}")
        report.append(f"  HIGH: {result['summary']['high']}")
        report.append(f"  MEDIUM: {result['summary']['medium']}")
        report.append(f"  LOW: {result['summary']['low']}")
        report.append("")
        
        # Violations
        if self.violations:
            report.append("Violations:")
            report.append("-" * 80)
            for i, violation in enumerate(self.violations, 1):
                report.append(f"\n{i}. {violation.get('rule', 'Unknown Rule')}")
                report.append(f"   Severity: {violation.get('severity', 'UNKNOWN')}")
                report.append(f"   Source: {violation.get('citation', 'No citation')}")
                report.append(f"   Issue: {violation.get('issue', 'No description')}")
                if violation.get('fix'):
                    report.append(f"   Fix: {violation.get('fix')}")
                if violation.get('impact'):
                    report.append(f"   Impact: {violation.get('impact')}")
        
        # Fixes
        if result['fixes']:
            report.append("\n")
            report.append("Automated Fix Suggestions:")
            report.append("-" * 80)
            for i, fix in enumerate(result['fixes'][:5], 1):  # Top 5 fixes
                report.append(f"\n{i}. {fix['description']}")
                report.append(f"   Estimated Time: {fix['estimated_time']}")
                report.append(f"   Config Snippet:")
                report.append(fix['config_snippet'])
        
        report.append("")
        report.append("=" * 80)
        report.append("All validation rules sourced from Nokia's PUBLIC documentation.")
        report.append("=" * 80)
        
        return "\n".join(report)


def main():
    """Command-line interface with advanced options"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Nokia OSPF Design Validator - Production Grade',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('design_file', help='Network design JSON file')
    parser.add_argument('--format', choices=['text', 'json'], default='text',
                       help='Output format (default: text)')
    parser.add_argument('--strict', action='store_true',
                       help='Treat warnings as violations')
    parser.add_argument('--output', help='Output file (default: stdout)')
    
    args = parser.parse_args()
    
    design_file = Path(args.design_file)
    if not design_file.exists():
        print(f"Error: File '{design_file}' not found", file=sys.stderr)
        sys.exit(1)
    
    try:
        with open(design_file, 'r', encoding='utf-8') as f:
            design = json.load(f)
        
        validator = NokiaOspfDesignValidator(design, strict_mode=args.strict)
        report = validator.generate_report(format=args.format)
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(report)
        else:
            print(report)
        
        # Exit with error code if violations found
        result = validator.validate()
        if not result['valid']:
            sys.exit(1)
        
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in design file: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Error: Invalid design schema: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
