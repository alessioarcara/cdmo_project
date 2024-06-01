
set NODES;
set COURIERS;

param m;
param n;
param l {COURIERS} >= 0;
param s {NODES} >= 0;
param D {NODES, NODES} >= 0;

var x{NODES, NODES} binary;


subject to Flow_Conservation {i in NODES}:
    sum {j in NODES} x[i,j] = sum {j in NODES} x[j,i];

