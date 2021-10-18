from z3 import *


def lex(x, y):
    # given arrays x and y, returns constraint imposing lex<= order between a and b
    # X1 ≤ Y1 ∧
    # (X1 = Y1 -> X2 ≤ Y2) ∧
    # (X1 = Y1 ∧ X2 = Y2 -> X3 ≤ Y3) ...
    # (X1 = Y1 ∧ X2 = Y2 ... ∧ Xk-1 = Yk-1 -> Xk ≤ Yk)
    # more elegant but maybe less efficient:
    # And([Implies(And([x[i] == y[i] for i in range(k)]), x[k] <= y[k]) for k in range(len(x))])

    return And([x[0] <= y[0]] +
               [Implies(And([x[i] == y[i] for i in range(k)]), x[k] <= y[k]) for k in range(1, len(x))])


def flatten(matrix):
    return [cell for row in matrix for cell in row]


def base_model(instance, rotation):
    vs = {}
    # define main problem variables and constraints
    w, l = Ints('width length')
    components = list(range(instance['n']))
    # board for dual model
    #board = [[Int(f'B_{c}_{r}') for r in range(instance["w"])] for c in range(instance['maxl'])]
    vs['w'], vs['l'] = w, l
    #vs['board'] = board
    # basic problem constraints
    constraints = [vs['w'] == instance["w"], vs['l'] >= instance['minl'], vs['l'] <= instance['maxl']]

    for i in components:
        x_i, y_i = Ints(f'x_{i} y_{i}')
        xhat_i, yhat_i = Ints(f'xhat_{i} yhat_{i}')
        area_i = Int(f'area_{i}')
        vs[f'x_{i}'], vs[f'y_{i}'] = x_i, y_i
        vs[f'xhat_{i}'], vs[f'yhat_{i}'] = xhat_i, yhat_i
        vs[f'area_{i}'] = area_i

        if rotation:
            rotation_i = Bool(f'rotation_{i}')
            vs[f'rotation_{i}'] = rotation_i
            constraints.append(If(rotation_i, x_i == (instance['inputy'][i]), x_i == (instance['inputx'][i])))
            constraints.append(If(rotation_i, y_i == (instance['inputx'][i]), y_i == (instance['inputy'][i])))
        else:
            constraints.append(x_i == (instance['inputx'][i]))
            constraints.append(y_i == (instance['inputy'][i]))

        constraints.append(xhat_i >= 0)
        constraints.append(xhat_i < w)
        constraints.append(xhat_i + x_i <= w)
        constraints.append(yhat_i >= 0)
        constraints.append(yhat_i < l)
        constraints.append(yhat_i + y_i <= l)

        constraints.append(area_i == (x_i * y_i))

        # channeling constraints
        #constraints += [(board[c][r] == i) == (And(vs[f'xhat_{i}'] <= r, vs[f'xhat_{i}'] + vs[f'x_{i}'] > r,
        #                                           vs[f'yhat_{i}'] <= c, vs[f'yhat_{i}'] + vs[f'y_{i}'] > c))
        #                for r in range(instance["w"]) for c in range(instance['maxl'])]

        # implied constraints: for each component i, # of cells of the board with value i must be equal to area_i
        #constraints.append(Sum([If(board[c][r] == i, 1, 0)
        #                        for r in range(instance["w"]) for c in range(instance['maxl'])])
        #                   == area_i)

    # implied constraints: for each horizontal (and vertical) line, the sum of traversed sides is bounded
    for col in range(instance['w']):
        constraints.append(Sum([If(And(vs[f'xhat_{i}'] < col, col <= vs[f'xhat_{i}'] + vs[f'x_{i}']), vs[f'y_{i}'], 0)
                                for i in components]) <= vs['l'])
    for row in range(instance['maxl']):
        constraints.append(Sum([If(And(vs[f'yhat_{i}'] < row, row <= vs[f'yhat_{i}'] + vs[f'y_{i}']), vs[f'x_{i}'], 0)
                                for i in components]) <= vs['w'])

    # board constraints
    #constraints += [And(board[c][r] >= 0, board[c][r] <= instance['n'])
    #                for r in range(instance["w"]) for c in range(instance['maxl'])]

    # no overlap constraints
    constraints += [
        Or(vs[f'xhat_{i}'] + vs[f'x_{i}'] <= vs[f'xhat_{j}'], vs[f'yhat_{i}'] + vs[f'y_{i}'] <= vs[f'yhat_{j}'],
           vs[f'xhat_{j}'] + vs[f'x_{j}'] <= vs[f'xhat_{i}'], vs[f'yhat_{j}'] + vs[f'y_{j}'] <= vs[f'yhat_{i}'])
        for i in components for j in components if i < j]

    # symmetry breaking
    # rows and columns symmetry
    constraints += [Implies(And(vs[f'xhat_{i}'] == vs[f'xhat_{j}'], vs[f'x_{i}'] == vs[f'x_{j}']),
                            If(vs[f'y_{i}'] <= vs[f'y_{j}'], vs[f'yhat_{j}'] <= vs[f'yhat_{i}'], vs[f'yhat_{i}'] <= vs[f'yhat_{j}']))
                    for i in components for j in components if i < j]

    constraints += [Implies(And(vs[f'yhat_{i}'] == vs[f'yhat_{j}'], vs[f'y_{i}'] == vs[f'y_{j}']),
                            If(vs[f'x_{i}'] <= vs[f'x_{j}'], vs[f'xhat_{j}'] <= vs[f'xhat_{i}'], vs[f'xhat_{i}'] <= vs[f'xhat_{j}']))
                    for i in components for j in components if i < j]
    # three block symmetry
    constraints += [Implies(And(vs[f'xhat_{i}'] == vs[f'xhat_{j}'], vs[f'x_{i}'] == vs[f'x_{j}'],
                                vs[f'yhat_{i}'] == vs[f'yhat_{k}'], vs[f'y_{i}'] + vs[f'y_{j}'] == vs[f'y_{k}']),
                            If(vs[f'x_{i}'] <= vs[f'x_{k}'],
                                And(vs[f'xhat_{i}'] <= vs[f'xhat_{k}'], vs[f'xhat_{i}'] == vs[f'xhat_{j}']),
                                And(vs[f'xhat_{k}'] <= vs[f'xhat_{i}'], vs[f'xhat_{i}'] == vs[f'xhat_{j}'])))
                    for i in components for j in components for k in components if i < j and j < k]

    constraints += [Implies(And(vs[f'yhat_{i}'] == vs[f'yhat_{j}'], vs[f'y_{i}'] == vs[f'y_{j}'],
                                vs[f'xhat_{i}'] == vs[f'xhat_{k}'], vs[f'x_{i}'] + vs[f'x_{j}'] == vs[f'x_{k}']),
                            If(vs[f'y_{i}'] <= vs[f'y_{k}'],
                                And(vs[f'yhat_{i}'] <= vs[f'yhat_{k}'], vs[f'yhat_{i}'] == vs[f'yhat_{j}']),
                                And(vs[f'yhat_{k}'] <= vs[f'yhat_{i}'], vs[f'yhat_{i}'] == vs[f'yhat_{j}'])))
                    for i in components for j in components for k in components if i < j and j < k]

    #constraints.append(lex(flatten(board),
    #                       [board[j][i] for i in range(instance['w']) for j in range(instance['maxl'] - 1, -1, -1)]))
    #constraints.append(lex(flatten(board),
    #                       [board[j][i] for i in range(instance['w'] - 1, -1, -1) for j in range(instance['maxl'])]))
    #constraints.append(lex(flatten(board),
    #                       [board[j][i] for i in range(instance['w'] - 1, -1, -1) for j in range(instance['maxl'] - 1, -1, -1)]))

    return constraints, vs
