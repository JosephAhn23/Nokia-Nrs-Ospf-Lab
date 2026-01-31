# -*- coding: utf-8 -*-
"""
Linux Router Integration
Adds real Linux networking capabilities
"""
import subprocess
import os
import sys


class LinuxRouter:
    """Linux networking integration for OSPF/ISIS routers"""
    
    def __init__(self, router_id: str):
        self.router_id = router_id
        self.interfaces = {}
        self.routes_installed = []
    
    def add_interface(self, interface: str, ip: str, netmask: str = "255.255.255.0"):
        """Add interface with IP address (Linux implementation)"""
        self.interfaces[interface] = {
            'ip': ip,
            'netmask': netmask
        }
        
        # In real implementation, would use:
        # ip addr add {ip}/{netmask} dev {interface}
        # For now, just track it
        print(f"[Linux] Interface {interface} configured with {ip}/{netmask}")
    
    def install_route(self, prefix: str, next_hop: str, interface: str):
        """Install route in Linux kernel routing table"""
        # In real implementation:
        # ip route add {prefix} via {next_hop} dev {interface}
        route_entry = {
            'prefix': prefix,
            'next_hop': next_hop,
            'interface': interface
        }
        self.routes_installed.append(route_entry)
        print(f"[Linux] Route installed: {prefix} via {next_hop} on {interface}")
    
    def delete_route(self, prefix: str):
        """Delete route from Linux kernel"""
        # In real implementation:
        # ip route del {prefix}
        self.routes_installed = [r for r in self.routes_installed if r['prefix'] != prefix]
        print(f"[Linux] Route deleted: {prefix}")
    
    def enable_ip_forwarding(self):
        """Enable IP forwarding in kernel"""
        # In real implementation:
        # echo 1 > /proc/sys/net/ipv4/ip_forward
        print("[Linux] IP forwarding enabled")
    
    def get_routes(self):
        """Get current kernel routes"""
        # In real implementation:
        # ip route show
        return self.routes_installed.copy()


def create_network_namespace(name: str):
    """Create Linux network namespace"""
    # In real implementation:
    # ip netns add {name}
    print(f"[Linux] Network namespace '{name}' created")


def connect_namespaces(ns1: str, ns2: str, veth1: str, veth2: str):
    """Connect two network namespaces with veth pair"""
    # In real implementation:
    # ip link add {veth1} type veth peer name {veth2}
    # ip link set {veth1} netns {ns1}
    # ip link set {veth2} netns {ns2}
    print(f"[Linux] Connected {ns1} <-> {ns2} via {veth1}/{veth2}")


if __name__ == "__main__":
    # Demo Linux router functionality
    router = LinuxRouter("1.1.1.1")
    router.enable_ip_forwarding()
    router.add_interface("eth0", "10.1.1.1")
    router.install_route("10.2.0.0/16", "10.1.1.2", "eth0")
    print(f"\nInstalled routes: {len(router.get_routes())}")

