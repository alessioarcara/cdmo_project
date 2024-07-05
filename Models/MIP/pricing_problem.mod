param n;
param depot := n+1;
set V := {1..depot};
set V_no_depot := {1..n};

param s{V_no_depot};
param d{V, V};
param pi{V};
param sigma;
param C;
param max_route_length;  # Current maximum route length

var x{V, V} binary;
var u{V} >= 0, <= n-1;

minimize MinReducedCost:
    sum{i in V, j in V} (d[i,j] - pi[i]) * x[i,j] - sigma;

s.t. Flow_Conservation {i in V}:
    sum {j in V} x[i,j] - sum {j in V} x[j,i] = 0;

s.t. Depot_Start:
    sum {j in V} x[depot,j] = 1;

s.t. Depot_End:
    sum {i in V} x[i,depot] = 1;

s.t. Avoid_Self_Visit {i in V}:
    x[i,i] = 0;

s.t. Capacity_Restriction:
    sum {i in V, j in V_no_depot} s[j] * x[i,j] <= C;

s.t. Subtour_Elimination {i in V_no_depot, j in V_no_depot: i != j}:
    u[i] - u[j] + n * x[i,j] <= n - 1;