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
    m, n, c, s, D = read_instances(file_name)
    ampl = AMPL()
    ampl.read(f'./Models/MIP/{model}.mod')

    ampl.param['n'] = n
    ampl.param['m'] = m
    ampl.param['d'] = {(i + 1, j + 1): D[i][j] for i in range(n + 1) for j in range(n + 1)}
    ampl.param['s'] = {i + 1: s[i] for i in range(n)}
    ampl.param['c'] = {k + 1: c[k] for k in range(m)}

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
    solve_result = ampl.get_value("solve_result")
    if solve_result == "solved":
        optimal = True
    else:
        optimal = False

    obj = round(ampl.getObjective('MaxCourDist').value())
    x = ampl.getVariable('x').getValues().toDict()
    sol = []
    depot = n+1
    
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

    instance = extract_integer_from_filename(file_name)

    print('='*50)
    print(f'time: {solving_time:.2f}')
    print(f'obj: {obj}')
    print(f'sol: {sol}')
    print('='*50)

    write_json_file(f'{model}_{solver}', obj, solving_time, optimal, sol, f'./res/MIP/{instance}.json')


def calculate_route_cost(route, n, D):
    cost = 0
    depot = n + 1
    curr_node = depot
    for next_node in route:
        cost += D[curr_node - 1][next_node - 1]
        curr_node = next_node
    cost += D[curr_node - 1][depot - 1]
    return cost

def make_initial_routes(n, capacities, s, D):
    routes = {}
    costs = {}
    covers = {}
    depot = n + 1
    nodes = set(range(1, n + 1))
    
    for k, capacity in enumerate(capacities, start=1):
        route = []
        curr_node = depot
        curr_w = 0

        while nodes:
            next_node = max((node for node in nodes if curr_w + s[node - 1] <= capacity), key=lambda x: s[x - 1], default=None)
            if next_node is None:
                break
                
            route.append(next_node)
            nodes.remove(next_node)
            curr_w += s[next_node - 1]
            curr_node = next_node
        routes[k] = [route]
        costs[(k, len(routes[k]))] = calculate_route_cost(route, n, D)
        covers.update({(k, i, 1): 1 if i in route else 0 for i in range(1, n + 1)})

    return routes, costs, covers

def extract_route(x, n):
    depot = n + 1
    route = [depot]
    current = depot
    while True:
        next_node = next(j for j in range(1, depot+1) if x[current,j].value() > 0.5)
        if next_node == depot:
            break
        route.append(next_node)
        current = next_node
    return route[1:]  # Remove depot from start and end

def solve_with_column_generation(file_name, solver):
    from amplpy import AMPL
    m, n, c, s, D = read_instances(file_name)
    ampl_master = AMPL()
    ampl_master.read('./Models/MIP/set_covering.mod')
    ampl_master.param['n'] = n
    ampl_master.param['m'] = m

    initial_routes, initial_costs, initial_covers = make_initial_routes(n, c, s, D)
                                                                        
    route_indices = {}
    for k, route_list in initial_routes.items():
        route_indices[k] = list(range(1, len(route_list) + 1))
        ampl_master.set['R'][k] = route_indices[k]
        
    for (k, r), value in initial_costs.items():
        ampl_master.param['c'][k, r] = value

    for (k, i, r), value in initial_covers.items():
        ampl_master.param['a'][k, i, r] = value

    ampl_master.setOption('solver', solver)

    ampl_pricing = AMPL()
    ampl_pricing.read('./Models/MIP/pricing_problem.mod')
    ampl_pricing.param['n'] = n
    ampl_pricing.param['d'] = {(i + 1, j + 1): D[i][j] for i in range(n + 1) for j in range(n + 1)}
    ampl_pricing.param['s'] = {i + 1: s[i] for i in range(n)}

    ampl_pricing.setOption('solver', solver)

    finding_better_routes = True
    while finding_better_routes:
        ampl_master.solve()
        dual_values = [ampl_master.getConstraint('Visit_Once').get(i).dual() for i in range(1, n + 1)]
        dual_values.append(0)
        print("Dual values:", dual_values)

        ampl_pricing.param['pi'] = {i+1: dual_values[i] for i in range(n + 1)}
        
        finding_better_routes = False
        for k in range(1, m + 1):
            ampl_pricing.param['C'] = c[k - 1]
            ampl_pricing.solve()

            reduced_cost = ampl_pricing.obj['MinReducedCost'].value()

            if reduced_cost < 0:
                finding_better_routes = True
                x = ampl_pricing.var['x']
                new_route = extract_route(x, n)
                initial_routes[k].append(new_route)
                new_route_index = len(route_indices[k]) + 1
                route_indices[k].append(new_route_index)
                new_cost = calculate_route_cost(new_route, n, D)
                print("New route:", new_route)
                ampl_master.set['R'][k] = route_indices[k]
                ampl_master.param['c'][k, new_route_index] = new_cost            
                for i in range(1, n + 1):
                    ampl_master.param['a'][k, i, new_route_index] = 1 if i in new_route else 0

    x = ampl_master.var['x']
    print(x.getValues())
    for k in range(1, m + 1):
        print(k)
        for r in route_indices[k]:
            if x[k,r].value() > 0.5:
                print(x[k,r].value())
                route = initial_routes[k][r -1]
                print(f"Route {route} is used with cost {ampl_master.param['c'][k,r]}.")
            

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
        elif model_type == "mip2":
            solve_with_column_generation(file_name, solver_name)
        else:
            print(f"Unknown model type: {model_type}")
            print_usage()
            sys.exit(1)

    except Exception as e:
        print(f"An error occurred: {e}")
        print_usage()
        sys.exit(1)
