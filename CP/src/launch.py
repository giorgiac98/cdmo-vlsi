from minizinc import Instance, Model, Solver
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

def solve_model(w, c, dim):
    # Load the model from file
    model = Model("vlsi.mzn")
    # Find the MiniZinc solver configuration for Gecode
    gecode = Solver.lookup("gecode")
    # Create an Instance of the model for Gecode
    instance = Instance(gecode, model)
    # Assign 4 to n
    instance["w"] = w
    instance['c'] = c
    instance['dx'] = [x[0] for x in dim]
    instance['dy'] = [y[0] for y in dim]

    result = instance.solve()
    return instance, result

def plot(width, height, blocks):
    colors = ['red', 'blue', 'green', 'cyan', 'pink', 'purple', 'brown', 'olive', 'grey', 'orange']

    fig, ax = plt.subplots()
    for i in range(0, len(blocks)):
        w,h,x,y = blocks[i]
        ax.add_patch(Rectangle((x,y), w, h, facecolor=colors[i], lw=1))

    ax.set_ylim(0, height)
    ax.set_xlim(0, width)
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.grid(True)
    plt.show()


for i in range(1,41):
    lines = []
    with open(f'../../instances/ins-{i}.txt') as f:
        lines = f.readlines()
    lines = [l.strip('\n') for l in lines]
    dim = [l.split(' ') for l in lines[2:]]
    dim = [[int(d[0]), int(d[1])] for d in dim]
    w = int(lines[0].strip('\n'))
    c = int(lines[1].strip('\n'))

    instance, result = solve_model(w, c, dim)
    # Output
    print(result)
    print(result["h"])
    print(result["x"])
    print(result["y"])

    #with open(f'out/ins-{i}.txt') as f:


    plot(w, result["h"], [(instance['dx'][i], instance['dy'][i], result["x"][i], result["y"][i]) for i in range(0,c)])
