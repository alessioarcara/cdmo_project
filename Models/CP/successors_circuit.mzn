include "alldifferent.mzn";
include "circuit.mzn";
include "element.mzn";
include "int_set_channel.mzn";

% Input parameters
int: m;                                    % number of couriers
int: n;                                    % number of items
set of int: K = 1..m;                      % set of couriers
set of int: N = 1..n;                      % set of items
set of int: V = 1..(n+2*m);                % set of vertices
array[K] of int: l;                        % load capacities of couriers
array[N] of int: s;                        % sizes of items
array[1..(n+2*m), 1..(n+2*m)] of int: D;   % distance matrix

% Decision variables
array[V] of var V: successors;
%array[V] of var V: predecessors;
array[V] of var K: assignments;
array[K] of var set of N: b;               % array of assigned items to courier
array[V] of var 0..max(D): dp;             % array of arc travelled distance
array[K] of var 0..sum(D): distances;      % array of total distance

% Constraints
% alldifferent + subtour elimination

constraint circuit(successors);

% the successors of the end depots are the start depots
constraint forall(k in K)(
    successors[n+m+k] == n + k
);

%% i predecessori degli start depot sono gli end depot 
%constraint forall(k in K)(
%    predecessors[n+k] == n + m + k
%);

%constraint forall(k in K)(
%    predecessors[]
%);


% (4)
%constraint forall(k in K)(assignments[n+k] == k /\ assignments[n+m+k] == k);
% (7)
constraint all_different(successors);
% (8) (9)
%constraint forall(i in N)(element(successors[i], assignments, assignments[i]));

constraint forall(i in N)(
    assignments[successors[i]] = assignments[i]
);

%constraint forall(i in N)(
%    assignments[predecessors[i]] = assignments[i]
%);
% (11.2)
constraint int_set_channel([assignments[i] | i in N], b);
% (12)
constraint forall(k in K)(sum([s[i] | i in b[k]]) <= l[k]);
% (13.2)
constraint forall(i in V)(
 element(i, dp, D[i, successors[i]])
);
% (14)
constraint forall(k in K)(dp[n+m+k] == 0);


%%% PREDECESSORS - SUCCESSORS CONSTRAINTS %%%

constraint circuit(successors);
%constraint circuit(predecessors); % redundant

%constraint forall(i in N) (
%    successors[predecessors[i]] = i
%);

%constraint forall(i in N) (
%    predecessors[successors[i]] = i
%);

%%%


% Objective variable
constraint distances = [sum([dp[i] | i in 1..n+m where assignments[i] == k]) | k in K];

% Objective function
solve minimize max(distances);