import sys
import minizinc
from minizinc import Model, Solver, Instance
from datetime import timedelta

def read_instances(file_name):
    with open(file_name, 'r') as file:
        lines = file.readlines()
        m = int(lines[0].strip())
        n = int(lines[1].strip())
        l = [int(i) for i in lines[2].strip().split()]
        s = [int(i) for i in lines[3].strip().split()]
        D = []
        for line in lines[4:]:
            D.append([int(i) for i in line.strip().split()])
        return m, n, l, s, D



if __name__ == "__main__":
    # TODO: aggiungere print istruzioni python script
    file_name = sys.argv[1]
    solver_name = sys.argv[2]
    seconds = timedelta(seconds=int(sys.argv[3]))
    m, n, l, s, D = read_instances(file_name)
    print(f"n={n}")
    model = Model("./model.mzn")
    solver = Solver.lookup(solver_name)
    #solver.stdFlags = ["-t"]
    instance = Instance(solver, model)

    instance["m"] = m
    instance["n"] = n
    instance["l"] = l
    instance["s"] = s
    instance["D"] = D
    result = instance.solve(timeout=seconds)
    print(result["X"])
    print(result["total_distance"])
