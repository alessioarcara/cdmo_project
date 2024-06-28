param n;                              
param m;
set V_no_depot := {1..n};
set K := {1..m};
set R {K};

param c {k in K, r in R[k]} >= 0;
param a {k in K, V_no_depot, r in R[k]} binary;

var x {k in K, r in R[k]} binary;

minimize total: sum {k in K, r in R[k]} c[k,r] * x[k,r];

s.t. Visit_Once {i in V_no_depot}:
	sum {k in K, r in R[k]} a[k,i,r] * x[k,r] >= 1;

s.t. K_Couriers_Used {k in K}:
    sum {r in R[k]} x[k,r] = 1;