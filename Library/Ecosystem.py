import numpy as np
from scipy import interpolate

class Organism():
    def __init__(self,
                 row,
                 colon,
                 reproductionRate=0.1,
                 growthRate = 0.1,
                 lifeLength = 20,
                 height = 1,
                 colour = [0, 1, 0],
                 density = 0,
                 fitness = None,
                 featureTemplate = None,
                 outcompeteParameter = 0):
        self.row = row
        self.colon = colon
        self.reproductionRate = reproductionRate
        self.growthRate = growthRate
        self.lifeLength = lifeLength
        self.age = 0
        self.height = height # Determines which plants can overtake others. Larger overtakes lower.
        self.colour = colour

        self.outcompeteParameter = outcompeteParameter

        self.featureTemplate = featureTemplate

        # When density = fitness, the forest is fully grown.
        self.density = density

        if fitness == None:
            self.fitness = self.CalculateFitness(self.row, self.colon)
        else:
            self.fitness = fitness

    def Step(self):
        self.age += 1
        '''
        if self.age == self.lifeLength:
            self.Die()
        else:
        '''

        self.Grow()

        self.Reproduce()

    def Die(self):
        # The plant dies.
        self.organisms[self.row][self.colon] = None

    def Grow(self):
        if self.density < self.fitness:
            densityIncrease = self.growthRate*self.fitness
            self.density = np.min((self.density+densityIncrease, self.fitness))

    def Reproduce(self):
        r = np.random.rand()
        if r < self.reproductionRate*self.fitness:
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
                        if self.organisms[newRow][newColon]:
                            # If the new tile already contains a plant, that plant will be replaced if the height is lower
                            # than this plant.
                            if self.height > self.organisms[newRow][newColon].height:
                                # Forest spreads over grass.
                                self.organisms[newRow][newColon] = self.__class__(newRow, newColon, fitness = newFitness)
                            elif self.height == self.organisms[newRow][newColon].height:
                                if self.__class__ != self.organisms[newRow][newColon].__class__:
                                    r = np.random.rand()
                                    if r < newFitness/(self.organisms[newRow][newColon].fitness + newFitness + self.outcompeteParameter):
                                        # The new plant out competes the old plant.
                                        self.organisms[newRow][newColon] = self.__class__(newRow, newColon, fitness=newFitness)
                        else:
                            # The tile is empty, plants spreads.
                            self.organisms[newRow][newColon] = self.__class__(newRow, newColon, fitness = newFitness)

    @classmethod
    def CalculateFitness(cls, row=None, colon=None):
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
        cls.organisms = [[None for colon in range(cls.mainProgram.settings.N_COLONS)]
                      for row in range(cls.mainProgram.settings.N_ROWS)]
        return cls.organisms
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
    def SeedWorld(cls, seedAmount, organism, minFitness = 0):
        for iSeed in range(seedAmount):
            seedPlaced = False
            while seedPlaced == False:
                row = np.random.randint(0, cls.mainProgram.settings.N_ROWS)
                colon = np.random.randint(0, cls.mainProgram.settings.N_COLONS)

                if cls.mainProgram.world.moisture[row, colon] < 2 and cls.organisms[row][colon] == None:
                    # The tile needs to be empty and not ocean.
                    if organism.CalculateFitness(row, colon) > minFitness:
                        # The tile needs to be sufficiently suitable for the plant.
                        cls.organisms[row][colon]=organism(row, colon)
                        seedPlaced = True

    @classmethod
    def GetImage(cls):
        colourArray = np.zeros((cls.mainProgram.settings.N_ROWS, cls.mainProgram.settings.N_COLONS, 3))

        for row in range(cls.mainProgram.settings.N_ROWS):
            for colon in range(cls.mainProgram.settings.N_COLONS):
                if cls.mainProgram.world.moisture[row, colon] == 2:
                    colourArray[row, colon, :] = [0, 0, 0]
                elif cls.organisms[row][colon]:
                    colourArray[row, colon, :] = cls.organisms[row][colon].colour
                else:
                    colourArray[row, colon, :] = [1, 1, 1]
        return colourArray

class Vegetation(Organism):
    def __init__(self,
                 row,
                 colon,
                 reproductionRate=0.5,
                 growthRate=0.2,
                 lifeLength=10,
                 height=1,
                 colour=[0, 1, 0],
                 density = 0,
                 fitness=None,
                 featureTemplate=None,
                 grazingBiomass = 0.5,
                 browsingBiomass = 0.5):
        super().__init__(row,
                         colon,
                         reproductionRate,
                         growthRate=growthRate,
                         lifeLength=lifeLength,
                         height=height,
                         colour=colour,
                         density=density,
                         fitness=fitness,
                         featureTemplate=featureTemplate,
                         outcompeteParameter=self.mainProgram.settings.VEGETATION_OUTCOMPETE_PARAMETER)

        # Determines the amount of available food for grazers and browsers
        self.grazingBiomass = grazingBiomass
        self.browsingBiomass = browsingBiomass

class Grass(Vegetation):
    def __init__(self,
                 row,
                 colon,
                 reproductionRate = 0.5,
                 growthRate = 0.4,
                 lifeLength = 10,
                 height = 1,
                 colour = [0.8, 1, 0.5],
                 fitness = None,
                 density = 0,
                 featureTemplate = None,
                 grazingBiomass = 1,
                 browsingBiomass = 0.2):
        super().__init__(row,
                         colon,
                         reproductionRate,
                         growthRate=growthRate,
                         lifeLength=lifeLength,
                         height = height,
                         colour=colour,
                         density=density,
                         fitness=fitness,
                         featureTemplate=featureTemplate,
                         grazingBiomass=grazingBiomass,
                         browsingBiomass=browsingBiomass)
    def Die(self):
        # A little known fact is that grass is immortal, and thus can never truly die.
        self.density = 0
        pass

class Forest(Vegetation):
    def __init__(self,
                 row,
                 colon,
                 reproductionRate = 0.1,
                 growthRate = 0.1,
                 lifeLength = 50,
                 height = 2,
                 colour = [0.2, 0.5, 0.3],
                 density = 0,
                 fitness = None,
                 featureTemplate = None,
                 grazingBiomass = 0.2,
                 browsingBiomass = 1):

        super().__init__(row,
                         colon,
                         reproductionRate,
                         growthRate=growthRate,
                         lifeLength=lifeLength,
                         height = height,
                         colour=colour,
                         density=density,
                         fitness=fitness,
                         featureTemplate=featureTemplate,
                         grazingBiomass=grazingBiomass,
                         browsingBiomass=browsingBiomass)



class Animal(Organism):
    def __init__(self,
                 row,
                 colon,
                 reproductionRate = 0.1,
                 growthRate = 0.1,
                 lifeLength = 50,
                 colour = [1, 0, 0],
                 density = 0,
                 fitness = None,
                 featureTemplate = None,
                 vegetationDestruction = 0.5):
        super().__init__(row,
                         colon,
                         reproductionRate,
                         growthRate=growthRate,
                         lifeLength=lifeLength,
                         colour=colour,
                         density=density,
                         fitness=fitness,
                         featureTemplate=featureTemplate,
                         outcompeteParameter=self.mainProgram.settings.ANIMAL_OUTCOMPETE_PARAMETER)
        self.vegetationDestruction = vegetationDestruction
    def Step(self):
        #self.age += 1

        self.Eat()

        self.Grow()

        self.Reproduce()

    def Eat(self):
        biomassEaten = self.vegetationDestruction*self.density
        self.mainProgram.plants[self.row][self.colon].density -= biomassEaten
        if self.mainProgram.plants[self.row][self.colon].density < 0:
            # The food has run out.
            self.mainProgram.plants[self.row][self.colon].Die()

            self.Migrate()
            self.Die()

    def Migrate(self):
        adjacentTiles = np.zeros((8, 2), dtype=int)
        adjacentTiles[:, 0] = int(self.row) + self.mainProgram.settings.ADJACENT_TILES_TEMPLATE[:, 0]
        adjacentTiles[:, 1] = np.mod(int(self.colon) + self.mainProgram.settings.ADJACENT_TILES_TEMPLATE[:, 1],
                                     self.mainProgram.settings.N_COLONS)

        remainingDensity = self.density
        while remainingDensity > 0:
            for adjacentTile in adjacentTiles:
                newRow = adjacentTile[0]
                newColon = adjacentTile[1]
                if newRow >=0 and \
                        newRow < self.mainProgram.settings.N_ROWS and \
                        self.mainProgram.world.moisture[newRow, newColon]<2:

                    adjacentAnimal = self.organisms[newRow][newColon]
                    if adjacentAnimal:
                        # Tile is already occupied
                        if self.__class__ == adjacentAnimal.__class__:
                            # Same species
                            if adjacentAnimal.density < adjacentAnimal.fitness:
                                newDensity = np.min((remainingDensity + adjacentAnimal.density, adjacentAnimal.fitness))
                                addedDensity = newDensity-adjacentAnimal.density
                                adjacentAnimal.density = newDensity
                                remainingDensity -= addedDensity
                        else:
                            # Different species
                            newFitness = self.CalculateFitness(newRow, newColon)
                            r = np.random.rand()
                            if r < newFitness / (self.organisms[newRow][newColon].fitness + newFitness + self.outcompeteParameter):
                                # New species outompetes the old.
                                newDensity = np.min((remainingDensity, newFitness))
                                remainingDensity -= newDensity
                                self.organisms[newRow][newColon] = self.__class__(newRow, newColon, density=newDensity,
                                                                                  fitness=newFitness)
                    else:
                        # Tile is empty
                        newFitness = self.CalculateFitness(newRow, newColon)
                        if newFitness>0:
                            newDensity = np.min((remainingDensity, newFitness))
                            remainingDensity -= newDensity
                            self.organisms[newRow][newColon] = self.__class__(newRow, newColon, density=newDensity, fitness=newFitness)
            remainingDensity = 0


    @classmethod
    def CreateFitnessScales(cls):
        cls.elevationFitnessScale  = np.array([[0, 0], [0.2, 0.5], [0.5, 0.5], [1, 1]]),
        cls.temperatureFitnessScale  = np.array([[0, 0], [0.2, 0.5], [0.5, 0.5], [1, 1]]),
        cls.moistureFitnessScale  = np.array([[0, 0], [0.2, 0.5], [0.5, 0.5], [1, 1]])
        cls.biomassFitnessScale = np.array([[0, 0], [1, 1]])

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
        cls.biomassFitnessInterpolator = interpolate.interp1d(x=cls.biomassFitnessScale[:, 0],
                                                                y = cls.biomassFitnessScale[:, 1],
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

        x = np.linspace(0, 1, cls.mainProgram.settings.VEGETATION_INTERPOLATION_RESOLUTION)
        cls.biomassFitnessPreComputed = cls.biomassFitnessInterpolator(x)

class Grazer(Animal):
    def __init__(self,
                 row,
                 colon,
                 reproductionRate = 0.1,
                 growthRate = 0.1,
                 lifeLength = 50,
                 colour = [1, 0, 0],
                 density = 0,
                 fitness = None,
                 featureTemplate=None,
                 vegetationDestruction = 0.9):
        super().__init__(row,
                         colon,
                         reproductionRate,
                         growthRate=growthRate,
                         lifeLength=lifeLength,
                         colour=colour,
                         density=density,
                         fitness=fitness,
                         featureTemplate=featureTemplate,
                         vegetationDestruction=vegetationDestruction)
    @classmethod
    def CalculateFitness(cls, row, colon):
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


        plant = cls.mainProgram.plants[row][colon]
        if plant == None:
            biomassFitness = 0
        else:
            iBiomass = np.floor((cls.mainProgram.settings.VEGETATION_INTERPOLATION_RESOLUTION-1)*
                                  plant.fitness*plant.grazingBiomass)
            biomassFitness = cls.biomassFitnessPreComputed[int(iBiomass)]

        return elevationFitness * temperatureFitness * moistureFitness * biomassFitness

class Browser(Animal):
    def __init__(self,
                 row,
                 colon,
                 reproductionRate = 0.1,
                 growthRate = 0.1,
                 lifeLength = 50,
                 colour = [0, 0, 1],
                 density = 0,
                 fitness = None,
                 featureTemplate=None,
                 vegetationDestruction = 0):
        super().__init__(row,
                         colon,
                         reproductionRate,
                         growthRate=growthRate,
                         lifeLength=lifeLength,
                         colour=colour,
                         density=density,
                         fitness=fitness,
                         featureTemplate=featureTemplate,
                         vegetationDestruction=vegetationDestruction)
    @classmethod
    def CalculateFitness(cls, row, colon):
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


        plant = cls.mainProgram.plants[row][colon]
        if plant == None:
            biomassFitness = 0
        else:
            iBiomass = np.floor((cls.mainProgram.settings.VEGETATION_INTERPOLATION_RESOLUTION-1)*
                                  plant.fitness*plant.browsingBiomass)
            biomassFitness = cls.biomassFitnessPreComputed[int(iBiomass)]

        return elevationFitness * temperatureFitness * moistureFitness * biomassFitness

