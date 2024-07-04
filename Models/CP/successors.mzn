include "alldifferent.mzn";
include "element.mzn";
include "int_set_channel.mzn";

int: m;  % Number of couriers
int: n;  % Number of items
set of int: COURIERS = 1..m;
set of int: ITEMS = 1..n;
set of int: NODES = 1..(n+2*m);

array[COURIERS] of int: l;  % Load capacities of couriers
array[ITEMS] of int: s; % Sizes of items
array[1..(n+2*m), 1..(n+2*m)] of int: D; % Distance matrix

% Variables
array[NODES] of var 0..(n+2*m): successors; % (1)
array[NODES] of var 1..m: assignments; % (3)
array[NODES] of var 0..n+1: positions;
array[COURIERS] of var set of ITEMS: b; % (11.1)
array[NODES] of var 0..max(D): dp; % upperbound da definire

% Constraints
constraint forall(i in 1..m)(successors[n+m+i] == 0); % (2)

constraint all_different_except_0(successors); % (7)

constraint forall(i in 1..m)(assignments[n+i] == i /\ assignments[n+m+i] == i); % (4)

constraint forall(i in 1..n+m)(element(successors[i], assignments, assignments[i]) /\ successors[i] != i); % 8 + 9 l'assignment del successore ha lo stesso assignment
  
constraint int_set_channel([assignments[i] | i in ITEMS], b); % 11.2
constraint forall(i in COURIERS)(sum([s[j] | j in b[i]]) <= l[i]); % 12

constraint forall(i in 1..m)(positions[n+i] = 0); % 6;
constraint forall(i in 1..n+m)(
  element(successors[i], positions, positions[i] + 1) % 10.1 
);

constraint forall(i in 1..m)(dp[n+m+i] == 0); 
constraint forall(i in 1..n+m)(
 element(i, dp, D[i, successors[i]])
); % 13.2

% symmetry breaking
constraint forall(i in 1..m-1)(successors[n+i] < successors[n+i+1]);

array[COURIERS] of var int: distances = [sum([dp[node] | node in 1..n+m where assignments[node] == c]) | c in COURIERS];

solve minimize max(distances);