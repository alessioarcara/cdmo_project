import sys
from datetime import timedelta


def read_instances(file_name):
    with open(file_name, 'r') as file:
        lines = file.readlines()
        m = int(lines[0].strip())
        n = int(lines[1].strip())
        l = [int(i) for i in lines[2].strip().split()]
        s = [int(i) for i in lines[3].strip().split()]
        D = []
        for line in lines[4:]:
            D.append([int(i) for i in line.strip().split()])
        return m, n, l, s, D


def expand_matrix(matrix, m):
    import numpy as np
    matrix = np.array(matrix)
    n = matrix.shape[0]

    expanded_matrix = np.zeros((n + 2* m - 1, n + 2*m - 1), dtype=np.int32)
    expanded_matrix[:n, :n] = matrix
    expanded_matrix[n:, :n] = matrix[-1, :]
    expanded_matrix[:n, n:] = matrix[:, -1].reshape(-1, 1)
    print(expanded_matrix)
    return expanded_matrix


def print_usage():
    print("Usage: python mcp.py <file_name> <model_type> <solver_name> <timeout_seconds>")


def solve_with_cp(file_name, solver_name, timeout_seconds):
    from minizinc import Model, Solver, Instance
    m, n, l, s, D = read_instances(file_name)
    model = Model("./Models/cp2.mzn")
    solver = Solver.lookup(solver_name)
    instance = Instance(solver, model)

    instance["m"] = m
    instance["n"] = n
    instance["l"] = l
    instance["s"] = s
    instance["D"] = expand_matrix(D, m)

    print(f"n={n}, m={m}")
    print(f"l={l}")


    result = instance.solve(timeout=timeout_seconds)

    print(result.statistics)
    print(result)
    #print(result["total_distance"])


def solve_with_mip(file_name, solver_name, timeout_seconds):
    from amplpy import AMPL
    m, n, l, s, D = read_instances(file_name)
    ampl = AMPL()
    ampl.read("./Models/mip.mod")

    ampl.param['n'] = n
    ampl.param['m'] = m
    ampl.param['d'] = {(i + 1, j + 1): D[i][j] for i in range(n + 1) for j in range(n + 1)}
    ampl.param['s'] = {i + 1: s[i] for i in range(n)}
    ampl.param['l'] = {k + 1: l[k] for k in range(m)}
    
    ampl.setOption('solver', solver_name)
    ampl.setOption('solver_options', f'time_limit={timeout_seconds}')
    ampl.solve()

    x = ampl.getVariable('x').getValues().toPandas()
    y = ampl.getVariable('y').getValues().toPandas()
    u = ampl.getVariable('u').getValues().toPandas()

    y_df = y.reset_index().pivot(index='index1', columns='index0', values='y.val')
    y_df.index.name = 'K'
    y_df.columns.name = 'V'

    u_df = u.reset_index().pivot(index='index1', columns='index0', values='u.val')
    u_df.index.name = 'K'
    u_df.columns.name = 'V'
    print("\ny:")
    print(y_df)
    print("\nu:")
    print(u_df)

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print_usage()
        sys.exit(1)

    try:
        file_name = sys.argv[1]
        model_type = sys.argv[2]
        solver_name = sys.argv[3]
        timeout_seconds = int(sys.argv[4])

        if model_type == "cp":
            solve_with_cp(file_name, solver_name, timedelta(seconds=timeout_seconds))
        elif model_type == "mip":
            solve_with_mip(file_name, solver_name, timeout_seconds)
        else:
            print(f"Unknown model type: {model_type}")
            print_usage()
            sys.exit(1)

    except Exception as e:
        print(f"An error occurred: {e}")
        print_usage()
        sys.exit(1)
