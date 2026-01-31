# -*- coding: utf-8 -*-
"""
Generate Demo Output
Creates a text file showing OSPF/ISIS convergence in action
"""
import sys
import io
from contextlib import redirect_stdout
from demo import main as ospf_demo
from isis_demo import main as isis_demo
from combined_demo import main as combined_demo


def generate_demo_output():
    """Generate demo output files"""
    
    # OSPF Demo Output
    print("Generating OSPF demo output...")
    output_buffer = io.StringIO()
    with redirect_stdout(output_buffer):
        try:
            ospf_demo()
        except:
            pass
    ospf_output = output_buffer.getvalue()
    
    with open("demo_output_ospf.txt", "w", encoding="utf-8") as f:
        f.write("="*70 + "\n")
        f.write("OSPF DEMONSTRATION - Adjacency Formation & Convergence\n")
        f.write("="*70 + "\n\n")
        f.write(ospf_output)
    
    # ISIS Demo Output
    print("Generating ISIS demo output...")
    output_buffer = io.StringIO()
    with redirect_stdout(output_buffer):
        try:
            isis_demo()
        except:
            pass
    isis_output = output_buffer.getvalue()
    
    with open("demo_output_isis.txt", "w", encoding="utf-8") as f:
        f.write("="*70 + "\n")
        f.write("ISIS DEMONSTRATION - Adjacency Formation & Convergence\n")
        f.write("="*70 + "\n\n")
        f.write(isis_output)
    
    # Combined Demo Output
    print("Generating combined OSPF/ISIS demo output...")
    output_buffer = io.StringIO()
    with redirect_stdout(output_buffer):
        try:
            combined_demo()
        except:
            pass
    combined_output = output_buffer.getvalue()
    
    with open("demo_output_combined.txt", "w", encoding="utf-8") as f:
        f.write("="*70 + "\n")
        f.write("OSPF/ISIS COMBINED DEMONSTRATION\n")
        f.write("="*70 + "\n\n")
        f.write(combined_output)
    
    print("\n" + "="*70)
    print("Demo output files generated:")
    print("  - demo_output_ospf.txt")
    print("  - demo_output_isis.txt")
    print("  - demo_output_combined.txt")
    print("="*70)


if __name__ == "__main__":
    generate_demo_output()

