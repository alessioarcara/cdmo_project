% Symmetry Breaking Constraint

%constraint forall(i in 1..m-1)(successors[n+1] < successors[n+i+1])
%constraint forall(i in 1..m-1, j in i+1..m where l[i]==l[j])(successors[n+i] < successors[n+j]);

%Symmetry breaking for vehicles with equal capacities
constraint forall(i in 1..m-1, j in i+1..m where l[i] == l[j]) (successors[n+i] < successors[n+j]);
%Symmetry breaking for vehicles with different capacities
constraint forall(i in 1..m-1, j in i+1..m where l[i] > l[j]) (successors[n+i] < successors[n+j]);