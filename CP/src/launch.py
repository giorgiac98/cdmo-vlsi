from minizinc import Instance, Model, Solver
from minizinc.result import Status
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from datetime import timedelta

def solve_CP(input):
    # Load the model from file
    model = Model("vlsi.mzn")
    # Find the MiniZinc solver configuration for Gecode
    gecode = Solver.lookup("gecode")
    # Create an Instance of the model for Gecode
    instance = Instance(gecode, model)
    # Assign 4 to n
    instance["w"] = input['w']
    instance['n'] = input['n']
    instance['x'] = input['x']
    instance['y'] = input['y']
    instance['maxl'] = input['maxl']

    result = instance.solve(timeout=timedelta(minutes=5))
    output = {'solved': result.status==Status.OPTIMAL_SOLUTION,
              'time': result.statistics['time'],
              'l': result['l'], 'xhat': result['xhat'], 'yhat': result['yhat']}
    output.update(input)

    return output


def solve_model(w, c, dim):
    # Load the model from file
    model = Model("vlsi.mzn")
    # Find the MiniZinc solver configuration for Gecode
    gecode = Solver.lookup("gecode")
    # Create an Instance of the model for Gecode
    instance = Instance(gecode, model)
    # Assign 4 to n
    instance["w"] = w
    instance['n'] = c
    instance['x'] = [x[0] for x in dim]
    instance['y'] = [y[1] for y in dim]
    instance['maxl'] = sum(instance['y'])


    result = instance.solve(timeout=timedelta(minutes=5))
    return instance, result


def plot(instance, width, height, blocks):
    colors = ['red', 'blue', 'green', 'cyan', 'pink', 'purple', 'brown', 'olive', 'grey', 'orange']
    if len(blocks) <= len(colors):
        fig, ax = plt.subplots()
        for i in range(0, len(blocks)):
            w,h,x,y = blocks[i]
            ax.add_patch(Rectangle((x,y), w, h, facecolor=colors[i], lw=1, alpha=0.75))

        ax.set_ylim(0, height)
        ax.set_xlim(0, width)
        ax.set_xlabel('x')
        ax.set_ylabel('y')
        ax.grid(True)
        plt.savefig(f'../out/fig-ins-{instance}.png')
    else:
        print('Not enough colors')


for i in range(1, 41):
    lines = []
    with open(f'../../instances/ins-{i}.txt', 'r') as f:
        lines = f.readlines()
    lines = [l.strip('\n') for l in lines]
    dim = [l.split(' ') for l in lines[2:]]
    dim = [[int(d[0]), int(d[1])] for d in dim]
    print(f'Solving instance {i}')
    print(f'dim: {dim}')
    w = int(lines[0].strip('\n'))
    c = int(lines[1].strip('\n'))

    instance, result = solve_model(w, c, dim)
    # Output
    print(result)
    print(result.status == Status.OPTIMAL_SOLUTION)
    print(result.statistics)
    out = f'{w} {result["l"]}\n{c}\n'
    out += '\n'.join([f'{dim[i][0]} {dim[i][1]} '
                      f'{result["xhat"][i]} {result["yhat"][i]}'
                      for i in range(c)])
    print('=====OUTPUT=====')
    print(out)

    with open(f'../out/ins-{i}.txt', 'w') as f:
        f.write(out)

    plot(i, w, result["l"], [(instance['x'][i], instance['y'][i],
        result["xhat"][i], result["yhat"][i]) for i in range(0,c)])
