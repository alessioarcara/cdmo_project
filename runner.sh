#!/bin/bash

METHOD=$1
MODEL=$2
SOLVER=$3
SCRIPT="mcp.py"

for i in $(seq -w 1 10); do 
    INSTANCE="./Instances/inst$i.dat"
    python $SCRIPT $INSTANCE $METHOD $MODEL $SOLVER 275
done

for i in 13 16 19; do 
    INSTANCE="./Instances/inst$i.dat"
    python $SCRIPT $INSTANCE $METHOD $MODEL $SOLVER 275
done
