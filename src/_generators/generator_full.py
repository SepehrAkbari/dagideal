'''
Generates M2 script to compute the defining ideal of a graph-constrained secant variety.

Includes the full set of generators for the ideal, without any simplification or pruning. It is intended for small examples where the number of generators is manageable.
'''

import itertools


class ConstrainedSecantGenerator:

    def __init__(self, shape, rank, constraints=None, field="QQ"):
        self.shape = shape
        self.rank = rank
        self.constraints = set(constraints) if constraints else set()
        self.field = field

    def get_factor_var(self, mode, row, col):
        if (mode, row, col) in self.constraints:
            return "0"
        return f"v_({mode},{row},{col})"

    def get_tensor_var(self, indices):
        idx_str = ",".join(map(str, indices))
        return f"t_({idx_str})"

    def generate_m2_script(self):
        m2_code = f"-- Graph-Constrained Secant Variety Generator\n"
        m2_code += f"-- Tensor Shape: {self.shape}, CP Rank: {self.rank}\n\n"
        
        # non-zero factors (latent components)
        factor_vars = []
        for mode, dim in enumerate(self.shape):
            for row in range(dim):
                for col in range(self.rank):
                    if (mode, row, col) not in self.constraints:
                        factor_vars.append(self.get_factor_var(mode, row, col))
        
        # observable tensor variables
        tensor_vars = []
        ranges = [range(dim) for dim in self.shape]
        for indices in itertools.product(*ranges):
            tensor_vars.append(self.get_tensor_var(indices))

        # polynomial ring
        all_vars = factor_vars + tensor_vars
        m2_code += f"kk = {self.field}\n"
        m2_code += f"R = kk[{', '.join(all_vars)}]\n\n"

        # constrained CP ideal
        m2_code += "I = ideal(\n"
        generators = []
        for indices in itertools.product(*ranges):
            t_var = self.get_tensor_var(indices)
            cp_sum_terms = []
            
            for j in range(self.rank):
                term_factors = []
                for mode, row_idx in enumerate(indices):
                    term_factors.append(self.get_factor_var(mode, row_idx, j))
                
                if "0" not in term_factors:
                    cp_sum_terms.append("*".join(term_factors))
            
            cp_expr = " + ".join(cp_sum_terms) if cp_sum_terms else "0"
            generators.append(f"    {t_var} - ({cp_expr})")
        
        m2_code += ",\n".join(generators)
        m2_code += "\n)\n\n"

        # elimination
        m2_code += f"-- implicit equations by elimination of factor variables\n"
        m2_code += f"factorVars = {{{', '.join(factor_vars)}}}\n"
        m2_code += f"J = eliminate(factorVars, I)\n\n"
        
        m2_code += f"print \"Betti Table of the Generators\"\n"
        m2_code += f"print net betti gens J\n\n"
        
        m2_code += f"-- print \"The Explicit Polynomials\"\n"
        m2_code += f"-- print toString gens J\n"

        return m2_code

    def export(self, filename="compute_secant.m2"):
        script = self.generate_m2_script()
        with open(filename, "w") as f:
            f.write(script)
        print(f"Compiled into {filename}")