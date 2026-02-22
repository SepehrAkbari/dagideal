'''
Generates M2 script to compute the defining ideal of a graph-constrained secant variety.

This version uses Strassen's Equations (degree-4 invariants) as a computational shortcut.
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

    def _generate_strassen_shortcut(self):
        if self.shape != [3, 3, 3]:
            return "-- Strassen shortcut only applies to 3x3x3 tensors.\nstrassenIdeal = ideal(0)\n\n"

        m2_code = "-- Constructing Slices for Strassen's Equations\n"
        slices = []
        for i in range(3):
            rows = []
            for j in range(3):
                col_vars = [self.get_tensor_var([i, j, k]) for k in range(3)]
                rows.append("{" + ", ".join(col_vars) + "}")
            m2_code += f"X_{i} = matrix{{\n    " + ",\n    ".join(rows) + "\n}\n"
            slices.append(f"X_{i}")

        m2_code += "\n-- Helper function for the 3x3 Adjugate\n"
        m2_code += "adj = M -> matrix {\n"
        m2_code += "    { det submatrix(M,{1,2},{1,2}), -det submatrix(M,{1,2},{0,2}),  det submatrix(M,{1,2},{0,1}) },\n"
        m2_code += "    {-det submatrix(M,{0,2},{1,2}),  det submatrix(M,{0,2},{0,2}), -det submatrix(M,{0,2},{0,1}) },\n"
        m2_code += "    { det submatrix(M,{0,1},{1,2}), -det submatrix(M,{0,1},{0,2}),  det submatrix(M,{0,1},{0,1}) }\n"
        m2_code += "}\n\n"

        m2_code += "-- Computing the Strassen Matrix: X0*adj(X1)*X2 - X2*adj(X1)*X0\n"
        m2_code += "S_matrix = X_0 * adj(X_1) * X_2 - X_2 * adj(X_1) * X_0\n"
        m2_code += "strassenIdeal = ideal flatten entries S_matrix\n\n"
        return m2_code

    def generate_m2_script(self):
        m2_code = f"-- Graph-Constrained Secant Variety\n"
        m2_code += f"-- Tensor Shape: {self.shape}, CP Rank: {self.rank}\n\n"
        
        factor_vars = []
        for mode, dim in enumerate(self.shape):
            for row in range(dim):
                for col in range(self.rank):
                    if (mode, row, col) not in self.constraints:
                        factor_vars.append(self.get_factor_var(mode, row, col))
        
        tensor_vars = []
        ranges = [range(dim) for dim in self.shape]
        for indices in itertools.product(*ranges):
            tensor_vars.append(self.get_tensor_var(indices))

        all_vars = factor_vars + tensor_vars
        m2_code += f"kk = {self.field}\n"
        m2_code += f"R = kk[{', '.join(all_vars)}]\n\n"

        m2_code += "I_cp = ideal(\n"
        generators = []
        for indices in itertools.product(*ranges):
            t_var = self.get_tensor_var(indices)
            cp_sum_terms = []
            for j in range(self.rank):
                term_factors = [self.get_factor_var(mode, row_idx, j) for mode, row_idx in enumerate(indices)]
                if "0" not in term_factors:
                    cp_sum_terms.append("*".join(term_factors))
            cp_expr = " + ".join(cp_sum_terms) if cp_sum_terms else "0"
            generators.append(f"    {t_var} - ({cp_expr})")
        m2_code += ",\n".join(generators) + "\n)\n\n"

        m2_code += self._generate_strassen_shortcut()

        m2_code += f"-- Implicit equations by elimination\n"
        m2_code += f"factorVars = {{{', '.join(factor_vars)}}}\n"
        m2_code += f"J = eliminate(factorVars, I_cp + strassenIdeal)\n\n"
        m2_code += f"print \"Betti Table of the Generators\"\n"
        m2_code += f"print net betti gens J\n\n"
        return m2_code

    def export(self, filename="compute_secant.m2"):
        with open(filename, "w") as f:
            f.write(self.generate_m2_script())
        print(f"Compiled into {filename}")