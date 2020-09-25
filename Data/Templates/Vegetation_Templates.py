import numpy as np

import Library.Vegetation as Vegetation



class NormalGrass(Vegetation.Grass):
    def __init__(self, row, colon, fitness = None):
        super().__init__(row,
                         colon,
                         reproductionRate=0.8,
                         lifeLength=10,
                         fitness=fitness)

    @classmethod
    def CreateFitnessScales(cls):
        maxZ = cls.mainProgram.settings.ELEVATION_LEVELS
        cls.elevationFitnessScale = np.array([[0, 1], [0.4*maxZ, 1], [0.6*maxZ, 0.8], [0.85*maxZ, 0], [maxZ, 0]])
        cls.temperatureFitnessScale = np.array([[-50, 0], [-15, 0], [0, 0.3], [10, 0.8], [20, 1], [30, 0.9]])
        cls.moistureFitnessScale = np.array([[0, 0], [0.1, 0], [0.2, 0.5], [0.5, 0.8], [1, 1]])

class NormalTree(Vegetation.Tree):
    def __init__(self,row, colon, fitness = None):
        super().__init__(row,
                         colon,
                         reproductionRate=0.4,
                         lifeLength=50,
                         fitness = fitness)
    @classmethod
    def CreateFitnessScales(cls):
        maxZ = cls.mainProgram.settings.ELEVATION_LEVELS
        cls.elevationFitnessScale = np.array([[0, 1], [0.4*maxZ, 1], [0.5*maxZ, 0.6], [0.6*maxZ, 0], [maxZ, 0]])
        cls.temperatureFitnessScale = np.array([[-50, 0], [-5, 0], [0, 0.1], [10, 0.7], [20, 1], [30, 0.8]])
        cls.moistureFitnessScale = np.array([[0, 0], [0.3, 0], [0.4, 0.4], [0.6, 0.9], [1, 1]])

class Jungle(Vegetation.Tree):
    def __init__(self,row, colon, fitness = None):
        super().__init__(row,
                         colon,
                         reproductionRate=0.5,
                         lifeLength=50,
                         fitness = fitness,
                         colour = [0.2, 0.5, 0.1],
                         featureTemplate='jungle')
    @classmethod
    def CreateFitnessScales(cls):
        maxZ = cls.mainProgram.settings.ELEVATION_LEVELS
        cls.elevationFitnessScale = np.array([[0, 1], [0.4*maxZ, 1], [0.5*maxZ, 0.6], [0.6*maxZ, 0], [maxZ, 0]])
        cls.temperatureFitnessScale = np.array([[-50, 0], [-5, 0], [0, 0], [10, 0], [20, 0.8], [30, 1.0]])
        cls.moistureFitnessScale = np.array([[0, 0], [0.3, 0], [0.4, 0], [0.6, 0.9], [1, 1]])

class SpruceForest(Vegetation.Tree):
    def __init__(self,row, colon, fitness = None):
        super().__init__(row,
                         colon,
                         reproductionRate=0.3,
                         lifeLength=50,
                         fitness = fitness,
                         colour = [0, 0.4, 0.3],
                         featureTemplate='spruce_forest')
    @classmethod
    def CreateFitnessScales(cls):
        maxZ = cls.mainProgram.settings.ELEVATION_LEVELS
        cls.elevationFitnessScale = np.array([[0, 1], [0.5*maxZ, 1], [0.6*maxZ, 0.8], [0.75*maxZ, 0], [maxZ, 0]])
        cls.temperatureFitnessScale = np.array([[-50, 0], [-8, 0], [0, 0.7], [5, 1.0], [20, 0.4], [30, 0]])
        cls.moistureFitnessScale = np.array([[0, 0], [0.2, 0], [0.4, 0.5], [0.6, 0.7], [1, 1]])

class PineForest(Vegetation.Tree):
    def __init__(self,row, colon, fitness = None):
        super().__init__(row,
                         colon,
                         reproductionRate=0.3,
                         lifeLength=50,
                         fitness = fitness,
                         colour = [1, 0.3, 0],
                         featureTemplate='pine_forest')
    @classmethod
    def CreateFitnessScales(cls):
        maxZ = cls.mainProgram.settings.ELEVATION_LEVELS
        cls.elevationFitnessScale = np.array([[0, 1], [0.5*maxZ, 1], [0.6*maxZ, 0.8], [0.75*maxZ, 0], [maxZ, 0]])
        cls.temperatureFitnessScale = np.array([[-50, 0], [0, 0], [10, 0.8], [20, 1], [30, 1]])
        cls.moistureFitnessScale = np.array([[0, 0], [0.3, 0], [0.4, 1], [0.5, 0.7], [1, 0.3]])

class BroadleafForest(Vegetation.Tree):
    def __init__(self,row, colon, fitness = None):
        super().__init__(row,
                         colon,
                         reproductionRate=0.3,
                         lifeLength=50,
                         fitness = fitness,
                         colour = [0, 0.7, 0.1],
                         featureTemplate='temperate_forest')
    @classmethod
    def CreateFitnessScales(cls):
        maxZ = cls.mainProgram.settings.ELEVATION_LEVELS
        cls.elevationFitnessScale = np.array([[0, 1], [0.5*maxZ, 1], [0.6*maxZ, 0.8], [0.75*maxZ, 0], [maxZ, 0]])
        cls.temperatureFitnessScale = np.array([[-50, 0], [0, 0], [0.5, 0.5], [10, 1], [15, 0.8], [30, 0.5]])
        cls.moistureFitnessScale = np.array([[0, 0], [0.3, 0], [0.4, 0.7], [0.8, 1], [1, 1]])

