from minizinc import Instance, Model, Solver
from minizinc.result import Status
from datetime import timedelta


def solve_CP(instance, rotation, solver, search_heuristic, restart_strategy, timeout=300000):
    model = Model(f"CP/src/vlsi{'-rot' if rotation else ''}.mzn")
    gecode = Solver.lookup(solver)
    mzn = Instance(gecode, model)

    mzn["w"] = instance['w']
    mzn['n'] = instance['n']
    if rotation:
        mzn['inputx'] = instance['inputx']
        mzn['inputy'] = instance['inputy']
    else:
        mzn['x'] = instance['inputx']
        mzn['y'] = instance['inputy']
    mzn['minl'] = instance['minl']
    mzn['maxl'] = instance['maxl']
    mzn['search_heuristic'] = search_heuristic
    mzn['restart_strategy'] = restart_strategy

    processes = -1 if solver == 'gecode' else None
    result = mzn.solve(timeout=timedelta(milliseconds=timeout), processes=processes)
    # print(result['board'])
    if result.status == Status.OPTIMAL_SOLUTION:
        output = {'solved': True, 'time': result.statistics['time'], 'l': result.objective, 'xhat': result['xhat'],
                  'yhat': result['yhat'], 'x': result['x'], 'y': result['y'],
                  'rotation': result['rotation'] if rotation else None}
    else:
        output = {'solved': False}
    instance.update(output)
    if instance['solved']:
        print('SOLVED')
    else:
        print('NOT SOLVED WITHIN TIME LIMIT')
    return instance
