include "diffn.mzn";

int: w; % width of the plate
int: c; % number of circuits to be placed
int: maxl;
var 1..maxl: l;

set of int: xRange = 0..w-1;

array [1..c] of int: dx;
array [1..c] of int: dy;

array [1..c] of var 1..w: dimx;
array [1..c] of var 1..maxl: dimy;
array [1..c] of var xRange: x;
array [1..c] of var 0..maxl: y;

constraint forall (i in 1..c) (dimx[i] == dx[i] /\ dimy[i] == dy[i]);

constraint l >= 0;
constraint forall (i in 1..c) (y[i] >= 0 /\ y[i] < l);

constraint forall (k in 1..w) (sum([dy[i] | i in 1..c where x[i] < k /\ x[i] + dx[i] >= k]) <= l);
constraint forall (k in 1..maxl) (sum([dx[i] | i in 1..c where y[i] < k /\ y[i] + dy[i] >= k]) <= w);

constraint diffn(x, y, dimx, dimy);

constraint forall (i in 1..c) (x[i] + dx[i] <= w);
constraint forall (i in 1..c) (y[i] + dy[i] <= l);

solve minimize l;
