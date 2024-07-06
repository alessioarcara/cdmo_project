import sys
from util import (MethodType,
                  print_result,
                  read_instances,
                  expand_matrix,
                  measure_solve_time,
                  extract_integer_from_filename,
                  write_json_file,
                  make_initial_routes)

def print_usage():
    print("Usage: python mcp.py <file_name> <model_type> <model_name> <solver_name> <timeout_seconds> [use_warm_start]")
    print("  <file_name>: Path to the instance file")
    print("  <model_type>: 'cp', 'sat' or 'mip'")
    print("  <model_name>: Name of the model to use")
    print("  <solver_name>: Name of the solver to use")
    print("  <timeout_seconds>: Timeout in seconds")
    print("  [use_warm_start]: Optional. 'true' to use warm start (only applicable for HiGHS solver in MIP)")


def solve_with_cp(file_name, model, solver, timeout_seconds):
    from minizinc import Model, Solver, Instance
    from datetime import timedelta
    m, n, l, s, D = read_instances(file_name)
    model = Model(f'./Models/{model}.mzn')
    solver = Solver.lookup(solver)
    instance = Instance(solver, model)

    instance["m"] = m
    instance["n"] = n
    instance["l"] = l
    instance["s"] = s
    instance["D"] = expand_matrix(D, m)

    print(f"n={n}, m={m}")
    print(f"l={l}")

    result = instance.solve(timeout=timedelta(seconds=timeout_seconds))

    print(result.statistics)
    print(result)

def solve_with_sat(file_name, solver, timeout_seconds, model='swc'):
    from Models.SAT.sat_model import sat_model
    m, n, l, s, D = read_instances(file_name)
    obj, time, sol = sat_model(m, n, s, l, D, symmetry_breaking = False, implied_constraint = True, timeout_duration=timeout_seconds)

    optimal = True if time < timeout_seconds else False

    instance = extract_integer_from_filename(file_name)

    write_json_file(f'{model}_{solver}', obj, time, optimal, sol, f'./res/SAT/{instance}.json')


def solve_with_mip(
        file_name,
        model_name,
        solver_name,
        timeout_seconds,
        use_warm_start=False
        ):
    from amplpy import AMPL, modules
    import os
    modules.activate(os.environ["AMPL_LICENSE"])
    m, n, c, s, D = read_instances(file_name)

    ampl = AMPL()
    ampl.read(f'./Models/MIP/{model_name}.mod')

    ampl.param['n'] = n
    ampl.param['m'] = m
    ampl.param['d'] = {(i + 1, j + 1): D[i][j] for i in range(n + 1) for j in range(n + 1)}
    ampl.param['s'] = {i + 1: s[i] for i in range(n)}
    ampl.param['c'] = {k + 1: c[k] for k in range(m)}

    def solve():
        if use_warm_start:
            greedy_routes = make_initial_routes(n, c, s, D)
            print('=' * 50)
            print("Greedy routes:", greedy_routes)

            x = ampl.getVariable('x')
            y = ampl.getVariable('y')
            u = ampl.getVariable('u')
            maxCourDist = ampl.getVariable('maxCourDist')

            depot = n + 1
            max_route_length = 0
            for k in range(1, m + 1):
                routes = greedy_routes.get(k, [[]])
                route_length = 0
                prev_node = depot
                y[depot, k].setValue(1)

                for route in routes:
                    if not route:
                        continue

                    for i, curr_node in enumerate(route, start=1):
                        y[curr_node, k].setValue(1)
                        x[prev_node, curr_node, k].setValue(1)
                        u[curr_node, k].setValue(i)
                        route_length += D[prev_node - 1][curr_node - 1]
                        prev_node = curr_node
                    x[route[-1], depot, k].setValue(1)  # Return to depot
                    route_length += D[route[-1] - 1][depot - 1]

                max_route_length = max(max_route_length, route_length)
            print("Greedy obj:", max_route_length)
            print('=' * 50)
            maxCourDist.setValue(max_route_length)
        ampl.solve()

    ampl.setOption('solver', solver_name)
    warmstart = 1 if use_warm_start else 0

    if solver_name == 'highs':
        ampl.setOption(f'{solver_name}_options', f'time_limit={timeout_seconds} outlev=1 warmstart={warmstart} tech:threads=1')
    elif solver_name == 'cbc':
        ampl.setOption(f'{solver_name}_options', f'timelimit={timeout_seconds} logLevel=1')
    elif solver_name == 'scip':
        ampl.setOption(f'{solver_name}_options', f'timelimit={timeout_seconds} outlev=1')
    elif solver_name == 'gcg':
        ampl.setOption(f'{solver_name}_options', f'timelimit={timeout_seconds} outlev=1')

    solving_time = measure_solve_time(solve)
    solve_result = ampl.get_value("solve_result")
    obj = ampl.getObjective('MaxCourDist').value()
    optimal = solve_result == "solved"

    x = ampl.getVariable('x').getValues().toDict()
    sol = []
    depot = n + 1

    # Extract solution
    for k in range(1, m + 1):
        route = []
        curr_node = depot

        while True:
            next_node = None
            for j in range(1, depot):
                if (curr_node, j, k) in x and x[(curr_node, j, k)] > 0.5:
                    next_node = j
                    break

            if next_node is None or next_node == depot:
                break

            route.append(next_node)
            curr_node = next_node

        sol.append(route)

    if solve_result in ["infeasible", "unbounded"] or solving_time > 300 or obj == 0.0 or all(len(route) == 0 for route in sol):
        print_result(solving_time, solve_result, obj, sol, False)
        return
    print_result(solving_time, solve_result, obj, sol, True)

    instance = extract_integer_from_filename(file_name)
    key = f'{model_name}_{solver_name}' + ('_WM' if use_warm_start else '')
    write_json_file(key,
                    obj,
                    solving_time,
                    optimal,
                    sol,
                    f'./res/MIP/{instance}.json')


if __name__ == "__main__":
    if len(sys.argv) not in [6, 7]:
        print_usage()
        sys.exit(1)
    try:
        file_name = sys.argv[1]
        model_type = MethodType(sys.argv[2])
        model_name = sys.argv[3]
        solver_name = sys.argv[4]
        timeout_seconds = int(sys.argv[5])
        use_warm_start = sys.argv[6] == 'true' if len(sys.argv) == 7 else False

        if model_type == MethodType.CP:
            solve_with_cp(file_name, model_name, solver_name, timeout_seconds)
        elif model_type = MethodType.SAT:
            solve_with_sat(file_name, solver_name, timeout_seconds)
        elif model_type == MethodType.MIP:
            solve_with_mip(file_name, model_name, solver_name, timeout_seconds,
                           use_warm_start=use_warm_start)
    except Exception as e:
        print(f"An error occurred: {e}")
        print_usage()
        sys.exit(1)
