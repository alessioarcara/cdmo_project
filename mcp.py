import sys
from datetime import timedelta
from util import read_instances, expand_matrix, measure_solve_time, extract_integer_from_filename, write_json_file


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


def solve_with_mip(file_name, solver, timeout_seconds, model='three_index_vehicle_flow'):
    from amplpy import AMPL
    m, n, l, s, D = read_instances(file_name)
    ampl = AMPL()
    ampl.read(f'./Models/{model}.mod')

    ampl.param['n'] = n
    ampl.param['m'] = m
    ampl.param['d'] = {(i + 1, j + 1): D[i][j] for i in range(n + 1) for j in range(n + 1)}
    ampl.param['s'] = {i + 1: s[i] for i in range(n)}
    ampl.param['l'] = {k + 1: l[k] for k in range(m)}

    ampl.setOption('solver', solver)
    if solver_name == 'highs':
        ampl.setOption(f'{solver}_options', f'time_limit={timeout_seconds} outlev=1')
    elif solver_name == 'cbc':
        ampl.setOption(f'{solver}_options', f'timelimit={timeout_seconds} logLevel=1')
    elif solver_name == 'scip':
        ampl.setOption(f'{solver}_options', f'timelimit={timeout_seconds} outlev=1')
    elif solver_name == 'gcg':
        ampl.setOption(f'{solver}_options', f'timelimit={timeout_seconds} outlev=1')

    solving_time = measure_solve_time(ampl.solve)
    obj = round(ampl.getObjective('MaxCourDist').value())
    solve_result = ampl.get_value("solve_result")
    if solve_result == "solved":
        optimal = True
    else:
        optimal = False

    y = ampl.getVariable('y').getValues().toPandas()
    y_df = y.reset_index().pivot(index='index1', columns='index0', values='y.val')

    sol = [
        [idx for idx, val in enumerate(row_data[:-1], start=1) if round(val) == 1]
        for _, row_data in y_df.iterrows()
    ]

    instance = extract_integer_from_filename(file_name)

    print('='*50)
    print(f'time: {solving_time:.2f}')
    print(f'obj: {obj}')
    print(f'sol: {sol}')
    print('='*50)

    write_json_file(f'{model}_{solver}', obj, solving_time, optimal, sol, f'./res/MIP/{instance}.json')


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
