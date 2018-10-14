import six
from metaplot.api import *

def test_PluginMount():

    class PluginType(six.with_metaclass(PluginMount)):
        pass

    class Plugin1(PluginType):
        text = 'Plugin1'

    class Plugin2(PluginType):
        text = 'Plugin2'

    assert PluginType.plugins == [Plugin1, Plugin2]

def test_FunctionLine(capsys):
    line = FunctionLine('func')
    assert isinstance(line, FunctionLine)
    assert line.func == 'func'
    print(line)
    a = capsys.readouterr().out
    assert a == "FunctionLine(func)\n"

def test_MetadataLine(capsys):
    line = MetadataLine('name', ['t', 'x', 'y'])
    assert isinstance(line, MetadataLine)
    assert line.key == 'name'
    assert line.data == ['t', 'x', 'y']
    print(line)
    a = capsys.readouterr().out
    assert a == "MetadataLine(name, ['t', 'x', 'y'])\n"

def test_DataLine(capsys):
    line = DataLine([1, 2, 3])
    assert isinstance(line, DataLine)
    assert line.data == [1, 2, 3]
    print(line)
    a = capsys.readouterr().out
    assert a == "DataLine([1, 2, 3])\n"

def test_decomment():
    indata = ['# comment', ' # comment', 'data', 'data # comment', '#:name abc']
    assert list(decomment(indata)) == ['data', 'data']
    assert list(decomment(indata,r'#[^:>]')) == ['data', 'data', '#:name abc']

    indata = ['// comment', ' // comment', 'data // comment']
    assert list(decomment(indata,r'//')) == ['data']
