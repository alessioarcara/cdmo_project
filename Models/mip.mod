
param m;
param n;
set VEHICLES := 1..m;
set NODES := 1..n;
set ARCS within (NODES cross NODES);
param l {VEHICLES};
param s {NODES};
param D {ARCS};
