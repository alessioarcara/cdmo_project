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
    nodes = set(range(1, n + 1))

    for k, capacity in enumerate(capacities, start=1):
        route = []
        curr_w = 0

        while nodes:
            next_node = max((node for node in nodes if curr_w + s[node - 1] <= capacity), key=lambda x: s[x - 1], default=None)
            if next_node is None:
                break

            route.append(next_node)
            nodes.remove(next_node)
            curr_w += s[next_node - 1]

        if route:
            routes[k] = [route]
        else:
            routes[k] = []

        # Add singleton routes for each courier
        for i in range(1, n + 1):
            if [i] not in routes[k]:
                routes[k].append([i])

        # Calculate costs and covers for all routes
        for idx, r in enumerate(routes[k]):
            costs[(k, idx + 1)] = calculate_route_cost(r, n, D)
            covers.update({(k, i, idx + 1): 1 if i in r else 0 for i in range(1, n + 1)})

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
    from minizinc import Model, Solver, Instance
    import copy

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
    ampl_master.setOption('relax_integrality', True)

    # ampl_pricing = AMPL()
    # ampl_pricing.read('./Models/MIP/pricing_problem.mod')
    # ampl_pricing.param['n'] = n
    # ampl_pricing.param['d'] = {(i + 1, j + 1): D[i][j] for i in range(n + 1) for j in range(n + 1)}
    # ampl_pricing.param['s'] = {i + 1: s[i] for i in range(n)}

    # ampl_pricing.setOption('solver', solver)
    # ampl_pricing.setOption(f'{solver}_options', f'time_limit={30}')

    mzn_pricing = Model("./Models/MIP/pricing_problem.mzn")
    mzn_solver = Solver.lookup("gecode")
    mzn_instance = Instance(mzn_solver, mzn_pricing)

    finding_better_routes = True
    while finding_better_routes:
        finding_better_routes = False
        for k in range(1, m + 1):
            ampl_master.solve()
            dual_values = [ampl_master.getConstraint('Visit_Once').get(i).dual() for i in range(1, n + 1)]
            dual_values.append(0)
            dual_values_2 = [ampl_master.getConstraint('K_Couriers_Used').get(k).dual() for k in range(1, m + 1)]

            mzn_instance = Instance(mzn_solver, mzn_pricing)
            s2 = copy.deepcopy(s)
            s2.append(0)
            mzn_instance["n"] = n
            mzn_instance["s"] = s2
            mzn_instance["d"] = D
            mzn_instance["C"] = c[k - 1]
            mzn_instance["pi"] = dual_values
            mzn_instance["sigma"] = dual_values_2[k-1]

            result = mzn_instance.solve()
            print(result)
            reduced_cost = result["objective"]
            print("Reduced cost:", reduced_cost)


            # ampl_pricing.param['pi'] = {i+1: dual_values[i] for i in range(n + 1)}
            # ampl_pricing.param['sigma'] = dual_values_2[k-1]
            # ampl_pricing.param['C'] = c[k - 1]
            # ampl_pricing.solve()

            # reduced_cost = ampl_pricing.obj['MinReducedCost'].value()
            # print("Reduced cost:", reduced_cost)

            if reduced_cost <= -0.001:
                finding_better_routes = True
                new_route = [p for p in result["P"] if p != n+1]
                initial_routes[k].append(new_route)
                new_route_index = len(route_indices[k]) + 1
                route_indices[k].append(new_route_index)
                new_cost = calculate_route_cost(new_route, n, D)
                print(f"Route: {new_route}, Cost: {new_cost}")

                # new_route = []
                # #x = ampl_pricing.var['x']
                # #new_route = extract_route(x, n)
                # initial_routes[k].append(new_route)
                # new_route_index = len(route_indices[k]) + 1
                # route_indices[k].append(new_route_index)
                # new_cost = calculate_route_cost(new_route, n, D)
                # print(f"New route: {new_route} with cost: {new_cost}")
                ampl_master.set['R'][k] = route_indices[k]
                ampl_master.param['c'][k, new_route_index] = new_cost
                for i in range(1, n + 1):
                    ampl_master.param['a'][k, i, new_route_index] = 1 if i in new_route else 0

    ampl_master.setOption('relax_integrality', False)
    ampl_master.solve()
    x = ampl_master.var['x']
    print(x.getValues())
    for k in range(1, m + 1):
        print(k)
        for r in route_indices[k]:

            if x[k, r].value() > 0.5:
                print(x[k, r].value())
                route = initial_routes[k][r - 1]
                print(f"Route {route} is used with cost {ampl_master.param['c'][k, r]}.")

