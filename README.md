# Heterogeneous Min-Max Vehicle Routing Problem

This repository represents the group project for Combinatorial Decision Making
and Optimization 2024/2024, focusing on implementing and evaluating diverse
solving techniques (*CP*, *SAT*, *MIP*) for the **Heterogeneous Min-Max Vehicle
Routing Problem**. The objective is to efficiently plan routes for couriers
with varying capacities to collect all available items while minimizing the
maximum distance traveled by any courier.

## Usage

To reproduce our results, please ensure Docker is installed on your system.
Once Docker is installed, you can solve the different instances by running the
following bash script in your terminal:

```{bash}
$ run_docker.sh <instance_file> <method> <solver> <time>
```

Parameters:

* `<instance_file>`: Path to the instance file.
* `<method>`: Method to use (`cp`, `sat`, `mip`).
* `<solver>`: Solver to employ based on the chosen method:
    - **CP**: `gecode`, `chuffed`
    - **MIP**: `highs`, `cbc`, `gcg`, `scip`
* `<time>`: Maximum time in seconds allowed for the solver to run.

> [!IMPORTANT]
> To use MIP, you need to obtain an AMPL license, which is available for free
> through the community edition. After acquiring your license, modify the
> corresponding line in the Dockerfile accordingly.

```{dockerfile}
AMPL_LICENSE="your_license"
```

### Example Usage:

```{bash}
$ run_docker.sh ./Instances/inst01.dat mip highs 60
```

## Repository Structure

```
Repository
├── Instances/          # Contains problem instances
├── Models/             # Contains different formulations used
│   └── CP/
│   └── MIP/
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


