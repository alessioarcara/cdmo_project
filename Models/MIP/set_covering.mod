param n;
param m;
set V := {1..n+1};
set R;

param c {R} >= 0;
param a {R, N} binary;

var x {R} binary;
var maxCourDist >= 0;

minimize MaxCourDist: maxCourDist;

s.t. MaxCourDist_Def:
    maxCourDist >= sum {r in R} c[r] * x[r];
    
s.t. Visit_Once {i in V}:
	sum {r in R} a[r,i] * x[r] >= 1;
	
s.t. All_Couriers_Used:
	sum {r in R} x[r] = K;