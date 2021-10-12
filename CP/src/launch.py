from minizinc import Instance, Model, Solver
from minizinc.result import Status
from datetime import timedelta


def solve_CP(instance, solver, search_heuristic, restart_strategy, timeout=300000):
    model = Model("CP/src/vlsi.mzn")
    gecode = Solver.lookup(solver)
    mzn = Instance(gecode, model)

    mzn["w"] = instance['w']
    mzn['n'] = instance['n']
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
        output = {'solved': True,
                  'time': result.statistics['time'],
                  'l': result.objective, 'xhat': result['xhat'], 'yhat': result['yhat'],
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
