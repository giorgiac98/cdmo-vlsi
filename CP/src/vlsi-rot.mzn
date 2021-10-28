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
constraint forall (i in circuits) (inputx[i] == inputy[i] -> rotation[i] = false);

% implied constraints
constraint cumulative(xhat, x, y, l) :: domain;
constraint cumulative(yhat, y, x, w) :: domain;
% constraint forall (k in 1..w) (sum([y[i] | i in circuits where xhat[i] < k /\ xhat[i] + x[i] >= k]) <= l);
% constraint forall (k in 1..maxl) (sum([x[i] | i in circuits where yhat[i] < k /\ yhat[i] + y[i] >= k]) <= w);


% rows and columns symmetry
constraint symmetry_breaking_constraint(
    forall (i,j in circuits where i < j) ((xhat[i] == xhat[j] /\ x[i] == x[j]) -> yhat[i] <= yhat[j] ));
constraint symmetry_breaking_constraint(
    forall (i,j in circuits where i < j) ((yhat[i] == yhat[j] /\ y[i] == y[j]) -> xhat[i] <= xhat[j] ));

% three blocks symmetry
constraint symmetry_breaking_constraint(
    forall (i,j,k in circuits where i > j /\ j > k)
        ((xhat[i] == xhat[j] /\ x[i] == x[j] /\ yhat[i] == yhat[k] /\ y[i] + y[j] == y[k]) -> xhat[k] <= xhat[i] ));
constraint symmetry_breaking_constraint(
    forall (i,j,k in circuits where i > j /\ j > k)
        ((yhat[i] == yhat[j] /\ y[i] == y[j] /\ xhat[i] == xhat[k] /\ x[i] + x[j] == x[k]) -> yhat[k] <= yhat[i] ));


% force the biggest block to be always to the bottom left of the second biggest
constraint xhat[1] <= xhat[2] /\ yhat[1] <= yhat[2];


int: search_heuristic;
int: restart_strategy;

ann: search_ann_xhat =
if search_heuristic == 1 then
  int_search(xhat, dom_w_deg, indomain_min)
elseif search_heuristic == 2 then
  int_search(xhat, impact, indomain_min)
else
  int_search(xhat, input_order, indomain_min)
endif;

ann: search_ann_yhat =
if search_heuristic == 1 then
  int_search(yhat, dom_w_deg, indomain_min)
elseif search_heuristic == 2 then
  int_search(yhat, impact, indomain_min)
else
  int_search(yhat, input_order, indomain_min)
endif;

ann: restart_ann =
if restart_strategy == 1 then
  restart_luby(150)
elseif restart_strategy == 2 then
  restart_geometric(2, 50)
else
  restart_none
endif;

solve :: search_ann_xhat
      :: search_ann_yhat
      :: restart_ann
         minimize l;