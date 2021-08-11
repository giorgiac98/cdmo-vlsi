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
nqueens = Model("queens.mzn")
# Find the MiniZinc solver configuration for Gecode
gecode = Solver.lookup("gecode")
# Create an Instance of the n-Queens model for Gecode
instance = Instance(gecode, nqueens)
# Assign 4 to n
instance["n"] = 4
result = instance.solve()
# Output the array q
print(result["q"])

plot(9, 12, [(3,3,4,0,'red'), (2,4,7,0,'blue'), (2,8,7,4,'green'), (3,9,4,3,'cyan'), (4,12,0,0,'pink')])
