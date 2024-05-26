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


def print_usage():
    print("Usage: python mcp.py <file_name> <model_type> <solver_name> <timeout_seconds>")


def solve_with_cp(file_name, solver_name, timeout_seconds):
    from minizinc import Model, Solver, Instance
    m, n, l, s, D = read_instances(file_name)
    print(f"n={n}")
    model = Model("./Models/cp.mzn")
    solver = Solver.lookup(solver_name)
    instance = Instance(solver, model)

    instance["m"] = m
    instance["n"] = n
    instance["l"] = l
    instance["s"] = s
    instance["D"] = D

    result = instance.solve(timeout=timeout_seconds)

    print(result["X"])
    print(result["total_distance"])


def solve_with_mip(file_name, solver_name, timeout_seconds):
    from amplpy import AMPL
    ampl = AMPL()
    pass


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
