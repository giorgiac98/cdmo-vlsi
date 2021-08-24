from minizinc import Instance, Model, Solver
from minizinc.result import Status
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from datetime import timedelta


def solve_CP(input):
    # Load the model from file
    model = Model("CP/src/vlsi.mzn")
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
