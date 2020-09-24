import numpy as np

import Library.Vegetation as Vegetation



class NormalGrass(Vegetation.Grass):
    def __init__(self,
                 row,
                 colon):
        maxZ = self.mainProgram.settings.ELEVATION_LEVELS
        elevationFitnessScale = np.array([[0, 1], [0.4*maxZ, 1], [0.6*maxZ, 0.8], [0.8*maxZ, 0], [maxZ, 0]])
        temperatureFitnessScale = np.array([[-30, 0], [-10, 0], [0, 0.2], [10, 0.8], [20, 1], [30, 0.9]])
        moistureFitnessScale = np.array([[0, 0], [0.2, 0.5], [0.5, 0.8], [1, 1]])

        super().__init__(row,
                         colon,
                         reproductionRate=0.5,
                         lifeLength=10,
                         elevationFitnessScale=elevationFitnessScale,
                         temperatureFitnessScale=temperatureFitnessScale,
                         moistureFitnessScale=moistureFitnessScale)