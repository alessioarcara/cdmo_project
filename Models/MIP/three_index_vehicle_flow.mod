param n;
param m;
param depot := n+1;
set V_no_depot := {1..n};                # set of items excluding the depot
set V := {1..depot};                     # set of items (including depot)
set K := {1..m};                         # set of couriers

param s{V_no_depot};                     # size of each item
param d{V, V};                           # distance between items
param c{K};                              # capacity of each courier

var x{V, V, K} binary;                   # 1 if courier k travels from i to j, 0 otherwise
var y{V, K} binary;                      # 1 if courier k visits i, 0 otherwise
var u{V, K} >= 0, <= n-1;                # auxiliary variables for subtour elimination
var load{K} >= 0;
var maxCourDist >= 0;                    # maximum distance travelled by any courier

minimize MaxCourDist: maxCourDist;

s.t. MaxCourDist_Def {k in K}:
    sum {i in V, j in V} d[i,j] * x[i,j,k] <= maxCourDist;

s.t. Visit_Once {i in V_no_depot}:
    sum {k in K} y[i,k] = 1;

s.t. Each_Courier_Leaves_Depot {k in K}:
    y[depot, k] <= 1;

s.t. Avoid_Self_Visit {i in V, k in K}:
    x[i,i,k] = 0;

s.t. Flow_Conservation_In {i in V, k in K}:
    sum {j in V} x[i,j,k] = y[i,k];

s.t. Flow_Conservation_Out {i in V, k in K}:
    sum {j in V} x[j,i,k] = y[i,k];

s.t. Load_Def{k in K}:
    load[k] = sum{i in V_no_depot} s[i] * y[i, k];

s.t. Capacity_Restriction{k in K}:
    load[k] <= c[k];

s.t. Subtour_Elimination {i in V_no_depot, j in V_no_depot, k in K: i != j}:
    u[i,k] - u[j,k] + n * x[i,j,k] <= n-1;
