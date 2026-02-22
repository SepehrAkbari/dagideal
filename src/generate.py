import argparse
import os

from _generators.generator_flattening import ConstrainedSecantGenerator as flattening_generator
from _generators.generator_slicing import ConstrainedSecantGenerator as slicing_generator
from _generators.generator_strassen import ConstrainedSecantGenerator as strassen_generator
from _generators.generator_full import ConstrainedSecantGenerator as full_generator

# Target 1: 3x3x3 Tensor, Rank 3
# Causal Constraint: Node 1 does not directly influence Node 3 via two latent paths.
constraints = [
    (2, 0, 1), # Mode 2, Row 0, Col 1 is zero
    (2, 1, 2)  # Mode 2, Row 1, Col 2 is zero
]

shape = [3, 3, 3]
rank = 3
field="ZZ/32003" 


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Macaulay2 script for constrained secant variety.")
    parser.add_argument("--g", type=str, default="slicing", choices=["full", "slicing", "strassen"])
    args = parser.parse_args()
    
    if args.g == "full":
        gen = full_generator(
            shape=shape, 
            rank=rank, 
            constraints=constraints, 
            field=field
        )
        gen.export("target1_full.m2")
    elif args.g == "slicing":
        gen = slicing_generator(
            shape=shape, 
            rank=rank, 
            constraints=constraints, 
            field=field,
            slice_minor_size=3
        )
        gen.export("target1_slicing.m2")
    elif args.g == "strassen":
        gen = strassen_generator(
            shape=shape, 
            rank=rank, 
            constraints=constraints, 
            field=field
        )
        gen.export("target1_strassen.m2")
    elif args.g == "flattening":
        gen = flattening_generator(
            shape=shape, 
            rank=rank, 
            constraints=constraints, 
            field=field
        )
        gen.export("target1_flattening.m2")
    else:
        print("Invalid generator choice. Use --g with one of: full, slicing, strassen, flattening.")
        os.exit(1)