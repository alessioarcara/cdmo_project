#!/bin/bash

METHOD=$1
MODEL=$2
SOLVER=$3
LOWER_BOUND=$4
UPPER_BOUND=$5
SCRIPT="mcp.py"

for i in $(seq -w $LOWER_BOUND $UPPER_BOUND); do 
    INSTANCE="./Instances/inst$i.dat"

    python $SCRIPT $INSTANCE $METHOD $MODEL $SOLVER 285

done
