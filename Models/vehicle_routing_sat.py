from z3 import *

def at_least_one_seq(bool_vars):
    return Or(bool_vars)

def at_most_one_seq(bool_vars, name):
    constraints = []
    n = len(bool_vars)
    s = [Bool(f"s_{name}_{i}") for i in range(n - 1)]
    constraints.append(Or(Not(bool_vars[0]), s[0]))
    constraints.append(Or(Not(bool_vars[n-1]), Not(s[n-2])))
    for i in range(1, n - 1):
        constraints.append(Or(Not(bool_vars[i]), s[i]))
        constraints.append(Or(Not(bool_vars[i]), Not(s[i-1])))
        constraints.append(Or(Not(s[i-1]), s[i]))
    return And(constraints)

def exactly_one_seq(bool_vars, name):
    return And(at_least_one_seq(bool_vars), at_most_one_seq(bool_vars, name))

def at_least_k_seq(bool_vars, k, name):
    return at_most_k_seq([Not(var) for var in bool_vars], len(bool_vars)-k, name)

def at_most_k_seq(bool_vars, k, name):
    constraints = []
    n = len(bool_vars)
    s = [[Bool(f"s_{name}_{i}_{j}") for j in range(k)] for i in range(n - 1)]
    constraints.append(Or(Not(bool_vars[0]), s[0][0]))
    constraints += [Not(s[0][j]) for j in range(1, k)]
    for i in range(1, n-1):
        constraints.append(Or(Not(bool_vars[i]), s[i][0]))
        constraints.append(Or(Not(s[i-1][0]), s[i][0]))
        constraints.append(Or(Not(bool_vars[i]), Not(s[i-1][k-1])))
        for j in range(1, k):
            constraints.append(Or(Not(bool_vars[i]), Not(s[i-1][j-1]), s[i][j]))
            constraints.append(Or(Not(s[i-1][j]), s[i][j]))
    constraints.append(Or(Not(bool_vars[n-1]), Not(s[n-2][k-1])))   
    return And(constraints)

def exactly_k_seq(bool_vars, k, name):
    return And(at_most_k_seq(bool_vars, k, name), at_least_k_seq(bool_vars, k, name))

def vehicle_routing_sat(m, n, sj, li, D, timeout = None, symmetry_breaking=True):
    # Decision variables
    x = [[Bool(f"x_{i}_{j}") for j in range(n)] for i in range(m)]  # x[i, j]: courier i delivers item j
    y = [[[Bool(f"y_{i}_{j}_{k}") for k in range(n + 1)] for j in range(n + 1)] for i in range(m)]  # y[i, j, k]: courier i travels from j to k
    u = [[Int(f"u_{i}_{j}") for j in range(n + 1)] for i in range(m)]  # u[i, j]: position of item j in the tour of courier i
    
    sol = Solver()
    if timeout:
        sol.set("timeout", timeout)

    # Constraints
    # 1. Load capacity constraints
    for i in range(m):
        sol.add(Sum([If(x[i][j], sj[j], 0) for j in range(n)]) <= li[i])

    # 2. Each item must be assigned to exactly one courier
    for j in range(n):
        sol.add(exactly_one_seq([x[i][j] for i in range(m)], f"assign_item_{j}"))

    # 3. Route constraints: each courier's tour must start and end at the origin
    for i in range(m):
        # Start at the origin
        sol.add(exactly_one_seq([y[i][n][k] for k in range(n)], f"start_{i}"))
        # End at the origin
        sol.add(exactly_one_seq([y[i][k][n] for k in range(n)], f"end_{i}"))
    
        for j in range(n):
            # If a courier visits an item, it must leave that item
            sol.add(Sum([If(y[i][j][k], 1, 0) for k in range(n + 1)]) == If(x[i][j], 1, 0))
            # If a courier arrives at an item, it must leave from that item
            sol.add(Sum([If(y[i][k][j], 1, 0) for k in range(n + 1)]) == If(x[i][j], 1, 0))

    # 4. Ensure no single-node loops
    for i in range(m):
        for j in range(n + 1):
            sol.add(y[i][j][j] == False)
        
    # 5. Subtour elimination constraints (Miller-Tucker-Zemlin formulation)
    for i in range(m):
        for j in range(1, n + 1):
            sol.add(And(u[i][j] >= 1, u[i][j] <= n))
    
        for j in range(n):
            for k in range(n + 1):
                if j != k:
                    sol.add(Implies(y[i][j][k], u[i][j] + 1 == u[i][k]))
                    
        for k in range(n):
            sol.add(Implies(y[i][n][k], u[i][k] == 1))
    
    # 6. Define the maximum distance traveled by any courier
    max_distance = Int('max_distance')

    distances = [Sum([If(y[i][j][k], D[j][k], 0) for j in range(n + 1) for k in range(n + 1)]) for i in range(m)]
    for i in range(m):
        sol.add(distances[i] <= max_distance)

    # Symmetry breaking
    if (symmetry_breaking):
        pass

    # Binary search for minimizing the maximum distance
    low = 0
    high = sum(max(row) for row in D)  # Initial upper bound
    
    best_solution = None
    best_max_distance = None
    while low <= high:
        mid = (low + high) // 2
        sol.push()
        if timeout:
            sol.set("timeout", timeout)
        sol.add(max_distance <= mid)
        if sol.check() == sat:
            best_solution = sol.model()
            best_max_distance = best_solution.evaluate(max_distance)
            high = mid - 1
        else:
            low = mid + 1
        sol.pop()
        
    if best_solution:
        print("Solution found:")
        routes = []
        for i in range(m):
            items = [j for j in range(n) if is_true(best_solution.evaluate(x[i][j]))]
            distance_traveled = best_solution.evaluate(distances[i])
            print(f"Courier {i + 1} delivers items: {items}")
            print(f"Distance traveled by courier {i + 1}: {distance_traveled}")
            route = []
            for j in range(n + 1):
                for k in range(n + 1):
                    if is_true(best_solution.evaluate(y[i][j][k])):
                        route.append((j, k))
            routes.append(route)
            print(f"Route of courier {i + 1}: {route}")
        return routes
    else:
        return print("No solution found")
