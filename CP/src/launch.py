from minizinc import Instance, Model, Solver
from minizinc.result import Status
from datetime import timedelta


def solve_CP(instance, timeout=300000):
    # Load the model from file
    model = Model("CP/src/vlsi.mzn")
    # Find the MiniZinc solver configuration for Gecode
    gecode = Solver.lookup("gecode")
    # Create a minizinc instance of the model for Gecode
    mzn = Instance(gecode, model)
    # Initialization
    mzn["w"] = instance['w']
    mzn['n'] = instance['n']
    mzn['x'] = instance['inputx']
    mzn['y'] = instance['inputy']
    mzn['minl'] = instance['minl']
    mzn['maxl'] = instance['maxl']

    result = mzn.solve(timeout=timedelta(milliseconds=timeout), processes=2)
    # print(result['board'])
    if result.status == Status.OPTIMAL_SOLUTION:
        output = {'solved': True,
                  'time': result.statistics['time'],
                  'l': result['l'], 'xhat': result['xhat'], 'yhat': result['yhat'],
                  'x': instance['inputx'], 'y': instance['inputy'],
                  # 'xsym': result['xsym'], 'ysym': result['ysym']
                  }
    else:
        output = {'solved': False}
    instance.update(output)
    if instance['solved']:
        print('SOLVED')
    else:
        print('NOT SOLVED WITHIN TIME LIMIT')
    return instance
