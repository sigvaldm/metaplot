from __future__ import print_function
import numpy as np
from copy import deepcopy
from metaplot.api import ureg
from functools import reduce
import metaplot.compiled_filters as compiled_filters

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

def last(series):
    """
    Print the last value in series to terminal.
    """
    # TBD: series[-1].to_compact() produces an error
    # TBD: Find a way to exctract name instead of writing "series"
    y = series.to_compact()
    print("Last datapoint in series:",y[-1])
    return series

def plain(series):
    """
    Removes any filters from series.
    """
    series.meta['filter'] = '-'
    return series

def infer_auto_quantities(*quantities):
    # This shoul perhaps be implemented in overloaded operators

    quantities = list(quantities)

    others = list(filter(lambda x: x.to_base_units().u != 'auto', quantities))

    if len(others)==0:
        # All quantities are auto. Keep them as they are.
        return quantities

    units = others[0].to_base_units().u

    dims = [o.dimensionality for o in others]
    if not all([d==units.dimensionality for d in dims]):
        raise ValueError("Mixed dimensionalities when inferring auto units")

    for i in range(len(quantities)):
        if quantities[i].to_base_units().u == 'auto':
            quantities[i] *= units/quantities[i].to_base_units().u

    return quantities

def ema(tau):
    def func(y):

        raw = plain(deepcopy(y))
        raw.set_plot_properties(color='#CCCCCC', linewidth=1, zorder=0)
        y.coseries.append(raw)

        t = y.xaxis

        # Re-assignment of non-local variables are impossible in Python 2
        # (in Python 3 the nonlocal keyword can be used). Make a local
        # copy of tau.
        tau_ = tau

        # Make sure tau_ and t has same units before passing to compiled
        # code which is unaware of units.
        if not isinstance(tau_, ureg.Quantity):
            tau_ *= t[0].to_base_units().u
            tau_ = tau_.to(t.u)

        compiled_filters.ema(t.m, y.m, tau_.m)

        return y

    return func

def truth(value, reltol=0, tol=0):
    if reltol != 0:
        tol = value*reltol

    def func(y):

        upper = plain(deepcopy(y))
        upper.ito_base_units()
        upper.m[:] = value+tol
        upper.set_plot_properties(color='#333333', linewidth=1, linestyle='--')
        y.coseries.append(upper)

        if tol != 0:
            lower = deepcopy(upper)
            upper.m[:] = value-tol
            y.coseries.append(lower)

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

