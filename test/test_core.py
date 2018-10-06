from metaplot.core import *

def test_format_name():
    assert format_name('I[10]') == '$I_{10}$'
    assert format_name("I['subscript']") == '$I_\mathrm{subscript}$'
    assert format_name('I["subscript"]') == '$I_\mathrm{subscript}$'
