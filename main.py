import os
import numpy as np
from argparse import ArgumentParser
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from CP.src.launch import solve_CP
from SAT.src.launch import solve_SAT
from SMT.src.launch import solve_SMT


def plot(width, height, blocks, tech, i, rotation, show=True):
    cmap = plt.cm.get_cmap('viridis', len(blocks))
    fig, ax = plt.subplots(figsize=(9, 9))
    for component, (w, h, x, y) in enumerate(blocks):
        label = f'{w}x{h}, ({x},{y})'
        if rotation is not None:
            label += f', R={1 if rotation[component] else 0}'
        ax.add_patch(Rectangle((x, y), w, h, facecolor=cmap(component), edgecolor='k', label=label, lw=3, alpha=0.8))
    ax.set_ylim(0, height)
    ax.set_xlim(0, width)
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    # ax.grid(True)
    ax.legend()
    ax.set_title(f'INSTANCE {i}')
    plt.savefig(f'{tech}/out/fig-ins-{i}.png')
    if show:
        plt.show(block=False)
        plt.pause(3)
        plt.close(fig)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('technology', type=str, help='The technology to use (CP or SMT)')
    parser.add_argument('-s', '--start', type=int, help='First instance to solve', default=1)
    parser.add_argument('-e', '--end', type=int, help='Last instance to solve', default=40)
    parser.add_argument('-t', '--timeout', type=int, help='Timeout (ms)', default=300000)
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose')
    parser.add_argument('-a', '--area', action="store_true", help="orders circuits by area")
    parser.add_argument('-r', '--rotation', action="store_true", help="enables circuits rotation")

    # technology-specific arguments
    parser.add_argument('--solver', type=str, help='CP solver (default: chuffed)', default='chuffed')
    parser.add_argument('--heu', type=int, help='CP search heuristic (default: impact, min)', default=3)
    parser.add_argument('--restart', type=int, help='CP restart strategy (default: luby)', default=3)
    args = parser.parse_args()
    args.technology = args.technology.upper()
    params = {'rotation': args.rotation}
    if args.technology == 'CP':
        solver = solve_CP
        if args.solver not in ('gecode', 'chuffed'):
            raise ValueError(f'wrong solver {args.solver}; supported ones are gecode and chuffed')
        if args.heu not in (1, 2, 3):
            raise ValueError(f'wrong search heuristic {args.heu}; supported ones are gecode and chuffed')
        if args.restart not in (1, 2, 3):
            raise ValueError(f'wrong solver {args.solver}; supported ones are gecode and chuffed')
        params.update({'solver': args.solver, 'search_heuristic': args.heu, 'restart_strategy': args.restart})
    elif args.technology == 'SAT':
        solver = solve_SAT
    elif args.technology == 'SMT':
        solver = solve_SMT
    else:
        raise ValueError('Wrong technology, either CP or SMT')

    if not os.path.exists(f'{args.technology}/out'):
        os.mkdir(f'{args.technology}/out')

    print(f'SOLVING INSTANCES {args.start} - {args.end} USING {args.technology} MODEL')
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
            print(f'TIME: {instance["time"]}')
            with open(f'{args.technology}/out/ins-{i}.txt', 'w') as f:
                f.write(out)
            res = [(xi, yi, xhati, yhati)
                   for xi, yi, xhati, yhati in zip(instance['x'], instance['y'], instance['xhat'], instance['yhat'])]
            plot(instance['w'], instance['l'], res, args.technology, i, instance['rotation'])
