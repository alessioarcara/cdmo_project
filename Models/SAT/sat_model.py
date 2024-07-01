from z3 import *
from .utils import *
from .my_encodings import *
import time

def sat_model(m, n, s, l, D, timeout = None):
    # n: number of items
    # m: number of couriers
    # l: load capacities of couriers
    # s: sizes of items
    # D: distance matrix between points (including the origin)

    start_time = time.time()

    y = [[Bool(f"y_{i}_{k}") for k in range(m)] for i in range(n)]  # y[i, k]: courier k delivers item i
    x = [[[Bool(f"x_{i}_{j}_{k}") for k in range(m)] for j in range(n + 1)] for i in range(n + 1)]  # x[i, j, k]: courier k travels from i to j
    u = [[Bool(f"u_{i}_{j}") for j in range(n)] for i in range(n)]  # u[i, k]: position of item i in the tour of courier k
    
    solver = Solver()    

    # Constraints
    # 1. Each item must be assigned to exactly one courier
    for i in range(n):
        solver.add(exactly_one([y[i][k] for k in range(m)], f"assign_item_{i}"))

    # 2. Load capacity constraints
    for k in range(m):
        solver.add(Pb_seq_counter([y[i][k] for i in range(n)],  s, l[k],  f"load_{k}"))

    # 3. Route constraints: each courier's tour must start and end at the origin
    for k in range(m):
        # Start at the origin
        solver.add(exactly_one([x[n][j][k] for j in range(n+1)], f"start_{k}"))
        # End at the origin
        solver.add(exactly_one([x[i][n][k] for i in range(n+1)], f"end_{k}"))

        for i in range(n):
            # If a courier visits an item, it must leave that item
            solver.add(Implies(y[i][k], exactly_one([x[i][j][k] for j in range(n + 1)], f"visit_{k}_{i}")))
            # If a courier arrives at an item, it must leave from that item
            solver.add(Implies(y[i][k], exactly_one([x[j][i][k] for j in range(n + 1)], f"arrive_{k}_{i}")))

            # If y[i][j] is false, all x[i][j][k] are false
            solver.add(And([Or(y[i][k], Not(x[i][j][k])) for j in range(n + 1)]))
            solver.add(And([Or(y[i][k], Not(x[j][i][k])) for j in range(n + 1)]))

    # 4. Ensure no single-node loops
    for k in range(m):
        for i in range(n):
            solver.add(Not(x[i][i][k]))

    # 5. Subtour elimination constraints
    for i in range(n):
        solver.add(exactly_one(u[i], f"position{i}"))

    for k in range(m):
        for i in range(n):
            for j in range(n):
                solver.add(Implies(x[i][j][k], successive(u[i], u[j])))
            solver.add(Implies(x[n][j][k], u[j][0]))

    # 6. Define the distance traveled by any courier
    flatten_x = [[] for _ in range(m)]
    flatten_D = [D[i][j] for i in range(n + 1) for j in range(n + 1) if D[i][j] != 0]

    for k in range(m):
        for i in range(n + 1):
            for j in range(n + 1):
                if i != j:
                    flatten_x[k].append(x[i][j][k])
    
    encoding_time = time.time()
    print(f"Encoding finished at time {round(encoding_time - start_time, 1)}s, now start solving/optimization search")

    # Binary search for minimizing the maximum distance
    low = 0
    high = sum(max(row) for row in D)  # Initial upper bound

    best_solution = None
    best_max_distance = None

    while low <= high:
        mid = (low + high) // 2

        # Add the current distance constraint
        distance_constraints = []
        for k in range(m):
            distance_constraints.extend(Pb_seq_counter(flatten_x[k], flatten_D, mid, f"distance_{k}"))
        
        solver.push()
        solver.add(And(distance_constraints))

        if solver.check() == sat:
            best_solution = solver.model()
            best_max_distance = mid
            high = mid - 1
        else:
            low = mid + 1
        
        solver.pop()
    
    if best_solution:
        routes = []
        print(best_max_distance)
        for k in range(m):
            items = [i for i in range(n) if is_true(best_solution.evaluate(y[i][k]))]
            print(f"Courier {k + 1} delivers items: {items}")
            route = []
            for i in range(n + 1):
                for j in range(n + 1):
                    if is_true(best_solution.evaluate(x[i][j][k])):
                        route.append((i, j))
            routes.append(route)
            print(f"Route of courier {k + 1}: {route}")
        return routes
    else:
        return print('unsat')
    