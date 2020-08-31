import numpy as np
import matplotlib.pyplot as plt

import Library.Noise as Noise


perlinObject = Noise.Perlin2D(maxOctaves = 8)

N_ROWS = 128
N_COLONS = 128
z = np.zeros((N_ROWS, N_COLONS))
for row in range(N_ROWS):
    for colon in range(N_COLONS):
        z[row, colon] = perlinObject.SampleOctaves(colon / N_COLONS, row / N_ROWS, persistance = 0.7, initialOctavesToSkip = 2)
plt.imshow(z)
plt.show()


