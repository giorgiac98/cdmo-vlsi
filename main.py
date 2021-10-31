import os
import numpy as np
from argparse import ArgumentParser
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from CP.src.launch import solve_CP
from SAT.src.launch import solve_SAT
from SMT.src.launch import solve_SMT


def plot_board(width, height, blocks, args, i, rotation, show_plot=False, show_axis=False):
    cmap = plt.cm.get_cmap('nipy_spectral', len(blocks))
    fig, ax = plt.subplots(figsize=(9, 9))
    for component, (w, h, x, y) in enumerate(blocks):
        label = f'{w}x{h}, ({x},{y})'
        if rotation is not None:
            label += f', R={1 if rotation[component] else 0}'
        ax.add_patch(Rectangle((x, y), w, h, facecolor=cmap(component), edgecolor='k', label=label, lw=2, alpha=0.8))
    ax.set_ylim(0, height)
    ax.set_xlim(0, width)
    ax.set_xlabel('width', fontsize=15)
    ax.set_ylabel('length', fontsize=15)
    ax.legend()
    ax.set_title(f'Instance {i}, size (WxH): {width}x{height}', fontsize=22)
    if not show_axis:
        ax.set_xticks([])
        ax.set_yticks([])
    plt.savefig(f'{args.technology}/out/fig-ins-{i}.png')
    if show_plot:
        plt.show(block=False)
        plt.pause(1)
    plt.close(fig)


def plot_timings(timings, args):
    np.save(f'timings/{args.technology}{"-a" if args.area else ""}{"-rot" if args.rotation else ""}-timings', timings)
    fig, ax = plt.subplots(1, 1)
    ax.bar(range(len(timings)), timings)
    ax.set_title('Execution time for each instance')
    ax.set_xlabel('Instance')
    ax.set_ylabel('Time (s)')
    plt.show()


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('technology', type=str, help='The technology to use (CP, SAT or SMT)')
    parser.add_argument('-s', '--start', type=int, help='First instance to solve', default=1)
    parser.add_argument('-e', '--end', type=int, help='Last instance to solve', default=40)
    parser.add_argument('-t', '--timeout', type=int, help='Timeout (ms)', default=300000)
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose')
    parser.add_argument('-a', '--no-area', dest="area", action="store_false", help="do not order circuits by area", default=True)
    parser.add_argument('-r', '--rotation', action="store_true", help="enables circuits rotation")

    # technology-specific arguments
    parser.add_argument('--solver', type=str, help='CP solver (default: chuffed)', default='chuffed')
    parser.add_argument('--heu', type=int, help='CP search heuristic (default: input_order, min)', default=0)
    parser.add_argument('--restart', type=int, help='CP restart strategy (default: luby)', default=1)

    parser.add_argument('--sat-search', action="store_true", help="enables custom z3 sat search")

    parser.add_argument('--smt-model', type=str, help='SMT model to use (default: base)', default='base')
    parser.add_argument('-d', '--dual', dest="dual", action="store_true", help="add dual model", default=True)

    args = parser.parse_args()
    args.technology = args.technology.upper()
    params = {'rotation': args.rotation}
    if args.technology == 'CP':
        solver = solve_CP
        if args.solver not in ('gecode', 'chuffed'):
            raise ValueError(f'wrong solver {args.solver}; supported ones are gecode and chuffed')
        if args.heu not in (0, 1, 2):
            raise ValueError(f'wrong search heuristic {args.heu}; supported ones are (0, 1, 2)')
        if args.restart not in (0, 1, 2):
            raise ValueError(f'wrong restart {args.restart}; supported ones are (0, 1, 2)')
        params.update({'solver': args.solver, 'search_heuristic': args.heu, 'restart_strategy': args.restart})
    elif args.technology == 'SAT':
        solver = solve_SAT
        params.update({'custom_search': args.sat_search})
    elif args.technology == 'SMT':
        solver = solve_SMT
        if args.smt_model not in ('base', 'array'):
            raise ValueError(f'wrong smt model {args.smt_model}; supported ones are "base", "array"')
        params.update({'dual': args.dual, 'kind': args.smt_model})
    else:
        raise ValueError('Wrong technology, either CP or SMT')

    if not os.path.exists(f'{args.technology}/out'):
        os.mkdir(f'{args.technology}/out')

    print(f'SOLVING INSTANCES {args.start} - {args.end} USING {args.technology} MODEL')
    timings = []
    for i in range(args.start, args.end + 1):
        print('=' * 20)
        print(f'INSTANCE {i}')
        with open(f'instances/ins-{i}.txt') as f:
            lines = f.readlines()
        if args.verbose:
            print(''.join(lines))
        lines = [l.strip('\n') for l in lines]
        w = int(lines[0].strip('\n'))
        n = int(lines[1].strip('\n'))
        dim = [l.split(' ') for l in lines[2:]]
        x, y = list(zip(*map(lambda xy: (int(xy[0]), int(xy[1])), dim)))
        xy = np.array([x, y]).T
        if args.area:
            areas = np.prod(xy, axis=1)
            sorted_idx = np.argsort(areas)[::-1]
            xy = xy[sorted_idx]
            x = list(map(int, xy[:, 0]))
            y = list(map(int, xy[:, 1]))
        min_area = np.prod(xy, axis=1).sum()
        minl = int(min_area / w)
        xy[:, 0] = xy[:, 0].max()
        oversized_area = np.prod(xy, axis=1).sum()
        maxl = int(oversized_area / w)
        instance = {"w": w, 'n': n, 'inputx': x, 'inputy': y, 'minl': minl, 'maxl': maxl, 'rotation': None}
        instance = solver(instance, **params)
        if instance['solved']:
            out = f"{instance['w']} {instance['l']}\n{instance['n']}\n"
            out += '\n'.join([f"{xi} {yi} {xhati} {yhati}"
                              for xi, yi, xhati, yhati in zip(instance['x'], instance['y'],
                                                              instance['xhat'], instance['yhat'])])
            if args.verbose:
                print(out)
            print(f'TIME: {instance["fulltime"]}')
            timings.append(instance['time'])
            with open(f'{args.technology}/out/out-{i}.txt', 'w') as f:
                f.write(out)
            res = [(xi, yi, xhati, yhati)
                   for xi, yi, xhati, yhati in zip(instance['x'], instance['y'], instance['xhat'], instance['yhat'])]
            plot_board(instance['w'], instance['l'], res, args, i, instance['rotation'])
        else:
            timings.append(300)
    plot_timings(timings, args)
