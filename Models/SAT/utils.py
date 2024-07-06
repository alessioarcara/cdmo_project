import matplotlib.pyplot as plt
import networkx as nx
from networkx.drawing.nx_agraph import graphviz_layout
from z3 import *

def toBinary(num, length = None):
    num_bin = bin(num).split("b")[-1]
    if length:
        return "0"*(length - len(num_bin)) + num_bin
    return num_bin

def display_routing(routes, D):
    if routes is None:
        return
    G = nx.DiGraph()
    for route in routes:
        for (j, k) in route:
            if j != k:
                G.add_edge(j, k, len=D[j][k])
    
    # Use spring layout for better visualization
    # pos = nx.spring_layout(G, weight='length', seed=42)
    pos = graphviz_layout(G)
    
    edge_labels = {(j, k): f"{D[j][k]}" for (j, k) in G.edges()}
    
    labels = {i: str(i) for i in range(len(D) - 1)}
    labels[len(D) - 1] = "Depot"
    
    plt.figure(figsize=(10, 7))
    nx.draw(G, pos, with_labels=True, labels=labels, node_size=500, node_color="lightblue", font_size=10, font_weight="bold", arrows=True)
    edge_labels = {(j, k): f"{D[j][k]}" for (j, k) in G.edges()}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red')

    plt.show()

def getDifferentSolution(sol,mod, *params):
  for t in params:
    sol.add(Or([t[i] != mod.eval(t[i]) for i in range(len(t))]))
      
# special case for a matrix; requires number of rows and columns
def getDifferentSolutionMatrix(sol,mod, x, rows, cols):
    sol.add(Or([x[i,j] != mod.eval(x[i,j]) for i in range(rows) for j in range(cols)]))

# ensure that we get a solution with a less value of z
def getLessSolution(sol,mod, z):
    sol.add(z < mod.eval(z))

def millisecs_left(t, timeout):
    return int((timeout - t) * 1000)

def obj_function(model, m, distances, y):
    n = len(distances)
    max_distance = 0
    for i in range(m):
        total_distance = 0
        for j in range(n):
            for k in range(n):
                if is_true(model.evaluate(y[i][j][k])):
                    total_distance += distances[j][k]
        max_distance = max(max_distance, total_distance)
    return max_distance

def output_to_dimacs(solver):
    # Create a goal and add the solver's assertions to it
    goal = Goal()
    goal.add(solver.assertions())

    # Apply tactics to simplify, bit-blast, and convert to CNF
    apply_result = Then(Tactic('simplify'), Tactic('bit-blast'), Tactic('tseitin-cnf')).apply(goal)

    assert len(apply_result) == 1, "Unexpected number of subgoals"
    
    # Create a map from BoolExpr to integer
    var_map = {}
    for f in apply_result[0]:
        assert f.decl().kind() == Z3_OP_OR, "Expected OR clauses"
        for e in f.children():
            if e.decl().kind() == Z3_OP_NOT:
                assert len(e.children()) == 1
                assert e.children()[0].decl().kind() == Z3_OP_UNINTERPRETED
                var_map[e.children()[0]] = 0
            else:
                assert e.decl().kind() == Z3_OP_UNINTERPRETED
                var_map[e] = 0

    # Assign unique IDs to each variable
    id = 1
    for key in list(var_map.keys()):
        var_map[key] = id
        id += 1

    # Write to DIMACS file
    with open('problem.cnf', 'w') as fos:
        fos.write("c DIMACS file format\n")
        fos.write(f"p cnf {len(var_map)} {len(apply_result[0])}\n")
        for f in apply_result[0]:
            for e in f.children():
                if e.decl().kind() == Z3_OP_NOT:
                    fos.write(f"-{var_map[e.children()[0]]} ")
                else:
                    fos.write(f"{var_map[e]} ")
            fos.write("0\n")
