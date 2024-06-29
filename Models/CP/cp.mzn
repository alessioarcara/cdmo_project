include "alldifferent.mzn";

int: m;
int: n;
set of int: COURIERS = 1..m;
set of int: ITEMS = 1..n;

array[COURIERS] of int: l;  
array[ITEMS] of int: s;
array[1..n+1, 1..n+1] of int: D;

array [COURIERS, ITEMS] of var 0..n: X;

constraint all_different_except_0(X);
constraint sum(X) == (n*(n+1))/2;
constraint forall(i in COURIERS, j in 1..n-1)(X[i, j] == 0 -> forall(k in j+1..n)(X[i,k] == 0));
%constraint forall(i in COURIERS)(X[i,1] > 0);

array[COURIERS] of var int: total_distance;
constraint
  forall(i in COURIERS) (
    total_distance[i] = 
      (if X[i, 1] == 0 then 0 else D[n+1, X[i, 1]] endif) +
      sum([D[X[i, j], X[i, j+1]] | j in 1..n-1 where X[i, j] != 0 /\ X[i, j+1] != 0]) +
      sum([D[X[i, j], n+1] | j in 1..n-1 where (X[i, j] != 0 /\ (X[i, j+1] == 0 \/ j+1 == n))])
  );

constraint forall(i in COURIERS)(sum([s[X[i, j]] | j in ITEMS where s[X[i, j]] != 0]) <= l[i]);
  
solve minimize max(total_distance);
