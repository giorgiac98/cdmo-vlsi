from minizinc import Instance, Model, Solver
from minizinc.result import Status
from datetime import timedelta


def solve_CP(instance):
    # Load the model from file
    model = Model("CP/src/vlsi.mzn")
    # Find the MiniZinc solver configuration for Gecode
    gecode = Solver.lookup("gecode")
    # Create a minizinc instance of the model for Gecode
    mzn = Instance(gecode, model)
    # Assign 4 to n
    mzn["w"] = instance['w']
    mzn['n'] = instance['n']
    mzn['x'] = instance['x']
    mzn['y'] = instance['y']
    mzn['maxl'] = instance['maxl']

    result = mzn.solve(timeout=timedelta(minutes=5))
    output = {'solved': result.status == Status.OPTIMAL_SOLUTION,
              'time': result.statistics['time'],
              'l': result['l'], 'xhat': result['xhat'], 'yhat': result['yhat']}
    instance.update(output)
    if instance['solved']:
        print('SOLVED')
    else:
        print('NOT SOLVED WITHIN TIME LIMIT')
    return instance
