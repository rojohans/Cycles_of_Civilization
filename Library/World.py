import panda3d.core as p3d
import numpy as np
from scipy import interpolate
import matplotlib.pyplot as plt
import noise

import Library.Noise as Noise

class WorldClass():
    def __init__(self, discrete = False, numberOfErosionIterations = 500):

        #self.elevationFloat = self.CreateMap(minValue = 0,
        #                                maxValue = self.mainProgram.settings.ELEVATION_LEVELS-1,
        #                                persistance = 0.5,
        #                                initialOctavesToSkip = 2,
        #                                applyDistributionFilter = False,
        #                                distributionSteps = self.mainProgram.settings.ELEVATION_DISTRIBUTION)
        '''
        self.elevationFloat = self.CreateMap(rows=self.mainProgram.settings.N_ROWS,
                                             colons=self.mainProgram.settings.N_COLONS,
                                        minValue = 0,
                                        maxValue = self.mainProgram.settings.ELEVATION_LEVELS-1,
                                        persistance = 1,
                                        initialOctavesToSkip = 2,
                                        applyDistributionFilter = False,
                                        distributionSteps = self.mainProgram.settings.ELEVATION_DISTRIBUTION)
        self.elevation = self.ApplyDistributionFilter(self.elevationFloat, self.mainProgram.settings.ELEVATION_DISTRIBUTION)
        '''
        self.elevation, self.topography = self.CreateElevationMap(numberOfErosionIterations = numberOfErosionIterations)

        #self.elevationInterpolated = self.CreateMap(rows=self.mainProgram.settings.N_ROWS*self.mainProgram.settings.MODEL_RESOLUTION,
        #                                            colons=self.mainProgram.settings.N_COLONS*self.mainProgram.settings.MODEL_RESOLUTION,
        #                                            minValue=0,
        #                                            maxValue=self.mainProgram.settings.ELEVATION_LEVELS - 1,
        #                                            persistance=0.5,
        #                                            initialOctavesToSkip=2,
        #                                            applyDistributionFilter=False,
        #                                            distributionSteps=self.mainProgram.settings.ELEVATION_DISTRIBUTION)
        #self.elevationInterpolated = self.ApplyDistributionFilter(self.elevationInterpolated,
        #                                                          self.mainProgram.settings.ELEVATION_DISTRIBUTION)
        '''
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
        self.elevationInterpolated = self.elevationInterpolator(np.linspace(-0.5, self.mainProgram.settings.N_COLONS-0.5, self.mainProgram.settings.N_COLONS*self.mainProgram.settings.MODEL_RESOLUTION),
                                         np.linspace(-0.5, self.mainProgram.settings.N_ROWS-0.5, self.mainProgram.settings.N_ROWS*self.mainProgram.settings.MODEL_RESOLUTION))
        

        
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

        #self.slope = self.CreateSlopeMap()



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
                  rows,
                  colons,
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


        perlinMap = self.CreatePerlinMap(rows=rows, colons=colons,persistance = persistance, initialOctavesToSkip = initialOctavesToSkip)

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

    def CreatePerlinMap(self, rows, colons, persistance = 1, initialOctavesToSkip = 0):
        perlinMaxResolution = np.max([rows, colons])
        perlinMaxOctaves = int(np.ceil(np.log2(perlinMaxResolution)))

        perlinObject = Noise.Perlin2D(maxOctaves=perlinMaxOctaves)
        z = np.zeros((rows, colons))
        for row in range(rows):
            for colon in range(colons):
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
        rows = np.size(map, 0)
        colons = np.size(map, 1)
        numberOfTiles = rows * colons
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

        map = np.reshape(map, (rows, colons))

        if discrete:
            map = map.astype(int)

        return map

    def CreateElevationMap(self, numberOfErosionIterations = 500):
        import perlin_numpy
        import Library.Erosion as Erosion

        shape = (self.mainProgram.settings.N_ROWS*(self.mainProgram.settings.MODEL_RESOLUTION-2),
                 self.mainProgram.settings.N_COLONS*(self.mainProgram.settings.MODEL_RESOLUTION-2))
        octaves = int(np.log2(np.max(shape))-1)

        rockMap = perlin_numpy.generate_fractal_noise_2d(shape, (2, 4), octaves=octaves, lacunarity=2, persistence=0.4,
                                                                tileable=(False, True))
        roughNoise = perlin_numpy.generate_fractal_noise_2d(shape, (2, 4), octaves=8, lacunarity=2, persistence=0.8,
                                                            tileable=(False, True))
        rockMap -= np.min(rockMap)
        rockMap /= np.max(rockMap)

        roughNoise -= np.min(roughNoise)
        roughNoise /= np.max(roughNoise)
        #elevation *= 8 * 30*0.5
        rockMap *= 512/10
        rockMap += 10 * roughNoise

        elevation = np.zeros((shape[0], shape[1], 2))
        elevation[:, :, 0] = rockMap

        Erosion.HydrolicErosion.InitializeRainDropTemplates(maximumRainDropRadius=20)

        self.hydrolicErosion = Erosion.HydrolicErosion(terrain=elevation,
                                                       evaporationRate=0.1,
                                                       deltaT=0.1,
                                                       flowSpeed=3,
                                                       sedimentFlowSpeed=1,
                                                       gridLength=1,
                                                       carryCapacityLimit=4,
                                                       erosionRate=[0.05, 0.5],
                                                       depositionRate=0.1,
                                                       maximumErosionDepth=10)

        self.thermalErosion = Erosion.ThermalErosion(terrain=elevation,
                                                     maximumSlope=[90, 30],
                                                     flowSpeed=1,
                                                     deltaT=0.1)

        self.thermalWeathering = Erosion.ThermalWeathering(terrain=elevation,
                                                           weatheringRate=[1, 1])

        for i in range(numberOfErosionIterations):
            if i > 400:
                rainAmount = 0
            else:
                rainAmount = 0.01 * (1 + np.sin(i / 15)) / 2
            self.hydrolicErosion.Rain(numberOfDrops=1, radius=10, dropSize=rainAmount, application='even')
            self.hydrolicErosion()

            if i < 400:
                self.thermalWeathering.Weather(0.02)
            self.thermalErosion()

        elevation = np.sum(elevation, 2)
        elevation -= np.min(elevation)
        elevation /= np.max(elevation)
        elevation *= self.mainProgram.settings.ELEVATION_LEVELS

        from scipy import interpolate
        interpolator = interpolate.interp2d(np.linspace(-0.5, self.mainProgram.settings.N_COLONS-0.5, self.mainProgram.settings.N_COLONS*(self.mainProgram.settings.MODEL_RESOLUTION-2)),
                             np.linspace(-0.5, self.mainProgram.settings.N_ROWS-0.5, self.mainProgram.settings.N_ROWS*(self.mainProgram.settings.MODEL_RESOLUTION-2)),
                             elevation.copy())
        tileElevation = interpolator(range(self.mainProgram.settings.N_COLONS), range(self.mainProgram.settings.N_ROWS))

        return tileElevation, elevation


    def CreateTemperatureMap(self):
        '''
        Generates a temperature map from three layers. 1) Perlin noise
                                                       2) Latitude
                                                       3) Elevation
        :return:
        '''
        temperaturePerlin = self.CreateMap(rows=self.mainProgram.settings.N_ROWS,
                                           colons=self.mainProgram.settings.N_COLONS,
                                            minValue = self.mainProgram.settings.TEMPERATURE_MIN_VALUE,
                                           maxValue = self.mainProgram.settings.TEMPERATURE_MAX_VALUE,
                                           persistance = 0.5,
                                           initialOctavesToSkip = 3)
        temperatureElevation = self.mainProgram.settings.TEMPERATURE_MIN_VALUE*\
                               (self.elevation/(self.mainProgram.settings.ELEVATION_LEVELS-1))**3
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
        moisturePerlin = self.CreateMap(rows=self.mainProgram.settings.N_ROWS,
                                        colons=self.mainProgram.settings.N_COLONS,
                                        minValue = 0,
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
        moistureMap -= np.min(moistureMap)
        moistureMap /= np.max(moistureMap)
        moistureMap *= 0.99
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

class SphericalWorld():
    def __init__(self, nDivisions = 0):
        self.icosahedronVertices, self.icosahedronFaces = self.GetIcosahedron()

        self.nDivisions = nDivisions

        for i in range(20):
            if i == 0:
                self.v, self.f = self.SubdivideTriangle(self.icosahedronVertices[self.icosahedronFaces[0, :]],
                                                        divisions=self.nDivisions)
            else:
                v, f = self.SubdivideTriangle(self.icosahedronVertices[self.icosahedronFaces[i, :]], divisions=self.nDivisions)
                f[:, 1:] += np.size(self.v, 0)

                self.v = np.concatenate((self.v, v), axis = 0)
                self.f = np.concatenate((self.f, f), axis = 0)

        self.v = self.NormalizeVertices(self.v)
        self.unscaledVertices = self.v.copy()

        self.faceCoordinates = self.CalculateFaceCoordinates(self.v, self.f)
        self.unscaledFaceCoordinates = self.faceCoordinates.copy()

        n = self.PerlinNoise(self.v, octaves=10, persistence=0.9)**2
        n -= 0.3
        n[n<0] = 0
        n /= np.max(n)

        #print(np.shape(self.v))
        #print(np.shape(n))
        n *= 100
        n += 100
        self.v[:, 0] *= n[:, 0]
        self.v[:, 1] *= n[:, 0]
        self.v[:, 2] *= n[:, 0]

        self.vertexRadius = self.CalculateVertexRadius(self.v)
        self.faceRadius = self.CalculateFaceRadius(self.v, self.f)
        self.minRadius = np.min(self.faceRadius)

        self.faceCoordinates[:, 0] *= self.faceRadius
        self.faceCoordinates[:, 1] *= self.faceRadius
        self.faceCoordinates[:, 2] *= self.faceRadius

        self.faceConnections = self.CalculateFaceConnections(self.faceCoordinates)

    @staticmethod
    def GetIcosahedron():
        #https: // en.wikipedia.org / wiki / Regular_icosahedron
        PHI = (1 + np.sqrt(5)) / 2 # Golden ratio
        vertices = np.array([
            [-1, PHI, 0],
            [1, PHI, 0],
            [-1, -PHI, 0],
            [1, -PHI, 0],
            [0, -1, PHI],
            [0, 1, PHI],
            [0, -1, -PHI],
            [0, 1, -PHI],
            [PHI, 0, -1],
            [PHI, 0, 1],
            [-PHI, 0, -1],
            [-PHI, 0, 1],
        ])
        faces = np.array([
            [0, 11, 5],
            [0, 5, 1],
            [0, 1, 7],
            [0, 7, 10],
            [0, 10, 11],
            [1, 5, 9],
            [5, 11, 4],
            [11, 10, 2],
            [10, 7, 6],
            [7, 1, 8],
            [3, 9, 4],
            [3, 4, 2],
            [3, 2, 6],
            [3, 6, 8],
            [3, 8, 9],
            [4, 9, 5],
            [2, 4, 11],
            [6, 2, 10],
            [8, 6, 7],
            [9, 8, 1],
        ])
        return vertices, faces

    @staticmethod
    def SubdivideTriangle(cornerTriangles, divisions = 1, onlyGetSize = False):
        #xCorner = baseVertices[baseFaces[0, :]]
        v0 = cornerTriangles[1, :] - cornerTriangles[0, :]
        v1 = cornerTriangles[2, :] - cornerTriangles[0, :]
        xBase = cornerTriangles[0, :]

        divisions += 2

        # Calculate the total number of vertices
        nVertices = 0
        for i0, l0 in enumerate(np.linspace(0, 1, divisions)):
            for l1 in np.linspace(0, 1 - l0, divisions - i0):
                nVertices += 1

        # Calculates the vertices
        vertices = np.empty((nVertices, 3))
        nVertice = 0
        for i0, l0 in enumerate(np.linspace(0, 1, divisions)):
            for l1 in np.linspace(0, 1 - l0, divisions - i0):
                vertices[nVertice, :] = xBase + l0 * v0 + l1 * v1
                nVertice += 1

        # Calculate the total number of faces
        m = 0
        nFaces = 0
        for i0 in np.linspace(0, divisions - 2, divisions - 1, dtype=int):
            for i1 in np.linspace(0, divisions - i0 - 2, divisions - i0 - 1):
                nFaces += 1
                if i1 > 0:
                    nFaces += 1
            m += divisions - i0

        # Calculates the faces
        faces = []
        m = 0
        nFace = 0
        for i0 in np.linspace(0, divisions - 2, divisions - 1, dtype=int):
            for i1 in np.linspace(0, divisions - i0 - 2, divisions - i0 - 1, dtype=int):
                faces.append([3, m + i1 + 1, m + i1, m + divisions - i0 + i1])
                nFace += 1
                if i1 > 0:
                    faces.append([3, m + i1, m + divisions - i0 + i1 - 1, m + divisions - i0 + i1])
                    nFace += 1
            m += divisions - i0
        faces = np.array(faces)

        return vertices, faces

    def NormalizeVertices(self, vertices):
        r = np.sqrt(vertices[:, 0]**2 + vertices[:, 1]**2 + vertices[:, 2]**2)
        vertices[:, 0] /= r
        vertices[:, 1] /= r
        vertices[:, 2] /= r
        return vertices

    @staticmethod
    def PerlinNoise(vertices, octaves = 10, persistence = 0.5, lacunarity = 2.0, seed = None, scale = 1.0):
        '''
        :param vertices:
        :param octaves: Determines the maximum resolution
        :param persistence: Determines the amplitude impact of each layer
        :param lacunarity:
        :return:
        '''
        scale = 1.0
        if seed == None:
            seed = np.random.randint(0, 100)

        noiseArray = np.empty((np.size(vertices, 0), 1))

        for i, vertex in enumerate(vertices):
            noiseArray[i, 0] = noise.pnoise3(vertex[0] / scale,
                                            vertex[1] / scale,
                                            vertex[2] / scale,
                                            octaves=octaves,
                                            persistence=persistence,
                                            lacunarity=lacunarity,
                                            base=seed)
        noiseArray -= np.min(noiseArray)
        noiseArray /= np.max(noiseArray)
        return noiseArray

    @staticmethod
    def WarpedPerlinNoise(vertices, xWarp, yWarp, zWarp, octaves = 10, persistence = 0.5, lacunarity = 2.0, seed = None, scale = 1.0):
        '''
        :param vertices:
        :param octaves: Determines the maximum resolution
        :param persistence: Determines the amplitude impact of each layer
        :param lacunarity:
        :return:
        '''
        if seed == None:
            seed = np.random.randint(0, 100)

        noiseArray = np.empty((np.size(vertices, 0), 1))

        for i, vertex in enumerate(vertices):
            noiseArray[i, 0] = noise.pnoise3((xWarp[i] + vertex[0]) / scale,
                                             (yWarp[i] + vertex[1]) / scale,
                                             (zWarp[i] + vertex[2]) / scale,
                                             octaves=octaves,
                                             persistence=persistence,
                                             lacunarity=lacunarity,
                                             base=seed)
        noiseArray -= np.min(noiseArray)
        noiseArray /= np.max(noiseArray)
        return noiseArray

    def CalculateVertexRadius(self, vertices):
        return np.sqrt(vertices[:, 0]**2 + vertices[:, 1]**2 + vertices[:, 2]**2)

    def CalculateFaceRadius(self, vertices, faces):
        vertexRadius = np.sqrt(vertices[:, 0] ** 2 + vertices[:, 1] ** 2 + vertices[:, 2] ** 2)
        return np.sum(vertexRadius[faces[:, 1:]], axis = 1)/3

    def CalculateFaceNormals(self, vertices, faces):
        normals = np.empty((np.size(faces, 0), 3))
        for iFace in range(np.size(faces, 0)):
            #normal_writer.add_data3(p3d.Vec3(self.normals[y, x, 0], self.normals[y, x, 1], self.normals[y, x, 2]))
            v = vertices[faces[iFace, 1:]]
            v0 = v[1, :] - v[0, :]
            v1 = v[2, :] - v[0, :]
            normals[iFace, :] = [v0[1]*v1[2] - v1[1]*v0[2], v1[0]*v0[2] - v0[0]*v1[2], v0[0]*v1[1] - v1[0]*v0[1]]
        return normals

    def CalculateFaceTemperature(self, vertices, faces, faceRadius):
        temperatures = np.empty((np.size(faces, 0), 1))
        minRadius = np.min(faceRadius)
        faceRadiusScaled = faceRadius.copy() - minRadius
        faceRadiusScaled /= np.max(faceRadiusScaled)
        for iFace in range(np.size(faces, 0)):
            v = vertices[faces[iFace, 1:]]
            v = np.sum(v, axis = 0)/3
            latitudeAngle = np.arcsin( v[2]/faceRadius[iFace] )
            temperatures[iFace, 0] = 0 + 1.5*np.cos(latitudeAngle)**2 - 1.5*faceRadiusScaled[iFace]**2
        return temperatures

    def Smooth(self, vertices, faces, vertexRadius, faceRadius):
        vertexRadiusSmoothed =vertexRadius.copy()
        l = 0.8
        for iFace in range(np.size(faces, 0)):
            tris = faces[iFace, 1:]
            r = vertexRadiusSmoothed[faces[iFace, 1:]]
            vertexRadiusSmoothed[tris[0]] = faceRadius[iFace]*l + (1-l)*r[0]
            vertexRadiusSmoothed[tris[1]] = faceRadius[iFace]*l + (1-l)*r[1]
            vertexRadiusSmoothed[tris[2]] = faceRadius[iFace]*l + (1-l)*r[2]
        return vertexRadiusSmoothed

    @staticmethod
    def CalculateFaceCoordinates(vertices, faces):
        faceCoordinates = np.empty((np.size(faces, 0), 3))

        for iFace in range(np.size(faces, 0)):
            v = vertices[faces[iFace, 1:]]
            v = np.sum(v, axis = 0)/3
            faceCoordinates[iFace, :] = v
        return faceCoordinates

    def CalculateFaceConnections(self, faceCoordinates):
        faceConnections = np.empty((np.size(faceCoordinates, 0), 3), dtype=int)

        from scipy.spatial import cKDTree

        data = faceCoordinates.copy()
        r = np.sqrt(data[:, 0]**2 + data[:, 1]**2 + data[:, 2]**2)
        data[:, 0] /= r
        data[:, 1] /= r
        data[:, 2] /= r

        faceTree = cKDTree(data=data)
        for iFace in range(np.size(faceCoordinates, 0)):
            r, id = faceTree.query(data[iFace, :], 4)
            faceConnections[iFace, :] = id[1:]
        return faceConnections


class WorldProperties():
    def __init__(self, mainProgram, temperature, elevation, slope):
        self.mainProgram = mainProgram
        self.temperature = temperature
        self.elevation = elevation
        self.slope = slope

    def DetermineWater(self):
        '''
        Determines which tiles are covered with water.
        :return:
        '''
        #self.isWater = np.empty((np.size(self.mainProgram.world.f, 0), 0))
        self.isWater = np.ones((np.size(self.mainProgram.world.f, 0), 1), dtype=bool)
        for iFace in range(np.size(self.mainProgram.world.f, 0)):
            if self.mainProgram.world.faceRadius[iFace] > self.mainProgram.waterWorld.faceRadius[iFace]:
                self.isWater[iFace] = False
            else:
                self.isWater[iFace] = True


class VisualWorld():
    def __init__(self, mainProgram, vertices, faces, faceNormals):
        self.mainProgram = mainProgram
        self.vertices = vertices
        self.faces = faces
        self.faceNormals = faceNormals

        # Wether the object's textures are up-to-date.
        self.textureUpdatedStatus = False

        # getV3n3c4t2() : vertices3, normals3, colours4, textureCoordinates2
        # v3n3t2 : vertices3, normals3, textureCoordinates2
        #vertex_format = p3d.GeomVertexFormat.get_v3n3t2()
        vertex_format = p3d.GeomVertexFormat.getV3n3c4t2()

        # vertex_format = p3d.GeomVertexFormat.get_v3t2()
        self.vertexData = p3d.GeomVertexData("triangle_data", vertex_format, p3d.Geom.UH_static)

        pos_writer = p3d.GeomVertexWriter(self.vertexData, "vertex")
        normal_writer = p3d.GeomVertexWriter(self.vertexData, "normal")
        colour_writer = p3d.GeomVertexWriter(self.vertexData, 'color')
        tex_writer = p3d.GeomVertexWriter(self.vertexData, 'texcoord')

        for iFace in range(np.size(self.faces, 0)):
            vertices = self.vertices[self.faces[iFace, 1:]]
            pos_writer.add_data3(vertices[0, 0], vertices[0, 1], vertices[0, 2])
            pos_writer.add_data3(vertices[1, 0], vertices[1, 1], vertices[1, 2])
            pos_writer.add_data3(vertices[2, 0], vertices[2, 1], vertices[2, 2])

            colour_writer.add_data4(1, 1, 1, 1)
            colour_writer.add_data4(1, 1, 1, 1)
            colour_writer.add_data4(1, 1, 1, 1)

            #vertices /= np.sqrt(vertices[0]**2 + vertices[1]**2 + vertices[2]**2)
            normal = self.faceNormals[iFace, :]
            normal /= np.sqrt(normal[0]**2 + normal[1]**2 + normal[2]**2)


            vertices = np.sum(vertices, axis=0) / 3
            vertices /= np.sqrt(vertices[0] ** 2 + vertices[1] ** 2 + vertices[2] ** 2)

            textureKey = self.DetermineTextureKey(iFace)

            rIndices = self.mainProgram.closeTexture.textureIndices[textureKey]
            tex_writer.addData2f(rIndices[0], 0)
            tex_writer.addData2f(rIndices[1], 0)
            tex_writer.addData2f((rIndices[0] + rIndices[1])/2, np.sqrt(3)/2)

        tri = p3d.GeomTriangles(p3d.Geom.UH_static)

        # Creates the triangles.
        n = 0
        for iFace in range(np.size(self.faces, 0)):
            tri.add_vertices(n, n+1, n+2)
            n += 3

        # Assigns a normal to each vertex.
        for iFace in range(np.size(self.faces, 0)):

            normal = self.faceNormals[iFace, :]
            normal_writer.add_data3(p3d.Vec3(normal[0], normal[1], normal[2]))
            normal_writer.add_data3(p3d.Vec3(normal[0], normal[1], normal[2]))
            normal_writer.add_data3(p3d.Vec3(normal[0], normal[1], normal[2]))

        geom = p3d.Geom(self.vertexData)
        geom.add_primitive(tri)

        node = p3d.GeomNode("Planet")
        node.add_geom(geom)
        self.node = p3d.NodePath(node)

        self.node.reparentTo(render)
        self.node.setTexture(self.mainProgram.closeTexture.stitchedTexture)
        self.node.setTransparency(p3d.TransparencyAttrib.MAlpha)

    def DetermineTextureKey(self, i):
        if len(self.mainProgram.featureList[i]) > 0:
            textureKey = self.mainProgram.featureList[i][0].template.textureKey
        else:
            textureKey = None

        if textureKey == None:
            if self.mainProgram.worldProperties.slope[i] > 30:
                if self.mainProgram.worldProperties.temperature[i, 0] < 0.1:
                    textureKey = 'snow'
                else:
                    textureKey = 'rock'
            else:
                if self.mainProgram.worldProperties.temperature[i, 0] < 0.3:
                    textureKey = 'snow'
                elif self.mainProgram.worldProperties.temperature[i, 0] < 0.4:
                    textureKey = 'tundra'
                else:
                    textureKey = 'grass'
        return textureKey
