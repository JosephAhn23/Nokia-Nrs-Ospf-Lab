# -*- coding: utf-8 -*-
"""
OSPF Router with Linux Integration
Combines OSPF protocol with Linux kernel routing
"""
from ospf_router import OSPFRouter
from linux_router import LinuxRouter


class OSPFRouterLinux(OSPFRouter):
    """OSPF router with Linux kernel integration"""
    
    def __init__(self, router_id: str, area_id: str = "0.0.0.0"):
        super().__init__(router_id, area_id)
        self.linux_router = LinuxRouter(router_id)
        self.linux_router.enable_ip_forwarding()
    
    def add_interface(self, interface: str, ip: str, mask: str = "255.255.255.0", cost: int = 10):
        """Add interface with Linux integration"""
        super().add_interface(interface, ip, mask, cost)
        self.linux_router.add_interface(interface, ip, mask)
    
    def _build_routing_table(self, distances, previous):
        """Build routing table and install in Linux kernel"""
        super()._build_routing_table(distances, previous)
        
        # Install routes in Linux kernel
        for prefix, route in self.routing_table.items():
            self.linux_router.install_route(prefix, route.next_hop, route.interface)
    
    def get_kernel_routes(self):
        """Get routes from Linux kernel"""
        return self.linux_router.get_routes()

