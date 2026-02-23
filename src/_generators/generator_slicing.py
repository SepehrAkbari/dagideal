'''
Generates M2 script to compute the defining ideal of a graph-constrained secant variety.

Extracts all possible 2D matrix slices from an N-way tensor by fixing N-2 modes, and injects their minors into the ideal.
'''

import itertools


class ConstrainedSecantGenerator:

    def __init__(self, shape, rank, constraints=None, field="QQ", slice_minor_size=3):
        self.shape = shape
        self.rank = rank
        self.constraints = set(constraints) if constraints else set()
        self.field = field
        self.slice_minor_size = slice_minor_size

    def get_factor_var(self, mode, row, col):
        if (mode, row, col) in self.constraints:
            return "0"
        return f"v_({mode},{row},{col})"

    def get_tensor_var(self, indices):
        idx_str = ",".join(map(str, indices))
        return f"t_({idx_str})"

    def _generate_slice_minors(self):
        m2_code = "-- Constructing all 2D Slices for an N-way tensor\n"
        slice_matrices = []
        N = len(self.shape)
        
        for mode_row, mode_col in itertools.combinations(range(N), 2):
            fixed_modes = [m for m in range(N) if m not in (mode_row, mode_col)]
            fixed_ranges = [range(self.shape[m]) for m in fixed_modes]
            
            for fixed_indices in itertools.product(*fixed_ranges):
                rows = []
                for i in range(self.shape[mode_row]):
                    col_vars = []
                    for j in range(self.shape[mode_col]):
                        full_idx = [0] * N
                        full_idx[mode_row] = i
                        full_idx[mode_col] = j
                        for m_idx, fixed_val in zip(fixed_modes, fixed_indices):
                            full_idx[m_idx] = fixed_val
                        
                        col_vars.append(self.get_tensor_var(full_idx))
                    rows.append("{" + ", ".join(col_vars) + "}")
                
                fixed_str = "_".join(map(str, fixed_indices)) if fixed_indices else "all"
                mat_name = f"S_{mode_row}_{mode_col}_fixed_{fixed_str}"
                m2_code += f"{mat_name} = matrix{{\n    " + ",\n    ".join(rows) + "\n}\n"
                slice_matrices.append(mat_name)

        m2_code += f"\n{self.slice_minor_size}x{self.slice_minor_size} minors of all 2D slices\n"
        det_terms = [f"minors({self.slice_minor_size}, {name})" for name in slice_matrices]
        m2_code += f"sliceIdeal = {' + '.join(det_terms)}\n\n"
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

        m2_code += self._generate_slice_minors()

        m2_code += f"-- Implicit equations by elimination\n"
        m2_code += f"factorVars = {{{', '.join(factor_vars)}}}\n"
        m2_code += f"J = eliminate(factorVars, I_cp + sliceIdeal)\n\n"
        m2_code += f"print \"--- Betti Table of the Generators ---\"\n"
        m2_code += f"print net betti gens J\n\n"
        return m2_code

    def export(self, filename="compute_secant.m2"):
        with open(filename, "w") as f:
            f.write(self.generate_m2_script())
        print(f"Compiled into {filename}")