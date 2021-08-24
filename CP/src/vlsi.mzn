include "diffn.mzn";

int: w; % width of the plate
int: n; % number of circuits to be placed
int: maxl;
var 1..maxl: l;

set of int: nRange = 1..n;
set of int: xRange = 0..w-1;

array [nRange] of 1..w: x;
array [nRange] of 1..maxl: y;

array [nRange] of var xRange: xhat;
array [nRange] of var 0..maxl: yhat;

constraint l >= 0;
constraint forall (i in nRange) (yhat[i] >= 0 /\ yhat[i] < l);

constraint forall (k in 1..w) (sum([y[i] | i in nRange where xhat[i] < k /\ xhat[i] + x[i] >= k]) <= l);
constraint forall (k in 1..maxl) (sum([x[i] | i in nRange where yhat[i] < k /\ yhat[i] + y[i] >= k]) <= w);

constraint diffn(xhat, yhat, x, y);

constraint forall (i in nRange) (xhat[i] + x[i] <= w);
constraint forall (i in nRange) (yhat[i] + y[i] <= l);

solve minimize l;
