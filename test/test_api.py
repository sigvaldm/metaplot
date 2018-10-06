from metaplot.api import *

def test_decomment():
    indata = ['# comment', ' # comment', 'data', 'data # comment', '#:name abc']
    assert list(decomment(indata)) == ['data', 'data']
    assert list(decomment(indata,r'#[^:>]')) == ['data', 'data', '#:name abc']

    indata = ['// comment', ' // comment', 'data // comment']
    assert list(decomment(indata,r'//')) == ['data']
