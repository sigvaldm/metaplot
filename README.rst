MetaPlot
========

.. image:: https://travis-ci.com/sigvaldm/metaplot.svg?branch=master
    :target: https://travis-ci.com/sigvaldm/metaplot

.. image:: https://coveralls.io/repos/github/sigvaldm/metaplot/badge.svg?branch=master
    :target: https://coveralls.io/github/sigvaldm/metaplot?branch=master

MetaPlot is in a very early development phase. To install and run development version::

    git clone https://github.com/sigvaldm/metaplot.git
    cd metaplot
    pip install -e .

Installation using ``-e`` means that it is the files in the current folder that are used, so the installed version responds to changes in the source code immediately without reinstallation, e.g. if a pull is made from this repository.

Examples of use of MetaPlot::

    $ mpl pictetra.hst ne
    $ mpl pictetra.hst ne ni
    $ mpl ne ni pictetra.hst
    $ mpl pictetra.hst ne+ni
    $ mpl pictetra.hst "I[0]"
    $ mpl pictetra.hst I
    $ mpl pictetra.hst "sum(I)"
    $ mpl pictetra.hst ne 3.2
    $ mpl pictetra.hst "ema(1e-6)(I)"
