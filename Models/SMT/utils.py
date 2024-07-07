from z3 import *

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