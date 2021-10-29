# VLSI design: CP, SAT and SMT approaches
In the last couple of decades we have been witnessing a trend of shrinking and miniaturization of electronic components (transistors). Indeed, having smaller components allows to fit more of them in a given area; on the other hand, smaller transistors allows to obtain a smaller chip (in terms of area) with the same computational capabilities of a chip which uses bigger transistors. This process is called Very large-scale integration (VLSI), that is, the process of designing an integrated circuit by embedding millions or even billions of transistors on a single silicon semiconductor microchip. Given the huge number of components involved, the development of smart techniques to address this process has become critical for developing modern-day devices.

This repository describes a Combinatorial Optimization approach to the VLSI problem. In particular, three different technologies are employed to address the problem at hand, namely Constraint Programming (CP), propositional SATisfiability (SAT) and Satisfiability Modulo Theories (SMT).

## Requirements
The following packages are required:
- minizinc
- z3-solver
- matplotlib
- numpy

You can install them on your own, or use the provided `requirements.txt` file to install them by running
```
$ pip install -r requirements.txt
```

## Usage
All the solvers are executed by launching the `main.py` file and supplying the required technology (CP, SAT, SMT). All the other parameters are optional.

```
python main.py technology [-h] [-s START] [-e END] [-t TIMEOUT] [-v] [-a] [-r]
               [--solver SOLVER] [--heu HEU] [--restart RESTART]
               [--smt-model SMT_MODEL]
```

Command line arguments:

| Argument                                         | Description                                                                  |
| ------------------------------------------------ | -----------------------------------------------------------------------------|
| `technology`                                     | The technology solver to use (CP/SAT/SMT)                                    |
| `-h, --help`                                     | Shows help message                                                           |
| `-s START, --start START`                        | First instance to solve (default: 1)                                         |
| `-e END, --end END`                              | Last instance to solve (default: 40)                                         |
| `-t TIMEOUT, --timeout TIMEOUT`                  | Sets the timeout (ms, default: 300000)                                       |
| `-v, --verbose`                                  | Enables verbose output (default: false)                                      |
| `-a, --area`                                     | Sorts circuits by area before feeding them to the solver (default: true)     |
| `-r, --rotation`                                 | Enables circuits rotation (default: false)                                   |
| `--solver SOLVER`                                | (CP ONLY) CP solver to use (gecode/chuffed, default: chuffed)                |
| `--heu HEU`                                      | (CP ONLY) CP search heuristic (0/1/2, default: 0)                            |
| `--restart RESTART`                              | (CP ONLY) CP restart strategy (0/1/2, default: 1)                            |
| `--smt-model SMT_MODEL`                          | (SMT ONLY) SMT model to use (base/array, default: base)                      |
