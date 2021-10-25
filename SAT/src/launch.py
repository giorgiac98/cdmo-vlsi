from time import time
from z3 import Solver
from SAT.src.base_model import base_model, get_solution


def solve_SAT(instance, rotation, timeout=300000):
    print(f'W = {instance["w"]}, N = {instance["n"]}')
    instance['solved'] = False
    start_time = time()
    elapsed_time = 0

    for l in range(instance['minl'], instance['maxl'] + 1):
        sol = Solver()
        constraints, vs = base_model(instance, l, rotation)
        setup_time = time() - start_time
        elapsed_time += setup_time
        sol.set(timeout=int(timeout - elapsed_time))
        sol.add(constraints)
        status = str(sol.check())
        solve_time = time() - start_time + setup_time
        elapsed_time += solve_time

        if status == 'sat':
            print('FOUND OPTIMAL SOLUTION')
            instance['solved'] = True
            instance['l'] = l
            xs, ys, xhats, yhats, rotations = get_solution(vs['B'], sol.model(), instance, rotation)
            instance['x'] = xs
            instance['y'] = ys
            instance['xhat'] = xhats
            instance['yhat'] = yhats
            instance['rotation'] = rotations
            instance['fulltime'] = f'setup: {setup_time:.2f} s, solve: {solve_time:.2f} s'
            instance['time'] = setup_time + solve_time
            return instance
        elif status == 'unsat':
            print(f'UNSAT WITH L = {l}')
        else:
            print('TIMEOUT')
            break
    return instance
