import numpy as np

import Library.Noise as Noise

class WorldClass():
    def __init__(self, discrete = False):

        self.elevation = self.CreateMap(minValue = 0,
                                        maxValue = self.mainProgram.settings.ELEVATION_LEVELS-1,
                                        persistance = 0.7,
                                        initialOctavesToSkip = 2,
                                        discreteSteps=self.mainProgram.settings.DISCRETE_ELEVATION,
                                        applyDistributionFilter = True,
                                        distributionSteps = self.mainProgram.settings.ELEVATION_DISTRIBUTION)

        self.soilFertility = self.CreateMap(minValue = 0,
                                            maxValue = self.mainProgram.settings.SOIL_FERTILITY_LEVELS-1,
                                            persistance = 1.2,
                                            initialOctavesToSkip = 3,
                                            discreteSteps = self.mainProgram.settings.DISCRETE_SOIL_FERTILITY_LEVELS,
                                            applyDistributionFilter = True,
                                            distributionSteps = self.mainProgram.settings.SOIL_FERTILITY_DISTRIBUTION)

        self.topographyRoughness = self.CreateMap(minValue = 0,
                                                  maxValue = self.mainProgram.settings.TOPOGRAPHY_ROUGHNESS_LEVELS-1,
                                                  persistance = 1,
                                                  initialOctavesToSkip = 3,
                                                  discreteSteps=self.mainProgram.settings.DISCRETE_TOPOGRAPHY_ROUGHNESS_LEVELS,
                                                  applyDistributionFilter = True,
                                                  distributionSteps = self.mainProgram.settings.TOPOGRAPHY_ROUGHNESS_DISTRIBUTION)

        self.soilFertility[self.elevation<=1] = -1
        self.topographyRoughness[self.elevation <= 1] = -1

        #self.waterAbundance =

    def CreateMap(self,
                  minValue = 0,
                  maxValue = 1,
                  persistance = 1,
                  initialOctavesToSkip = 0,
                  applyDistributionFilter = False,
                  discreteSteps = False,
                  distributionSteps = None):
        '''
        Generates a perlin noise which are scaled according to input values. The noise is then filtered (if the correct
        input was given).
        :param minValue:
        :param maxValue:
        :param persistance:
        :param initialOctavesToSkip:
        :param applyDistributionFilter:
        :param discreteSteps:
        :param distributionSteps:
        :return:
        '''
        perlinMap = self.CreatePerlinMap(persistance = persistance, initialOctavesToSkip = initialOctavesToSkip)

        perlinMin = np.min(perlinMap)
        perlinMax = np.max(perlinMap)
        perlinMap = (perlinMap - perlinMin) / (perlinMax - perlinMin)
        perlinMap = (maxValue-minValue) * perlinMap + minValue

        if applyDistributionFilter:
            perlinMap = self.ApplyDistributionFilter(perlinMap, distributionSteps)
        else:
            if discreteSteps:
                perlinMap = np.round(perlinMap)

        return perlinMap

    def CreatePerlinMap(self, persistance = 1, initialOctavesToSkip = 0):
        perlinMaxResolution = np.max([self.mainProgram.settings.N_ROWS, self.mainProgram.settings.N_COLONS])
        perlinMaxOctaves = int(np.ceil(np.log2(perlinMaxResolution)))

        perlinObject = Noise.Perlin2D(maxOctaves=perlinMaxOctaves)
        z = np.zeros((self.mainProgram.settings.N_ROWS, self.mainProgram.settings.N_COLONS))
        for row in range(self.mainProgram.settings.N_ROWS):
            for colon in range(self.mainProgram.settings.N_COLONS):
                z[row, colon] = perlinObject.SampleOctaves(colon / perlinMaxResolution,
                                                           row / perlinMaxResolution,
                                                           persistance=persistance,
                                                           initialOctavesToSkip=initialOctavesToSkip)
        return z

    def ApplyDistributionFilter(self, map, distribution):
        '''
        Changes the map values to correspond with the distribution values in the input. If distribution = [0.6, 0.3, 0.1]
        60% of the map values will be 0, 30% 1 and 10% 2.
        :param map:
        :param distribution: A list of float values, the sum is assumed to be one.
        :return:
        '''
        numberOfTiles = self.mainProgram.settings.N_ROWS * self.mainProgram.settings.N_COLONS
        probabilityTemplate = np.ones((numberOfTiles, 1))
        tmpCount = 0
        for i in range(len(distribution)):
            p = distribution[i]
            levelSize = int(np.ceil(p * numberOfTiles))
            probabilityTemplate[tmpCount:tmpCount + levelSize] = i
            tmpCount += levelSize
        map = np.reshape(map, (numberOfTiles, 1))
        map -= len(distribution) + 1000

        for i in range(numberOfTiles):
            minValue = np.min(map)
            tmpIndex = np.where(map == minValue)[0]
            tmpIndex = tmpIndex[np.random.randint(0, len(tmpIndex))]
            map[tmpIndex] = probabilityTemplate[i]

        map = np.reshape(map, (self.mainProgram.settings.N_ROWS, self.mainProgram.settings.N_COLONS))
        map = map.astype(int)

        return map

    @classmethod
    def VisualizeMaps(cls, maps):
        import matplotlib.pyplot as plt
        for map in maps:
            plt.figure()
            plt.imshow(map)
        plt.show()

    @classmethod
    def Initialize(cls, mainProgram):
        cls.mainProgram = mainProgram

