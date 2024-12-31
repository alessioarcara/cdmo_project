include "globals.mzn";

%%% Parameters %%%
int: m;                                           % Number of couriers
int: n;                                           % Number of items
set of int: K = 1..m;                             % Set of couriers
set of int: N = 1..n;                             % Set of items
set of int: V = 1..(n + 2 * m);                   % Set of nodes (items + depots)
array[K] of int: l;                               % Maximum capacities of couriers
array[N] of int: s;                               % Sizes of items
array[V, V] of int: D;                            % Distance matrix between items

%%% Decision variables %%%
array[V] of var V: successors;                    % Successor nodes
array[V] of var V: predecessors;                  % Predecessor nodes
array[V] of var K: assignments;                   % Node-to-Courier assignments

%%% Auxiliary variables %%%
array[V] of var 0..sum(D): cumulative_distances;  % Cumulative travel distance at each node
array[1..(n + m)] of var 0..max(l): cumulative_capacities; % Cumulative capacities at each node
var 0..sum(D): maximum_distance;                  % Max distance travelled by any courier


%%% Constraints %%%

% Define depots
set of int: Start_Depots = n + 1..n + m;                                % Start depots
set of int: End_Depots = n + m + 1..n + 2 * m;                          % End depots 
set of int: Start_Depots_Excluding_First = n + 2..n + m;                % Start depots excluding the first one
set of int: End_Depots_Excluding_Last = n + m + 1..n + 2 * m - 1;       % End depots excluding the last one

% Ensure the nodes form a valid circuit
constraint circuit(successors);
constraint circuit(predecessors);

% Depots must link properly
constraint forall(i in Start_Depots_Excluding_First)(predecessors[i] = i + m - 1);
constraint forall(i in End_Depots_Excluding_Last)(successors[i] = i - m + 1);
constraint successors[n + 2 * m] = n + 1;
constraint predecessors[n + 1] = n + 2 * m;

% Assign couriers correctly to depots
constraint forall(i in Start_Depots)(assignments[i] = i - n);
constraint forall(i in End_Depots)(assignments[i] = i - n - m);

% Ensure courier consistency for successors and predecessors
constraint forall(i in N)(assignments[successors[i]] = assignments[i]);
constraint forall(i in N)(assignments[predecessors[i]] = assignments[i]);

% Ensure couriers don't exceed max capacity
constraint bin_packing_capa(l, [assignments[i] | i in N], s);

% Channeling constraints between successors and predecessors (Implied)
constraint forall(i in N) (
    (successors[predecessors[i]] == i) /\ (predecessors[successors[i]] == i)
);

% Cumulative capacity constraints
constraint forall(i in Start_Depots)(cumulative_capacities[i] = 0);
constraint forall(i in N)(
    cumulative_capacities[i] = cumulative_capacities[predecessors[i]] + s[i]
);


% Force all couriers to take at least one item 
constraint forall(i in Start_Depots)(successors[i] != i + m);
constraint forall(i in End_Depots)(predecessors[i] != i - m);

% Cumulative distance constraints
constraint forall(i in Start_Depots)(cumulative_distances[i] = 0);
constraint forall(i in Start_Depots)(
    cumulative_distances[successors[i]] = D[n + 1, successors[i]]
);
constraint forall(i in N)(
    cumulative_distances[successors[i]] = cumulative_distances[i] + D[i, successors[i]]
);

% Symmetry-breaking constraint
constraint forall(i in Start_Depots)(successors[i] <= predecessors[i + m]);

% Objective function: Minimize the maximum distance traveled by any courier
constraint maximum_distance = max([cumulative_distances[i] | i in End_Depots]);


solve :: seq_search([
    int_search(successors, first_fail, indomain_split),
    int_search(assignments, first_fail, indomain_split),
    int_search(predecessors,first_fail,indomain_split),
    ])
    minimize maximum_distance;
