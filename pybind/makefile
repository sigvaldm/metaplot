CC=c++
CFLAGS=-O3 -Wall -shared -std=c++11 -fPIC `python3 -m pybind11 --includes`
EXTENSION=`python3-config --extension-suffix`
FNAME=ema

all:
	$(CC) $(CFLAGS) $(FNAME).cpp -o $(FNAME)$(EXTENSION)
