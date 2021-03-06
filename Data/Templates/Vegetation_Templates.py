import numpy as np

import Library.Ecosystem as Vegetation



class NormalGrass(Vegetation.Grass):
    def __init__(self, row, colon, fitness = None):
        super().__init__(row,
                         colon,
                         density=0.1,
                         reproductionRate=10.0,
                         growthRate = 0.55,
                         lifeLength=10,
                         fitness=fitness)

    @classmethod
    def CreateFitnessScales(cls):
        maxZ = cls.mainProgram.settings.ELEVATION_LEVELS
        cls.elevationFitnessScale = np.array([[0, 1], [0.4*maxZ, 1], [0.6*maxZ, 0.8], [0.85*maxZ, 0], [maxZ, 0]])
        cls.temperatureFitnessScale = np.array([[-50, 0], [-12, 0], [0, 0.5], [10, 0.8], [20, 1], [30, 0.9]])
        cls.moistureFitnessScale = np.array([[0, 0], [0.1, 0], [0.2, 0.5], [0.6, 1], [1, 0.9]])

class Jungle(Vegetation.Forest):
    def __init__(self,row, colon, fitness = None):
        super().__init__(row,
                         colon,
                         reproductionRate=0.2,
                         growthRate=0.25,
                         lifeLength=50,
                         density=0.1,
                         fitness = fitness,
                         eatenMultiplier=1,
                         colour = [0.05, 0.2, 0],
                         featureTemplate='jungle')
    @classmethod
    def CreateFitnessScales(cls):
        maxZ = cls.mainProgram.settings.ELEVATION_LEVELS
        cls.elevationFitnessScale = np.array([[0, 1], [0.4*maxZ, 1], [0.5*maxZ, 0.6], [0.6*maxZ, 0], [maxZ, 0]])
        cls.temperatureFitnessScale = np.array([[-50, 0], [15, 0], [25, 1], [30, 1.0]])
        cls.moistureFitnessScale = np.array([[0, 0], [0.4, 0], [0.6, 0.9], [1, 1]])

class SpruceForest(Vegetation.Forest):
    def __init__(self,row, colon, fitness = None):
        super().__init__(row,
                         colon,
                         reproductionRate=0.15,
                         growthRate=0.05,
                         lifeLength=50,
                         density=0.1,
                         fitness = fitness,
                         colour = [0, 0.25, 0.2],
                         featureTemplate='spruce_forest')
    @classmethod
    def CreateFitnessScales(cls):
        maxZ = cls.mainProgram.settings.ELEVATION_LEVELS
        cls.elevationFitnessScale = np.array([[0, 1], [0.5*maxZ, 1], [0.6*maxZ, 0.7], [0.7*maxZ, 0], [maxZ, 0]])
        cls.temperatureFitnessScale = np.array([[-50, 0], [-8, 0], [0, 0.7], [5, 1.0], [20, 0.2], [30, 0]])
        cls.moistureFitnessScale = np.array([[0, 0], [0.2, 0], [0.4, 0.5], [0.6, 0.7], [1, 1]])

class FirForest(Vegetation.Forest):
    def __init__(self,row, colon, fitness = None):
        super().__init__(row,
                         colon,
                         reproductionRate=0.15,
                         growthRate=0.05,
                         lifeLength=50,
                         density=0.1,
                         fitness = fitness,
                         colour = [0, 0.15, 0.1],
                         featureTemplate='spruce_forest')
    @classmethod
    def CreateFitnessScales(cls):
        maxZ = cls.mainProgram.settings.ELEVATION_LEVELS
        cls.elevationFitnessScale = np.array([[0, 0.5], [0.5*maxZ, 1], [0.65*maxZ, 1], [0.75*maxZ, 0], [maxZ, 0]])
        cls.temperatureFitnessScale = np.array([[-50, 0], [-8, 0], [0, 0.4], [5, 1.0], [25, 0], [30, 0]])
        cls.moistureFitnessScale = np.array([[0, 0], [0.2, 0], [0.5, 1], [0.7, 1], [1, 0.7]])

class PineForest(Vegetation.Forest):
    def __init__(self,row, colon, fitness = None):
        super().__init__(row,
                         colon,
                         reproductionRate=0.15,
                         growthRate=0.05,
                         lifeLength=50,
                         density=0.1,
                         fitness = fitness,
                         colour = [0.2, 0.5, 0.1],
                         featureTemplate='pine_forest')
    @classmethod
    def CreateFitnessScales(cls):
        maxZ = cls.mainProgram.settings.ELEVATION_LEVELS
        cls.elevationFitnessScale = np.array([[0, 1], [0.5*maxZ, 1], [0.6*maxZ, 0.7], [0.7*maxZ, 0], [maxZ, 0]])
        cls.temperatureFitnessScale = np.array([[-50, 0], [0, 0], [10, 0.8], [20, 1], [30, 0.8]])
        cls.moistureFitnessScale = np.array([[0, 0], [0.2, 0], [0.4, 1], [0.5, 0.7], [1, 0.3]])

class BroadleafForest(Vegetation.Forest):
    def __init__(self,row, colon, fitness = None):
        super().__init__(row,
                         colon,
                         reproductionRate=0.15,
                         growthRate=0.1,
                         lifeLength=50,
                         density=0.1,
                         fitness = fitness,
                         colour = [0, 0.7, 0.1],
                         featureTemplate='temperate_forest')
    @classmethod
    def CreateFitnessScales(cls):
        maxZ = cls.mainProgram.settings.ELEVATION_LEVELS
        cls.elevationFitnessScale = np.array([[0, 1], [0.4*maxZ, 1], [0.5*maxZ, 0.7], [0.65*maxZ, 0], [maxZ, 0]])
        cls.temperatureFitnessScale = np.array([[-50, 0], [0, 0], [0.5, 0.2], [10, 1], [15, 0.8], [30, 0.5]])
        cls.moistureFitnessScale = np.array([[0, 0], [0.3, 0], [0.4, 0.3], [0.6, 0.9], [0.8, 1], [1, 1]])

