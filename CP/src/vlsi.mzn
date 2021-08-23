include "lex_chain_greatereq.mzn";

int: w; % width of the plate
int: c; % number of circuits to be placed
var int: l;

array [1..c] of int: dx;
array [1..c] of int: dy;

array [1..c, 1..2] of var int: origins;

constraint forall(i in 1..c) (origins[i, 1] >= 0 /\ origins[i, 1] < w);

% constraint lex_chain_greatereq(origins);

constraint l >= 0;
constraint forall(i in 1..c) (origins[i, 2] >= 0 /\ origins[i, 2] < l);
constraint forall(i,j in 1..c where i < j) (
        origins[i, 1] + dx[i] <= origins[j, 1] \/
        origins[i, 2] + dy[i] <= origins[j, 2] \/
        origins[j, 1] + dx[j] <= origins[i, 1] \/
        origins[j, 2] + dy[j] <= origins[i, 2]
    );
constraint forall (i in 1..c) (origins[i, 1] + dx[i] <= w);
constraint forall (i in 1..c) (origins[i, 2] + dy[i] <= l);

solve minimize l;
