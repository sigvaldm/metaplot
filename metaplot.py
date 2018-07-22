#!/usr/bin/env python
"""
TODO:
    Use CSV package.

    FILTER metadata. Could have values such as ExpAvg(2.5) which then eval's user costomizable filter classes.

    Some sort of option to include statistical error curves, e.g. min, mean, max.
    Should be based on evaluating expressions like everything else so min and max could be derived using e.g. StDev.

    PREFIX metadata. To apply e.g. SI prefixes. User customizable PREFIX classes?

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
"""
from numpy import cos, sin
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import sympy as sp
import csv
import re
import sys
from copy import copy, deepcopy
from sympy.physics import units
import pint

ureg = pint.UnitRegistry()

def decomment(file, expression=r'#[^:]'):
    """
    Generator removing single line comments in iterable ``file``.
    ``expression`` is the regex for the comment symbol(s).
    """
    for row in file:
        raw = re.split(expression, row)[0].strip()
        if raw: yield raw

def reader(csvfile, **kwargs):
    """
    metaplot file reader based on Python's csv.reader(). This uses a sniffer to automatically determine the format of the CSV or textfile. This should work most of the times, but occasionally, the format has to be specified manually. In that case, all of the arguments normally accepted by csv.reader() is accepted by

    Keyword arguments:
    ------------------
    has_header
    """

    sample = [a for a,b in zip(decomment(csvfile,'#'),range(5))]
    sample = '\n'.join(sample)
    csvfile.seek(0)

    snf        = csv.Sniffer()
    dialect    = kwargs.pop('dialect'   , snf.sniff(sample))
    has_header = kwargs.pop('has_header', snf.has_header(sample))

    name_exists = False
    for row in csv.reader(decomment(csvfile), dialect, **kwargs):

        # Remove empty columns arising due to multiple delimiters
        row = [x for x in row if x]

        if row[0] == '#:NAME':
            name_exists = True

        # Annotate header row with #:NAME unless #:NAME already exist
        if has_header and row[0][:2] != '#:':
            has_header = False
            if not name_exists:
                row.insert(0, '#:NAME')
                yield row
        else:
            yield row

class Series(ureg.Quantity):
    def __new__(cls, value, units=None, dtype=np.float):
        return super().__new__(cls, np.array(value, dtype=dtype), units=units)

    def to_compact(self):
        highest = max(abs(self.m))*self.u
        new_unit = highest.to_compact().u
        return self.to(new_unit)

    def ito_compact(self):
        highest = max(abs(self.m))*self.u
        new_unit = highest.to_compact().u
        self.ito(new_unit)

class DataFrame(dict):

    def __init__(self, reader):
        self.meta = {}
        valid_keys = ['NAME', 'MUL', 'LONG', 'UNIT']

        raw_data = []
        raw_meta = {}
        for row in reader:

            meta_match = re.match(r'#:(.*)',row[0])
            if meta_match:
                key = meta_match.group(1)
                assert key in valid_keys
                raw_meta[key] = row[1:]

            else:
                raw_data.append(row)

        assert 'NAME' in raw_meta, "Missing NAME"
        assert len(raw_meta['NAME']) == len(set(raw_meta['NAME'])), "Duplicate NAMEs"
        raw_data = list(map(list, zip(*raw_data))) # Transpose lists

        for i, name in enumerate(raw_meta['NAME']):
            mul = self.get_meta('MUL', name, 1.0)
            self[name] = Series(raw_data[i], dtype=np.float)*mul
            self[name].meta = {}
            for key in raw_meta:
                self[name].meta[key] = raw_meta[key][i]

            self[name] *= ureg[raw_meta['UNIT'][i]]

        self._build_indexables()

    def _build_indexables(self):
        indexables = {}
        for key in self:
            match = re.match('(\w+)\[(\d+)]', key)
            if match:
                name, index = match.groups()
                if name not in indexables: indexables[name] = {}
                indexables[name][int(index)] = self[key]

        for key in indexables:
            self[key] = indexables[key]

    def parse(self, expression):
        for key in self:
            expression = re.sub(key,"self['"+key+"']",expression)
        return eval(expression)

    def get_meta(self, meta_key, data_key, default=None):
        if meta_key in self.meta:
            return self.meta[meta_key].get(data_key, default)
        else:
            return default

    def plot(self, x, y):

        # Since data may be pre-processed for plotting
        # it must be deepcopied to avoid permanent changes
        ydata = deepcopy(self.parse(y))
        xdata = deepcopy(self.parse(x))

        xlabel = self.get_meta('LONG', x)
        if xlabel: xlabel = xlabel.capitalize()
        else: xlabel = x

        ylabel = self.get_meta('LONG', y)
        if ylabel: ylabel = ylabel.capitalize()
        else: ylabel = y

        xunit = self.get_meta('UNIT', x, '')
        if xunit:
            prefix = si(xdata)
            xunit = ' [$\\mathrm{' + prefix + xunit + '}$]'

        yunit = self.get_meta('UNIT', y, '')
        if yunit:
            prefix = si(ydata)
            yunit = ' [$\\mathrm{' + prefix + yunit + '}$]'

        plt.plot(xdata, ydata)
        plt.title(ylabel + ' vs. ' + xlabel)
        plt.xlabel(xlabel+xunit)
        plt.ylabel(ylabel+yunit)
        plt.grid()

# def plot(x, y):

#         print(type(x))
#         x = deepcopy(x)
#         y = deepcopy(y)
#         print(type(x))

#         if 'LONG' in x.meta:
#             xlabel = x.meta['LONG'].capitalize()
#         else:
#             xlabel = x.meta['NAME']

#         if 'LONG' in y.meta:
#             ylabel = y.meta['LONG'].capitalize()
#         else:
#             ylabel = y.meta['NAME']

#         plt.title(ylabel + ' vs. ' + xlabel)

#         if 'UNIT' in x.meta:
#             x = si(x)
#             xunit = ' [$\\mathrm{' + x.meta['UNIT'] + '}$]'

#         if 'UNIT' in y.meta:
#             y = si(y)
#             yunit = ' [$\\mathrm{' + y.meta['UNIT'] + '}$]'

#         plt.plot(x, y)
#         plt.xlabel(xlabel+xunit)
#         plt.ylabel(ylabel+yunit)
#         plt.grid(True)

def plot(x, y):

        # if 'LONG' in x.meta:
        #     xlabel = x.meta['LONG'].capitalize()
        # else:
        #     xlabel = x.meta['NAME']

        # if 'LONG' in y.meta:
        #     ylabel = y.meta['LONG'].capitalize()
        # else:
        #     ylabel = y.meta['NAME']

        # plt.title(ylabel + ' vs. ' + xlabel)

        # if 'UNIT' in x.meta:
        #     x = si(x)
        #     xunit = ' [$\\mathrm{' + x.meta['UNIT'] + '}$]'

        # if 'UNIT' in y.meta:
        #     y = si(y)
        #     yunit = ' [$\\mathrm{' + y.meta['UNIT'] + '}$]'

        x = x.to_compact()
        y = y.to_compact()

        xunit = '${:~L}$'.format(x.u)
        yunit = '${:~L}$'.format(y.u)

        plt.plot(x, y)
        plt.xlabel(xunit)
        plt.ylabel(yunit)
        plt.grid(True)

if __name__ == '__main__':

    with open(sys.argv[1]) as csvfile:
        reader = reader(csvfile, delimiter=' ', has_header=False)
        df = DataFrame(reader)


    # plot(df['t'], df['I[0]']+df['I[1]']+df['I[2]'])
    plot(df['t'], df['ne']+df['I[0]'])

    # df.plot(sum(df.I))
    # metaplot sum(I) pictetra.hst
    # metaplot sum(I) V[0] -- pictetra.hst pictetra2.hst

    plt.show()


#     # df.plot('t', 'sum(I)')
#     # plot(df['t'],df['I[0]'])
#     df['I[0]'].meta['UNIT'] = units.A
#     df['I[1]'].meta['UNIT'] = units.A
#     Isum = df['I[0]']+df['I[1]']
#     plot(df['t'],Isum)
#     # plot(df['t'], df['I[0]'])
#     plt.show()
#     # plot(df['t'],df['I[0]'])
#     # plt.show()
#     # df.plot('t', 'I[0]')
#     # plt.show()
