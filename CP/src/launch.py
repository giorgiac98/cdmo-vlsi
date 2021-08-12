from minizinc import Instance, Model, Solver
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

def plot(width, height, blocks):
    fig, ax = plt.subplots()
    for w,h,x,y,c in blocks:
        ax.add_patch(Rectangle((x,y), w, h, facecolor=c, lw=1))

    ax.set_ylim(0, height)
    ax.set_xlim(0, width)
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.grid(True)
    plt.show()

# Load n-Queens model from file
nqueens = Model("vlsi.mzn")
# Find the MiniZinc solver configuration for Gecode
gecode = Solver.lookup("gecode")
# Create an Instance of the n-Queens model for Gecode
instance = Instance(gecode, nqueens)
# Assign 4 to n
instance["w"] = 9
instance['c'] = 5
instance['dx'] = [3, 2, 2, 3, 4]
instance['dy'] = [3, 4, 8, 9, 12]

result = instance.solve()
# Output
print(result)
print(result["h"])
print(result["x"])
print(result["y"])

colors = ['red', 'blue', 'green', 'cyan', 'pink']

plot(9, result["h"], [(instance['dx'][i], instance['dy'][i], result["x"][i], result["y"][i], colors[i]) for i in range(0,5)])
# [(3,3,4,0,'red'), (2,4,7,0,'blue'), (2,8,7,4,'green'), (3,9,4,3,'cyan'), (4,12,0,0,'pink')])
