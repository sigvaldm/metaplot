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
        new = super().__new__(cls, np.array(value, dtype=dtype), units=units)
        new.meta = {}
        return new

    def to_compact(self):
        highest = max(abs(self.m))*self.u
        new_unit = highest.to_compact().u
        return self.to(new_unit)

    def ito_compact(self):
        highest = max(abs(self.m))*self.u
        new_unit = highest.to_compact().u
        self.ito(new_unit)

    def __copy__(self):
        newone = type(self)()
        newone.__dict__.update(self.__dict__)
        self.meta = copy(self.meta)
        return newone

    def __deepcopy__(self, memo):
        newone = type(self)()
        newone.__dict__.update(self.__dict__)
        self.meta = deepcopy(self.meta, memo)
        return newone

    """
    OPERATORS
    """

    def __add__(self, other):
        ret = super().__add__(other)
        ret.meta = deepcopy(self.meta)
        return ret
"""
Possible operators to overload:
__abs__ __add__ __array_prepare__ __array_priority__ __array_wrap__ __bool__
__bytes__ __class__ __complex__ __copy__ __deepcopy__ __delattr__ __dict__
__dir__ __div__ __divmod__ __doc__ __eq__ __float__ __floordiv__ __format__
__ge__ __getattr__ __getattribute__ __getitem__ __gt__ __hash__ __iadd__
__idiv__ __ifloordiv__ __imod__ __imul__ __init__ __init_subclass__ __int__
__ipow__ __isub__ __iter__ __itruediv__ __le__ __len__ __long__ __lt__
__mod__ __module__ __mul__ __ne__ __neg__ __nonzero__ __pos__ __pow__ __radd__
__rdiv__ __rdivmod__ __reduce__ __reduce_ex__ __repre__ __rfloordiv__ __rmod__
__rmul__ __round__ __rpow__ __rsub__ __rtruediv__ __setattr__ __setitem__
__sizeof__ __str__ __sub__ __subclasshook__ __truediv__ __unicode__ __weakref__
"""

class DataFrame(dict):

    def __init__(self, reader):
        valid_keys = ['NAME', 'MUL', 'LONG', 'UNIT']

        raw_data = []
        raw_meta = {}
        for row in reader:

            meta_match = re.match(r'#:(.*)',row[0])
            if meta_match:
                key = meta_match.group(1)
                assert key in valid_keys, "Unknown key: {}".format(key)
                raw_meta[key] = row[1:]

            else:
                # FIXME: This can be optimized by taking a datatype meta and
                # converting it to that type before storing. Numbers take less
                # space than strings.
                raw_data.append(row)

        assert 'NAME' in raw_meta, "Missing NAME"
        assert len(raw_meta['NAME']) == len(set(raw_meta['NAME'])),\
            "Duplicate NAMEs"

        raw_data = list(map(list, zip(*raw_data))) # Transpose list

        for i, name in enumerate(raw_meta['NAME']):

            # Making a dataseries
            self[name] = Series(raw_data[i], dtype=np.float)

            # Putting all the metadata in the series
            for key in raw_meta:
                self[name].meta[key] = raw_meta[key][i]

            # meta = {}
            # for key in raw_meta:
            #     meta[key] = raw_meta[key][i]

            # units = meta.pop('UNIT','')

            # Making a dataseries
            # self[name] = Series(raw_data[i], dtype=np.float, units=units)
            # self.name = name

            # Putting all the metadata in the series
            # for key in raw_meta:
            #     self[name].meta[key] = raw_meta[key][i]

        self._apply_meta()
        self._build_indexables()

    def _apply_meta(self):

        for series in self.values():
            mul  = series.meta.pop('MUL', 1.0)
            unit = series.meta.pop('UNIT', '')
            series *= mul
            series *= ureg[unit]

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

def plot(x, y):

        if 'LONG' in x.meta:
            xlabel = x.meta['LONG'].capitalize()
        else:
            xlabel = x.meta['NAME']

        if 'LONG' in y.meta:
            ylabel = y.meta['LONG'].capitalize()
        else:
            ylabel = y.meta['NAME']

        plt.title(ylabel + ' vs. ' + xlabel)

        x = x.to_compact()
        y = y.to_compact()

        xunit = ' [${:~L}$]'.format(x.u)
        yunit = ' [${:~L}$]'.format(y.u)

        plt.plot(x, y)
        plt.xlabel(xlabel+xunit)
        plt.ylabel(ylabel+yunit)
        plt.grid(True)

if __name__ == '__main__':

    with open(sys.argv[1]) as csvfile:
        reader = reader(csvfile, delimiter=' ', has_header=False)
        df = DataFrame(reader)


    plot(df['t'], df['I[0]']+df['I[1]'])
    # plot(df['t'], df['I[0]']+df['I[1]']+df['I[2]'])
    # plot(df['t'], df['ne']+df['I[0]'])

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
