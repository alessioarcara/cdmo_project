include "globals.mzn";

int: n;
int: depot = n+1;
int: C; 
set of int: V = 1..n+1;
set of int: V_no_depot = 1..n;
array[V] of int: s;
array[V, V] of float: d;
array[V] of float: pi;
float: sigma;

array[V] of var V: P;
array[V_no_depot] of var 0..C: L;

var float: reduced_cost = 
   d[depot, P[1]] - pi[1] + sum(i in V_no_depot) (d[P[i], P[i+1]] - pi[P[i]]) - sigma;

solve minimize reduced_cost;

constraint all_different_except(P, {depot});

constraint L[1] = s[P[1]];  % start with empty courier

constraint forall(i in 2..n) (
    L[i] = L[i-1] + s[P[i]]
);

constraint forall(i in V_no_depot) (
    P[i] = depot -> P[i+1] = depot
);