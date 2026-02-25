'''
Test generation.
'''

import os
import subprocess


def gen_test(gen_type, shape, rank, constraints, m2_filename, field="ZZ/32003"):
    m2_filepath = os.path.join("M2", m2_filename)
    os.makedirs(os.path.dirname(m2_filepath), exist_ok=True)
    
    cmd = [
        "python3", os.path.join("generate.py"),
        "--type", gen_type,
        "--field", field,
        "--shape", shape,
        "--rank", str(rank),
        "--constraints", constraints,
        "--out", m2_filename
    ]
    
    subprocess.run(cmd, check=True)
    

if __name__ == "__main__":
    test1_shape = "3,3,3"
    test1_rank = 2
    test1_const = "2,0,0"
    
    test2_shape = "3,3,3"
    test2_rank = 3
    test2_const = "2,0,1;2,1,2"
    
    test3_shape = "4,4,4"
    test3_rank = 3
    test3_const = "2,0,0;2,0,1;2,1,0;2,1,1"
    
    for i, (shape, rank, const) in enumerate([(test1_shape, test1_rank, test1_const), 
                                              (test2_shape, test2_rank, test2_const), 
                                              (test3_shape, test3_rank, test3_const)]):
        for gen in ['flattening', 'full', 'slicing', 'strassen', 'terracini']:
            gen_test(gen, shape, rank, const, f"test{i+1}_{gen}.m2")