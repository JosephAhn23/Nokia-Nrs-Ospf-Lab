# -*- coding: utf-8 -*-
"""
Implementation Verification
Proves the code actually works by running tests
"""
import sys
import traceback


def verify_ospf():
    """Verify OSPF implementation works"""
    print("="*60)
    print("VERIFYING OSPF IMPLEMENTATION")
    print("="*60)
    
    try:
        from ospf_router import OSPFRouter, OSPFState
        from ospf_network import OSPFNetwork
        
        # Test 1: Router creation
        print("\n[TEST 1] Creating OSPF router...")
        router = OSPFRouter("1.1.1.1")
        assert router.router_id == "1.1.1.1", "Router ID mismatch"
        print("  [OK] Router created successfully")
        
        # Test 2: Interface addition
        print("\n[TEST 2] Adding interface...")
        router.add_interface("eth0", "10.1.1.1")
        assert "eth0" in router.interfaces, "Interface not added"
        print("  [OK] Interface added successfully")
        
        # Test 3: Neighbor adjacency
        print("\n[TEST 3] Testing adjacency formation...")
        router.receive_hello("2.2.2.2", "eth0")
        assert "2.2.2.2" in router.neighbors, "Neighbor not added"
        # State goes through INIT -> TWO_WAY -> EXSTART -> EXCHANGE -> FULL
        assert router.neighbors["2.2.2.2"]["state"] in [OSPFState.TWO_WAY, OSPFState.FULL], "State transition failed"
        print("  [OK] Adjacency formation working (state transitions functional)")
        
        # Test 4: Network creation
        print("\n[TEST 4] Creating OSPF network...")
        network = OSPFNetwork()
        r1 = network.add_router("1.1.1.1")
        r2 = network.add_router("2.2.2.2")
        assert len(network.routers) == 2, "Network creation failed"
        print("  [OK] Network created with 2 routers")
        
        # Test 5: Router connection
        print("\n[TEST 5] Connecting routers...")
        network.connect_routers("1.1.1.1", "2.2.2.2", "eth0", "eth0", "10.1.12.1", "10.1.12.2")
        assert "2.2.2.2" in r1.neighbors, "Routers not connected"
        print("  [OK] Routers connected successfully")
        
        print("\n" + "="*60)
        print("OSPF VERIFICATION: PASSED")
        print("="*60)
        return True
        
    except Exception as e:
        print(f"\n[FAILED] OSPF verification failed: {e}")
        traceback.print_exc()
        return False


def verify_isis():
    """Verify ISIS implementation works"""
    print("\n" + "="*60)
    print("VERIFYING ISIS IMPLEMENTATION")
    print("="*60)
    
    try:
        from isis_router import ISISRouter, ISISState, ISISLevel
        from isis_network import ISISNetwork
        
        # Test 1: Router creation
        print("\n[TEST 1] Creating ISIS router...")
        router = ISISRouter("0000.0000.0001", ISISLevel.LEVEL_1)
        assert router.system_id == "0000.0000.0001", "System ID mismatch"
        assert router.level == ISISLevel.LEVEL_1, "Level mismatch"
        print("  [OK] Router created successfully")
        
        # Test 2: Interface addition
        print("\n[TEST 2] Adding interface...")
        router.add_interface("eth0", "10.2.1.1")
        assert "eth0" in router.interfaces, "Interface not added"
        print("  [OK] Interface added successfully")
        
        # Test 3: Neighbor adjacency
        print("\n[TEST 3] Testing adjacency formation...")
        router.receive_hello("0000.0000.0002", "eth0", ISISLevel.LEVEL_1)
        assert "0000.0000.0002" in router.neighbors, "Neighbor not added"
        assert router.neighbors["0000.0000.0002"]["state"] == ISISState.UP, "State transition failed"
        print("  [OK] Adjacency formation working (INIT -> UP)")
        
        # Test 4: Network creation
        print("\n[TEST 4] Creating ISIS network...")
        network = ISISNetwork()
        r1 = network.add_router("0000.0000.0001", ISISLevel.LEVEL_1)
        r2 = network.add_router("0000.0000.0002", ISISLevel.LEVEL_1)
        assert len(network.routers) == 2, "Network creation failed"
        print("  [OK] Network created with 2 routers")
        
        # Test 5: Router connection
        print("\n[TEST 5] Connecting routers...")
        network.connect_routers("0000.0000.0001", "0000.0000.0002", "eth0", "eth0", "10.2.12.1", "10.2.12.2")
        assert "0000.0000.0002" in r1.neighbors, "Routers not connected"
        print("  [OK] Routers connected successfully")
        
        print("\n" + "="*60)
        print("ISIS VERIFICATION: PASSED")
        print("="*60)
        return True
        
    except Exception as e:
        print(f"\n[FAILED] ISIS verification failed: {e}")
        traceback.print_exc()
        return False


def verify_nokia_insights():
    """Verify Nokia insights are present"""
    print("\n" + "="*60)
    print("VERIFYING NOKIA-SPECIFIC INSIGHTS")
    print("="*60)
    
    try:
        from nokia_ospf_insights import NokiaOspfInsights
        
        # Test 1: Hello interval insight
        print("\n[TEST 1] Checking Hello Interval insight...")
        insight1 = NokiaOspfInsights.analyze_hello_interval_optimization()
        assert insight1.nokia_value == "10 seconds", "Hello interval insight missing"
        assert "BFD" in insight1.engineering_rationale, "BFD alignment not explained"
        print("  [OK] Hello Interval insight present (BFD alignment)")
        
        # Test 2: DR Priority insight
        print("\n[TEST 2] Checking DR Priority insight...")
        insight2 = NokiaOspfInsights.analyze_dr_priority_choice()
        assert "128" in insight2.nokia_value, "DR Priority insight missing"
        assert "FPGA" in insight2.hardware_optimization, "FPGA optimization not explained"
        print("  [OK] DR Priority insight present (FPGA optimization)")
        
        # Test 3: CP/MDA Architecture insight
        print("\n[TEST 3] Checking CP/MDA Architecture insight...")
        insight3 = NokiaOspfInsights.analyze_cp_mda_architecture()
        assert "CP/MDA" in insight3.choice, "CP/MDA insight missing"
        assert "DMA" in insight3.hardware_optimization, "DMA buffer explanation missing"
        print("  [OK] CP/MDA Architecture insight present")
        
        print("\n" + "="*60)
        print("NOKIA INSIGHTS VERIFICATION: PASSED")
        print("="*60)
        return True
        
    except Exception as e:
        print(f"\n[FAILED] Nokia insights verification failed: {e}")
        traceback.print_exc()
        return False


def main():
    """Run all verification tests"""
    print("\n" + "="*60)
    print("IMPLEMENTATION VERIFICATION")
    print("="*60)
    print("This script verifies the code actually works")
    print("="*60)
    
    results = []
    
    # Verify OSPF
    results.append(("OSPF", verify_ospf()))
    
    # Verify ISIS
    results.append(("ISIS", verify_isis()))
    
    # Verify Nokia insights
    results.append(("Nokia Insights", verify_nokia_insights()))
    
    # Summary
    print("\n" + "="*60)
    print("VERIFICATION SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "PASSED" if result else "FAILED"
        print(f"  {name}: {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n[PASS] ALL VERIFICATIONS PASSED - Code is functional")
        return 0
    else:
        print(f"\n[FAIL] {total - passed} verification(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())

