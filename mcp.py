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


    result = instance.solve(timeout=timeout_seconds)

    print(result.statistics)
    print(result)
    #print(result["total_distance"])


def solve_with_mip(file_name, solver_name, timeout_seconds):
    import pulp as pl
    m, n, l, s, D = read_instances(file_name)

    prob = pl.LpProblem("mcp", pl.LpMinimize)
    solver = pl.getSolver(solver_name)

    x = pl.LpVariable.dicts("x", (range(n), range(n)), cat='Binary')
    u = pl.LpVariable.dicts("u", (range(n)), cat='Integer',
                            lowBound=0, upBound=n)

    prob += pl.lpSum(D[i][j] * x[i][j] for i in range(n) for j in range(n))

    V = set(range(n))
    A = set((i, j) for i in V for j in V if i != j)


    # 1. Every item is visited once
    for i in V:
        prob += (pl.lpSum(x[i][j] for j in V if i != j) >= 1)

    # 2. Flow conservation
    for i in V:
        prob += (
            pl.lpSum(x[i][j] for j in V if i != j) ==
            pl.lpSum(x[j][i] for j in V if i != j)
        )

    # 3. Every courier leaves the depot at most once
    prob += (pl.lpSum(x[0][j] for j in V - {0}) <= 1)

    # 4. Sub tour elimination
    for k in range(m):
        for i in V - {n-1}:
            for j in V - {n-1}:
                if i != j:
                    prob += (u[j] - u[i] >= s[j] - l[k] * (1 - x[i][j]))

    prob.solve(solver)

    for i in V:
        for j in V:
            if pl.value(x[i][j]) == 1:
                print(f"x[{i}][{j}] = {pl.value(x[i][j])}")


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
