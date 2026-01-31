# -*- coding: utf-8 -*-
"""
Nokia SR-OS CLI Compatibility Layer
Provides SR-OS-like commands for router management
"""
from typing import Dict, List, Optional
from ospf_router import OSPFRouter
from isis_router import ISISRouter


class SR_OS_CLI:
    """Nokia SR-OS CLI command parser and executor"""
    
    def __init__(self):
        self.routers: Dict[str, OSPFRouter] = {}
        self.isis_routers: Dict[str, ISISRouter] = {}
        self.current_context = "root"
    
    def execute(self, command: str) -> str:
        """Execute SR-OS CLI command"""
        cmd_parts = command.strip().split()
        if not cmd_parts:
            return ""
        
        cmd = cmd_parts[0].lower()
        
        # Router configuration
        if cmd == "configure" and len(cmd_parts) > 1:
            return self._handle_configure(cmd_parts[1:])
        
        # Show commands
        elif cmd == "show":
            return self._handle_show(cmd_parts[1:])
        
        # Exit
        elif cmd == "exit":
            return self._handle_exit()
        
        else:
            return f"Unknown command: {command}"
    
    def _handle_configure(self, args: List[str]) -> str:
        """Handle configure commands"""
        if len(args) < 2:
            return "Incomplete command"
        
        if args[0] == "router" and args[1] == "ospf":
            return self._configure_ospf(args[2:])
        elif args[0] == "router" and args[1] == "isis":
            return self._configure_isis(args[2:])
        else:
            return f"Configuration context: {' '.join(args)}"
    
    def _configure_ospf(self, args: List[str]) -> str:
        """Configure OSPF"""
        if len(args) < 2:
            return "OSPF configuration context"
        
        if args[0] == "area" and args[1] == "0.0.0.0":
            if len(args) > 2 and args[2] == "interface":
                interface = args[3] if len(args) > 3 else "eth0"
                return f"OSPF interface {interface} configured in area 0.0.0.0"
        
        return "OSPF configuration applied"
    
    def _configure_isis(self, args: List[str]) -> str:
        """Configure ISIS"""
        if len(args) < 2:
            return "ISIS configuration context"
        
        if args[0] == "interface":
            interface = args[1] if len(args) > 1 else "eth0"
            return f"ISIS interface {interface} configured"
        
        return "ISIS configuration applied"
    
    def _handle_show(self, args: List[str]) -> str:
        """Handle show commands"""
        if not args:
            return "Show command requires arguments"
        
        if args[0] == "router" and len(args) > 1:
            if args[1] == "ospf":
                return self._show_ospf(args[2:])
            elif args[1] == "isis":
                return self._show_isis(args[2:])
        
        return f"Show: {' '.join(args)}"
    
    def _show_ospf(self, args: List[str]) -> str:
        """Show OSPF information"""
        if not args:
            return "OSPF status: Active\nNeighbors: 0"
        
        if args[0] == "neighbor":
            return "OSPF Neighbors:\n  None"
        elif args[0] == "database":
            return "OSPF Link State Database:\n  Empty"
        elif args[0] == "route":
            return "OSPF Routes:\n  None"
        
        return "OSPF information displayed"
    
    def _show_isis(self, args: List[str]) -> str:
        """Show ISIS information"""
        if not args:
            return "ISIS status: Active\nNeighbors: 0"
        
        if args[0] == "neighbor":
            return "ISIS Neighbors:\n  None"
        elif args[0] == "database":
            return "ISIS Link State Database:\n  Empty"
        
        return "ISIS information displayed"
    
    def _handle_exit(self) -> str:
        """Handle exit command"""
        if self.current_context != "root":
            self.current_context = "root"
            return "Exited configuration context"
        return "Exiting CLI"


def main():
    """Interactive SR-OS CLI"""
    cli = SR_OS_CLI()
    
    print("="*60)
    print("Nokia SR-OS CLI Simulator")
    print("="*60)
    print("Type 'exit' to quit")
    print()
    
    while True:
        try:
            command = input("A:router# ")
            if command.lower() in ['exit', 'quit']:
                break
            
            result = cli.execute(command)
            if result:
                print(result)
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except EOFError:
            break


if __name__ == "__main__":
    main()

