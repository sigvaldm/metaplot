from metaplot import *

def test_format_name():
    assert format_name('I[10]') == '$I_{10}$'
    assert format_name("I['subscript']") == '$I_\mathrm{subscript}$'
    assert format_name('I["subscript"]') == '$I_\mathrm{subscript}$'

def test_capitalize():
    assert capitalize("abcD") == "AbcD"

def test_ValueDict():
    x = ValueDict({2: 4, 3: 4})
    assert sum(x)==8

def test_compose():
    def square(x): return x**2
    def double(x): return 2*x
    def half(x): return x/2
    assert compose(double,square,half)(10)==50

def test_decomment():
    indata = ['# comment', ' # comment', 'data', 'data # comment', '#:name abc']
    assert list(decomment(indata)) == ['data', 'data', '#:name abc']

    indata = ['// comment', ' // comment', 'data // comment']
    assert list(decomment(indata,r'//')) == ['data']
