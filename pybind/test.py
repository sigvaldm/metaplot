from ema import ema
import numpy as np
import matplotlib.pyplot as plt

t = np.linspace(0,1,11)
x = np.zeros(t.shape)
x[0] = 1
ema(t, x, 0.1)
plt.plot(t,x)
plt.show()
