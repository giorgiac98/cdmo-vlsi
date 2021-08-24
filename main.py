import numpy as np
from argparse import ArgumentParser
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from SMT.src.launch import solve_SMT
from CP.src.launch import solve_CP


def plot(width, height, blocks, tech, i, show=True):
    cmap = plt.cm.get_cmap('viridis', len(blocks))
    fig, ax = plt.subplots()
    for component, (w, h, x, y) in enumerate(blocks):
        ax.add_patch(Rectangle((x, y), w, h, facecolor=cmap(component), edgecolor='k', label=component, lw=3, alpha=0.8))
    ax.set_ylim(0, height)
    ax.set_xlim(0, width)
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    # ax.grid(True)
    ax.legend()
    plt.savefig(f'{tech}/out/fig-ins-{i}.png')
    if show:
        plt.show()


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('technology', type=str, help='The technology to use (CP or SMT)')
    parser.add_argument('-s', '--start', type=int, help='First instance to solve', default=1)
    parser.add_argument('-e', '--end', type=int, help='Last instance to solve', default=40)
    args = parser.parse_args()
    if args.technology == 'CP':
        solver = solve_CP
    elif args.technology == 'SMT':
        solver = solve_SMT
    else:
        raise ValueError('Wrong technology, either CP or SMT')
    print(f'SOLVING INSTANCES {args.start} - {args.end} USING {args.technology} MODEL')
    for i in range(args.start, args.end + 1):
        print('=' * 42)
        print(f'INSTANCE {i}')
        with open(f'instances/ins-{i}.txt') as f:
            lines = f.readlines()
        lines = [l.strip('\n') for l in lines]
        dim = [l.split(' ') for l in lines[2:]]
        x, y = list(zip(*map(lambda xy: (int(xy[0]), int(xy[1])), dim)))
        xy = np.array([x, y]).T
        areas = np.prod(xy, axis=1)
        sorted_idx = np.argsort(areas)[::-1]
        xy = xy[sorted_idx]
        sorted_x = list(map(int, xy[:, 0]))
        sorted_y = list(map(int, xy[:, 1]))

        instance = {"w": int(lines[0].strip('\n')),
                    'n': int(lines[1].strip('\n')),
                    'x': sorted_x, 'y': sorted_y,
                    'maxl': sum(y)}
        instance = solver(instance)
        if instance['solved']:
            out = f"{instance['w']} {instance['l']}\n{instance['n']}\n"
            out += '\n'.join([f"{xi} {yi} {xhati} {yhati}"
                              for xi, yi, xhati, yhati in zip(instance['x'], instance['y'], instance['xhat'], instance['yhat'])])
            print(out)
            with open(f'{args.technology}/out/ins-{i}.txt', 'w') as f:
                f.write(out)
            res = [(xi, yi, xhati, yhati)
                   for xi, yi, xhati, yhati in zip(instance['x'], instance['y'], instance['xhat'], instance['yhat'])]
            plot(instance['w'], instance['l'], res, args.technology, i)

