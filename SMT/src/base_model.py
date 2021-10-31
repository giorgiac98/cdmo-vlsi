from z3 import *


def lex_lesseq(x, y):
    # given arrays x and y, returns constraint imposing lex<= order between a and b
    # X1 ≤ Y1 ∧ (X1 = Y1 -> X2 ≤ Y2) ∧ (X1 = Y1 ∧ X2 = Y2 ... ∧ Xk-1 = Yk-1 -> Xk ≤ Yk)
    # note that in SAT ≤ is encoded as ->
    # more elegant but maybe less efficient:
    # And([Implies(And([x[i] == y[i] for i in range(k)]), Implies(x[k], y[k])) for k in range(len(x))])

    return And([Implies(x[0], y[0])] +
               [Implies(And([x[i] == y[i] for i in range(k)]), Implies(x[k], y[k]))
                for k in range(1, len(x))])


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


def base_model(instance, dual, rotation):
    vs = {}
    # define main problem variables and constraints
    w = IntVal(instance["w"])
    l = Int('length')
    circuits = list(range(instance['n']))
    vs['w'], vs['l'] = w, l
    # basic problem constraints
    constraints = [vs['l'] >= instance['minl'], vs['l'] <= instance['maxl']]

    for k in circuits:
        xhat_i, yhat_i = Ints(f'xhat_{k} yhat_{k}')
        vs[f'xhat_{k}'], vs[f'yhat_{k}'] = xhat_i, yhat_i

        if rotation:
            x_i, y_i = Ints(f'x_{k} y_{k}')
            rotation_i = Bool(f'rotation_{k}')
            vs[f'rotation_{k}'] = rotation_i
            constraints.append(If(rotation_i,
                                And(y_i == (instance['inputx'][k]), x_i == (instance['inputy'][k])),
                                And(y_i == (instance['inputy'][k]), x_i == (instance['inputx'][k]))))
        else:
            x_i = IntVal(instance['inputx'][k])
            y_i = IntVal(instance['inputy'][k])
        vs[f'x_{k}'], vs[f'y_{k}'] = x_i, y_i

        constraints.append(xhat_i >= 0)
        constraints.append(xhat_i < w)
        constraints.append(xhat_i + x_i <= w)
        constraints.append(yhat_i >= 0)
        constraints.append(yhat_i < l)
        constraints.append(yhat_i + y_i <= l)

        # channeling constraints
        if dual:
            xsym_i, ysym_i = Ints(f'xsym_{k} ysym_{k}')
            vs[f'xsym_{k}'], vs[f'ysym_{k}'] = xsym_i, ysym_i

            constraints.append(And(vs[f'xsym_{k}'] == (vs['w'] - vs[f'x_{k}'] - vs[f'xhat_{k}']),
                                   vs[f'ysym_{k}'] == (vs['l'] - vs[f'y_{k}'] - vs[f'yhat_{k}'])))

    if dual:
        for c in range(instance["w"]):
            xproj_c = Bool(f'xproj_{c}')
            vs[f'xproj_{c}'] = xproj_c
            constraints.append(xproj_c == (l == Sum([vs[f'y_{i}'] for i in circuits if vs[f'xhat_{i}'] == c])))
            xsymproj_c = Bool(f'xsymproj_{c}')
            vs[f'xsymproj_{c}'] = xsymproj_c
            constraints.append(xsymproj_c == (l == Sum([vs[f'y_{i}'] for i in circuits if vs[f'xsym_{i}'] == c])))

        for r in range(instance["maxl"]):
            yproj_r = Bool(f'yproj_{r}')
            vs[f'yproj_{r}'] = yproj_r
            constraints.append(yproj_r == (w == Sum([vs[f'x_{i}'] for i in circuits if vs[f'yhat_{i}'] == r])))
            ysymproj_r = Bool(f'ysymproj_{r}')
            vs[f'ysymproj_{r}'] = ysymproj_r
            constraints.append(ysymproj_r == (w == Sum([vs[f'x_{i}'] for i in circuits if vs[f'ysym_{i}'] == r])))

        f = {c: vs[f'xproj_{c}'] for c in range(instance["w"])}
        fsym = {c: vs[f'xsymproj_{c}'] for c in range(instance["w"])}
        g = {r: vs[f'yproj_{r}'] for r in range(instance["maxl"])}
        gsym = {r: vs[f'ysymproj_{r}'] for r in range(instance["maxl"])}
        constraints += [lex_lesseq(list(f.values()), list(fsym.values())),
                        lex_lesseq(list(g.values()), list(gsym.values()))]

    # implied constraints: for each horizontal (and vertical) line, the sum of traversed sides is bounded
    for col in range(instance['w']):
        constraints.append(Sum([If(And(vs[f'xhat_{i}'] < col, col <= vs[f'xhat_{i}'] + vs[f'x_{i}']), vs[f'y_{i}'], 0)
                                for i in circuits]) <= vs['l'])
    for row in range(instance['maxl']):
        constraints.append(Sum([If(And(vs[f'yhat_{i}'] < row, row <= vs[f'yhat_{i}'] + vs[f'y_{i}']), vs[f'x_{i}'], 0)
                                for i in circuits]) <= vs['w'])

    # no overlap constraints
    constraints += [
        Or(vs[f'xhat_{i}'] + vs[f'x_{i}'] <= vs[f'xhat_{j}'], vs[f'yhat_{i}'] + vs[f'y_{i}'] <= vs[f'yhat_{j}'],
           vs[f'xhat_{j}'] + vs[f'x_{j}'] <= vs[f'xhat_{i}'], vs[f'yhat_{j}'] + vs[f'y_{j}'] <= vs[f'yhat_{i}'])
        for i in circuits for j in circuits if i < j]

    # symmetry breaking
    # rows and columns symmetry
    constraints += [Implies(And(vs[f'xhat_{i}'] == vs[f'xhat_{j}'], vs[f'x_{i}'] == vs[f'x_{j}']),
                            If(vs[f'y_{i}'] <= vs[f'y_{j}'], vs[f'yhat_{j}'] <= vs[f'yhat_{i}'], vs[f'yhat_{i}'] <= vs[f'yhat_{j}']))
                    for i in circuits for j in circuits if i < j]

    constraints += [Implies(And(vs[f'yhat_{i}'] == vs[f'yhat_{j}'], vs[f'y_{i}'] == vs[f'y_{j}']),
                            If(vs[f'x_{i}'] <= vs[f'x_{j}'], vs[f'xhat_{j}'] <= vs[f'xhat_{i}'], vs[f'xhat_{i}'] <= vs[f'xhat_{j}']))
                    for i in circuits for j in circuits if i < j]
    # three block symmetry
    constraints += [Implies(And(vs[f'xhat_{i}'] == vs[f'xhat_{j}'], vs[f'x_{i}'] == vs[f'x_{j}'],
                                vs[f'yhat_{i}'] == vs[f'yhat_{k}'], vs[f'y_{i}'] + vs[f'y_{j}'] == vs[f'y_{k}']),
                            If(vs[f'x_{i}'] <= vs[f'x_{k}'],
                                And(vs[f'xhat_{i}'] <= vs[f'xhat_{k}'], vs[f'xhat_{i}'] == vs[f'xhat_{j}']),
                                And(vs[f'xhat_{k}'] <= vs[f'xhat_{i}'], vs[f'xhat_{i}'] == vs[f'xhat_{j}'])))
                    for i in circuits for j in circuits for k in circuits if i < j and j < k]

    constraints += [Implies(And(vs[f'yhat_{i}'] == vs[f'yhat_{j}'], vs[f'y_{i}'] == vs[f'y_{j}'],
                                vs[f'xhat_{i}'] == vs[f'xhat_{k}'], vs[f'x_{i}'] + vs[f'x_{j}'] == vs[f'x_{k}']),
                            If(vs[f'y_{i}'] <= vs[f'y_{k}'],
                                And(vs[f'yhat_{i}'] <= vs[f'yhat_{k}'], vs[f'yhat_{i}'] == vs[f'yhat_{j}']),
                                And(vs[f'yhat_{k}'] <= vs[f'yhat_{i}'], vs[f'yhat_{i}'] == vs[f'yhat_{j}'])))
                    for i in circuits for j in circuits for k in circuits if i < j and j < k]

    return constraints, vs
