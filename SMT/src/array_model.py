from z3 import *


def array_model(instance):
    vs = {}
    # define main problem variables and constraints
    w, l = Ints('width length')
    components = [Int(f'c_{i}') for i in range(instance['n'])]
    X = Array('X', IntSort(), IntSort())
    Y = Array('Y', IntSort(), IntSort())
    Xhat = Array('Xhat', IntSort(), IntSort())
    Yhat = Array('Yhat', IntSort(), IntSort())
    vs['w'], vs['l'] = w, l
    vs['X'], vs['Y'] = X, Y
    vs['Xhat'], vs['Yhat'] = Xhat, Yhat

    constraints = [vs['w'] == instance["w"], vs['l'] >= instance['minl'], vs['l'] <= instance['maxl']]
    # force components idx to be between 0 and 0, and all different
    constraints += [And(ci >= 0, ci < instance['n']) for ci in components]
    constraints += [Distinct(components)]
    for ci, xi, yi in zip(components, instance['inputx'], instance['inputy']):
        constraints.append(And(X[ci] == xi, Y[ci] == yi))
        constraints.append(And(Xhat[ci] >= 0, Xhat[ci] < w, Xhat[ci] + X[ci] <= w))
        constraints.append(And(Yhat[ci] >= 0, Yhat[ci] < l, Yhat[ci] + Y[ci] <= l))
        # implied constraints: for each horizontal (and vertical) line, the sum of traversed sides is bounded
        # FIXME definitely wrong
        constraints += [Sum([If(And(Xhat[ci] < col, col <= Xhat[ci] + X[ci]), Y[ci], 0)])
                        <= vs['w'] for col in range(instance['w'])]
        constraints += [Sum([If(And(Yhat[ci] < row, row <= Yhat[ci] + Y[ci]), X[ci], 0)])
                        <= vs['l'] for row in range(instance['maxl'])]

    # for i, ci in enumerate(components):
        # area_i = Int(f'area_{i}')
        # constraints.append(area_i == (X[i] * Y[i]))
        # vs[f'area_{i}'] = area_i


    # no overlap constraints
    constraints += [
        Or(Xhat[i] + X[i] <= Xhat[j], Yhat[i] + Y[i] <= Yhat[j],
           Xhat[j] + X[j] <= Xhat[i], Yhat[j] + Y[j] <= Yhat[i])
        for i in range(instance['n']) for j in range(instance['n']) if i < j]

    # symmetry breaking?
    constraints += [Implies(And(Xhat[i] == Xhat[j], X[i] == X[j]),
                            Yhat[i] <= Yhat[j])
                    for i in range(instance['n']) for j in range(instance['n']) if i < j]

    constraints += [Implies(And(Yhat[i] == Yhat[j], Y[i] == Y[j]),
                            Xhat[i] <= Xhat[j])
                    for i in range(instance['n']) for j in range(instance['n']) if i < j]

    # order using point in the grid - slow
    # constraints += [w * Yhat[i] + Xhat[i] < w * Yhat[i + 1] + Xhat[i + 1]
    #                 for i in range(instance['n'] - 1)]

    # order using areas - slow
    # constraints += [vs[f'area_{i}'] <= vs[f'area_{i + 1}']
    #                 for i in range(instance['n'] - 1)]

    return constraints, vs
