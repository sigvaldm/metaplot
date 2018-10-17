#!/usr/bin/env python
"""
TODO:
    Gets Unhashable type when doing something like 'mpl pictetra.hst "V[0:3]"'

    Use CSV package.

    FILTER metadata. Could have values such as ExpAvg(2.5) which then eval's user costomizable filter classes.

    Some sort of option to include statistical error curves, e.g. min, mean, max.
    Should be based on evaluating expressions like everything else so min and max could be derived using e.g. StDev.

    Arrays/subscripts in symbols. E.g. I[0], I[1] etc, or I_0, I_1, or even I['boom'], I['probe'].
    This should allow evaluation such as sum(I).

    Allow binding names to eval strings through kwargs.

    Some mechanism for legends.

    Tools for plotting convergence? Some mechanism for parameter sweeps.
    Perhaps some filtering tools, e.g. filtering rows where a given column
    is 'CG1'.

    Support loglog, semilogx, semilogy, automatic x-axis determination.
    Have a metaparameter of what variable to use for x axis for various
    fields.

    LaTeX-ready font, size, etc. on figures.

    Overload __add__ and other operators such that 'name' is meaningful
    even when not using the parse function (e.g I[0]+I[1]+I[2])

    Allow plotting an array, e.g. if I is plotted, plot I[0], I[1], etc.

    Let df.plot() have all the same arguments as plot()

    Think of a way to plot only same units on same plot

    Consider not wrapping Series values in np.array. It may inconvenience
    some things.

    Customizable default-properties for Matplotlib (e.g. linewidth and grid or
    not)

    When plotting multiple quantities in the same plot, e.g. kinetic and potential energy, one may be uJ while the other is mJ. The must be converted to the same prior to plotting.

    When plotting quantity with unit m**(-3) part of the xlabel is cut away.

    Make support for curve-fit

    Make parser for reader that removes multiple delimiters?
    Make parser for reader that auto-inserts name tag on CSV header rows?
    Make pandas-based parser?

    Make reader for other things than csv-files. E.g. dict_reader()?
    reader for 2D NumPy array with associated list of column names?

"""
import matplotlib.pyplot as plt
import sys
import os
from argparse import ArgumentParser

from metaplot.core import DataFrame, format_name
from metaplot.api import ureg

def mpl(*args):
    #
    # PARSE OPTIONS
    #

    if len(args)==0:
        args = sys.argv[1:]

    parser = ArgumentParser(description='metaplot (VERSION HERE)')
    parser.add_argument('files_and_expressions', nargs='*', metavar='file/expression',
                        help='a file or an expression if no such file exists')
    parser.add_argument('-x', default=None, metavar='expression',
                        help='specify expression for x-axis')
    parser.add_argument('--noshow', action='store_true',
                        help="don't show plot. Useful for timing")
    parser.add_argument('--xlabel', metavar='label',
                        help="x axis label")
    parser.add_argument('--ylabel', metavar='label',
                        help="y axis label")
    parser.add_argument('--title', metavar='label',
                        help="figure title")
    parser.add_argument('--save', metavar='file',
                        help="save to file")
    parser.add_argument('--dpi', metavar='dpi',
                        help="dots per inch used when using --save")
    options = parser.parse_args(args)

    # Split argument in files and not
    files = []
    expressions = []
    for arg in options.files_and_expressions:
        if os.path.isfile(arg):
            files.append(arg)
        else:
            expressions.append(arg)

    multiple_files = len(files)>1
    multiple_expressions = len(expressions)>1

    for f in files:
        df = DataFrame(f)

        for e in expressions:
            label = ''
            if multiple_files:
                label += f
            if multiple_files and multiple_expressions:
                label += ': '
            if multiple_expressions:
                label += format_name(e)
            df.plot(options.x, e, label=label)

    if multiple_files or multiple_expressions:
        plt.legend(loc='best')

    if options.xlabel:
        plt.xlabel(options.xlabel)

    if options.ylabel:
        plt.ylabel(options.ylabel)

    if options.title:
        plt.title(options.title)

    if options.save:
        plt.savefig(options.save, bbox_inches='tight', dpi=float(options.dpi))

    if not options.noshow:
        plt.show()

    # plot(df['t'], df['I[0]'])
    # plot(df['t'], df['I[0]']+df['I[1]'])
    # plot(df['t'], sum(df['I']))
    # plot(df['t'], df['ne']+df['I[0]'])
    # df.plot('t', 'I[0]')
    # df.plot('t', "sum(I)")
    # df.plot('t', "I[0]+I[1]")

    # metaplot sum(I) pictetra.hst
    # metaplot sum(I) V[0] -- pictetra.hst pictetra2.hst
