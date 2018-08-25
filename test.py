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
