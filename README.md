# Heterogeneous Min-Max Vehicle Routing Problem

This repository represents the group project for Combinatorial Decision Making
and Optimization 2024/2024, focusing on implementing and evaluating diverse
solving techniques (*CP*, *SAT*, *MIP*) for the **Heterogeneous Min-Max Vehicle
Routing Problem**. The objective is to efficiently plan routes for couriers
with varying capacities to collect all available items while minimizing the
maximum distance traveled by any courier.

![Solution for instance 1](example.png)

## Usage

To reproduce our results, please ensure Docker is installed on your system.
Once Docker is installed, you can solve the different instances by running the
following bash script in your terminal:

```{bash}
$ run_docker.sh <instance_file> <method> <method_name> <solver_name> <time> [use_warm_start]
```

### Parameters

* `<instance_file>`: Path to the instance file.
* `<method>`: Method to use (`cp`, `sat`, `mip`).
* `<model_name>`: Formulation to use (depends on the chosen method):
    - **MIP**: `three_index_vehicle_flow`, `three_index_vehicle_flow_SB`, `three_index_vehicle_flow_SB_IMPLIED`
* `<solver_name>`: Solver to employ (depends on the chosen method):
    - **CP**: `gecode`, `chuffed`
    - **MIP**: `highs`, `cbc`, `gcg`, `scip`
* `<time>`: Maximum time in seconds allowed for the solver to run.
* `[use_warm_start]`: Optional. 'true' to use warm start (only applicable for HiGHS solver in MIP).

> [!IMPORTANT]
> To use MIP, you need to obtain an AMPL license, which is available for free
> through the community edition. After acquiring your license, modify the
> corresponding line in the Dockerfile accordingly.

```{dockerfile}
AMPL_LICENSE="your_license"
```

### Example Usage:

```{bash}
$ run_docker.sh ./Instances/inst01.dat mip three_index_vehicle_flow highs 275
```

## Repository Structure

```
Repository
├── Instances/          # Contains problem instances
├── Models/             # Contains different formulations used
│   └── CP/
│   └── MIP/
│   │   ├── three_index_vehicle_flow
│   │   ├── three_index_vehicle_flow_SB
│   │   └── three_index_vehicle_flow_SB_IMPLIED
│   └── SAT/
├── Notebooks/          # Jupyter notebooks for plotting results and graphs
├── res/                # Contains results obtained on different instances and techniques
│   └── CP/
│   └── MIP/
│   └── SAT/
├── runner.sh           # Bash script to run method and solver on all instances (Python)
├── run_docker.sh       # Bash script to run method and solver on specific instance (Docker)
└── [other files]
```

## Authors

- Alessio Arcara
- Alessia Crimaldi
- Alessio Pittiglio


