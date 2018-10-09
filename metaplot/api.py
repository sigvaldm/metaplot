import pint
import imp
import os
import re
import csv
import six
from os.path import join as joinpath
"""
Information on plugin API
https://stackoverflow.com/questions/932069/building-a-minimal-plugin-architecture-in-python
https://lkubuntu.wordpress.com/2012/10/02/writing-a-python-plugin-api/
http://martyalchin.com/2008/jan/10/simple-plugin-framework/
https://stackoverflow.com/questions/100003/what-are-metaclasses-in-python#6581949

"""

ureg = pint.UnitRegistry()

class PluginMount(type):
    def __init__(cls, name, bases, attrs):
        if not hasattr(cls, 'plugins'):
            cls.plugins = []
        else:
            cls.plugins.append(cls)

class Reader(six.with_metaclass(PluginMount)):
    priority = 1

class Filter(six.with_metaclass(PluginMount)):
    pass

class FunctionLine(object):
    def __init__(self, func):
        self.func = func
    def __repr__(self):
        return "FunctionLine: {}".format(self.func)

class MetadataLine(object):
    def __init__(self, key, data):
        self.key = key
        self.data = data
    def __repr__(self):
        return "MetadataLine: {}\n{}".format(self.key, self.data)

class DataLine(object):
    def __init__(self, data):
        self.data = data
    def __repr__(self):
        return "DataLine: \n{}".format(self.data)

def decomment(file, exp=r'#'):
    """
    Generator removing single line comments in iterable ``file``.
    ``exp`` is the regex for the comment symbol(s).
    """
    exp= re.compile(exp)
    for line in file:
        raw = exp.split(line)[0].strip()
        if raw: yield raw

class asSingletonIterable(object):
    def __init__(self, s):
        self.s = s
        self.used = False
    def __next__(self):
        if self.used:
            raise StopIteration
        else:
            self.used = True
            return self.s
    def __iter__(self):
        return self

def csv_parser(file=None, **kwargs):

    if file != None:
        sample = [a for a,b in zip(decomment(file,'#'),range(5))]
        sample = '\n'.join(sample)
        file.seek(0)

        snf        = csv.Sniffer()
        dialect    = kwargs.pop('dialect'   , snf.sniff(sample))
        has_header = kwargs.pop('has_header', snf.has_header(sample))
        kwargs['dialect'] = dialect

    return lambda x: list(csv.reader(asSingletonIterable(x), **kwargs))[0]

def csv_reader(file, **kwargs):

    parse       = kwargs.pop('parse', csv_parser(file))
    re_comment  = kwargs.pop('re_comment', r'#[^:>]')
    re_function = kwargs.pop('re_function', r'#>(.*)')
    re_metadata = kwargs.pop('re_metadata', r'#:(\S+)\s*(.*)')

    re_function = re.compile(re_function)
    re_metadata = re.compile(re_metadata)

    for line in decomment(file, re_comment):
        function_match = re_function.match(line)
        metadata_match = re_metadata.match(line)
        if function_match:
            func = function_match.group(1)
            yield FunctionLine(func)
        elif metadata_match:
            key = metadata_match.group(1)
            data = parse(metadata_match.group(2))
            yield MetadataLine(key, data)
        else:
            data = parse(line)
            yield DataLine(data)

class DefaultReader(Reader):
    priority = 0
    reader = csv_reader
    def rule(file):
        return True

class _PluginManager(object):
    def __init__(self):
        self.plugins_loaded = False

    def load_plugins(self):
        if not self.plugins_loaded:
            home = os.path.expanduser("~")
            inst_dir = os.path.dirname(__file__)
            plugin_paths = []
            plugin_paths.append(joinpath(home, ".metaplot", "plugins"))
            plugin_paths.append(joinpath(inst_dir, "plugins"))

            for path in plugin_paths:
                for file in os.listdir(path):
                    if file.endswith(".py"):
                        info = imp.find_module(joinpath(path, file[:-3]))
                        imp.load_module(file[:-3], *info)

            self.plugins_loaded = True

    def get_reader(self, file):
        self.load_plugins()
        Reader.plugins.sort(key=lambda x: x.priority, reverse=True)
        for p in Reader.plugins:
            if p.rule(file):
                return p.reader(file)
                break
        raise RuntimeError('No valid reader found in api.Reader')


plugin_manager = _PluginManager()
