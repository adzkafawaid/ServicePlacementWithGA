#!/usr/bin/env python3
"""
Script untuk verifikasi constraint user pada solusi terbaik GA
"""

import json
from placementMain import EnvConfig

def verify_user_constraints(chromosome, ec):
    """
    Verifikasi apakah semua user constraints terpenuhi pada kromosom
    """
    print("=== VERIFIKASI USER CONSTRAINTS ===")
    
    all_satisfied = True
    
    # Periksa setiap user constraint
    for (app, mod_dst, node) in ec.user_module_node:
        idx = ec.module2idx.get((app, mod_dst), None)
        if idx is None:
            print(f"❌ GAGAL: Mapping (app={app}, module={mod_dst}) tidak ditemukan dalam module2idx")
            all_satisfied = False
            continue
            
        if node >= len(chromosome[0]):
            print(f"❌ GAGAL: Node {node} di luar range (max: {len(chromosome[0])-1})")
            all_satisfied = False
            continue
            
        if chromosome[idx][node] != 1:
            print(f"❌ GAGAL: Module {mod_dst} (app {app}) TIDAK dialokasikan di node user {node}")
            print(f"    Service idx: {idx}, Node {node}, Value: {chromosome[idx][node]}")
            all_satisfied = False
        else:
            print(f"✅ OK: Module {mod_dst} (app {app}) dialokasikan di node user {node}")
    
    if all_satisfied:
        print("\n🎉 SEMUA USER CONSTRAINTS TERPENUHI!")
    else:
        print("\n❌ ADA USER CONSTRAINTS YANG TIDAK TERPENUHI!")
        
    return all_satisfied

def test_user_constraint_implementation():
    """
    Test langsung apakah implementasi user constraint sudah benar dengan membuat solusi GA
    """
    print("=== TEST IMPLEMENTASI USER CONSTRAINT ===\n")
    
    # Import yang diperlukan
    from solutionGA import SolutionGA
    import numpy
    
    # Inisialisasi environment
    ec = EnvConfig("data/appDefinition.json", "data/networkDefinition.json", "data/usersDefinition.json")
    
    print(f"Total user constraints: {len(ec.user_module_node)}")
    print("Contoh user constraints:")
    for i, (app, mod_dst, node) in enumerate(list(ec.user_module_node)[:5]):  # Show first 5
        idx = ec.module2idx.get((app, mod_dst), None)
        print(f"  {i+1}. App {app}, Module {mod_dst} -> Service idx {idx}, Target node {node}")
    print("  ...")
    
    # Test dengan membuat beberapa solusi GA
    print("\n=== TESTING SOLUTION GENERATION ===")
    
    rng = numpy.random.RandomState(42)
    
    for test_num in range(3):
        print(f"\n--- Test Solution {test_num + 1} ---")
        try:
            # Buat solusi baru
            solution = SolutionGA(rng, ec, {})
            
            # Cek apakah semua user constraint terpenuhi
            constraint_satisfied = True
            violated_constraints = []
            
            for (app, mod_dst, node) in ec.user_module_node:
                idx = ec.module2idx.get((app, mod_dst), None)
                if idx is not None and node < ec.getNumberOfNodes():
                    if solution.chromosome[idx][node] != 1:
                        constraint_satisfied = False
                        violated_constraints.append((app, mod_dst, node, idx))
            
            if constraint_satisfied:
                print("✅ SEMUA USER CONSTRAINTS TERPENUHI!")
            else:
                print(f"❌ {len(violated_constraints)} user constraint DILANGGAR:")
                for app, mod_dst, node, idx in violated_constraints[:3]:  # Show first 3
                    print(f"  - App {app}, Module {mod_dst} (idx {idx}) tidak di node {node}")
                    
        except Exception as e:
            print(f"❌ ERROR: {e}")
    
    # Test fungsi checkConstraints
    print("\n=== TESTING checkConstraints FUNCTION ===")
    
    try:
        solution = SolutionGA(rng, ec, {})
        constraints_ok = solution.checkConstraints()
        print(f"checkConstraints() returned: {constraints_ok}")
        
        if constraints_ok:
            print("✅ checkConstraints PASS - constraint checking is working!")
        else:
            print("❌ checkConstraints FAIL - ada error di constraint checking")
            
    except Exception as e:
        print(f"❌ ERROR in checkConstraints: {e}")

def main():
    """
    Main function - jalankan test implementasi user constraint
    """
    test_user_constraint_implementation()

if __name__ == "__main__":
    main()
