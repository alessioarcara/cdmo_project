#!/bin/bash

if [ $# -ne 4 ]; then
    echo "Usage: $0 <instance> <method> <solver> <time>"
    exit 1
fi

INSTANCE="$1"
METHOD="$2"
SOLVER="$3"
TIME="$4"

if ! docker image inspect mcp &> /dev/null; then
    echo "Building Docker image from the Dockerfile"
    docker build -t mcp .
fi

echo "Running mcp.py on instance $INSTANCE using method $METHOD and solver $SOLVER"
docker run -v "$(pwd)/res:/src/res" -e instance="$INSTANCE" -e method="$METHOD" -e solver="$SOLVER" -e time="$TIME" mcp
