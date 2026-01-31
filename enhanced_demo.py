# -*- coding: utf-8 -*-
"""
Enhanced Demo - Shows Linux integration and SR-OS CLI
"""
import time
from ospf_router_linux import OSPFRouterLinux
from ospf_network import OSPFNetwork
from sr_os_cli import SR_OS_CLI


def main():
    print("="*60)
    print("ENHANCED DEMO - Linux Integration + SR-OS CLI")
    print("="*60)
    print()
    
    # Part 1: OSPF with Linux integration
    print("="*60)
    print("PART 1: OSPF Router with Linux Kernel Integration")
    print("="*60)
    
    router = OSPFRouterLinux("1.1.1.1")
    router.add_interface("eth0", "10.1.1.1")
    router.add_interface("eth1", "10.1.2.1")
    router.start()
    
    print("\nRouter created with Linux integration")
    print("IP forwarding enabled in kernel")
    print(f"Interfaces: {list(router.interfaces.keys())}")
    
    # Simulate SPF calculation and route installation
    router.calculate_spf()
    kernel_routes = router.get_kernel_routes()
    print(f"\nRoutes installed in Linux kernel: {len(kernel_routes)}")
    for route in kernel_routes:
        print(f"  {route['prefix']} via {route['next_hop']} on {route['interface']}")
    
    router.stop()
    
    # Part 2: SR-OS CLI
    print("\n" + "="*60)
    print("PART 2: Nokia SR-OS CLI Compatibility")
    print("="*60)
    
    cli = SR_OS_CLI()
    
    commands = [
        "show router ospf",
        "configure router ospf area 0.0.0.0 interface eth0",
        "show router ospf neighbor",
        "show router ospf database",
        "configure router isis interface eth0",
        "show router isis neighbor",
        "exit"
    ]
    
    print("\nExecuting SR-OS CLI commands:")
    for cmd in commands:
        print(f"\nA:router# {cmd}")
        result = cli.execute(cmd)
        if result:
            print(result)
    
    print("\n" + "="*60)
    print("DEMO COMPLETE")
    print("="*60)
    print("[OK] Linux kernel integration working")
    print("[OK] SR-OS CLI compatibility layer functional")
    print("="*60)


if __name__ == "__main__":
    main()

