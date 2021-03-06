import re
import pint
import numpy as np
import matplotlib.pyplot as plt
from copy import deepcopy
from metaplot.aux import ValueDict, capitalize, ema, last, compose, plain, truth, infer_auto_quantities
from metaplot.api import FunctionLine, MetadataLine, DataLine, csv_reader, ureg, plugin_manager

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

        new = super(Series, cls).__new__(cls, value, units)
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
        # new = super(Series, self).to(self, other, *args, **kwargs)
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
        ret = super(Series, self).__add__(other)
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

class DataFrame(dict):

    def __init__(self, arg):
        if isinstance(arg, str):
            self._init_from_filename(arg)
        elif isinstance(arg, io.IOBase):
            self._init_from_file(arg)
        else:
            self._init_from_reader(arg)

    def _init_from_filename(self, filename):
        with open(filename) as file:
            self._init_from_file(file)

    def _init_from_file(self, file):
        # reader = csv_reader(file)
        reader = plugin_manager.get_reader(file)
        self._init_from_reader(reader)

    def _init_from_reader(self, reader):
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

        raw_data = np.array(raw_data, dtype=np.float).T
        #raw_data = list(map(list, zip(*raw_data))) # Transpose list

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

        series = eval(expression)

        if isinstance(series, (int, float)):
            series = Series(series*np.ones(self[self.meta['xaxis']].shape), 'auto')

        return series

    def plot(self, x=None, y=None, label=None, max_samples=1000):

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

        plot(x_series, y_series, xname=xname, yname=yname, label=label, max_samples=max_samples)

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

def equalize_axis_units(ax, xunits=None, yunits=None):
    """
    Sets the units on the axes of all plots (Line2D) in pyplot. If None it will
    be scaled to fit all plots.
    """

    xs = [l.get_data()[0] for l in ax.lines]
    ys = [l.get_data()[1] for l in ax.lines]

    xs = infer_auto_quantities(*xs)
    ys = infer_auto_quantities(*ys)

    xmax = max([x.to_compact().u for x in xs])
    ymax = max([y.to_compact().u for y in ys])

    if xunits == None: xunits = xmax
    if yunits == None: yunits = ymax

    for line in ax.lines:
        x, y = line.get_data()
        x.ito(xunits)
        y.ito(yunits)
        line.set_data(x, y)

    ax.relim()
    ax.autoscale_view()

def downsample(x,  max_samples):

    if max_samples==0 or len(x)<max_samples:
        return x

    else:
        ratio = int(np.ceil(len(x)/max_samples))
        trim = int(np.floor(len(x)/ratio)*ratio)
        x._magnitude = np.average(x.m[:trim].reshape(-1, ratio), 1)
        return x

def plot(x, y, xname=None, yname=None, xlong=None, ylong=None, title=None, label=None, xunits=None, yunits=None, max_samples=1000):

        # TBD: There's a bug, plotting t against t makes to_compact()
        # do nothing on y. Doing a deepcopy() before this did not help.
        # This bug also appear when plotting a ValueDict, e.g. I

        if isinstance(y, ValueDict):

            for v in y:
                # TBD: Are the arguments well thought out?
                label = format_name(v.meta['name'])
                plot(x, v, xname=xname, xlong=xlong, title=title, label=label, xunits=xunits, yunits=yunits, max_samples=max_samples)
            plt.legend(loc='best')
            return

        x = downsample(x, max_samples)
        y = downsample(y, max_samples)

        y = y.apply_filter(x)

        for cs in y.coseries:
            # Title, xlabel and ylabel will be overwritten.
            # Label should not be written here. Possibly in plot
            # properties by some filter.
            plot(x, cs, max_samples=max_samples)

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
        p[0].set(**y.meta['plot_properties'])

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

        ax = plt.gca()
        equalize_axis_units(ax, xunits, yunits)

        scaled_x, scaled_y = p[0].get_data()

        if scaled_x.u != ureg[None]:
            xlabel += r' $\left[{:~L}\right]$'.format(scaled_x.u)

        if scaled_y.u != ureg[None]:
            ylabel += r' $\left[{:~L}\right]$'.format(scaled_y.u)

        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.title(title)
        plt.grid(True)
