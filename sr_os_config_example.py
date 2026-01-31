# -*- coding: utf-8 -*-
"""
Nokia SR-OS Configuration Examples
Shows actual SR-OS CLI patterns for OSPF/ISIS configuration
"""
from typing import List


class SR_OS_Config:
    """Nokia SR-OS configuration examples for NRS prep"""
    
    @staticmethod
    def ospf_basic_config() -> List[str]:
        """Basic OSPF configuration on SR-OS"""
        return [
            "configure router ospf",
            "    area 0.0.0.0",
            "        interface \"system\"",
            "            interface-type point-to-point",
            "        exit",
            "        interface \"to-router2\"",
            "            interface-type point-to-point",
            "            hello-interval 10",
            "            dead-interval 40",
            "        exit",
            "    exit",
            "exit"
        ]
    
    @staticmethod
    def ospf_with_bfd() -> List[str]:
        """OSPF with BFD integration (Nokia-specific)"""
        return [
            "configure router ospf",
            "    area 0.0.0.0",
            "        interface \"to-router2\"",
            "            bfd-enable",
            "            hello-interval 10",
            "        exit",
            "    exit",
            "exit",
            "configure router bfd",
            "    interface \"to-router2\"",
            "        min-rx-interval 100",
            "        min-tx-interval 100",
            "        multiplier 3",
            "    exit",
            "exit"
        ]
    
    @staticmethod
    def isis_basic_config() -> List[str]:
        """Basic ISIS configuration on SR-OS"""
        return [
            "configure router isis",
            "    interface \"system\"",
            "        interface-type point-to-point",
            "    exit",
            "    interface \"to-router2\"",
            "        interface-type point-to-point",
            "        level-capability level-1",
            "    exit",
            "exit"
        ]
    
    @staticmethod
    def debug_ospf_adjacency() -> List[str]:
        """SR-OS debug commands for OSPF adjacency issues"""
        return [
            "# Show OSPF neighbors",
            "show router ospf neighbor detail",
            "",
            "# Show OSPF interface state",
            "show router ospf interface detail",
            "",
            "# Debug OSPF packets",
            "debug router ospf packet hello",
            "debug router ospf packet db-description",
            "",
            "# Show OSPF database",
            "show router ospf database detail",
            "",
            "# Check for mismatched parameters",
            "show router ospf interface \"to-router2\" detail | match \"Hello|Dead|Area\""
        ]
    
    @staticmethod
    def troubleshoot_adjacency_failure() -> List[str]:
        """Troubleshooting steps for OSPF adjacency failure"""
        return [
            "# Step 1: Check neighbor state",
            "show router ospf neighbor",
            "",
            "# Step 2: Verify interface is up",
            "show router interface",
            "",
            "# Step 3: Check OSPF interface parameters",
            "show router ospf interface detail",
            "",
            "# Step 4: Verify area ID matches",
            "show router ospf interface \"to-router2\" detail | match Area",
            "",
            "# Step 5: Check for authentication mismatch",
            "show router ospf interface \"to-router2\" detail | match Auth",
            "",
            "# Step 6: Enable debug to see packets",
            "debug router ospf packet hello",
            "debug router ospf packet db-description",
            "",
            "# Step 7: Check MTU mismatch",
            "show router interface \"to-router2\" detail | match MTU"
        ]


def print_config(config_name: str, commands: List[str]):
    """Print configuration example"""
    print(f"\n{'='*60}")
    print(f"{config_name}")
    print(f"{'='*60}")
    for line in commands:
        print(line)
    print()


def main():
    """Display SR-OS configuration examples"""
    print("="*60)
    print("Nokia SR-OS Configuration Examples")
    print("For NRS-1/NRS-2 Certification Prep")
    print("="*60)
    
    config = SR_OS_Config()
    
    print_config("Basic OSPF Configuration", config.ospf_basic_config())
    print_config("OSPF with BFD Integration", config.ospf_with_bfd())
    print_config("Basic ISIS Configuration", config.isis_basic_config())
    print_config("Debug OSPF Adjacency", config.debug_ospf_adjacency())
    print_config("Troubleshoot Adjacency Failure", config.troubleshoot_adjacency_failure())
    
    print("="*60)
    print("Note: These are SR-OS CLI patterns for reference.")
    print("Practice on actual SR-OS equipment for NRS certification.")
    print("="*60)


if __name__ == "__main__":
    main()

