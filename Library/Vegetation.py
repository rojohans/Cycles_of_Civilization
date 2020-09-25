import numpy as np
from scipy import interpolate

class Plant():
    def __init__(self,
                 row,
                 colon,
                 reproductionRate=0.1,
                 lifeLength = 20,
                 height = 1,
                 colour = [0, 1, 0],
                 fitness = None,
                 featureTemplate = None):
        self.row = row
        self.colon = colon
        self.reproductionRate = reproductionRate
        self.lifeLength = lifeLength
        self.age = 0
        self.height = height
        self.colour = colour

        self.featureTemplate = featureTemplate

        if fitness == None:
            self.fitness = self.CalculateFitness(self.row, self.colon)
        else:
            self.fitness = fitness

    def Step(self):
        self.age += 1
        if self.age == self.lifeLength:
            self.Die()
        else:
            r = np.random.rand()
            #if r < self.reproductionRate:
            if r < self.reproductionRate*self.fitness:
                self.Reproduce()

    def Die(self):
        r = np.random.rand()
        if r < self.fitness*self.reproductionRate:
            # A new plant regrows.
            self.plants[self.row][self.colon] = self.__class__(self.row, self.colon, fitness=self.fitness)
        else:
            # The plant dies.
            self.plants[self.row][self.colon] = None

    def Reproduce(self):
        adjacentTiles = np.zeros((8, 2), dtype=int)
        adjacentTiles[:, 0] = int(self.row) + self.mainProgram.settings.ADJACENT_TILES_TEMPLATE[:, 0]
        adjacentTiles[:, 1] = np.mod(int(self.colon) + self.mainProgram.settings.ADJACENT_TILES_TEMPLATE[:, 1],
                                     self.mainProgram.settings.N_COLONS)

        for adjacentTile in adjacentTiles:
            newRow = adjacentTile[0]
            newColon = adjacentTile[1]
            if newRow >=0 and \
                    newRow < self.mainProgram.settings.N_ROWS and \
                    self.mainProgram.world.moisture[newRow, newColon]<2:
                newFitness = self.CalculateFitness(newRow, newColon)
                if newFitness > 0:
                    if self.plants[newRow][newColon]:
                        # If the new tile already contains a plant, that plant will be replaced if the height is lower
                        # than this plant.
                        if self.height > self.plants[newRow][newColon].height:
                            self.plants[newRow][newColon] = self.__class__(newRow, newColon, fitness = newFitness)
                        elif self.height == self.plants[newRow][newColon].height:
                            r = np.random.rand()
                            if r < newFitness/(self.plants[newRow][newColon].fitness+newFitness):
                                self.plants[newRow][newColon] = self.__class__(newRow, newColon, fitness=newFitness)
                    else:
                        # The tile is empty, plants spreads.
                        self.plants[newRow][newColon] = self.__class__(newRow, newColon, fitness = newFitness)

    @classmethod
    def CalculateFitness(cls, row=None, colon=None):

        #elevationFitness = self.elevationFitnessInterpolator(self.mainProgram.world.elevation[row, colon])
        #temperatureFitness = self.temperatureFitnessInterpolator(self.mainProgram.world.temperature[row, colon])
        #moistureFitness = self.moistureFitnessInterpolator(self.mainProgram.world.moisture[row, colon])


        iElevation = np.floor(cls.mainProgram.settings.VEGETATION_INTERPOLATION_RESOLUTION*
                              cls.mainProgram.world.elevation[row, colon]/
                              cls.mainProgram.settings.ELEVATION_LEVELS)
        elevationFitness = cls.elevationFitnessPreComputed[int(iElevation)]

        iTemperature = np.floor(cls.mainProgram.settings.VEGETATION_INTERPOLATION_RESOLUTION*
                                (cls.mainProgram.world.temperature[row, colon]+50)/80)
        temperatureFitness = cls.temperatureFitnessPreComputed[int(iTemperature)]

        iMoisture = np.floor(cls.mainProgram.settings.VEGETATION_INTERPOLATION_RESOLUTION*
                              cls.mainProgram.world.moisture[row, colon])
        moistureFitness = cls.moistureFitnessPreComputed[int(iMoisture)]

        return elevationFitness * temperatureFitness * moistureFitness

    @classmethod
    def Initialize(cls, mainProgram):
        cls.mainProgram = mainProgram
        cls.plants = [[None for colon in range(cls.mainProgram.settings.N_COLONS)]
                      for row in range(cls.mainProgram.settings.N_ROWS)]
        return cls.plants

    @classmethod
    def InitializeFitnessInterpolators(cls):
        cls.CreateFitnessScales()
        cls.CreateFitnessInterpolators()
        cls.CreateFitnessValuesPrecomputed()

    @classmethod
    def CreateFitnessScales(cls):
        cls.elevationFitnessScale  = np.array([[0, 0], [0.2, 0.5], [0.5, 0.5], [1, 1]]),
        cls.temperatureFitnessScale  = np.array([[0, 0], [0.2, 0.5], [0.5, 0.5], [1, 1]]),
        cls.moistureFitnessScale  = np.array([[0, 0], [0.2, 0.5], [0.5, 0.5], [1, 1]])

    @classmethod
    def CreateFitnessInterpolators(cls):
        cls.elevationFitnessInterpolator = interpolate.interp1d(x=cls.elevationFitnessScale[:, 0],
                                                                 y = cls.elevationFitnessScale[:, 1],
                                                                 kind = 'linear')
        cls.temperatureFitnessInterpolator = interpolate.interp1d(x=cls.temperatureFitnessScale[:, 0],
                                                                   y = cls.temperatureFitnessScale[:, 1],
                                                                   kind = 'linear')
        cls.moistureFitnessInterpolator = interpolate.interp1d(x=cls.moistureFitnessScale[:, 0],
                                                                y = cls.moistureFitnessScale[:, 1],
                                                                kind = 'linear')

    @classmethod
    def CreateFitnessValuesPrecomputed(cls):
        x = np.linspace(0, 1, cls.mainProgram.settings.VEGETATION_INTERPOLATION_RESOLUTION)
        maxZ = cls.mainProgram.settings.ELEVATION_LEVELS
        x *= maxZ
        cls.elevationFitnessPreComputed = cls.elevationFitnessInterpolator(x)

        x = np.linspace(0, 1, cls.mainProgram.settings.VEGETATION_INTERPOLATION_RESOLUTION)
        x *= 30 - -50
        x += -50
        cls.temperatureFitnessPreComputed = cls.temperatureFitnessInterpolator(x)

        x = np.linspace(0, 1, cls.mainProgram.settings.VEGETATION_INTERPOLATION_RESOLUTION)
        cls.moistureFitnessPreComputed = cls.moistureFitnessInterpolator(x)

    @classmethod
    def SeedWorld(cls, seedAmount, plant, minFitness = 0):
        for iSeed in range(seedAmount):
            seedPlaced = False
            while seedPlaced == False:
                row = np.random.randint(0, cls.mainProgram.settings.N_ROWS)
                colon = np.random.randint(0, cls.mainProgram.settings.N_COLONS)

                if cls.mainProgram.world.moisture[row, colon] < 2 and cls.plants[row][colon] == None:
                    # The tile needs to be empty and not ocean.
                    if plant.CalculateFitness(row, colon) > minFitness:
                        # The tile needs to be sufficiently suitable for the plant.
                        cls.plants[row][colon]=plant(row, colon)
                        seedPlaced = True

    @classmethod
    def GetImage(cls):
        colourArray = np.zeros((cls.mainProgram.settings.N_ROWS, cls.mainProgram.settings.N_COLONS, 3))

        for row in range(cls.mainProgram.settings.N_ROWS):
            for colon in range(cls.mainProgram.settings.N_COLONS):
                if cls.mainProgram.world.moisture[row, colon] == 2:
                    colourArray[row, colon, :] = [0, 0, 0]
                elif cls.plants[row][colon]:
                    colourArray[row, colon, :] = cls.plants[row][colon].colour
                else:
                    colourArray[row, colon, :] = [1, 1, 1]
        return colourArray

class Grass(Plant):
    def __init__(self,
                 row,
                 colon,
                 reproductionRate = 0.5,
                 lifeLength = 10,
                 height = 1,
                 colour = [0.7, 0.9, 0.2],
                 fitness = None,
                 featureTemplate = None):
        super().__init__(row,
                         colon,
                         reproductionRate,
                         lifeLength,
                         height = height,
                         colour=colour,
                         fitness=fitness,
                         featureTemplate=featureTemplate)

class Tree(Plant):
    def __init__(self,
                 row,
                 colon,
                 reproductionRate = 0.1,
                 lifeLength = 50,
                 height = 2,
                 colour = [0.2, 0.5, 0.3],
                 fitness = None,
                 featureTemplate = None):
        super().__init__(row,
                         colon,
                         reproductionRate,
                         lifeLength,
                         height = height,
                         colour=colour,
                         fitness=fitness,
                         featureTemplate=featureTemplate)





