from metaplot.aux import *
from metaplot.core import Series
import numpy as np

def test_ValueDict():
    x = ValueDict({2: 4, 3: 4})
    assert sum(x)==8

def test_compose():
    def square(x): return x**2
    def double(x): return 2*x
    def half(x): return x/2
    assert compose(double,square,half)(10)==50

def test_capitalize():
    assert capitalize("abcD") == "AbcD"

def test_last(capsys):
    x = Series(np.linspace(-1e-3,1e-3,100), 'A')
    y = last(x)
    a = capsys.readouterr().out
    assert a == "Last datapoint in series: 1.0 milliampere\n"
    assert all(y==x)

def test_plain():
    x = Series(np.linspace(-1e-3,1e-3,100), 'A')
    x.meta['filter'] = 'somefilter'
    y = plain(x)
    assert all(y==x)
    assert y.meta['filter'] == '-'
    # assert x.meta['filter'] == 'somefilter'

def test_ema():
    t = Series(np.linspace(0,1,11))
    dt = t[1]-t[0]
    tau = 0.1
    ind = np.array(range(len(t)))

    input = np.zeros(ind.shape)
    input[0] = 1
    input = Series(input)
    input.xaxis = t

    output = ema(tau)(input)
    true_output = np.exp(-ind*dt/tau)

    assert np.allclose(output, true_output)
    # assert not np.allclose(input, output)
