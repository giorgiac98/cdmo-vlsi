from time import time
from z3 import *
from SMT.src.base_model import base_model
from SMT.src.array_model import array_model


def solve_SMT(instance, dual, rotation, kind='base', timeout=300000):
    print(f'W = {instance["w"]}, N = {instance["n"]}')
    opt = Optimize()
    start_time = time()
    if kind == 'base':
        constraints, vs = base_model(instance, dual, rotation)
    elif kind == 'array':
        constraints, vs = array_model(instance)
    else:
        raise ValueError('wrong model parameter, implemented models are: base, array')

    setup_time = time() - start_time
    opt.add(constraints)
    opt.set(timeout=timeout)
    opt.minimize(vs['l'])
    solve_time = time() - start_time + setup_time

    if str(opt.check()) == 'sat':
        print('FOUND OPTIMAL SOLUTION')
        model = opt.model()
        instance['solved'] = True
        instance['l'] = model[vs['l']].as_long()
        if kind == 'base':
            instance['x'] = [model[vs[f'x_{i}']].as_long() for i in range(instance['n'])]
            instance['y'] = [model[vs[f'y_{i}']].as_long() for i in range(instance['n'])]
            instance['xhat'] = [model[vs[f'xhat_{i}']].as_long() for i in range(instance['n'])]
            instance['yhat'] = [model[vs[f'yhat_{i}']].as_long() for i in range(instance['n'])]
            if rotation:
                instance['rotation'] = [model[vs[f'rotation_{i}']] for i in range(instance['n'])]
        else:
            instance['x'] = [model.eval(vs['X'][i]).as_long() for i in range(instance['n'])]
            instance['y'] = [model.eval(vs['Y'][i]).as_long() for i in range(instance['n'])]
            instance['xhat'] = [model.eval(vs['Xhat'][i]).as_long() for i in range(instance['n'])]
            instance['yhat'] = [model.eval(vs['Yhat'][i]).as_long() for i in range(instance['n'])]
        instance['fulltime'] = f'setup: {setup_time:.2f} s, solve: {solve_time:.2f} s'
        instance['time'] = setup_time + solve_time
    elif str(opt.check()) == 'unsat':
        print('UNSOLVABLE')
        instance['solved'] = False
    else:
        print('TIMEOUT')
        instance['solved'] = False
    return instance
