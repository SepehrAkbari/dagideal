'''
Generates M2 script to compute the dimension of a graph-constrained secant variety.

Uses Terracini's Lemma to evaluate the Jacobian rank at a random point, providing an exact dimension computation without Gröbner bases.
'''

import itertools


class ConstrainedSecantGenerator:
    
    def __init__(self, shape, rank, constraints=None, field="ZZ/32003"):
        self.shape = shape
        self.rank = rank
        self.constraints = set(constraints) if constraints else set()
        self.field = field

    def get_factor_var(self, mode, row, col):
        if (mode, row, col) in self.constraints:
            return "0"
        return f"v_({mode},{row},{col})"

    def generate_m2_script(self):
        m2_code = f"-- Graph-Constrained Secant Variety\n"
        m2_code += f"-- Tensor Shape: {self.shape}, CP Rank: {self.rank}\n\n"
        
        factor_vars = []
        for mode, dim in enumerate(self.shape):
            for row in range(dim):
                for col in range(self.rank):
                    if (mode, row, col) not in self.constraints:
                        factor_vars.append(self.get_factor_var(mode, row, col))
        
        m2_code += f"kk = {self.field}\n"
        m2_code += f"R = kk[{', '.join(factor_vars)}]\n\n"

        m2_code += "-- The CP Parameterization Map\n"
        ranges = [range(dim) for dim in self.shape]
        
        cp_expressions = []
        for indices in itertools.product(*ranges):
            cp_sum_terms = []
            for j in range(self.rank):
                term_factors = [self.get_factor_var(mode, row_idx, j) for mode, row_idx in enumerate(indices)]
                if "0" not in term_factors:
                    cp_sum_terms.append("*".join(term_factors))
            cp_expr = " + ".join(cp_sum_terms) if cp_sum_terms else "0"
            cp_expressions.append(cp_expr)

        m2_code += f"F = matrix{{{{ {', '.join(cp_expressions)} }}}}\n\n"

        m2_code += "-- Compute the symbolic Jacobian\n"
        m2_code += "J = jacobian F\n\n"

        m2_code += "-- Evaluate the Jacobian at a random numerical point\n"
        m2_code += "randomVals = apply(gens R, v -> v => random kk)\n"
        m2_code += "J_eval = sub(J, randomVals)\n\n"

        num_params = len(factor_vars)
        scaling_redundancies = self.rank * (len(self.shape) - 1)
        expected_dim = num_params - scaling_redundancies

        m2_code += f"print \"--- Geometric Identifiability Report ---\"\n"
        m2_code += f"print \"Total Free Parameters (Vertices): {num_params}\"\n"
        m2_code += f"print \"Scaling Redundancies: {scaling_redundancies}\"\n"
        m2_code += f"print \"Expected Dimension (if identifiable): {expected_dim}\"\n"
        m2_code += f"print \"\"\n"
        m2_code += f"print \"Actual Dimension of Constrained Variety (Jacobian Rank):\"\n"
        m2_code += f"print rank J_eval\n"

        return m2_code

    def export(self, filename="compute_secant.m2"):
        with open(filename, "w") as f:
            f.write(self.generate_m2_script())
        print(f"Compiled into {filename}")