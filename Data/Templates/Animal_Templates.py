import numpy as np

import Library.Ecosystem as Ecosystem




class NormalBrowser(Ecosystem.Browser):
    def __init__(self, row, colon, density = 0.1,fitness = None):
        super().__init__(row,
                         colon,
                         reproductionRate=0.2,
                         lifeLength=10,
                         density= density,
                         fitness=fitness,
                         colour = [0, 0, 1])

    @classmethod
    def CreateFitnessScales(cls):
        maxZ = cls.mainProgram.settings.ELEVATION_LEVELS
        cls.elevationFitnessScale = np.array([[0, 1], [0.4*maxZ, 1], [0.6*maxZ, 0.8], [0.85*maxZ, 0], [maxZ, 0]])
        cls.temperatureFitnessScale = np.array([[-50, 0], [5, 0.0], [10, 0.6], [20, 1], [30, 1]])
        cls.moistureFitnessScale = np.array([[0, 0], [0.1, 0], [0.2, 0.5], [0.5, 0.8], [1, 1]])
        cls.biomassFitnessScale = np.array([[0, 0], [0.4, 1], [1, 1]])


class NormalGrazer(Ecosystem.Grazer):
    def __init__(self, row, colon, density = 0.1, fitness = None):
        super().__init__(row,
                         colon,
                         reproductionRate=0.2,
                         lifeLength=10,
                         density=density,
                         fitness=fitness,
                         colour = [1, 0, 0])

    @classmethod
    def CreateFitnessScales(cls):
        maxZ = cls.mainProgram.settings.ELEVATION_LEVELS
        cls.elevationFitnessScale = np.array([[0, 1], [0.4*maxZ, 1], [0.6*maxZ, 0.8], [0.85*maxZ, 0], [maxZ, 0]])
        cls.temperatureFitnessScale = np.array([[-50, 0], [5, 0.0], [10, 0.6], [20, 1], [30, 1]])
        cls.moistureFitnessScale = np.array([[0, 0], [0.1, 0], [0.2, 0.5], [0.5, 0.8], [1, 1]])
        cls.biomassFitnessScale = np.array([[0, 0], [0.4, 1], [1, 1]])


class Boar(Ecosystem.Browser):
    def __init__(self, row, colon, density = 0.1,fitness = None):
        super().__init__(row,
                         colon,
                         reproductionRate=0.5,
                         growthRate=0.2,
                         lifeLength=10,
                         density= density,
                         fitness=fitness,
                         colour = [0, 0, 1],
                         featureTemplate='boar_herd')

    @classmethod
    def CreateFitnessScales(cls):
        maxZ = cls.mainProgram.settings.ELEVATION_LEVELS
        cls.elevationFitnessScale = np.array([[0, 1], [0.4*maxZ, 1], [0.7*maxZ, 0], [maxZ, 0]])
        cls.temperatureFitnessScale = np.array([[-50, 0], [0, 0], [10, 0.6], [27, 1], [30, 1]])
        cls.moistureFitnessScale = np.array([[0, 0], [0.3, 0], [0.7, 1], [1, 1]])
        cls.biomassFitnessScale = np.array([[0, 0], [0.4, 1], [1, 1]])

class Turkey(Ecosystem.Browser):
    def __init__(self, row, colon, density = 0.1,fitness = None):
        super().__init__(row,
                         colon,
                         reproductionRate=0.5,
                         growthRate=0.2,
                         lifeLength=10,
                         density= density,
                         fitness=fitness,
                         colour = [0.5, 0, 1])

    @classmethod
    def CreateFitnessScales(cls):
        maxZ = cls.mainProgram.settings.ELEVATION_LEVELS
        cls.elevationFitnessScale = np.array([[0, 1], [0.4*maxZ, 1], [0.6*maxZ, 0], [maxZ, 0]])
        cls.temperatureFitnessScale = np.array([[-50, 0], [0, 0], [10, 0.6], [20, 1], [22, 1], [30, 0.8]])
        cls.moistureFitnessScale = np.array([[0, 0], [0.3, 0], [0.6, 1], [1, 0.7]])
        cls.biomassFitnessScale = np.array([[0, 0], [0.4, 1], [1, 1]])

class Deer(Ecosystem.Browser):
    def __init__(self, row, colon, density = 0.1,fitness = None):
        super().__init__(row,
                         colon,
                         reproductionRate=0.5,
                         growthRate=0.2,
                         lifeLength=10,
                         density= density,
                         fitness=fitness,
                         colour = [0, 1, 1])

    @classmethod
    def CreateFitnessScales(cls):
        maxZ = cls.mainProgram.settings.ELEVATION_LEVELS
        cls.elevationFitnessScale = np.array([[0, 1], [0.4*maxZ, 1], [0.6*maxZ, 0.8], [0.85*maxZ, 0], [maxZ, 0]])
        cls.temperatureFitnessScale = np.array([[-50, 0], [-10, 0], [0, 0.7], [10, 1], [20, 0.6], [30, 0.5]])
        cls.moistureFitnessScale = np.array([[0, 0], [0.1, 0], [0.2, 0.4], [0.7, 1], [1, 0.7]])
        cls.biomassFitnessScale = np.array([[0, 0], [0.4, 1], [1, 1]])

#-------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------

class Caribou(Ecosystem.Grazer):
    def __init__(self, row, colon, density = 0.1, fitness = None):
        super().__init__(row,
                         colon,
                         reproductionRate=0.2,
                         lifeLength=10,
                         density=density,
                         fitness=fitness,
                         colour = [1, 1, 0])

    @classmethod
    def CreateFitnessScales(cls):
        maxZ = cls.mainProgram.settings.ELEVATION_LEVELS
        cls.elevationFitnessScale = np.array([[0, 1], [0.4*maxZ, 1], [0.6*maxZ, 0.8], [0.85*maxZ, 0], [maxZ, 0]])
        cls.temperatureFitnessScale = np.array([[-50, 0], [-15, 0.0], [-5, 0.7], [0, 1], [20, 0], [30, 0]])
        cls.moistureFitnessScale = np.array([[0, 0], [0.1, 0], [0.2, 0.5], [0.5, 0.8], [1, 1]])
        cls.biomassFitnessScale = np.array([[0, 0], [0.4, 1], [1, 1]])

class Bison(Ecosystem.Grazer):
    def __init__(self, row, colon, density = 0.1, fitness = None):
        super().__init__(row,
                         colon,
                         reproductionRate=0.2,
                         lifeLength=10,
                         density=density,
                         fitness=fitness,
                         colour = [0.9, 0.5, 0])

    @classmethod
    def CreateFitnessScales(cls):
        maxZ = cls.mainProgram.settings.ELEVATION_LEVELS
        cls.elevationFitnessScale = np.array([[0, 1], [0.4*maxZ, 1], [0.6*maxZ, 0.8], [0.85*maxZ, 0], [maxZ, 0]])
        cls.temperatureFitnessScale = np.array([[-50, 0], [-5, 0.0], [5, 1], [10, 1], [20, 0.6], [30, 0.2]])
        cls.moistureFitnessScale = np.array([[0, 0], [0.1, 0], [0.2, 0.5], [0.5, 0.8], [1, 1]])
        cls.biomassFitnessScale = np.array([[0, 0], [0.4, 1], [1, 1]])

class Horse(Ecosystem.Grazer):
    def __init__(self, row, colon, density = 0.1, fitness = None):
        super().__init__(row,
                         colon,
                         reproductionRate=0.2,
                         lifeLength=10,
                         density=density,
                         fitness=fitness,
                         colour = [1, 0, 0])

    @classmethod
    def CreateFitnessScales(cls):
        maxZ = cls.mainProgram.settings.ELEVATION_LEVELS
        cls.elevationFitnessScale = np.array([[0, 1], [0.4*maxZ, 1], [0.6*maxZ, 0.8], [0.85*maxZ, 0], [maxZ, 0]])
        cls.temperatureFitnessScale = np.array([[-50, 0], [5, 0.0], [10, 0.6], [20, 1], [30, 0.8]])
        cls.moistureFitnessScale = np.array([[0, 0], [0.1, 0], [0.2, 0.5], [0.5, 0.8], [1, 1]])
        cls.biomassFitnessScale = np.array([[0, 0], [0.4, 1], [1, 1]])

#-------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------
class Wolf(Ecosystem.Predator):
    def __init__(self, row, colon, density = 0.1, fitness = None):
        super().__init__(row,
                         colon,
                         reproductionRate=0.3,
                         growthRate=0.1,
                         vegetationDestruction=0.1,
                         lifeLength=10,
                         density=density,
                         fitness=fitness,
                         colour = [1, 0, 0])

    @classmethod
    def CreateFitnessScales(cls):
        maxZ = cls.mainProgram.settings.ELEVATION_LEVELS
        cls.elevationFitnessScale = np.array([[0, 1], [0.4*maxZ, 1], [0.6*maxZ, 0.8], [0.85*maxZ, 0], [maxZ, 0]])
        cls.temperatureFitnessScale = np.array([[-50, 0], [5, 0.0], [10, 0.6], [20, 1], [30, 0.8]])
        cls.moistureFitnessScale = np.array([[0, 0], [0.1, 0], [0.2, 0.5], [0.5, 0.8], [1, 1]])
        cls.foodFitnessScale = np.array([[0, 0], [0.2, 0], [0.6, 1], [1, 1]])

# --Grazers--
# Bison
# Sheep
# Horse
# Rabbit

# --Browsers--
# Boar
# Turkey
# Goat
# Deer

# --Predators--
# Wolf







