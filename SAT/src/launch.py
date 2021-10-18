from time import time
from z3 import *


def base_model(instance, l):
    constraints = []
    vs = {}
    circuits = list(range(instance['n']))

    vs['B'] = [[[Bool(f'B_{i}_{j}_{k}') for k in circuits] for j in range(instance['w'])] for i in range(l)]

    return constraints, vs


def solve_SAT(instance, rotation, timeout=300000):
    print(f'W = {instance["w"]}, N = {instance["n"]}')

    start_time = time()
    elapsed_time = 0
    for l in range(instance['minl'], instance['maxl'] + 1):
        sol = Solver()
        constraints, vs = base_model(instance, l)
        setup_time = time() - start_time
        sol.set(timeout=timeout - elapsed_time)
        status = str(sol.check())
        solve_time = time() - start_time + setup_time
        elapsed_time += setup_time + solve_time

        if status == 'sat':
            print('FOUND OPTIMAL SOLUTION')
            model = sol.model()
            instance['solved'] = True
            instance['l'] = model[vs['l']].as_long()

            instance['time'] = f'setup: {setup_time:.2f} s, solve: {solve_time:.2f} s'
        elif status == 'unsat':
            print('UNSOLVABLE')
            instance['solved'] = False
        else:
            print('TIMEOUT')
            instance['solved'] = False
    return instance
