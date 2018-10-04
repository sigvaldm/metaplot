import imp
from os.path import join as joinpath
import os
import metaplot.api as api

home = os.path.expanduser("~")
inst_dir = joinpath(os.path.dirname(__file__), "..")
plugin_paths = []
plugin_paths.append(joinpath(home, ".metaplot", "plugins"))
plugin_paths.append(joinpath(inst_dir, "plugins"))

for path in plugin_paths:
    for file in os.listdir(path):
        if file.endswith(".py"):
            info = imp.find_module(joinpath(path, file[:-3]))
            imp.load_module(file[:-3], *info)
