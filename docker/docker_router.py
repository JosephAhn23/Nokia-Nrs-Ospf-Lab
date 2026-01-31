# -*- coding: utf-8 -*-
"""
Docker Router - OSPF router running in container
"""
import os
import time
import socket
from ospf_router import OSPFRouter
from ospf_network import OSPFNetwork


def get_container_ip():
    """Get container's IP address"""
    hostname = socket.gethostname()
    try:
        ip = socket.gethostbyname(hostname)
        return ip
    except:
        return "127.0.0.1"


def main():
    router_id = os.getenv("ROUTER_ID", "1.1.1.1")
    container_name = os.getenv("HOSTNAME", "router1")
    
    print(f"Starting OSPF router {router_id} in container {container_name}")
    
    # Create router
    router = OSPFRouter(router_id)
    
    # Add interface (simplified - in real implementation would use container networking)
    interface_ip = get_container_ip()
    router.add_interface("eth0", interface_ip)
    
    # Start router
    router.start()
    
    # Keep running
    try:
        while True:
            time.sleep(10)
            router.print_status()
    except KeyboardInterrupt:
        router.stop()


if __name__ == "__main__":
    main()

