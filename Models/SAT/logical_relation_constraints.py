from z3 import *

def successor(v, u):
    n = len(v)
    clauses = []

    clauses.append(Not(u[0]))
    for i in range(n-1):
        clauses.append(v[i] == u[i+1])
    clauses.append(Not(v[n-1]))

    return And(clauses)
