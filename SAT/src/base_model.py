from itertools import combinations
from z3 import *
import numpy as np


def lex_lesseq(x, y):
    # given arrays x and y, returns constraint imposing lex<= order between a and b
    # X1 ≤ Y1 ∧ (X1 = Y1 -> X2 ≤ Y2) ∧ (X1 = Y1 ∧ X2 = Y2 ... ∧ Xk-1 = Yk-1 -> Xk ≤ Yk)
    # note that in SAT ≤ is encoded as ->
    # more elegant but maybe less efficient:
    # And([Implies(And([x[i] == y[i] for i in range(k)]), Implies(x[k], y[k])) for k in range(len(x))])

    return And([Implies(x[0], y[0])] +
               [Implies(And([x[i] == y[i] for i in range(k)]), Implies(x[k], y[k]))
                for k in range(1, len(x))])


def at_least_one(vs):
    return Or(vs)


def at_most_one(vs):
    return And([Not(And(pair[0], pair[1])) for pair in combinations(vs, 2)])


def exactly_one(vs):
    return And(at_least_one(vs), at_most_one(vs))


def equal_counts(a, b):
    return And([Not(Xor(ai, bi)) for ai, bi in zip(a, b)])


def base_model(instance, l, rotation):
    constraints = []
    vs = {}
    circuits = list(range(instance['n']))
    w = instance['w']

    board = [[[Bool(f'B_{i}_{j}_{k}') for k in circuits] for j in range(w)] for i in range(l)]
    vs['B'] = board
    # xproj = [[Bool(f'xproj_{k}_{i}') for i in range(l)] for k in circuits]
    # yproj = [[Bool(f'yproj_{k}_{i}') for i in range(w)] for k in circuits]
    # vs['xproj'] = xproj
    # vs['yproj'] = yproj
    # for k in circuits:
    #     for i in range(l):
    #         constraints.append(Implies(at_least_one([board[i][j][k] for j in range(w)]), xproj[k][i]))
    #     for j in range(w):
    #         constraints.append(Implies(at_least_one([board[i][j][k] for i in range(l)]), yproj[k][j]))
    #
    # for c1 in circuits:
    #     for c2 in range(c1, len(circuits)):
    #         for i in range(l):
    #             # FIXME equal counts è sbagliato, noi vogliamo che abbiano lo stesso numero di bit a true
    #             constraints.append(Implies(And(xproj[c1][i], xproj[c2][i], equal_counts(yproj[c1], yproj[c2])),
    #                                        lex_lesseq(yproj[c1], yproj[c2])))

    # no overlap constraint
    constraints += [exactly_one(board[i][j]) for j in range(w) for i in range(l)]

    for c, x, y in zip(circuits, instance['inputx'], instance['inputy']):
        possible_locations = []
        for xhat in range(w - x + 1):
            for yhat in range(l - y + 1):
                possible_locations.append(And([board[i][j][c]
                                               for i in range(yhat, yhat + y)
                                               for j in range(xhat, xhat + x)]))
        if rotation and x != y:
            for xhat in range(w - y + 1):
                for yhat in range(l - x + 1):
                    possible_locations.append(And([board[i][j][c]
                                                   for i in range(yhat, yhat + x)
                                                   for j in range(xhat, xhat + y)]))
        # each circuit is placed in exactly one location
        constraints.append(exactly_one(possible_locations))

    # symmetry breaking constraints
    slice0 = [board[i][j][0] for j in range(w) for i in range(l)]
    slice1 = [board[i][j][1] for j in range(w) for i in range(l)]
    constraints.append(lex_lesseq(slice0, slice1))

    return constraints, vs


def get_solution(B, model, instance, rotation):
    board = np.array([[[is_true(model[B[i][j][k]])
                        for k in range(instance['n'])]
                       for j in range(instance['w'])]
                      for i in range(instance['l'])])
    xs, ys = [], []
    xhats, yhats = [], []
    rotations = [] if rotation else None
    for k in range(instance['n']):
        yhat, xhat = np.unravel_index(board[:, :, k].argmax(), board[:, :, 0].shape)
        y = board[:, xhat, k].sum()
        x = board[yhat, :, k].sum()
        xhats.append(xhat)
        yhats.append(yhat)
        xs.append(x)
        ys.append(y)
        if rotation:
            rotations.append(False if (x, y) == (instance['inputx'][k], instance['inputy'][k]) else True)
    return xs, ys, xhats, yhats, rotations
