from z3 import *


def solve_SMT(instance, timeout=300000):
    # assert all([k in instance for k in ('n', 'w', 'maxl', 'X', 'Y')])
    print(f'W = {instance["w"]}, N = {instance["n"]}')
    opt = Optimize()
    vs = {}
    # define main problem variables and constraints
    w, l = Ints('width length')
    components = [Int(f'c_{i}') for i in range(instance['n'])]
    X = Array('X', IntSort(), IntSort())
    Y = Array('Y', IntSort(), IntSort())
    vs['w'], vs['l'] = w, l
    vs['X'], vs['Y'] = X, Y

    constraints = [vs['w'] == instance["w"], vs['l'] >= instance['minl'], vs['l'] <= instance['maxl']]
    # force components idx to be betwenn 0 and 0, and all different
    constraints += [And(ci >= 0, ci < instance['n']) for ci in components]
    constraints += [Distinct(components)]
    for ci, xi, yi in zip(components, instance['inputx'], instance['inputy']):
        constraints.append(And(X[ci] == xi, Y[ci] == yi))

    for i, ci in enumerate(components):
        # x_i, y_i = Ints(f'x_{i} y_{i}')
        # constraints.append(x_i == (instance['X'][i]))
        # constraints.append(y_i == (instance['Y'][i]))

        xhat_i, yhat_i = Ints(f'xhat_{i} yhat_{i}')
        constraints.append(xhat_i >= 0)
        constraints.append(xhat_i < w)
        constraints.append(xhat_i + X[i] <= w)
        constraints.append(yhat_i >= 0)
        constraints.append(yhat_i < l)
        constraints.append(yhat_i + Y[i] <= l)

        # area_i = Int(f'area_{i}')
        # constraints.append(area_i == (x_i * y_i))

        # vs[f'x_{i}'], vs[f'y_{i}'] = x_i, y_i
        vs[f'xhat_{i}'], vs[f'yhat_{i}'] = xhat_i, yhat_i
        # vs[f'area_{i}'] = area_i

        # # implied constraints: for each horizontal (and vertical) line, the sum of traversed sides is bounded
        constraints += [Sum([If(And(vs[f'xhat_{i}'] < col, col <= vs[f'xhat_{i}'] + X[i]), Y[i], 0)])
                        <= vs['w'] for col in range(instance['w'])]
        constraints += [Sum([If(And(vs[f'yhat_{i}'] < row, row <= vs[f'yhat_{i}'] + Y[i]), X[i], 0)])
                        <= vs['l'] for row in range(instance['maxl'])]
    # no overlap constraints
    constraints += [
        Or(vs[f'xhat_{i}'] + X[i] <= vs[f'xhat_{j}'], vs[f'yhat_{i}'] + Y[i] <= vs[f'yhat_{j}'],
           vs[f'xhat_{j}'] + X[j] <= vs[f'xhat_{i}'], vs[f'yhat_{j}'] + Y[j] <= vs[f'yhat_{i}'])
        for i in range(instance['n']) for j in range(instance['n']) if i < j]

    # symmetry breaking?
    constraints += [Implies(And(vs[f'xhat_{i}'] == vs[f'xhat_{j}'], X[i] == X[j]),
                            vs[f'yhat_{i}'] <= vs[f'yhat_{j}'])
                    for i in range(instance['n']) for j in range(instance['n']) if i < j]

    constraints += [Implies(And(vs[f'yhat_{i}'] == vs[f'yhat_{j}'], Y[i] == Y[j]),
                            vs[f'xhat_{i}'] <= vs[f'xhat_{j}'])
                    for i in range(instance['n']) for j in range(instance['n']) if i < j]

    # order using point in the grid - not working
    # constraints += [w * vs[f'yhat_{i}'] + vs[f'xhat_{i}'] < w * vs[f'yhat_{i + 1}'] + vs[f'xhat_{i + 1}']
    #                 for i in range(instance['n'] - 1)]

    # order using areas - working but slow
    # constraints += [X[i] * Y[i] <= X[i + 1] * Y[i + 1]
    #                 for i in range(instance['n'] - 1)]

    opt.add(constraints)
    opt.set("timeout", timeout)
    opt.minimize(l)
    if str(opt.check()) == 'sat':
        print('FOUND OPTIMAL SOLUTION')
        model = opt.model()
        instance['solved'] = True
        instance['l'] = model[vs['l']].as_long()
        instance['x'] = [model.eval(vs['X'][i]).as_long() for i in range(instance['n'])]
        instance['y'] = [model.eval(vs['Y'][i]).as_long() for i in range(instance['n'])]
        instance['xhat'] = [model[vs[f'xhat_{i}']].as_long() for i in range(instance['n'])]
        instance['yhat'] = [model[vs[f'yhat_{i}']].as_long() for i in range(instance['n'])]
        # instance['time'] = opt.statistics()
    elif str(opt.check()) == 'unsat':
        print('UNSOLVABLE')
        instance['solved'] = False
    else:
        print('TIMEOUT')
        instance['solved'] = False
    return instance
