include "alldifferent.mzn";

% Input parameters
int: m;
int: n;
set of int: COURIERS = 1..m;
set of int: ITEMS = 1..n;
array[COURIERS] of int: l;  
array[ITEMS] of int: s;
array[1..n+1, 1..n+1] of int: D;

% Decision variable
array [COURIERS, ITEMS] of var 0..n: X;

% Constraints
% (1) in X there is a selection order of the items (columns) by each courier (rows)
%     taken items cannot be duplicated
%     while the zeros represent that no item is taken and can be duplicated
constraint all_different_except_0(X);

% (2) the sum of the items size taken by a courier must be less than the courier's capacity
constraint forall(i in COURIERS)(sum([s[X[i, j]] | j in ITEMS where s[X[i, j]] != 0]) <= l[i]);

% (3) all couriers must leave, so must take at least an item
constraint forall(i in COURIERS)(X[i,1] > 0);

% (4) Gauss Sum (sum of integer numbers from 1 to n) to be sure that every item is taken, so it appears in X
constraint sum(X) == (n*(n+1))/2;

% (5) after a 0, so no more item is taken by the courier, no more items will be taken
constraint forall(i in COURIERS, j in 1..n-1)(X[i, j] == 0 -> forall(k in j+1..n)(X[i,k] == 0));

% (6) total distance calculation
array[COURIERS] of var int: total_distance;
constraint
  forall(i in COURIERS) (
    total_distance[i] = 
      (if X[i, 1] == 0 then 0 else D[n+1, X[i, 1]] endif) +
      sum([D[X[i, j], X[i, j+1]] | j in 1..n-1 where X[i, j] != 0 /\ X[i, j+1] != 0]) +
      sum([D[X[i, j], n+1] | j in 1..n-1 where (X[i, j] != 0 /\ (X[i, j+1] == 0 \/ j+1 == n))])
  );

% Objective function
solve minimize max(total_distance);