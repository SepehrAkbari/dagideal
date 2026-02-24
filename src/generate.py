'''
Generates M2 script to compute the defining ideal of a sample graph-constrained secant variety.
'''

import argparse
import os


def parse_constraints(c_str):
    if not c_str:
        return []
    constraints = []
    for item in c_str.split(';'):
        parts = item.split(',')
        if len(parts) == 3:
            constraints.append(tuple(map(int, parts)))
    return constraints


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Compile M2 scripts for constrained secant varieties.")
    parser.add_argument('--type', type=str, required=True, choices=['flattening', 'full', 'slicing', 'strassen', 'terracini'], help="Which algebraic shortcut to use.")
    parser.add_argument('--field', type=str, default="ZZ/32003", help="Base field for computations (default: finite field of size 32003)")
    parser.add_argument('--shape', type=str, required=True, help="Tensor dimensions, e.g., '3,3,3'")
    parser.add_argument('--rank', type=int, required=True, help="CP Rank")
    parser.add_argument('--constraints', type=str, default="", help="Zeroed paths, e.g., '2,0,0;2,1,2'")
    parser.add_argument('--out', type=str, required=True, help="Output filename (saved in src/M2/)")
    
    args = parser.parse_args()
    
    shape = list(map(int, args.shape.split(',')))
    constraints = parse_constraints(args.constraints)
    
    if args.type == 'flattening':
        from _generators.generator_flattening import ConstrainedSecantGenerator
    elif args.type == 'full':
        from _generators.generator_full import ConstrainedSecantGenerator
    elif args.type == 'slicing':
        from _generators.generator_slicing import ConstrainedSecantGenerator
    elif args.type == 'strassen':
        from _generators.generator_strassen import ConstrainedSecantGenerator
    elif args.type == 'terracini':
        from _generators.generator_terracini import ConstrainedSecantGenerator
        
    gen = ConstrainedSecantGenerator(shape=shape, rank=args.rank, constraints=constraints, field=args.field)
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    out_path = os.path.join(base_dir, 'M2', args.out)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    
    gen.export(out_path)