from z3 import *
from .utils import *
from .cardinality_constraints import *
from .pseudoboolean_constraints import * 
from .logical_relation_constraints import *
import time

def sat_model(m, n, s, l, D, symmetry_breaking = None, implied_constraint = None, timeout_duration = None):
    # n: number of items
    # m: number of couriers
    # l: load capacities of couriers
    # s: sizes of items
    # D: distance matrix between points (including the origin)

    start_time = time.time()

    x = [[Bool(f"x_{i}_{j}") for j in range(n)] for i in range(m)]  # x[i, j]: courier i delivers item j
    y = [[[Bool(f"y_{i}_{j}_{k}") for k in range(n + 1)] for j in range(n + 1)] for i in range(m)]  # y[i, j, k]: courier i travels from j to k
    seq = [[Bool(f"seq_{i}_{j}") for j in range(n)] for i in range(n)]  # seq[i][j]: item i is in position j in the sequence
    
    solver = Solver()
    
    # Constraints
    # 1. Each item must be assigned to exactly one courier
    for j in range(n):
        solver.add(exactly_one([x[i][j] for i in range(m)], f"assign_item_{j}"))

    # 2. Load capacity constraints for each courier
    for i in range(m):
        # solver.add(Pb_adder_networks([x[i][j] for j in range(n)], s, l[i]))
        solver.add(Pb_seq_counter([x[i][j] for j in range(n)], s, l[i], f"load_courier_{i}"))

    # 3. Route constraints: each courier's route must start and end at the origin
    for i in range(m):
        # Start at the origin
        solver.add(exactly_one([y[i][n][k] for k in range(n)], f"start_{i}"))
        # End at the origin
        solver.add(exactly_one([y[i][k][n] for k in range(n)], f"end_{i}"))

        for j in range(n):
            # If a courier visits an item, it must leave that item
            solver.add(Implies(x[i][j], exactly_one([y[i][j][k] for k in range(n + 1)], f"visit_{i}_{j}")))
            # If a courier arrives at an item, it must leave from that item
            solver.add(Implies(x[i][j], exactly_one([y[i][k][j] for k in range(n + 1)], f"arrive_{i}_{j}")))

            # If y[i][j] is false, all y[i][j][k] must be false
            solver.add(And([Or(x[i][j], Not(y[i][j][k])) for k in range(n + 1)]))
            solver.add(And([Or(x[i][j], Not(y[i][k][j])) for k in range(n + 1)]))

    # 4. Preventing sub-tours within each courier's route
    for i in range(n):
        solver.add(exactly_one(seq[i], f"position_{i}"))

    for i in range(m):
        for j in range(n):
            for k in range(n):
                solver.add(Implies(y[i][j][k], successor(seq[j], seq[k])))
            solver.add(Implies(y[i][n][j], seq[j][0]))

    # Symmetry breaking constraints
    if symmetry_breaking:
        pass
        # Sort the list of loads, keeping the permutation used for later
        # L = [(l[i], i) for i in range(m)]
        # L.sort(reverse=True)
        # l, permutation = zip(*L)
        # l = list(l)
        # permutation = list(permutation)

        # Symmetry breaking constraint: impose the actual courier loads to be sorted decreasingly

        # Break symmetry within same load amounts
        # for i in range(m - 1):
            # solver.add(Implies(And([w[i][k] == w[i+1][k] for k in range(len(w[i]))]), lex_less_equal(x[i], x[i + 1])))

    # Additional implied constraints
    if implied_constraint:
        for i in range(m):
            solver.add(at_least_one(x[i]))

        # Ensure no single-node loops
        for i in range(m):
            for j in range(n):
                solver.add(Not(y[i][j][j]))
        
    # Define the distance traveled by any courier
    flatten_y = [[] for _ in range(m)]
    flatten_D = [D[i][j] for i in range(n + 1) for j in range(n + 1) if D[i][j] != 0]

    for i in range(m):
        for j in range(n + 1):
            for k in range(n + 1):
                if j != k:
                    flatten_y[i].append(y[i][j][k])
    
    encoding_time = time.time()
    timeout = encoding_time + timeout_duration

    # Binary search for minimizing the maximum distance
    low = 0
    high = sum(max(row) for row in D)  # Initial upper bound

    best_solution = None
    best_max_distance = None

    while low <= high:
        mid = (low + high) // 2
        solver.push()

        # Add the current distance constraint
        for i in range(m):
            solver.add(PbLe([(lit, flatten_D[idx]) for idx, lit in enumerate(flatten_y[i])], mid))
            # solver.add(Pb_adder_networks(flatten_y[i], flatten_D, mid))

        now = time.time()
        if now >= timeout:
            break
        solver.set('timeout', millisecs_left(now, timeout)) 

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
