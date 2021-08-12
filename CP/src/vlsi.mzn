include "diffn.mzn";

int: w; % width of the plate
int: c; % number of circuits to be placed
var int: h;

set of int: xRange = 0..w-1;

array [1..c] of int: dx;
array [1..c] of int: dy;

array [1..c] of var xRange: x;
array [1..c] of var int: y;

constraint h >= 0;
constraint forall (yo in y) (yo <= h /\ yo >= 0);
constraint forall(i,j in index_set(x) where i < j)(
        x[i] + dx[i] <= x[j] \/ y[i] + dy[i] <= y[j] \/
        x[j] + dx[j] <= x[i] \/ y[j] + dy[j] <= y[i]
    );
constraint forall (i in 1..c) (y[i] + dy[i] <= h);

solve minimize h;
