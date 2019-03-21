Usage
=====

Metaplot is a library for plotting CSV files, and is currently in a very experimental stage. It is not fully documented, but a brief summary follows.

As an example, the top of a CSV file may look like the following:

.. literalinclude:: history.dat

Comments starts with ``#`` and Metaplot metadata on lines starting with ``#:``.
The metadata includes a short symbolic name of the quantities in each column, a longer name which Metaplot can use for a description, which units the quantities are in. It also tells Metaplot which column to use as the x-axis (by default).

CSV files comes in different varieties, and Metaplot will attempt to sniff the format of the file. If it is not capable of reading a kind of CSV file, Metaplot has a plugin system which allows the user to make readers for different kinds of CSV file. This is implemented but not documented.

Metaplot can be used either as a library, or as a stand-alone command line tool to make plots. It has the following synposis::

    $ mpl [optional flags] <files and expressions>

Each expression will be plotted for each file in the list, and the order of files and expressions doesn't matter. Examples of plotting named quantities from files::

    $ mpl pictetra.hst ne
    $ mpl pictetra.hst history.dat ne ni
    $ mpl ne ni pictetra.hst
    $ mpl pictetra.hst "I[0]"
    $ mpl pictetra.hst I

Expressions must be enclosed in quotation marks whenever it contains symbols the shell would otherwise complain about. Metaplot will try to find correct labels and units on the axis, although this is at the time a bit faulty. Expressions can also be arithmetic expressions of named quantities, or constants::

    $ mpl pictetra.hst ne+ni
    $ mpl pictetra.hst "sum(I)"
    $ mpl pictetra.hst ne 3.2

Arithmetic expression that are dimensionally incorrect will issue an error, e.g., you cannot take the sum of meters and seconds.

Metaplot comes with several filters, which are just functions applied to dataseries. To plot the last datapoint in a series::

    $ mpl pictetra.hst "last(I)"

To apply exponential moving average (EMA) filter of 1 microsecond relaxation time::

    $ mpl pictetra.hst "ema(1e-6)(I)"

Whereas ``last`` don't take any hyperparameters, ``ema`` takes the relaxation time as a hyperparameter. After hyperparameters are applied, filters have _only_ the dataseries as a parameter.

``truth`` is useful to compare a curve to a ground truth. E.g if ``I`` should be -8.74 microamperes::

    $ mpl pictetra.hst "truth(-8.74e-6)(I)"

To allow for a tolerance of 1% or 1e-7, respectively::

    $ mpl pictetra.hst "truth(-8.74e-6, 0.01)(I)"
    $ mpl pictetra.hst "truth(-8.74e-6, tol=1e-7)(I)"

Filters can also be composed, using one of either two methods::

    $ mpl pictetra.hst "last(truth(-8.74e-6, 0.01)(ema(1e-6)(I)))"
    $ mpl pictetra.hst "compose(last, truth(-8.74e-6, 0.01), ema(1e-6))(I)"

Filters can also be applied under the ``filter`` metadata in the files, for instance as follows::

    #:filter    last    ema(1e-6)   -   -   compose(last, ema(1e-6))

The filters when specified in the CSV files are assumed to be a function of only one argument, namely the quantity to be plotted. This means that any hyperparameters are specified in the first paranthesis, but the latter paranthesis is omitted. For composition you will then have to use the ``compose()`` function since you cannot nest the functions using this syntax. Use ``-`` for columns without filter. To override filters applied in file from the command line interface, use the ``plain`` filter like this::

    $ mpl pictetra.hst "plain(I)"

Metaplot is supposed to support user-defined filters through the plugin-system in the future.
