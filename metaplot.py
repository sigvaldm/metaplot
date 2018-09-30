#!/usr/bin/env python
"""
TODO:
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
from numpy import cos, sin
import numpy as np
import matplotlib.pyplot as plt
import csv
import re
import sys
from copy import copy, deepcopy
import pint
import os
from getopt import getopt
from functools import reduce

ureg = pint.UnitRegistry()

class FunctionLine(object):
    def __init__(self, func):
        self.func = func
    def __repr__(self):
        return "FunctionLine: {}".format(self.func)

class MetadataLine(object):
    def __init__(self, key, data):
        self.key = key
        self.data = data
    def __repr__(self):
        return "MetadataLine: {}\n{}".format(self.key, self.data)

class DataLine(object):
    def __init__(self, data):
        self.data = data
    def __repr__(self):
        return "DataLine: \n{}".format(self.data)

def csv_parser(file, **kwargs):

    sample = [a for a,b in zip(decomment(file,'#'),range(5))]
    sample = '\n'.join(sample)
    file.seek(0)

    snf        = csv.Sniffer()
    dialect    = kwargs.pop('dialect'   , snf.sniff(sample))
    has_header = kwargs.pop('has_header', snf.has_header(sample))

    return lambda x: list(csv.reader(asSingletonIterable(x), dialect, **kwargs))[0]

def decomment(file, exp=r'#'):
    """
    Generator removing single line comments in iterable ``file``.
    ``exp`` is the regex for the comment symbol(s).
    """
    exp= re.compile(exp)
    for line in file:
        raw = exp.split(line)[0].strip()
        if raw: yield raw

class asSingletonIterable(object):
    def __init__(self, s):
        self.s = s
        self.used = False
    def __next__(self):
        if self.used:
            raise StopIteration
        else:
            self.used = True
            return self.s
    def __iter__(self):
        return self


def csv_reader(file, **kwargs):

    parse       = kwargs.pop('parse', csv_parser(file))
    re_comment  = kwargs.pop('re_comment', r'#[^:>]')
    re_function = kwargs.pop('re_function', r'#>(.*)')
    re_metadata = kwargs.pop('re_metadata', r'#:(\S+)\s*(.*)')

    re_function = re.compile(re_function)
    re_metadata = re.compile(re_metadata)

    for line in decomment(file, re_comment):
        function_match = re_function.match(line)
        metadata_match = re_metadata.match(line)
        if function_match:
            func = function_match.group(1)
            yield FunctionLine(func)
        elif metadata_match:
            key = metadata_match.group(1)
            data = parse(metadata_match.group(2))
            yield MetadataLine(key, data)
        else:
            data = parse(line)
            yield DataLine(data)

class Series(ureg.Quantity):

    """
    CONSTRUCTOR-LIKE FUNCTIONALITY
    """

    # NB: Do not re-order or change the first three arguments. Doing so breaks
    # a lot of compatibility with functionality for parent class.
    def __new__(cls, value, units=None, **meta):

        # Processing dummy meta-data (which will not be retained)
        mul   = meta.pop('mul', 1)
        dtype = meta.pop('dtype', np.float)
        xaxis = meta.pop('xaxis', None)

        # Would be nice to return name of variable here, but introspection
        # can not be done (in any good way). Would also be nice to write
        # what kind of quanitity it is (e.g. Force if the unit is Newton),
        # but pint do not have this functionality.
        if not 'name' in meta: meta['name']='?'

        meta['plot_properties'] = {}

        if dtype != None:
            if isinstance(value, (list, np.ndarray)):
                value = np.array(value, dtype=dtype)
            else:
                value = dtype(value)

        value *= mul

        new = super().__new__(cls, value, units)
        new.meta = deepcopy(meta)
        new.coseries = []
        new.xaxis = xaxis
        return new

    def __copy__(self):
        newone = type(self)(self.m, self.u)
        # This one overrides magnitude:
        # newone.__dict__.update(self.__dict__)
        newone.meta = copy(self.meta)
        newone.coseries = copy(self.coseries)
        newone.xaxis = copy(self.xaxis)
        return newone

    def __deepcopy__(self, memo):
        newone = type(self)(self.m, self.u)
        # This one overrides magnitude:
        # newone.__dict__.update(self.__dict__)
        newone.meta = deepcopy(self.meta, memo)
        newone.coseries = deepcopy(self.coseries, memo)
        newone.xaxis = deepcopy(self.xaxis, memo)
        return newone

    """
    METADATA ACCESSORS
    """

    def apply_filter(self, x=None, df=None):
        new = deepcopy(self)
        if 'filter' in new.meta:
            if new.meta['filter'] != '-':
                evalstr = new.meta['filter']+'(new)'
                new = eval(evalstr)
        return new

    def set_plot_properties(self, **kwargs):
        self.meta['plot_properties'].update(kwargs)

    """
    OVERLOADING PINT METHODS
    """

    def to(self, *args, **kwargs):
        new = ureg.Quantity.to(self, *args, **kwargs)
        # TBD: Why didn't the below line work?
        # new = super().to(self, other, *args, **kwargs)
        new.meta = deepcopy(self.meta)
        return new

    # Overload to work on arrays
    def to_compact(self):
        new = deepcopy(self)
        new.ito_compact()
        return new

    # This one actually do not exist in Pint
    def ito_compact(self):
        if isinstance(self.m, np.ndarray):
            highest = max(abs(self.m))*self.u
        else:
            highest = self
        new_unit = highest.to_compact().u
        self.ito(new_unit)

    """
    OVERLOADING OPERATORS
    """

    # Could add several like these
    def __add__(self, other):
        ret = super().__add__(other)
        # ret.meta = deepcopy(self.meta)
        ret.meta['name'] = self.meta['name'] + '+' + other.meta['name']
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

class ValueDict(dict):
    """
    Like a normal dict, but iterates over values instead of keys. Example::

        d  = {3:1, 5:1}
        vd = ValueDict(d)

        [x for x in d]  # returns [3, 5]
        [x for x in vd] # returns [1, 1]
        sum(d)          # returns 8
        sum(vd)         # returns 2

    Simlarly to how one can iterate over the values of a normal dict using
    .values(), one can iterate over the keys of a ValueDict using .keys().
    """
    def __iter__(self):
        for value in self.values():
            yield value

class DataFrame(dict):

    def __init__(self, reader):
        valid_column_keys = ['name', 'mul', 'long', 'units', 'filter']
        valid_frame_keys = ['xaxis']

        raw_data = []
        raw_meta = {}
        for line in reader:

            if isinstance(line, MetadataLine):
                assert line.key in valid_column_keys or line.key in valid_frame_keys,\
                        "Unknown key: {}".format(key)
                raw_meta[line.key] = line.data

            elif isinstance(line, FunctionLine):
                pass

            elif isinstance(line, DataLine):
                # FIXME: This can be optimized by taking a datatype meta and
                # converting it to that type before storing. Numbers take less
                # space than strings.
                raw_data.append(line.data)

            else:
                raise RuntimeError("Reader returne line that is neither "
                                   "DataLine, MetadataLine nor FunctionLine")

        assert 'name' in raw_meta, "Missing name"
        assert len(raw_meta['name']) == len(set(raw_meta['name'])),\
            "Duplicate names"

        raw_data = list(map(list, zip(*raw_data))) # Transpose list

        for i, name in enumerate(raw_meta['name']):

            meta = {}
            for key in raw_meta:
                if key in valid_column_keys:
                    meta[key] = raw_meta[key][i]
            units = meta.pop('units', None)

            self[name] = Series(raw_data[i], units=units, **meta)

        # Reading in metadata that's not column-wise, but global for the
        # whole dataframe.
        self.meta = {}
        for key in raw_meta:
            if key in valid_frame_keys:
                self.meta[key] = raw_meta[key][0]

        for key in self:
            if key != self.meta['xaxis']:
                self[key].xaxis = self[self.meta['xaxis']]

        self._build_indexables()

    def _build_indexables(self):
        # TBD: Delete keys 'I[0]' and so forth
        # TBD: Fix regex to match words as well as digits
        indexables = {}
        for key in self:
            match = re.match('(\w+)\[(\d+)]', key)
            if match:
                name, index = match.groups()
                if name not in indexables: indexables[name] = ValueDict()
                indexables[name][int(index)] = self[key]

        for key in indexables:
            self[key] = indexables[key]

    def parse(self, expression):
        # TBD: sin(I) evaluated to siself (probably siself['n'](I))
        # Require match of full variable, not just letter
        for key in self:

            # Replace the key when it occurs as a separate word.
            # Example: "n*sin(n)" -> "self['n']*sin(elf['n'])"
            # The 'n' in 'sin' is not replaced.
            pattern = r"\b{}\b".format(key)
            replacement = "self['{}']".format(key)
            expression = re.sub(pattern, replacement, expression)

        return eval(expression)

    def plot(self, x=None, y=None, label=None):

        if x == None and y == None:
            raise RuntimeError('Both x and y can not be None')

        if x == None:
            x = self.meta['xaxis']

        if y == None:
            y = x
            x = self.meta['xaxis']

        x_series = self.parse(x)
        y_series = self.parse(y)

        xname = None if x in self else x
        yname = None if y in self else y

        plot(x_series, y_series, xname=xname, yname=yname, label=label)

def format_name(s):

    # Format strings, e.g. I['sc'] and I["sc"] to I_\mathrm{sc}
    s = re.sub('\[[\'"]([^\]\'"]+)[\'"]\]',r'_\\mathrm{\1}',s)

    # Format numbers, e.g. I[0] to I_{0}
    s = re.sub('\[([^\]\'"]+)\]',r'_{\1}',s)

    # Wrap the whole thing in math-mode
    # TBD: Possible improvement, detect what are variable names and
    # put only those in math mode. Somewhat difficult, since it does
    # note have access to the registry in the DataFrame.
    # Perhaps things which is followed by (...) such as sum in sum(I[0])
    # could be interpreted as an operator and put in mathrm?
    # The best formatting would probably be acheived by actually using
    # the dataframe. Perhaps format_name could have an optional dataframe
    # as input? Or rather list of keys to typeset in math-mode.
    # This could be used by for instance the CLI parser.
    s = '${}$'.format(s)

    return s

def plot(x, y, xname=None, yname=None, xlong=None, ylong=None, title=None, label=None, xunits=None, yunits=None):

        # TBD: There's a bug, plotting t against t makes to_compact()
        # do nothing on y. Doing a deepcopy() before this did not help.
        # This bug also appear when plotting a ValueDict, e.g. I

        if isinstance(y, ValueDict):
            if yunits==None:
                yu = [a.to_compact().u for a in y]
                yunits = max(yu)

            for v in y:
                # TBD: Are the arguments well thought out?
                label = format_name(v.meta['name'])
                plot(x, v, xname=xname, xlong=xlong, title=title, label=label, xunits=xunits, yunits=yunits)
            plt.legend(loc='best')
            return

        y = y.apply_filter(x)

        for cs in y.coseries:
            # Title, xlabel and ylabel will be overwritten.
            # Label should not be written here. Possibly in plot
            # properties by some filter.
            plot(x, cs)

        if xunits==None:
            x = x.to_compact()
        else:
            x = x.to(xunits)

        if yunits==None:
            y = y.to_compact()
        else:
            y = y.to(yunits)

        capitalizable_x = False
        capitalizable_y = False

        if xlong != None:
            xlabel = xlong
            capitalizable_x = True
        elif xname != None:
            xlabel = format_name(xname)
        elif 'long' in x.meta:
            xlabel = x.meta['long']
            capitalizable_x = True
        elif 'name' in x.meta:
            xlabel = format_name(x.meta['name'])
        else:
            xlabel = ''

        if ylong != None:
            ylabel = ylong
            capitalizable_y = True
        elif yname != None:
            ylabel = format_name(yname)
        elif 'long' in y.meta:
            ylabel = y.meta['long']
            capitalizable_y = True
        elif 'name' in y.meta:
            ylabel = format_name(y.meta['name'])
        else:
            ylabel = ''

        if title == None:
            title = ylabel + ' vs. ' + xlabel

        if capitalizable_x:
            xlabel = capitalize(xlabel)

        if capitalizable_y:
            ylabel = capitalize(ylabel)
            title = capitalize(title)

        if x.u != ureg[None]:
            xlabel += r' $\left[{:~L}\right]$'.format(x.u)

        if y.u != ureg[None]:
            ylabel += r' $\left[{:~L}\right]$'.format(y.u)

        # If color is not set explicitly, filter will be blue,
        # then set to gray, and subsequently it will be plotted in orange
        # although blue is not used.
        # Write a unit test extracting colors when a filter is used
        # to check that it is correct.

        if 'color' in y.meta['plot_properties']:
            color = y.meta['plot_properties']['color']
        else:
            color = None

        p = plt.plot(x, y, label=label, color=color)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.title(title)
        plt.grid(True)

        p[0].set(**y.meta['plot_properties'])

def last(series):
    # TBD: series[-1].to_compact() produces an error
    # TBD: Find a way to exctract name instead of writing "series"
    print("Last datapoint in series:",series[-1])
    return series

def plain(series, x=None, df=None):
    series.meta['filter'] = '-'
    return series

def ema(tau):
    def func(y):

        raw = plain(deepcopy(y))
        raw.set_plot_properties(color='#CCCCCC', linewidth=1, zorder=0)
        y.coseries.append(raw)

        t = y.xaxis

        dt = t[1]-t[0]
        if not isinstance(tau, ureg.Quantity):
            dt = dt.to_base_units().m

        a = np.exp(-dt/tau)
        for i in range(1,len(y)):
            y[i] = (1-a)*y[i] + a*y[i-1]

        return y

    return func

def capitalize(s):
    """
    Capitalize first letter in a string but leave the rest untouched
    (unlike the built-in capitalize which lower-cases them).
    """
    return "{}{}".format(s[0].upper(), s[1:])

def compose(*fs):
    def inner(f, g):
        return lambda y: f(g(y))
    return reduce(inner, fs)

def mpl(*args):
    #
    # PARSE OPTIONS
    #

    if len(args)==0:
        args = sys.argv[1:]

    # Split argument in files and not
    files = []
    expargs = []
    for arg in args:
        if os.path.isfile(arg):
            files.append(arg)
        else:
            expargs.append(arg)

    # Separate out expressions from option expargs later
    optlist, expressions = getopt(expargs, "x:")
    options = {}
    for k, v in optlist:
        options[k] = v

    # Read out variables
    x = options.pop('-x', None)

    multiple_files = len(files)>1
    multiple_expressions = len(expressions)>1

    for f in files:
        with open(f) as csvfile:
            # r = oldreader(csvfile, delimiter=' ', has_header=False)
            r = csv_reader(csvfile)
            df = DataFrame(r)

        for e in expressions:
            label = ''
            if multiple_files:
                label += f
            if multiple_files and multiple_expressions:
                label += ': '
            if multiple_expressions:
                label += format_name(e)
            df.plot(x, e, label=label)

    if multiple_files or multiple_expressions:
        plt.legend(loc='best')

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
