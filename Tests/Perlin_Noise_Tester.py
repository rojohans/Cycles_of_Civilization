import numpy as np
import matplotlib.pyplot as plt

import Library.Noise as Noise


perlinObject = Noise.Perlin2D(maxOctaves = 8)

N_ROWS = 256
N_COLONS = 256
z = np.zeros((N_ROWS, N_COLONS))
for row in range(N_ROWS):
    for colon in range(N_COLONS):
        z[row, colon] = perlinObject.SampleOctaves(colon / N_COLONS, row / N_ROWS, persistance = 0.9, initialOctavesToSkip = 2)
plt.imshow(z)
plt.show()

'''
N_ROWS = 128
N_COLONS = 128

gridSize = 128
points = np.zeros((N_ROWS * N_COLONS, 3))
for row in range(N_ROWS):
    for colon in range(N_COLONS):
        points[colon + row * N_COLONS, 0] = 1 * np.cos(2 * np.pi * colon / N_COLONS)
        points[colon + row * N_COLONS, 1] = 1 * np.sin(2 * np.pi * colon / N_COLONS)
        points[colon + row * N_COLONS, 2] = 4 * row / N_ROWS
numberOfInitialIterationsToSkip = 1
amplitudeScaling = 1

elevationMap = Noise.PerlinNoiseSpherical(gridSize, points, numberOfInitialIterationsToSkip, amplitudeScaling)

#Noise.PerlinNoise2D


z = np.zeros((N_ROWS, N_COLONS))
for row in range(N_ROWS):
    for colon in range(N_COLONS):
        z[row, colon] = elevationMap[colon + row * N_COLONS]
z -= np.min(np.min(z))
z /= np.max(np.max(z))

plt.imshow(z)
plt.show()
'''




