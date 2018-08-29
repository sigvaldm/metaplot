import numpy as np
xs = np.linspace(0, 2*np.pi, 100)
ys1 = np.cos(xs)
ys2 = np.sin(xs)

with open('dummy.txt','w') as f:
    f.write('#SYMB t\tV\tI\n')
    for x,y1,y2 in zip(xs,ys1,ys2):
        f.write("{}\t{}\t{}\n".format(x,y1,y2))
