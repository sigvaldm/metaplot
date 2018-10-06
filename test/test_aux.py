from metaplot.aux import *

def test_compose():
    def square(x): return x**2
    def double(x): return 2*x
    def half(x): return x/2
    assert compose(double,square,half)(10)==50

def test_capitalize():
    assert capitalize("abcD") == "AbcD"

def test_ValueDict():
    x = ValueDict({2: 4, 3: 4})
    assert sum(x)==8
