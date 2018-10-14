Metaplot
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

Metaplot has the following synposis::

    $ mpl [optional flags] <files and expressions>

Each expression will be plotted for each file, and the order of files and expressions doesn't matter. Examples of plotting named quantities from files::

    $ mpl pictetra.hst ne
    $ mpl pictetra.hst history.dat ne ni
    $ mpl ne ni pictetra.hst
    $ mpl pictetra.hst "I[0]"
    $ mpl pictetra.hst I

Expressions must be enclosed in quotation marks whenever it contains symbols the shell would otherwise complain about. Expressions can also be arithmetic expressions of named quantities, or constants::

    $ mpl pictetra.hst ne+ni
    $ mpl pictetra.hst "sum(I)"
    $ mpl pictetra.hst ne 3.2

Metaplot comes with several filters, which are just functions applied to dataseries. To plot the last datapoint in a series::

    $ mpl pictetra.hst "last(I)"

To apply exponential moving average (EMA) filter of 1 microsecond relaxation time::

    $ mpl pictetra.hst "ema(1e-6)(I)"

Whereas `last` don't take any hyperparameters, `ema` takes the relaxation time as a hyperparameter. After hyperparameters are applied, filters have _only_ the dataseries as a parameter.

`truth` is useful to compare a curve to a ground truth. E.g if `I` should be -8.74 microamperes::

    $ mpl pictetra.hst "truth(-8.74e-6)(I)"

To allow for a tolerance of 1% or 1e-7, respectively::

    $ mpl pictetra.hst "truth(-8.74e-6, 0.01)(I)"
    $ mpl pictetra.hst "truth(-8.74e-6, tol=1e-7)(I)"

Filters can also be composed, using one of either two methods::

    $ mpl pictetra.hst "compose(last, truth(-8.74, 0.01), ema(1e-6))(I)"
    $ mpl pictetra.hst "last(truth(-8.74, 0.01)(ema(1e-6)(I)))"

Filters can also be applied under the `filter` metadata in the files. Then you must omit the latter parenthesis `(I)`. For composition you will then have to use the `compose` function. To turn off filters applied in file from the command line interface, use::

    $ mpl pictetra.hst "plain(I)"
