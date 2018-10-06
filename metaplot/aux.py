import numpy as np
from copy import deepcopy
from metaplot.api import ureg
from functools import reduce

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
    # TBD: series[-1].to_compact() produces an error
    # TBD: Find a way to exctract name instead of writing "series"
    y = series.to_compact()
    print("Last datapoint in series:",y[-1])
    return series

def plain(series):
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

