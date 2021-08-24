import numpy as np
from z3 import Optimize, Ints, Int, Or, And, Not, Implies, Sum
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle


def plot(width, height, blocks):
    colors = ['red', 'blue', 'green', 'cyan', 'pink', 'purple', 'brown', 'olive', 'grey', 'orange']
    if len(blocks) <= len(colors):
        fig, ax = plt.subplots()
        for i, (w, h, x, y) in enumerate(blocks):
            ax.add_patch(Rectangle((x, y), w, h, facecolor=colors[i], label=i, lw=1, alpha=0.75))

        ax.set_ylim(0, height)
        ax.set_xlim(0, width)
        ax.set_xlabel('x')
        ax.set_ylabel('y')
        ax.grid(True)
        ax.legend()
        plt.show()
    else:
        print('NOT ENOUGH COLORS')


for i in range(1, 41):
    with open(f'../../instances/ins-{i}.txt') as f:
        lines = f.readlines()
    lines = [l.strip('\n') for l in lines]
    dim = [l.split(' ') for l in lines[2:]]
    xy = np.array(list(map(lambda xy: (int(xy[0]), int(xy[1])), dim)))

    instance = {"w": int(lines[0].strip('\n')),
                'n': int(lines[1].strip('\n')),
                'x': xy[:, 0], 'y': xy[:, 1]}
    print('=' * 42 + f'\nINSTANCE {i}\nW = {instance["w"]}, N = {instance["n"]}')
    opt = Optimize()
    vs = {}
    w, l = Ints('width length')
    vs['w'], vs['l'] = w, l
    # basic problem constraints
    constraints = [vs['w'] == instance["w"], vs['l'] > 0]

    for i in range(instance['n']):
        x_i, y_i = Ints(f'x_{i} y_{i}')
        constraints.append(x_i == int(instance['x'][i]))
        constraints.append(y_i == int(instance['y'][i]))

        xhat_i, yhat_i = Ints(f'xhat_{i} yhat_{i}')
        constraints.append(xhat_i >= 0)
        constraints.append(xhat_i + x_i <= w)
        constraints.append(yhat_i >= 0)
        constraints.append(yhat_i < l)
        constraints.append(yhat_i + y_i <= l)
        vs[f'x_{i}'], vs[f'y_{i}'] = x_i, y_i
        vs[f'xhat_{i}'], vs[f'yhat_{i}'] = xhat_i, yhat_i

    no_overlap = [
        Or(vs[f'xhat_{i}'] + vs[f'x_{i}'] <= vs[f'xhat_{j}'], vs[f'yhat_{i}'] + vs[f'y_{i}'] <= vs[f'yhat_{j}'],
           vs[f'xhat_{j}'] + vs[f'x_{j}'] <= vs[f'xhat_{i}'], vs[f'yhat_{j}'] + vs[f'y_{j}'] <= vs[f'yhat_{i}'])
        for i in range(instance['n']) for j in range(instance['n']) if i != j]

    constraints += no_overlap

    opt.add(constraints)
    opt.set("timeout", 3000)
    opt.minimize(l)
    print(opt.check())
    model = opt.model()
    out = f"{model[vs['w']].as_long()} {model[vs['l']].as_long()}\n{instance['n']}\n"
    out += '\n'.join([f"{model[vs[f'x_{i}']].as_long()} {model[vs[f'y_{i}']].as_long()} "
                      f"{model[vs[f'xhat_{i}']].as_long()} {model[vs[f'yhat_{i}']].as_long()}"
                      for i in range(instance['n'])])
    print('SOLVED, SHOWING OUTPUT')
    print(out)

    res = [(model[vs[f'x_{i}']].as_long(), model[vs[f'y_{i}']].as_long(),
            model[vs[f'xhat_{i}']].as_long(), model[vs[f'yhat_{i}']].as_long())
           for i in range(instance['n'])]
    plot(model[vs['w']].as_long(), model[vs['l']].as_long(), res)
