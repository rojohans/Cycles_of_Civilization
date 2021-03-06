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
                 density = 0.1,
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

        self.canPerformStep = False

        self.outcompeteParameter = outcompeteParameter

        self.featureTemplate = featureTemplate

        # When density = fitness, the forest is fully grown.
        self.density = density

        if fitness == None:
            self.fitness = self.CalculateFitness(self.row, self.colon)
        else:
            self.fitness = fitness

    def Step(self):
        if self.canPerformStep:
                self.age += 1

                self.Grow()

                self.Reproduce()

                #if np.mod(self.age, 10) == 1:
                #    self.fitness = self.CalculateFitness(self.row, self.colon)
        self.canPerformStep = True

    def Die(self):
        # The plant dies.
        self.organisms[self.row][self.colon] = None

    def Grow(self):
        if self.density < self.fitness:
            # Logistic growth up to the fitness value.
            densityIncrease = self.density*self.growthRate*(1-self.density/self.fitness)

            # Linear growth up to the fitness value
            #densityIncrease = self.growthRate * self.fitness
            self.density = np.min((self.density+densityIncrease, self.fitness))

    def Reproduce(self):
        r = np.random.rand(9)
        if r[0] < self.reproductionRate*self.fitness*8:
            adjacentTiles = np.zeros((8, 2), dtype=int)
            adjacentTiles[:, 0] = self.row + self.mainProgram.settings.ADJACENT_TILES_TEMPLATE[:, 0]
            adjacentTiles[:, 1] = np.mod(self.colon + self.mainProgram.settings.ADJACENT_TILES_TEMPLATE[:, 1],
                                         self.mainProgram.settings.N_COLONS)

            for iTile, adjacentTile in enumerate(adjacentTiles):
                #r = np.random.rand()
                newRow = adjacentTile[0]
                newColon = adjacentTile[1]
                if r[iTile+1] < self.reproductionRate * self.fitness and \
                        newRow >=0 and \
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
                                    rOutCompete = np.random.rand()
                                    if rOutCompete < newFitness/(self.organisms[newRow][newColon].fitness + newFitness + self.outcompeteParameter):
                                        # The new plant out competes the old plant.
                                        self.organisms[newRow][newColon] = self.__class__(newRow, newColon, fitness=newFitness)
                        else:
                            # The tile is empty, plants spreads.
                            self.organisms[newRow][newColon] = self.__class__(newRow, newColon, fitness = newFitness)

    @classmethod
    def CalculateFitness(cls, row=None, colon=None):
        if cls.cachedFitnessMap[row][colon]:
            return cls.cachedFitnessMap[row][colon]
        else:
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

            fitness = elevationFitness * temperatureFitness * moistureFitness
            cls.cachedFitnessMap[row][colon] = fitness
            return fitness

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

        cls.cachedFitnessMap = [[None for colon in range(cls.mainProgram.settings.N_COLONS)]
                          for row in range(cls.mainProgram.settings.N_ROWS)]

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
    def GetImage(cls, densityScaling = False):
        colourArray = np.zeros((cls.mainProgram.settings.N_ROWS, cls.mainProgram.settings.N_COLONS, 3))

        for row in range(cls.mainProgram.settings.N_ROWS):
            for colon in range(cls.mainProgram.settings.N_COLONS):
                if cls.mainProgram.world.moisture[row, colon] == 2:
                    colourArray[row, colon, :] = [0.1, 0.1, 0.1]
                elif cls.organisms[row][colon]:
                    colour = cls.organisms[row][colon].colour
                    if densityScaling:
                        scale = 0.1+0.9*cls.organisms[row][colon].density
                        colour = [scale * colour[0],
                                  scale * colour[1],
                                  scale * colour[2]]
                    colourArray[row, colon, :] = colour
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
                 density = 0.0,
                 fitness=None,
                 featureTemplate=None,
                 grazingBiomass = 0.5,
                 browsingBiomass = 0.5,
                 eatenMultiplier = 1):
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

        self.eatenMultiplier = eatenMultiplier

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
                 density = 0.0,
                 featureTemplate = None,
                 grazingBiomass = 1,
                 browsingBiomass = 0.2,
                 eatenMultiplier = 1):
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
                         browsingBiomass=browsingBiomass,
                         eatenMultiplier=eatenMultiplier)
    #def Die(self):
        # A little known fact is that grass is immortal, and thus can never truly die.
        #self.density = 0.1
        #self.suspendedGrowthTurns = 10

class Forest(Vegetation):
    def __init__(self,
                 row,
                 colon,
                 reproductionRate = 0.1,
                 growthRate = 0.1,
                 lifeLength = 50,
                 height = 2,
                 colour = [0.2, 0.5, 0.3],
                 density = 0.0,
                 fitness = None,
                 featureTemplate = None,
                 grazingBiomass = 0.2,
                 browsingBiomass = 1,
                 eatenMultiplier = 100):

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
                         browsingBiomass=browsingBiomass,
                         eatenMultiplier=eatenMultiplier)

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
        if self.canPerformStep:
            self.age += 1

            if np.mod(self.age, 10) == 1:
                self.fitness = self.CalculateFitness(self.row, self.colon)

            '''
            foodShortage = self.Eat()
            if foodShortage:
                self.Starve(foodShortage)
            else:
                self.Grow()
                self.Reproduce()
            if self.density <= 0:
                self.Die()
                return
            '''

            #self.Reproduce()
            #self.Reproduce()
            #self.Reproduce()

            foodShortage = self.Eat()
            if foodShortage:
                #print('No Food')
                self.Starve(foodShortage)
                #self.Migrate(self.density*0.5, priority='best')
                #self.density *= 0.5
                #self.Die()
            else:
                #rint('Food')
                self.Grow()
                self.Reproduce()

            #if foodShortage:
            #    print('Animal should starve')


            #if self.mainProgram.plants[self.row][self.colon] == None:
            #    #print('no food')
            #    self.Migrate(self.density, priority='random')
            #    self.Die()

            '''
            # This migratio should be different for the browsers. They browsers hsould migrate randomly??
            if self.density/self.fitness > 0.5:
                self.Migrate(self.density * 0.1, priority='random')
                self.density *= 0.9
            else:
                self.Migrate(self.density * 0.1, priority='best')
                self.density *= 0.9
            '''

            #self.Reproduce()
        self.canPerformStep = True

    def Eat(self):
        #foodEaten = np.max([self.density * 81*self.vegetationDestruction * 0.2, self.vegetationDestruction])
        foodEaten = self.density * self.vegetationDestruction
        if self.mainProgram.plants[self.row][self.colon]:

            foodEaten *= (1 + self.mainProgram.plants[self.row][self.colon].density) / 2

            foodEaten *= self.mainProgram.plants[self.row][self.colon].eatenMultiplier
            self.mainProgram.plants[self.row][self.colon].density -= foodEaten

            if self.mainProgram.plants[self.row][self.colon].density <= 0:
                # Not enough food

                foodShortage = self.mainProgram.plants[self.row][self.colon].density

                #print('not enough food')
                self.mainProgram.plants[self.row][self.colon].Die()
                return foodShortage
            return None
        else:
            foodShortage = foodEaten
            return foodShortage

    def Grow(self):
        if self.density < self.fitness:

            #logistic growth
            carryCapacity = self.fitness
            #densityIncrease = self.density * self.growthRate * (1 - self.density / carryCapacity)
            densityIncrease = 2*self.mainProgram.plants[self.row][self.colon].density * self.density * self.growthRate * (1 - self.density / carryCapacity)

            #Exponential growth
            #densityIncrease = self.growthRate * self.density * self.mainProgram.plants[self.row][self.colon].density

            self.density = np.min((self.density + densityIncrease, self.fitness))

    def Starve(self, foodShortage):

        decayRate = 0.2
        densityDecay = -decayRate * self.density
        self.density = np.max((self.density + densityDecay, 0))
        if self.density <= 0.01:
            self.Die()

        #print('The animal should starve')

    def Migrate(self, migrationAmount, priority = 'best'):
        adjacentTiles = np.zeros((8, 2), dtype=int)
        adjacentTiles[:, 0] = int(self.row) + self.mainProgram.settings.ADJACENT_TILES_TEMPLATE[:, 0]
        adjacentTiles[:, 1] = np.mod(int(self.colon) + self.mainProgram.settings.ADJACENT_TILES_TEMPLATE[:, 1],
                                     self.mainProgram.settings.N_COLONS)

        if priority == 'best':
            tilesToMigrateTo = []
            for adjacentTile in adjacentTiles:
                newRow = adjacentTile[0]
                newColon = adjacentTile[1]
                if newRow >= 0 and \
                        newRow < self.mainProgram.settings.N_ROWS and \
                        self.mainProgram.world.moisture[newRow, newColon] < 2:
                    if self.mainProgram.plants[newRow][newColon]:
                        availableFood = self.mainProgram.plants[newRow][newColon].density
                    else:
                        availableFood = 0

                    tilesToMigrateTo.append((newRow, newColon, availableFood))
            dtype = [('row', int), ('colon', int), ('food', float)]
            tilesToMigrateTo = np.array(tilesToMigrateTo, dtype=dtype)  # create a structured array

            tilesToMigrateTo = np.sort(tilesToMigrateTo, order='food')
            tilesToMigrateTo = np.flip(tilesToMigrateTo, axis=0)
        elif priority == 'random':
            randomIndices = np.random.permutation(8)
            tilesToMigrateTo = np.zeros((8, 2), dtype=int)
            for i, index in enumerate(randomIndices):
                tilesToMigrateTo[i, :] = adjacentTiles[index, :]

        remainingDensity = migrationAmount
        for tile in tilesToMigrateTo:

            newRow = tile[0]
            newColon = tile[1]
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
            if remainingDensity <= 0:
                break
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
                 density = 0.0,
                 fitness = None,
                 featureTemplate=None,
                 vegetationDestruction = 0.25):
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
                 density = 0.0,
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

class Predator(Animal):
    def __init__(self,
                 row,
                 colon,
                 reproductionRate=0.1,
                 growthRate=0.1,
                 lifeLength=50,
                 colour=[1, 0, 0],
                 density=0.0,
                 fitness=None,
                 featureTemplate=None,
                 vegetationDestruction=0.2):
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
    def Eat(self):
        if self.mainProgram.animals[self.row][self.colon]:
            biomassEaten = self.vegetationDestruction*self.density
            self.mainProgram.animals[self.row][self.colon].density -= biomassEaten
            if self.mainProgram.animals[self.row][self.colon].density < 0.5:
                # The food has run out.
                self.mainProgram.animals[self.row][self.colon].Die()

                self.Migrate()
                self.Die()
        else:
            self.Migrate()
            self.Die()

    def Migrate(self):
        adjacentTiles = np.zeros((8, 2), dtype=int)
        adjacentTiles[:, 0] = int(self.row) + self.mainProgram.settings.ADJACENT_TILES_TEMPLATE[:, 0]
        adjacentTiles[:, 1] = np.mod(int(self.colon) + self.mainProgram.settings.ADJACENT_TILES_TEMPLATE[:, 1],
                                     self.mainProgram.settings.N_COLONS)

        remainingDensity = self.density
        while remainingDensity > 0:



            tilesToMigrateTo = []
            for adjacentTile in adjacentTiles:
                newRow = adjacentTile[0]
                newColon = adjacentTile[1]
                if newRow >=0 and \
                        newRow < self.mainProgram.settings.N_ROWS and \
                        self.mainProgram.world.moisture[newRow, newColon]<2:
                    if self.mainProgram.animals[newRow][newColon]:
                        availableFood = self.mainProgram.animals[newRow][newColon].density
                        tilesToMigrateTo.append((newRow, newColon, availableFood))

            dtype = [('row', int), ('colon', int), ('food', float)]
            tilesToMigrateTo = np.array(tilesToMigrateTo, dtype=dtype)  # create a structured array

            tilesToMigrateTo = np.sort(tilesToMigrateTo, order='food')
            tilesToMigrateTo = np.flip(tilesToMigrateTo, axis=0)



            #for adjacentTile in adjacentTiles:
            for tile in tilesToMigrateTo:
                newRow = tile[0]
                newColon = tile[1]
                #newRow = adjacentTile[0]
                #newColon = adjacentTile[1]

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
                return
            remainingDensity = 0

    def Grow(self):
        if self.density < self.fitness:
            densityIncrease = self.growthRate*self.fitness
            self.density = np.min((self.density+densityIncrease, self.fitness))
            if self.mainProgram.animals[self.row][self.colon]:
                if self.mainProgram.animals[self.row][self.colon].density < 0.5:
                    pass
                    self.Die()
            else:
                pass
                self.Die()
        else:
            self.Reproduce()

    @classmethod
    def CreateFitnessScales(cls):
        cls.elevationFitnessScale  = np.array([[0, 0], [0.2, 0.5], [0.5, 0.5], [1, 1]]),
        cls.temperatureFitnessScale  = np.array([[0, 0], [0.2, 0.5], [0.5, 0.5], [1, 1]]),
        cls.moistureFitnessScale  = np.array([[0, 0], [0.2, 0.5], [0.5, 0.5], [1, 1]])
        cls.foodFitnessScale = np.array([[0, 0], [1, 1]])

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
        cls.foodFitnessInterpolator = interpolate.interp1d(x=cls.foodFitnessScale[:, 0],
                                                            y = cls.foodFitnessScale[:, 1],
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
        cls.foodFitnessPreComputed = cls.foodFitnessInterpolator(x)

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


        prey = cls.mainProgram.animals[row][colon]
        if prey == None:
            foodFitness = 0
        else:
            ifood = np.floor((cls.mainProgram.settings.VEGETATION_INTERPOLATION_RESOLUTION-1)*
                                  prey.fitness)
            foodFitness = cls.foodFitnessPreComputed[int(ifood)]

        return elevationFitness * temperatureFitness * moistureFitness * foodFitness
