set ITEMS;

param c > 0;
param v{ITEMS} > 0;
param w{ITEMS} > 0;

var x{ITEMS} binary;

maximize total_profit:
    sum{i in ITEMS} v[i] * x[i];

subject to capacity_constraint:
    sum{i in ITEMS} w[i] * x[i] <= c;