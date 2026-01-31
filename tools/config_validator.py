# -*- coding: utf-8 -*-
"""
Nokia OSPF Configuration Validator
Validates configuration syntax against Nokia's public best practices
"""
import re
import sys

def validate_ospf_config(config_lines):
    """Validate OSPF configuration against best practices"""
    errors = []
    warnings = []
    
    has_nsr = False
    has_graceful_restart = False
    has_area_0 = False
    
    for i, line in enumerate(config_lines, 1):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        
        # Check for NSR without Graceful Restart
        if 'nsr' in line.lower():
            has_nsr = True
        if 'graceful-restart' in line.lower():
            has_graceful_restart = True
        
        # Check for Area 0.0.0.0
        if 'area 0.0.0.0' in line:
            has_area_0 = True
        
        # Check for NBMA without network-type
        if 'nbma' in line.lower() and 'network-type' not in line.lower():
            if i < len(config_lines):
                next_line = config_lines[i].strip() if i < len(config_lines) else ""
                if 'network-type' not in next_line:
                    warnings.append(f"Line {i}: NBMA interface should specify network-type")
    
    # Validate NSR + Graceful Restart
    if has_nsr and not has_graceful_restart:
        errors.append("NSR configured without Graceful Restart (recommended together)")
    
    # Validate Area 0 exists
    if not has_area_0:
        warnings.append("No Area 0.0.0.0 (backbone) configured")
    
    return errors, warnings

def main():
    if len(sys.argv) < 2:
        print("Usage: python config_validator.py <config_file>")
        sys.exit(1)
    
    config_file = sys.argv[1]
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config_lines = f.readlines()
        
        errors, warnings = validate_ospf_config(config_lines)
        
        if errors:
            print("ERRORS:")
            for error in errors:
                print(f"  - {error}")
        
        if warnings:
            print("\nWARNINGS:")
            for warning in warnings:
                print(f"  - {warning}")
        
        if not errors and not warnings:
            print("Configuration looks good!")
        
    except FileNotFoundError:
        print(f"Error: File '{config_file}' not found")
        sys.exit(1)

if __name__ == "__main__":
    main()

