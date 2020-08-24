import numpy as np

class WorldClass():
    def __init__(self):

        import Library.Noise as Noise

        gridSize = 128
        points = np.zeros((self.mainProgram.settings.N_ROWS* self.mainProgram.settings.N_COLONS, 3))
        for row in range(self.mainProgram.settings.N_ROWS):
            for colon in range(self.mainProgram.settings.N_COLONS):
                points[colon + row * self.mainProgram.settings.N_COLONS, 0] = 1*np.cos(2*np.pi*colon/self.mainProgram.settings.N_COLONS)
                points[colon + row * self.mainProgram.settings.N_COLONS, 1] = 1*np.sin(2*np.pi*colon/self.mainProgram.settings.N_COLONS)
                points[colon + row * self.mainProgram.settings.N_COLONS, 2] = 2*row/self.mainProgram.settings.N_ROWS
        numberOfInitialIterationsToSkip = 1
        amplitudeScaling = 1.2

        #print(points)

        elevationMap = Noise.PerlinNoiseSpherical(gridSize, points, numberOfInitialIterationsToSkip, amplitudeScaling)
        grassPropabilityList = Noise.PerlinNoiseSpherical(gridSize, points, numberOfInitialIterationsToSkip, amplitudeScaling=1.0)
        desertPropabilityList = Noise.PerlinNoiseSpherical(gridSize, points, numberOfInitialIterationsToSkip, amplitudeScaling=1.0)
        tundraProbabilityList = Noise.PerlinNoiseSpherical(gridSize, points, numberOfInitialIterationsToSkip, amplitudeScaling=1.0)

        self.z = np.zeros((self.mainProgram.settings.N_ROWS, self.mainProgram.settings.N_COLONS))
        for row in range(self.mainProgram.settings.N_ROWS):
            for colon in range(self.mainProgram.settings.N_COLONS):
                self.z[row, colon] = elevationMap[colon + row * self.mainProgram.settings.N_COLONS]
        self.z -= np.min(np.min(self.z))
        self.z /= np.max(np.max(self.z))



    @classmethod
    def Initialize(cls, mainProgram):
        cls.mainProgram = mainProgram







