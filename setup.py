#!/usr/bin/env python
"""
Copyright 2018 Sigvald Marholm <marholm@marebakken.com>

This file is part of metaplot.

metaplot is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

metaplot is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with metaplot.  If not, see <http://www.gnu.org/licenses/>.
"""

from setuptools import setup

with open('README.rst', encoding='utf-8') as f:
    long_description = f.read()

setup(name='metaplot',
      version='1.0.0.dev0',
      description='metaplot',
      long_description=long_description,
      author='Sigvald Marholm',
      author_email='marholm@marebakken.com',
      url='https://github.com/sigvaldm/metaplot.git',
      py_modules=['metaplot'],
      install_requires=['frmt >1,<2*dev*'],
      license='LGPL'
     )

