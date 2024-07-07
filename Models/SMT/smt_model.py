from z3 import *
from .utils import *
from .cardinality_constraints import *
import time

def smt_model(m, n, s, l, D,  implied_constraint = False, search='binary', timeout_duration = None):
    start_time = time.time()

    # Decision variables
    x = [[Bool(f"x_{i}_{j}") for j in range(n)] for i in range(m)]  # x[i, j]: courier i delivers item j
    y = [[[Bool(f"y_{i}_{j}_{k}") for k in range(n + 1)] for j in range(n + 1)] for i in range(m)]  # y[i, j, k]: courier i travels from j to k
    u = [[Int(f"u_{i}_{j}") for j in range(n + 1)] for i in range(m)]  # u[i, j]: position of item j in the tour of courier i

    solver = Solver()

    # Constraints
    # 1. Load capacity constraints
    for i in range(m):
        solver.add(Sum([If(x[i][j], s[j], 0) for j in range(n)]) <= l[i])

    # 2. Each item must be assigned to exactly one courier
    for j in range(n):
        solver.add(exactly_one_seq([x[i][j] for i in range(m)], f"assign_item_{j}"))

    # 3. Route constraints: each courier's tour must start and end at the origin
    for i in range(m):
        # Start at the origin
        solver.add(exactly_one_seq([y[i][n][k] for k in range(n)], f"start_{i}"))
        # End at the origin
        solver.add(exactly_one_seq([y[i][k][n] for k in range(n)], f"end_{i}"))
    
        for j in range(n):
            # If a courier visits an item, it must leave that item
            solver.add(Sum([If(y[i][j][k], 1, 0) for k in range(n + 1)]) == If(x[i][j], 1, 0))
            # If a courier arrives at an item, it must leave from that item
            solver.add(Sum([If(y[i][k][j], 1, 0) for k in range(n + 1)]) == If(x[i][j], 1, 0))

    # 4. Ensure no single-node loops
    for i in range(m):
        for j in range(n + 1):
            solver.add(y[i][j][j] == False)
        
    # 5. Subtour elimination constraints (Miller-Tucker-Zemlin formulation)
    for i in range(m):
        for j in range(1, n + 1):
            solver.add(And(u[i][j] >= 1, u[i][j] <= n))
    
        for j in range(n):
            for k in range(n + 1):
                if j != k:
                    solver.add(Implies(y[i][j][k], u[i][j] + 1 == u[i][k]))
                    
        for k in range(n):
            solver.add(Implies(y[i][n][k], u[i][k] == 1))
    
    # 6. Define the maximum distance traveled by any courier
    max_distance = Int('max_distance')

    distances = [Sum([If(y[i][j][k], D[j][k], 0) for j in range(n + 1) for k in range(n + 1)]) for i in range(m)]
    for i in range(m):
        solver.add(distances[i] <= max_distance)

    encoding_time = time.time()
    timeout = encoding_time + timeout_duration

    low = 0
    high = sum(max(row) for row in D)  # Initial upper bound

    if search == 'linear':
        solver.push()
        solver.set('timeout', millisecs_left(time.time(), timeout))
        while solver.check() == sat:
            best_solution = solver.model()
            best_max_distance = obj_function(best_solution, m, D, y)

            if best_max_distance <= low:
                break

            high = best_max_distance - 1
            solver.pop()
            solver.push()

            for i in range(m):
                solver.add(max_distance <= high)
            
            now = time.time()
            if now >= timeout:
                break
            solver.set('timeout', millisecs_left(now, timeout))

    elif search == 'binary':
        # Binary search for minimizing the maximum distance
        best_solution = None
        best_max_distance = None
        while low <= high:
            mid = (low + high) // 2
            solver.push()
            now = time.time()
            if now >= timeout:
                break
            solver.set('timeout', millisecs_left(now, timeout)) 

            solver.add(max_distance <= mid)
            if solver.check() == sat:
                best_solution = solver.model()
                best_max_distance = obj_function(best_solution, m, D, y)
                high = mid - 1
            else:
                low = mid + 1
            solver.pop()
            
    end_time = time.time()
    if end_time >= timeout:
        solving_time = timeout_duration
    else:
        solving_time = math.floor(end_time - encoding_time)
    
    if best_solution is None:
        ans = "N/A" if solving_time == timeout_duration else "UNSAT"
        return (ans, solving_time, None)
    else:
        routes = []
        for i in range(m):
            arcs = []
            for j in range(n + 1):
                for k in range(n + 1):
                    if is_true(best_solution.evaluate(y[i][j][k])):
                        arcs.append((j + 1, k + 1))

            route = []
            current_node = n + 1
            while arcs:
                for arc in arcs:
                    if arc[0] == current_node:
                        route.append(arc[1])
                        current_node = arc[1]
                        arcs.remove(arc)
                        break

            if route and route[-1] == n + 1:
                route.pop(-1)

            routes.append(route)

        return (best_max_distance, solving_time, routes)
