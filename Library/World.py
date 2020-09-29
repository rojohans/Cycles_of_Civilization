import numpy as np
from scipy import interpolate

import Library.Noise as Noise

class WorldClass():
    def __init__(self, discrete = False):

        self.elevationFloat = self.CreateMap(minValue = 0,
                                        maxValue = self.mainProgram.settings.ELEVATION_LEVELS-1,
                                        persistance = 0.5,
                                        initialOctavesToSkip = 2,
                                        applyDistributionFilter = False,
                                        distributionSteps = self.mainProgram.settings.ELEVATION_DISTRIBUTION)
        self.elevation = self.ApplyDistributionFilter(self.elevationFloat, self.mainProgram.settings.ELEVATION_DISTRIBUTION)
        extentedElevation = np.concatenate((self.elevation[:, self.mainProgram.settings.N_COLONS-2:self.mainProgram.settings.N_COLONS],
                                            self.elevation,
                                            self.elevation[:, 0:2]),
                                           axis=1)
        extentedElevation = np.concatenate((extentedElevation[0:1, :],
                                            extentedElevation,
                                            extentedElevation[self.mainProgram.settings.N_ROWS - 1:self.mainProgram.settings.N_ROWS, :]),
                                           axis=0)
        self.elevationInterpolator = interpolate.interp2d(np.linspace(-2, self.mainProgram.settings.N_COLONS-1+2, self.mainProgram.settings.N_COLONS+4),
                                                          np.linspace(-1, self.mainProgram.settings.N_ROWS-1 + 1, self.mainProgram.settings.N_ROWS+2),
                                                          extentedElevation, kind='cubic', fill_value=0)

        '''
        self.soilFertility = self.CreateMap(minValue = 0,
                                            maxValue = self.mainProgram.settings.SOIL_FERTILITY_LEVELS-1,
                                            persistance = 1.2,
                                            initialOctavesToSkip = 3,
                                            applyDistributionFilter = True,
                                            distributionSteps = self.mainProgram.settings.SOIL_FERTILITY_DISTRIBUTION)

        self.topographyRoughness = self.CreateMap(minValue = 0,
                                                  maxValue = self.mainProgram.settings.TOPOGRAPHY_ROUGHNESS_LEVELS-1,
                                                  persistance = 1,
                                                  initialOctavesToSkip = 3,
                                                  applyDistributionFilter = True,
                                                  distributionSteps = self.mainProgram.settings.TOPOGRAPHY_ROUGHNESS_DISTRIBUTION)
        self.soilFertility[self.elevation<=1] = -1
        self.topographyRoughness[self.elevation <= 1] = -1
        '''
        self.temperature = self.CreateTemperatureMap()

        self.moisture = self.CreateMoistureMap()

        #self.soilDepth =

        self.slope = self.CreateSlopeMap()



        # Makes the water shallow along all coasts.
        for row in np.linspace(1, self.mainProgram.settings.N_ROWS-2, self.mainProgram.settings.N_ROWS-2):
            for colon in range(self.mainProgram.settings.N_COLONS):
                if self.elevation[int(row), colon] == 0:

                    adjTiles = np.zeros((8, 2), dtype=int)
                    adjTiles[:, 0] = int(row) + self.mainProgram.settings.ADJACENT_TILES_TEMPLATE[:, 0]
                    adjTiles[:, 1] = np.mod(int(colon) + self.mainProgram.settings.ADJACENT_TILES_TEMPLATE[:, 1],
                                                 self.mainProgram.settings.N_COLONS)
                    for adjTile in adjTiles:
                        if self.elevation[adjTile[0], adjTile[1]] > 1:
                            self.elevation[int(row), colon] = 1
                            break

        #self.waterAbundance =

    def CreateMap(self,
                  minValue = 0,
                  maxValue = 1,
                  persistance = 1,
                  initialOctavesToSkip = 0,
                  applyDistributionFilter = False,
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
            pass
            #if discreteSteps:
            #    perlinMap = np.round(perlinMap)

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

    def ApplyDistributionFilter(self, map, distribution, discrete = False):
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
        # Calculate probabilityTemplate
        if discrete:
            for i in range(len(distribution)):
                p = distribution[i]
                levelSize = int(np.ceil(p * numberOfTiles))
                probabilityTemplate[tmpCount:tmpCount + levelSize] = i
                tmpCount += levelSize
        else:
            distributionCumulative = distribution.copy()
            for i in range(np.size(distribution, 0)):
                if i > 0:
                    distributionCumulative[i, 1] = distributionCumulative[i-1, 1] + distribution[i, 1]

            interpolator = interpolate.interp1d(x=distributionCumulative[:, 1],
                                                y=distributionCumulative[:, 0],
                                                kind='cubic')
            probabilityTemplate = interpolator(np.linspace(0, 1, numberOfTiles))

        # Alter map
        map = np.reshape(map, (numberOfTiles, 1))
        map -= len(distribution) + 100000
        for i in range(numberOfTiles):
            minValue = np.min(map)
            tmpIndex = np.where(map == minValue)[0]
            tmpIndex = tmpIndex[np.random.randint(0, len(tmpIndex))]
            map[tmpIndex] = probabilityTemplate[i]

        map = np.reshape(map, (self.mainProgram.settings.N_ROWS, self.mainProgram.settings.N_COLONS))

        if discrete:
            map = map.astype(int)

        return map

    def CreateTemperatureMap(self):
        '''
        Generates a temperature map from three layers. 1) Perlin noise
                                                       2) Latitude
                                                       3) Elevation
        :return:
        '''
        temperaturePerlin = self.CreateMap(minValue = self.mainProgram.settings.TEMPERATURE_MIN_VALUE,
                                           maxValue = self.mainProgram.settings.TEMPERATURE_MAX_VALUE,
                                           persistance = 0.5,
                                           initialOctavesToSkip = 3)
        temperatureElevation = self.mainProgram.settings.TEMPERATURE_MIN_VALUE*\
                               (self.elevation/(self.mainProgram.settings.ELEVATION_LEVELS-1))**2
        temperatureLatitude = np.zeros((self.mainProgram.settings.N_ROWS, self.mainProgram.settings.N_COLONS))
        for row in range(self.mainProgram.settings.N_ROWS):
            for colon in range(self.mainProgram.settings.N_COLONS):
                temperatureLatitude[row, colon] = np.cos(np.pi*(row-(self.mainProgram.settings.N_ROWS-1)/2)/(self.mainProgram.settings.N_ROWS-1))
        temperatureLatitude = (self.mainProgram.settings.TEMPERATURE_MAX_VALUE -
                               self.mainProgram.settings.TEMPERATURE_MIN_VALUE) *\
                              temperatureLatitude + self.mainProgram.settings.TEMPERATURE_MIN_VALUE

        temperatureTotalWeights = self.mainProgram.settings.TEMPERATURE_PERLIN_WEIGHT+\
                                  self.mainProgram.settings.TEMPERATURE_LATITUDE_WEIGHT
        temperatureMap = (temperaturePerlin*self.mainProgram.settings.TEMPERATURE_PERLIN_WEIGHT+\
                          temperatureLatitude*self.mainProgram.settings.TEMPERATURE_LATITUDE_WEIGHT)/\
                          temperatureTotalWeights + \
                          temperatureElevation*self.mainProgram.settings.TEMPERATURE_ELEVATION_WEIGHT
        return temperatureMap

    def CreateMoistureMap(self):
        '''
        Generates a moisture map from 4 layers. 1) Perlin noise
                                                2) Latitude (based on Hadley cells)
                                                3) Elevation
                                                4) Distance from ocean
        :return:
        '''
        moisturePerlin = self.CreateMap(minValue = 0,
                                        maxValue = 1,
                                        persistance = 0.5,
                                        initialOctavesToSkip = 3)

        moistureFromOcean = np.zeros((self.mainProgram.settings.N_ROWS, self.mainProgram.settings.N_COLONS))
        oceanCoordinates = []
        for row in range(self.mainProgram.settings.N_ROWS):
            for colon in range(self.mainProgram.settings.N_COLONS+2):
                if colon == 0:
                    colonWrapped = self.mainProgram.settings.N_COLONS-1
                elif colon == self.mainProgram.settings.N_COLONS+1:
                    colonWrapped = 0
                else:
                    colonWrapped = colon-1
                if self.elevation[row, colonWrapped] <= 1:
                    oceanCoordinates.append((row, colon))

        import scipy.spatial
        tree = scipy.spatial.KDTree(oceanCoordinates)

        for row in range(self.mainProgram.settings.N_ROWS):
            for colon in range(self.mainProgram.settings.N_COLONS):
                if self.elevation[row, colon] > 1:
                    p = tree.query((row, colon-1))

                    if p[0] < self.mainProgram.settings.MOISTURE_OCEAN_RANGE:
                        moistureFromOcean[row, colon] = (np.cos(np.pi*(p[0]-1)/self.mainProgram.settings.MOISTURE_OCEAN_RANGE)+1)/2
                    else:
                        moistureFromOcean[row, colon] = 0

        moistureLatitude = np.zeros((self.mainProgram.settings.N_ROWS, self.mainProgram.settings.N_COLONS))
        for row in range(self.mainProgram.settings.N_ROWS):
            for colon in range(self.mainProgram.settings.N_COLONS):
                moistureLatitude[row, colon] = (1+np.cos(6*np.pi*(row-(self.mainProgram.settings.N_ROWS-1)/2)/(self.mainProgram.settings.N_ROWS-1)))/2

        moistureElevation = self.mainProgram.settings.MOISTURE_ELEVATION_WEIGHT*\
                            (self.elevation/(self.mainProgram.settings.ELEVATION_LEVELS-1))**4

        moistureTotalWeights = self.mainProgram.settings.MOISTURE_PERLIN_WEIGHT + \
                               self.mainProgram.settings.MOISTURE_OCEAN_WEIGHT + \
                               self.mainProgram.settings.MOISTURE_LATITUDE_WEIGHT

        moistureMap = (moisturePerlin*self.mainProgram.settings.MOISTURE_PERLIN_WEIGHT +
                       moistureFromOcean*self.mainProgram.settings.MOISTURE_OCEAN_WEIGHT +
                       moistureLatitude*self.mainProgram.settings.MOISTURE_LATITUDE_WEIGHT)/moistureTotalWeights-\
                      moistureElevation

        moistureMap[moistureMap<0] = 0
        moistureMap[moistureMap>1] = 1
        moistureMap[self.elevation<=1] = 2
        return moistureMap

    def CreateSlopeMap(self):
        slopeMap = np.zeros((self.mainProgram.settings.N_ROWS, self.mainProgram.settings.N_COLONS))



        for row in range(self.mainProgram.settings.N_ROWS):
            for colon in range(self.mainProgram.settings.N_COLONS):
                adjacentTiles = np.zeros((4, 2))
                adjacentCross = 0.1 * self.mainProgram.settings.ADJACENT_TILES_TEMPLATE_CROSS.copy()
                adjacentTiles[:, 0] = row + adjacentCross[:, 0]
                adjacentTiles[:, 1] = colon + adjacentCross[:, 1]

                crossElevation = self.elevationInterpolator([colon-0.1, colon, colon+0.1], [row-0.1, row, row+0.1])

                diffx = np.array([0.2, 0, crossElevation[1, 2]-crossElevation[1, 0]])
                diffy = np.array([0, 0.2, crossElevation[2, 1]-crossElevation[0, 1]])
                normal = [diffx[1] * diffy[2] - diffx[2] * diffy[1],
                          diffx[2] * diffy[0] - diffx[0] * diffy[2],
                          diffx[0] * diffy[1] - diffx[1] * diffy[0]]
                normal /= np.sqrt(normal[0]**2 + normal[1]**2 + normal[2]**2)

                #slopeMap[row, colon] = 1 - normal[2]
                slopeMap[row, colon] = 2*np.arccos(normal[2]/1)/np.pi
        return slopeMap

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

