from numpy import cos, sin
import numpy as np
import matplotlib.pyplot as plt

class tabData(dict):

    def __init__(self, fname):
        raw_data  = []
        names     = []
        mul       = []
        raw_long = []
        raw_unit = []
        with open(fname,'r') as f:
            for l in f:

                # METADATA:
                # NAME
                # LONG
                # MUL
                # UNIT

                # Search for metadata
                meta = l.split('#NAME')
                if len(meta)>1:
                    names = meta[-1].split()

                meta = l.split('#MUL')
                if len(meta)>1:
                    mul = meta[-1].split()

                meta = l.split('#LONG')
                if len(meta)>1:
                    raw_long = meta[-1].split()

                meta = l.split('#UNIT')
                if len(meta)>1:
                    raw_unit = meta[-1].split()

                # Read raw data
                values = l.split('#')[0] # Remove comments
                values.strip()
                if len(values)>0:
                    raw_data.append(values.split())

        # Process raw data
        raw_data = np.array(raw_data, dtype=float)
        self.long = {}
        self.unit = {}
        for i in range(raw_data.shape[1]):
            self[names[i]] = float(mul[i])*raw_data[:,i]
            self.long[names[i]] = raw_long[i]
            self.unit[names[i]] = raw_unit[i]

    def parse(self, expression):
        for key in data.keys():
            expression = expression.replace(key,"self['"+key+"']")
        return eval(expression)

    def plot(self, x, y):
        plt.plot(self.parse(x), self.parse(y))

        xlabel = self.long[x] if x in self.long.keys() else x
        ylabel = self.long[y] if y in self.long.keys() else y
        plt.title(ylabel.capitalize() + ' vs. ' + xlabel)
        if x in self.unit.keys(): xlabel += ' ['+self.unit[x]+']'
        if y in self.unit.keys(): ylabel += ' ['+self.unit[y]+']'
        plt.xlabel(xlabel.capitalize())
        plt.ylabel(ylabel.capitalize())
        plt.grid()

if __name__ == '__main__':
    data = tabData('dummy.txt')
    data.plot('t', 'sin(t)')
    data.plot('t', 'V')
    plt.show()
