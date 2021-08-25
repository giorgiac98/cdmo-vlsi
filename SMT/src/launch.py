from z3 import Optimize, Ints, Int, Or, And, Not, Implies, Sum, If


def solve_SMT(instance, timeout=300000):
    assert all([k in instance for k in ('n', 'w', 'maxl', 'x', 'y')])
    components = list(range(instance['n']))
    print(f'\nW = {instance["w"]}, N = {instance["n"]}')
    opt = Optimize()
    vs = {}
    w, l = Ints('width length')
    vs['w'], vs['l'] = w, l
    # basic problem constraints
    constraints = [vs['w'] == instance["w"], vs['l'] == instance['maxl']]

    for i in components:
        x_i, y_i = Ints(f'x_{i} y_{i}')
        constraints.append(x_i == (instance['x'][i]))
        constraints.append(y_i == (instance['y'][i]))

        xhat_i, yhat_i = Ints(f'xhat_{i} yhat_{i}')
        constraints.append(xhat_i >= 0)
        constraints.append(xhat_i + x_i <= w)
        constraints.append(yhat_i >= 0)
        constraints.append(yhat_i < l)
        constraints.append(yhat_i + y_i <= l)
        vs[f'x_{i}'], vs[f'y_{i}'] = x_i, y_i
        vs[f'xhat_{i}'], vs[f'yhat_{i}'] = xhat_i, yhat_i

        # implied constraints: for each horizontal (and vertical) line, the sum of traversed sides is bounded
        constraints += [Sum([If(And(vs[f'xhat_{i}'] < col, col <= vs[f'xhat_{i}'] + vs[f'x_{i}']), vs[f'y_{i}'], 0)])
                        <= vs['w'] for col in range(instance['w'])]
        constraints += [Sum([If(And(vs[f'yhat_{i}'] < row, row <= vs[f'yhat_{i}'] + vs[f'y_{i}']), vs[f'x_{i}'], 0)])
                        <= vs['l'] for row in range(instance['maxl'])]

    no_overlap = [
        Or(vs[f'xhat_{i}'] + vs[f'x_{i}'] <= vs[f'xhat_{j}'], vs[f'yhat_{i}'] + vs[f'y_{i}'] <= vs[f'yhat_{j}'],
           vs[f'xhat_{j}'] + vs[f'x_{j}'] <= vs[f'xhat_{i}'], vs[f'yhat_{j}'] + vs[f'y_{j}'] <= vs[f'yhat_{i}'])
        for i in components for j in components if i < j]
    constraints += no_overlap

    opt.add(constraints)
    opt.set("timeout", timeout)
    opt.minimize(l)
    if str(opt.check()) == 'sat':
        print('SOLVED')
        model = opt.model()
        instance['solved'] = True
        instance['l'] = model[vs['l']].as_long()
        instance['xhat'] = [model[vs[f'xhat_{i}']].as_long() for i in components]
        instance['yhat'] = [model[vs[f'yhat_{i}']].as_long() for i in components]

    else:
        print('NOT SOLVED WITHIN TIME LIMIT')
        instance['solved'] = False
    return instance
