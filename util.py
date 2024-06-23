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

def expand_matrix(matrix, m):
    import numpy as np
    matrix = np.array(matrix)
    n = matrix.shape[0]

    expanded_matrix = np.zeros((n + 2* m - 1, n + 2*m - 1), dtype=np.int32)
    expanded_matrix[:n, :n] = matrix
    expanded_matrix[n:, :n] = matrix[-1, :]
    expanded_matrix[:n, n:] = matrix[:, -1].reshape(-1, 1)
    print(expanded_matrix)
    return expanded_matrix

def measure_solve_time(solve_function):
    import time
    start_time = time.time()
    solve_function()
    end_time = time.time()
    
    solving_time = end_time - start_time
    return solving_time

def extract_integer_from_filename(file_name: str):
    import re
    return int(re.findall(r'\d+', file_name)[0])

def write_json_file(key, obj, time, sol, path):
    import os
    import json
    optimal = time < 300
    
    data = {
        "time": time,
        "optimal": optimal,
        "obj": obj,
        "sol": sol
    }

    print("Data to write:", data)
    if os.path.exists(path):
        try:
            with open(path, 'r') as json_file:
                print("Reading existing JSON file.")
                file_data = json.load(json_file)
                print("Existing file data:", file_data)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON from file: {e}")
            file_data = {}
    else:
        file_data = {}

    file_data[key] = data

    with open(path, 'w') as json_file:
        json.dump(file_data, json_file, indent=4)

    print(f"JSON file successfully written to {path}")