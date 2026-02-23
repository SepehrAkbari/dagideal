'''
Orchestrates test generation and execution.
'''

import os
import subprocess
import time


def run_test(test_name, gen_type, shape, rank, constraints, m2_filename):
    print(f"[{time.strftime('%H:%M:%S')}] --- Starting {test_name} ---")
    
    m2_filepath = os.path.join("src", "M2", m2_filename)
    log_dir = "results"
    log_filepath = os.path.join(log_dir, f"{test_name}.log")
    
    os.makedirs(log_dir, exist_ok=True)
    
    gen_cmd = [
        "python", os.path.join("src", "generate.py"),
        "--type", gen_type,
        "--field", "ZZ/32003",
        "--shape", shape,
        "--rank", str(rank),
        "--constraints", constraints,
        "--out", m2_filename
    ]
    
    print(f"Generating {m2_filepath} using {gen_type} generator...")
    subprocess.run(gen_cmd, check=True)
    
    print(f"Executing M2... (routing to {log_filepath})")
    start_time = time.time()
    
    with open(log_filepath, "w") as log_file:
        m2_cmd = ["M2", "--script", m2_filepath]
        
        process = subprocess.run(m2_cmd, stdout=log_file, stderr=subprocess.STDOUT)
        
    elapsed = time.time() - start_time
    
    if process.returncode == 0:
        print(f"[{time.strftime('%H:%M:%S')}] {test_name} completed in {elapsed:.2f} seconds.\n")
    else:
        print(f"[{time.strftime('%H:%M:%S')}] {test_name} failed with return code {process.returncode}. Check log.\n")


if __name__ == "__main__":
    # Baseline Verification
    # Expected: Finishes very quickly. Betti table shows 9 quadrics.
    run_test("test1_baseline", "flattening", "3,3,3", 2, "2,0,0", "test1_baseline.m2")
    
    # Confounding Triangle
    # Expected: Takes moderate time. Shows how degree-4 bounds deform.
    run_test("test2_triangle", "strassen", "3,3,3", 3, "2,0,1;2,1,2", "test2_triangle.m2")
    
    # Overcomplete DAG
    # Constraint: We force a 2x2 bipartite zero block in the 3rd mode.
    # Expected: Longest runtime. Tests the flattening approach on an overcomplete model.
    run_test("test3_overcomplete", "flattening", "4,4,4", 3, "2,0,0;2,0,1;2,1,0;2,1,1", "test3_overcomplete.m2")
    
    print("Done.")