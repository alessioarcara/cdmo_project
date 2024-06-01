include "alldifferent.mzn";
include "element.mzn";
include "int_set_channel.mzn";
include "inverse_set.mzn";

int: m;
int: n;
set of int: COURIERS = 1..m;
set of int: ITEMS = 1..n;
set of int: NODES = 1..(n+2*m);

array[COURIERS] of int: l;  
array[ITEMS] of int: s;
array[1..(n+m), 1..(n+m)] of int: D; % n+m?

array[NODES] of var 0..(n+2*m): successors; % 1
array[NODES] of var 1..m: assignments; % 3
array[NODES] of var 0..n+1: positions;
array[COURIERS] of var set of ITEMS: b; % 11.a
array[NODES] of var 0..max(D): dp; % upperbound da definire

constraint forall(i in 1..m)(successors[n+m+i] == 0); % 2

constraint all_different_except_0(successors); % 7
constraint forall(i in 1..m)(assignments[n+i] == i /\ assignments[n+m+i] == i); % 4
constraint forall(i in 1..n+m)(element(successors[i], assignments, assignments[i]) /\ successors[i] != i); % 8 + 9 l'assignment del successore ha lo stesso assignment
  
constraint int_set_channel([assignments[i] | i in ITEMS], b); % 11.b
constraint forall(i in COURIERS)(sum([s[j] | j in b[i]]) <= l[i]); % 12

constraint forall(i in 1..m)(positions[n+i] = 0); % 6;
constraint forall(i in 1..n+m)(
  element(successors[i], positions, positions[i] + 1)
);

%constraint forall(i in 1..m)(dp[n+m+i] == 0);
constraint forall(i in 1..4)(
 element(i, dp, D[i, successors[i]])
);

solve satisfy;