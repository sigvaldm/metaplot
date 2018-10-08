import six
from metaplot.api import *

# def test_PluginMount():

#     class PluginType(six.with_metaclass(PluginMount)):
#         pass

#     class Plugin1(PluginType):
#         text = 'Plugin1'

#     class Plugin2(PluginType):
#         text = 'Plugin2'

#     assert PluginType.plugins.

def test_decomment():
    indata = ['# comment', ' # comment', 'data', 'data # comment', '#:name abc']
    assert list(decomment(indata)) == ['data', 'data']
    assert list(decomment(indata,r'#[^:>]')) == ['data', 'data', '#:name abc']

    indata = ['// comment', ' // comment', 'data // comment']
    assert list(decomment(indata,r'//')) == ['data']
