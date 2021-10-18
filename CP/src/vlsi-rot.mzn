include "globals.mzn";

int: w; % width of the plate
int: n; % number of circuits to be placed
int: minl;
int: maxl;

set of int: circuits = 1..n;
set of int: xRange = 0..w-1;
set of int: yRange = 0..maxl-1;
var minl..maxl: l = max(i in circuits)(yhat[i] + y[i]);

array [circuits] of 1..w: inputx;
array [circuits] of 1..maxl: inputy;
array [circuits] of var bool: rotation;
array [circuits] of var 1..w: x;
array [circuits] of var 1..maxl: y;

array [circuits] of var 0..w: xhat;
array [circuits] of var 0..maxl: yhat;

% main problem constraints
constraint forall (i in circuits) (yhat[i] < l);
constraint diffn(xhat, yhat, x, y) :: domain;

constraint forall (i in circuits) (xhat[i] + x[i] <= w);
constraint forall (i in circuits) (yhat[i] + y[i] <= l);

% handle rotations
constraint forall (i in circuits) (if rotation[i] then y[i] == inputx[i] /\ x[i] == inputy[i]
                                   else x[i] == inputx[i] /\ y[i] == inputy[i] endif);

% rows and columns symmetry
constraint symmetry_breaking_constraint(
    forall (i,j in circuits where i < j) ((xhat[i] == xhat[j] /\ x[i] == x[j]) ->
        (if y[i] >= y[j] then yhat[i] <= yhat[j] else yhat[j] <= yhat[i] endif)));

constraint symmetry_breaking_constraint(
    forall (i,j in circuits where i < j) ((yhat[i] == yhat[j] /\ y[i] == y[j]) ->
        (if x[i] >= x[j] then xhat[i] <= xhat[j] else xhat[j] <= xhat[i] endif)));

% three blocks symmetry
constraint symmetry_breaking_constraint(
    forall (i,j,k in circuits where i < j /\ j < k)
        ((xhat[i] == xhat[j] /\ x[i] == x[j] /\ yhat[i] = yhat[k] /\ y[i] + y[j] = y[k]) ->
        (if x[i] >= x[k] then xhat[i] <= xhat[k] /\ xhat[i] = xhat[j] else xhat[k] <= xhat[i] /\ xhat[i] = xhat[j] endif)));
constraint symmetry_breaking_constraint(
    forall (i,j,k in circuits where i < j /\ j < k)
        ((yhat[i] == yhat[j] /\ y[i] == y[j] /\ xhat[i] = xhat[k] /\ x[i] + x[j] = x[k]) ->
        (if y[i] >= y[k] then yhat[i] <= yhat[k] /\ yhat[i] = yhat[j] else yhat[k] <= yhat[i] /\ yhat[i] = yhat[j] endif)));

% the biggest block is always in 0, 0
constraint xhat[1] = 0;
constraint yhat[1] = 0;

% implied constraints
constraint cumulative(xhat, x, y, l) :: domain;
constraint cumulative(yhat, y, x, w) :: domain;
%constraint forall (k in 1..w) (sum([y[i] | i in circuits where xhat[i] < k /\ xhat[i] + x[i] >= k]) <= l);
%constraint forall (k in 1..maxl) (sum([x[i] | i in circuits where yhat[i] < k /\ yhat[i] + y[i] >= k]) <= w);

int: search_heuristic;
int: restart_strategy;

ann: search_ann_xhat =
if search_heuristic == 1 then
  int_search(xhat, smallest, indomain_min)
elseif search_heuristic == 2 then
  int_search(xhat, dom_w_deg, indomain_min)
else
  int_search(xhat, impact, indomain_min)
endif;

ann: search_ann_yhat =
if search_heuristic == 1 then
  int_search(yhat, first_fail, indomain_min)
elseif search_heuristic == 2 then
  int_search(yhat, dom_w_deg, indomain_min)
else
  int_search(yhat, impact, indomain_min)
endif;

ann: restart_ann =
if restart_strategy == 1 then
  restart_constant(150)
elseif restart_strategy == 2 then
  restart_geometric(2,50)
elseif restart_strategy == 3 then
  restart_luby(150)
else
  restart_none
endif;

solve :: search_ann_xhat
      :: search_ann_yhat
      :: restart_ann
         minimize l;