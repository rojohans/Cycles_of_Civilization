import numpy as np

from scipy import interpolate


class Perlin2D():
    def __init__(self, maxOctaves = 5):

        self.maxOctaves = maxOctaves
        self.gridSize = 2**maxOctaves + 1

        graidentAngles = 2 * np.pi * np.random.rand(self.gridSize**2, 1)[:, 0]
        self.gradients = [[[] for colon in range(self.gridSize)] for row in range(self.gridSize)]

        i = 0
        for row in range(self.gridSize):
            for colon in range(self.gridSize):
                self.gradients[row][colon] = [np.cos(graidentAngles[i]), np.sin(graidentAngles[i])]
                i += 1
            self.gradients[row][-1] = self.gradients[row][0]
        for colon in range(self.gridSize):
            self.gradients[-1][colon] = self.gradients[0][colon]

    def Sample(self, x, y, resolution):
        '''
        :param x: [0, 1]
        :param y: [0, 1]
        :param resolution:
        :return: The interpolated noise at the given coordinates and resolution. The output is not normalized and will
                 be in the range [-1, 1].
        '''

        scale = 2**self.maxOctaves / resolution

        xScaled = x * resolution
        yScaled = y * resolution

        colonLower = np.floor(xScaled)
        rowLower = np.floor(yScaled)
        colonUpper = colonLower + 1
        rowUpper = rowLower + 1

        colonLowerMaxResolution = int(colonLower * scale)
        rowLowerMaxResolution = int(rowLower * scale)
        colonUpperMaxResolution = int(colonUpper * scale)
        rowUpperMaxResolution = int(rowUpper * scale)

        # Indices of the gradients
        # 2 ----- 3
        # :       :
        # :       :
        # 0 ----- 1
        gradients = [self.gradients[rowLowerMaxResolution][colonLowerMaxResolution],
                     self.gradients[rowLowerMaxResolution][colonUpperMaxResolution],
                     self.gradients[rowUpperMaxResolution][colonLowerMaxResolution],
                     self.gradients[rowUpperMaxResolution][colonUpperMaxResolution]]
        distances = [[xScaled - colonLower, yScaled - rowLower],
                     [xScaled - colonUpper, yScaled - rowLower],
                     [xScaled - colonLower, yScaled - rowUpper],
                     [xScaled - colonUpper, yScaled - rowUpper]]

        influenceValues = []
        for i in range(4):
            influenceValues.append(self.ListDot(gradients[i], distances[i]))
        u = self.SmoothInterpolant(xScaled - colonLower)
        v = self.SmoothInterpolant(yScaled - rowLower)

        bottomValue = self.LinearInterpolation(influenceValues[0], influenceValues[1], u)
        topValue = self.LinearInterpolation(influenceValues[2], influenceValues[3], u)
        middleValue = self.LinearInterpolation(bottomValue, topValue, v)
        return middleValue

    def SampleOctaves(self, x, y, persistance = 0.5, initialOctavesToSkip = 0):
        '''
        Samples the noise at different resolutions. The different noise values are weighted and then summed.
        :param x:
        :param y:
        :param persistance: The change in amplitude between each resolution. If <1 layers of higher resolution will be
                            weighted less.
        :param initialOctavesToSkip:
        :return: A weighted sum of the noise at the given coordinate for different resolutions (octaves)
        '''

        amplitude = 1
        totalValue = 0
        for octave in np.linspace(initialOctavesToSkip, self.maxOctaves, self.maxOctaves-initialOctavesToSkip+1):
            totalValue += amplitude * self.Sample(x, y, 2**octave)
            amplitude *= persistance

        return totalValue

    def ListDot(self, v1, v2):
        # Performs the dot product on two lists of length 2.
        return v1[0] * v2[0] + v1[1] * v2[1]

    def LinearInterpolation(self, a, b, u):
        return b*u + a * (1-u)

    def SmoothInterpolant(self, a):
        '''
        Scales the a value such that the interpolation will appear more smooth. a* = 6a^5 - 15a^4 + 10a^3
        :param a:
        :return:
        '''
        return 6*a**5 - 15*a**4 + 10*a**3

