include "diffn.mzn";
include "cumulative.mzn";
include "lex_lesseq.mzn";

int: w; % width of the plate
int: n; % number of circuits to be placed
int: minl;
int: maxl;
var minl..maxl: l;

set of int: nRange = 1..n;
set of int: xRange = 0..w-1;
set of int: yRange = 0..maxl-1;

array [nRange] of 1..w: x;
array [nRange] of 1..maxl: y;

array [nRange] of var xRange: xhat;
array [nRange] of var yRange: yhat;
/*
array [nRange] of var xRange: xsym;
array [nRange] of var yRange: ysym;

array [yRange, xRange] of var 1..n+1: board;
array [yRange, xRange] of var 1..n+1: boardXsym;
array [yRange, xRange] of var 1..n+1: boardYsym;
array [yRange, xRange] of var 1..n+1: boardXYsym;

% channeling constraints
constraint forall (j in yRange, k in xRange, i in nRange)
        (k >= xhat[i] /\ k < (xhat[i]+x[i]) /\ j >= yhat[i] /\ j < (yhat[i]+y[i]) <-> board[j, k] = i);

constraint forall (i in nRange) (xsym[i] = w - x[i] - xhat[i] /\ ysym[i] = l - y[i] - yhat[i]);

constraint forall (j in yRange, k in xRange, i in nRange)
        (k >= xsym[i] /\ k < (xsym[i]+x[i]) /\ j >= yhat[i] /\ j < (yhat[i]+y[i]) <-> boardXsym[j, k] = i);

constraint forall (j in yRange, k in xRange, i in nRange)
        (k >= xhat[i] /\ k < (xhat[i]+x[i]) /\ j >= ysym[i] /\ j < (ysym[i]+y[i]) <-> boardYsym[j, k] = i);

constraint forall (j in yRange, k in xRange, i in nRange)
        (k >= xsym[i] /\ k < (xsym[i]+x[i]) /\ j >= ysym[i] /\ j < (ysym[i]+y[i]) <-> boardXYsym[j, k] = i);

% symmetry breaking constraints
constraint lex_lesseq(array1d(board), array1d(boardXsym));
constraint lex_lesseq(array1d(board), array1d(boardYsym));
constraint lex_lesseq(array1d(board), array1d(boardXYsym));

*/
% rows and columns symmetry
constraint forall (i,j in nRange where i < j) ((xhat[i] == xhat[j] /\ x[i] == x[j]) ->
        (if y[i] <= y[j] then yhat[i] <= yhat[j] else yhat[j] <= yhat[i] endif));

constraint forall (i,j in nRange where i < j) ((yhat[i] == yhat[j] /\ y[i] == y[j]) ->
        (if x[i] <= x[j] then xhat[i] <= xhat[j] else xhat[j] <= xhat[i] endif));

% three blocks symmetry
constraint forall (i,j,k in nRange where i < j /\ j < k)
        ((xhat[i] == xhat[j] /\ x[i] == x[j] /\ yhat[i] = yhat[k] /\ y[i] + y[j] = y[k]) ->
        (if x[i] <= x[k] then xhat[i] <= xhat[k] /\ xhat[i] = xhat[j] else xhat[k] <= xhat[i] /\ xhat[i] = xhat[j] endif));
constraint forall (i,j,k in nRange where i < j /\ j < k)
        ((yhat[i] == yhat[j] /\ y[i] == y[j] /\ xhat[i] = xhat[k] /\ x[i] + x[k] = x[k]) ->
        (if y[i] <= y[k] then yhat[i] <= yhat[k] /\ yhat[i] = yhat[j] else yhat[k] <= yhat[i] /\ yhat[i] = yhat[j] endif));

% implied constraints
constraint cumulative(xhat, x, y, l);
constraint cumulative(yhat, y, x, w);
%constraint forall (k in 1..w) (sum([y[i] | i in nRange where xhat[i] < k /\ xhat[i] + x[i] >= k]) <= l);
%constraint forall (k in 1..maxl) (sum([x[i] | i in nRange where yhat[i] < k /\ yhat[i] + y[i] >= k]) <= w);

% main problem constraints
constraint forall (i in nRange) (yhat[i] < l);
constraint diffn(xhat, yhat, x, y);

constraint forall (i in nRange) (xhat[i] + x[i] <= w);
constraint forall (i in nRange) (yhat[i] + y[i] <= l);

solve minimize l;
