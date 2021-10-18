include "globals.mzn";

int: w; % width of the plate
int: n; % number of circuits to be placed
int: minl;
int: maxl;

set of int: circuits = 1..n;
set of int: xRange = 0..w-1;
set of int: yRange = 0..maxl-1;
var minl..maxl: l = max(i in circuits)(yhat[i] + y[i]);

array [circuits] of 1..w: x;
array [circuits] of 1..maxl: y;

array [circuits] of var 0..w-min(x): xhat;
array [circuits] of var 0..maxl-min(y): yhat;

/*
array [circuits] of var xRange: xsym;
array [circuits] of var yRange: ysym;
constraint forall (i in circuits) (xsym[i] = w - x[i] - xhat[i] /\ ysym[i] = l - y[i] - yhat[i]);
array [yRange, xRange] of var 1..n+1: board;
array [yRange, xRange] of var 1..n+1: boardXsym;
array [yRange, xRange] of var 1..n+1: boardYsym;
array [yRange, xRange] of var 1..n+1: boardXYsym;

% channeling constraints

constraint forall (j in yRange, k in xRange, i in circuits)
        (k >= xhat[i] /\ k < (xhat[i]+x[i]) /\ j >= yhat[i] /\ j < (yhat[i]+y[i]) <-> board[j, k] = i);

constraint forall (j in yRange, k in xRange, i in circuits)
        (k >= xsym[i] /\ k < (xsym[i]+x[i]) /\ j >= yhat[i] /\ j < (yhat[i]+y[i]) <-> boardXsym[j, k] = i);

constraint forall (j in yRange, k in xRange, i in circuits)
        (k >= xhat[i] /\ k < (xhat[i]+x[i]) /\ j >= ysym[i] /\ j < (ysym[i]+y[i]) <-> boardYsym[j, k] = i);

constraint forall (j in yRange, k in xRange, i in circuits)
        (k >= xsym[i] /\ k < (xsym[i]+x[i]) /\ j >= ysym[i] /\ j < (ysym[i]+y[i]) <-> boardXYsym[j, k] = i);

% symmetry breaking constraints
constraint lex_lesseq(array1d(board), array1d(boardXsym));
constraint lex_lesseq(array1d(board), array1d(boardYsym));
constraint lex_lesseq(array1d(board), array1d(boardXYsym));
*/

/*
array [circuits] of var 1..w*maxl: origins;
% channeling constraints
constraint forall (i in circuits) (origins[i] == w * yhat[i] + xhat[i]);
% constraint alldifferent(origins);
constraint symmetry_breaking_constraint(lex_less(origins, [w * yhat[i] + xsym[i] | i in circuits]));
constraint symmetry_breaking_constraint(lex_less(origins, [w * ysym[i] + xhat[i] | i in circuits]));
constraint symmetry_breaking_constraint(lex_less(origins, [w * ysym[i] + xsym[i] | i in circuits]));
*/

/*
array [circuits] of var set of 1..w*maxl: cells;
constraint forall (i in circuits) (card(cells[i]) == x[i] * y[i]);
constraint forall (i in circuits, j in 0..x[i], k in 0..y[i]) (member(cells[i], w * (yhat[i] + j) + (xhat[i] + k)));
constraint all_disjoint(cells);
%constraint partition_set(cells, 1..w*maxl);
*/

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

% main problem constraints
constraint forall (i in circuits) (yhat[i] < l);
constraint diffn(xhat, yhat, x, y) :: domain;

constraint forall (i in circuits) (xhat[i] + x[i] <= w);
constraint forall (i in circuits) (yhat[i] + y[i] <= l);

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