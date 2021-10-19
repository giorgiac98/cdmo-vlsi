from time import time
from itertools import combinations

import numpy as np
from z3 import *


def at_least_one(vs):
    return Or(vs)


def at_most_one(vs):
    return And([Not(And(pair[0], pair[1])) for pair in combinations(vs, 2)])


def exactly_one(vs):
    return And(at_least_one(vs), at_most_one(vs))


def base_model(instance, l):
    constraints = []
    vs = {}
    circuits = list(range(instance['n']))
    w = instance['w']

    board = [[[Bool(f'B_{i}_{j}_{k}') for k in circuits] for j in range(w)] for i in range(l)]
    vs['B'] = board

    constraints += [at_most_one(board[i][j]) for j in range(w) for i in range(l)]

    for c, x, y in zip(circuits, instance['inputx'], instance['inputy']):
        possible_areas = []
        for xhat in range(w - x + 1):
            for yhat in range(l - y + 1):
                possible_areas.append(And([board[i][j][c]
                                           for i in range(yhat, yhat + y)
                                           for j in range(xhat, xhat + x)]))
        constraints.append(exactly_one(possible_areas))
    return constraints, vs


def solve_SAT(instance, rotation, timeout=300000):
    print(f'W = {instance["w"]}, N = {instance["n"]}')
    instance['solved'] = False
    start_time = time()
    elapsed_time = 0

    for l in range(instance['minl'], instance['maxl'] + 1):
        sol = Solver()
        constraints, vs = base_model(instance, l)
        setup_time = time() - start_time
        sol.set(timeout=int(timeout - elapsed_time))
        sol.add(constraints)
        status = str(sol.check())
        solve_time = time() - start_time + setup_time
        elapsed_time += setup_time + solve_time

        if status == 'sat':
            print('FOUND OPTIMAL SOLUTION')
            model = sol.model()
            instance['solved'] = True
            instance['l'] = l
            board = np.array([[[is_true(model[vs['B'][i][j][k]])
                                for k in range(instance['n'])]
                               for j in range(instance['w'])]
                              for i in range(l)])
            xhats, yhats = [], []
            for k in range(instance['n']):
                yhat, xhat = np.unravel_index(board[:, :, k].argmax(), board[:, :, 0].shape)
                xhats.append(xhat)
                yhats.append(yhat)
            instance['x'] = instance['inputx']
            instance['y'] = instance['inputy']
            instance['xhat'] = xhats
            instance['yhat'] = yhats
            instance['time'] = f'setup: {setup_time:.2f} s, solve: {solve_time:.2f} s'
            return instance
        elif status == 'unsat':
            print(f'UNSAT WITH L = {l}')
        else:
            print('TIMEOUT')
            break
    return instance
