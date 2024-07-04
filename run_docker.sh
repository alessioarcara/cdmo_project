#!/bin/bash

print_usage() {
    echo "Usage: $0 <instance> <method> <model> <solver> <time> [use_warm_start]"
    echo "  <instance>: Path to the instance file"
    echo "  <method>: 'cp', 'mip', or 'sat'"
    echo "  <model>: Name of the model to use"
    echo "  <solver>: Name of the solver to use"
    echo "  <time>: Timeout in seconds"
    echo "  [use_warm_start]: Optional. 'true' to use warm start (only applicable for HiGHS solver in MIP)"
}

if [ $# -lt 5 ] || [ $# -gt 6 ]; then
    print_usage
    exit 1
fi

INSTANCE="$1"
METHOD="$2"
MODEL="$3"
SOLVER="$4"
TIME="$5"
USE_WARM_START="${6:-false}"

if ! docker image inspect mcp &> /dev/null; then
    echo "Docker image 'mcp' not found. Building from Dockerfile..."
    docker build -t mcp . 
    echo "Docker image 'mcp' built successfully."
fi

echo "========================================"
echo "Executing MCP solver with the following parameters:"
echo "  Instance: $INSTANCE"
echo "  Method: $METHOD"
echo "  Model: $MODEL"
echo "  Solver: $SOLVER"
echo "  Timeout: $TIME"
echo "  Warm Start: $USE_WARM_START"
echo "========================================"

echo "Starting Docker container..."
docker run -v "$(pwd)/res:/src/res" \
    -e instance="$INSTANCE" \
    -e method="$METHOD" \
    -e model="$MODEL" \
    -e solver="$SOLVER" \
    -e time="$TIME" \
    -e use_warm_start="$USE_WARM_START" \
    mcp
