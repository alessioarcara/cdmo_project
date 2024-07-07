from z3 import *

def successor(v, u):
    n = len(v)
    clauses = []

    clauses.append(Not(u[0]))
    for i in range(n-1):
        clauses.append(v[i] == u[i+1])
    clauses.append(Not(v[n-1]))

    return And(clauses)

def same_load_constraint(v1, v2):
    assert(len(v1) == len(v2))
    return And([v1[k] == v2[k] for k in range(len(v1))])

def lex_less_equal(v1, v2):
    if len(v1) < len(v2):
        v1 = [False] * (len(v2) - len(v1)) + v1
    elif len(v2) < len(v1):
        v2 = [False] * (len(v1) - len(v2)) + v2
        
    assert len(v1) == len(v2), "Vectors must have the same length"
    
    n = len(v1)
    constraints = []
    
    # Cumulative condition for v1 <= v2 lexicographically
    for i in range(n):
        if i == 0:
            # At the first position, v1[i] must be less than or equal to v2[i]
            constraints.append(Or(Not(v1[i]), v2[i]))
        else:
            # At each subsequent position, all previous bits must be equal,
            # and the current bit must be less than or equal to the corresponding bit in v2
            constraints.append(Implies(And([v1[j] == v2[j] for j in range(i)]), Or(Not(v1[i]), v2[i])))
    
    return And(constraints)