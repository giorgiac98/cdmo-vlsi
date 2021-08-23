include "diffn_k.mzn";

int: w; % width of the plate
int: c; % number of circuits to be placed
int: maxl;
var 1..maxl: l;

array [1..c] of int: dx;
array [1..c] of int: dy;

array [1..c, 1..2] of var int: dim;
array [1..c, 1..2] of var int: origins;

constraint forall (i in 1..c) (dim[i, 1] == dx[i] /\ dim[i, 2] == dy[i]);

constraint l >= 0;
constraint forall (i in 1..c) (origins[i, 1] >= 0 /\ origins[i, 1] < w);
constraint forall (i in 1..c) (origins[i, 2] >= 0 /\ origins[i, 2] < l);

constraint forall (k in 1..w) (sum([dy[i] | i in 1..c where origins[i, 1] < k /\ origins[i, 1] + dx[i] >= k]) <= l);
constraint forall (k in 1..maxl) (sum([dx[i] | i in 1..c where origins[i, 2] < k /\ origins[i, 2] + dy[i] >= k]) <= w);

%constraint forall (k in 1..w) ( w >= sum(i in 1..c)
%        (if origins[i, 1] <= k /\ origins[i, 1] + dy[i] >= k
%        then dy[i] else 0 endif));

constraint diffn_k(origins, dim);

constraint forall (i in 1..c) (origins[i, 1] + dx[i] <= w);
constraint forall (i in 1..c) (origins[i, 2] + dy[i] <= l);

solve minimize l;
