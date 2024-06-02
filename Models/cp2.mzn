include "alldifferent.mzn";
include "element.mzn";
include "int_set_channel.mzn";
include "circuit.mzn";

int: m;
int: n;
set of int: COURIERS = 1..m;
set of int: ITEMS = 1..n;
set of int: NODES = 1..(n+2*m);

array[COURIERS] of int: l;  
array[ITEMS] of int: s;
array[1..(n+2*m), 1..(n+2*m)] of int: D; % n+m?

array[NODES] of var 0..(n+2*m): successors; % 1
array[NODES] of var 0..(n+2*m): predecessors; % sicuro?
array[NODES] of var 1..m: assignments; % 3
array[NODES] of var 0..n+1: positions;
array[COURIERS] of var set of ITEMS: b; % 11.a
array[1..(n+m)] of var 0..max(D): dp; % upperbound da definire
array[COURIERS] of var 1..sum(D): dists; % upperbound giusto?
array[1..(n+m)] of var 1..(100*m+(2*m+n)): y;
array[NODES] of var 0..max(l): cps;
%array[NODES] of var 1..(2*m+n): dps;

% si potrebbe provare a linkare invece che settarli a zero
% 




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

constraint forall(i in 1..n+m)(
 element(i, dp, D[i, successors[i]])
);

constraint
  forall(i in COURIERS) (
    dists[i] = sum([dp[j] | j in b[i]]) + dp[n+i]
  );
  
%%%% SYMMETRY BREAKING %%%%%

constraint forall(i in 1..m-1)(successors[n+i] < successors[n+i+1]); % symmetry breaking

%%%% LINKING assignments and successors %%%%%

constraint forall(i in 1..m)(
  y[n+i] = 100*assignments[n+i] + successors[n+i]
);

%%%% PREDECESSORS %%%%%

constraint forall(i, k in 1..n+m)(
  predecessors[k] = i <-> successors[i] = k
); % redundant constraint but better propagation

constraint forall(i in 1..m)(
  predecessors[n+m+i] = n+i
);

%%%% CAPACITY SUM %%%%%

constraint forall(i in NODES)(
  cps[i] <= l[assignments[i]]
); % 21


constraint forall(i in 1..m)(
  cps[n+i] == 0
);

constraint forall(i in 1..n)(
  element(successors[i], cps, cps[i] + s[i])
); % 20


% constraint forall(i in NODES)(
%   element(i, dps, D[i, successors[i]])
% );

solve
       %:: int_search(successors, dom_w_deg, indomain_min)
%       :: restart_luby(100)
      %:: int_search(dp, max_regret, indomain_min)
      minimize max(dists);