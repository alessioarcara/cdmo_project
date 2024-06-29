#!/bin/bash

METHOD=$1
SOLVER=$2
SCRIPT="mcp.py"

for i in $(seq -w 1 10); do 
    INSTANCE="./Instances/inst$i.dat"

    python $SCRIPT $INSTANCE $METHOD $SOLVER 295

done
