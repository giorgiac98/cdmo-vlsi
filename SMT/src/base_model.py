from z3 import *


def base_model(instance):
    vs = {}
    # define main problem variables and constraints
    w, l = Ints('width length')
    components = list(range(instance['n']))
    # board for dual model
    board = [[Int(f'B_{c}_{r}') for r in range(instance["w"])] for c in range(instance['maxl'])]
    vs['w'], vs['l'] = w, l
    vs['board'] = board
    # basic problem constraints
    constraints = [vs['w'] == instance["w"], vs['l'] >= instance['minl'], vs['l'] <= instance['maxl']]

    for i in components:
        x_i, y_i = Ints(f'x_{i} y_{i}')
        xhat_i, yhat_i = Ints(f'xhat_{i} yhat_{i}')
        area_i = Int(f'area_{i}')
        vs[f'x_{i}'], vs[f'y_{i}'] = x_i, y_i
        vs[f'xhat_{i}'], vs[f'yhat_{i}'] = xhat_i, yhat_i
        vs[f'area_{i}'] = area_i

        constraints.append(x_i == (instance['inputx'][i]))
        constraints.append(y_i == (instance['inputy'][i]))

        constraints.append(xhat_i >= 0)
        constraints.append(xhat_i < w)
        constraints.append(xhat_i + x_i <= w)
        constraints.append(yhat_i >= 0)
        constraints.append(yhat_i < l)
        constraints.append(yhat_i + y_i <= l)

        constraints.append(area_i == (x_i * y_i))




    # implied constraints: for each horizontal (and vertical) line, the sum of traversed sides is bounded
    for col in range(instance['w']):
        constraints.append(Sum([If(And(vs[f'xhat_{i}'] < col, col <= vs[f'xhat_{i}'] + vs[f'x_{i}']), vs[f'y_{i}'], 0)
                                for i in components]) <= vs['w'])
    for row in range(instance['maxl']):
        constraints.append(Sum([If(And(vs[f'yhat_{i}'] < row, row <= vs[f'yhat_{i}'] + vs[f'y_{i}']), vs[f'x_{i}'], 0)
                                for i in components]) <= vs['l'])

    # no overlap constraints
    constraints += [
        Or(vs[f'xhat_{i}'] + vs[f'x_{i}'] <= vs[f'xhat_{j}'], vs[f'yhat_{i}'] + vs[f'y_{i}'] <= vs[f'yhat_{j}'],
           vs[f'xhat_{j}'] + vs[f'x_{j}'] <= vs[f'xhat_{i}'], vs[f'yhat_{j}'] + vs[f'y_{j}'] <= vs[f'yhat_{i}'])
        for i in components for j in components if i < j]

    # symmetry breaking?
    constraints += [Implies(And(vs[f'xhat_{i}'] == vs[f'xhat_{j}'], vs[f'x_{i}'] == vs[f'x_{j}']),
                            vs[f'yhat_{i}'] <= vs[f'yhat_{j}'])
                    for i in components for j in components if i < j]

    constraints += [Implies(And(vs[f'yhat_{i}'] == vs[f'yhat_{j}'], vs[f'y_{i}'] == vs[f'y_{j}']),
                            vs[f'xhat_{i}'] <= vs[f'xhat_{j}'])
                    for i in components for j in components if i < j]

    return constraints, vs