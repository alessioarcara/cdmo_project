include "alldifferent.mzn";
include "element.mzn";
include "int_set_channel.mzn";

% Input parameters
int: m;                                        % number of couriers
int: n;                                        % number of items
set of int: K = 1..m;                          % set of couriers
set of int: N = 1..n;                          % set of items
set of int: V = 1..(n+2*m);                    % set of vertices
array[K] of int: l;                            % load capacities of couriers
array[N] of int: s;                            % sizes of items
array[1..(n+2*m), 1..(n+2*m)] of int: D;       % distance matrix

% Decision variables
array[V] of var 0..(n+2*m): successors;
array[V] of var K: assignments;
array[V] of var 0..n+1: positions;

% Auxiliary variables
array[K] of var set of N: b;                   % array of assigned items to courier
array[1..n+m] of var 0..max(D): dp;            % array of arc travelled distance
array[K] of var 1..sum(D): distances;          % array of total distance

% Constraints
% (2)
constraint forall(i in 1..m)(successors[n+m+i] == 0);
% (4)
constraint forall(i in 1..m)(assignments[n+i] == i /\ assignments[n+m+i] == i);
% (6)
constraint forall(i in 1..m)(positions[n+i] == 0);
% (7)
constraint all_different_except_0(successors);
% (8) (9)
constraint forall(i in 1..n+m)(element(successors[i], assignments, assignments[i]) /\ successors[i] != i);
% (10.1)
constraint forall(i in 1..n+m)(
  element(successors[i], positions, positions[i] + 1)
);
% (11.2)
constraint int_set_channel([assignments[i] | i in N], b);
% (12)
constraint forall(i in K)(sum([s[j] | j in b[i]]) <= l[i]);
% (13.2)
constraint forall(i in 1..n+m)(
  element(i, dp, D[i, successors[i]])
);
% Objective variable
constraint forall(i in K) (
  distances[i] = sum([dp[j] | j in b[i]]) + dp[n+i]
);


solve minimize max(distances);