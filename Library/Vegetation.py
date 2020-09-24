import numpy as np
from scipy import interpolate

class Plant():
    def __init__(self,
                 row,
                 colon,
                 reproductionRate=0.1,
                 lifeLength = 20,
                 elevationFitnessScale = np.array([[0, 0], [0.2, 0.5], [0.5, 0.5], [1, 1]]),
                 temperatureFitnessScale = np.array([[0, 0], [0.2, 0.5], [0.5, 0.5], [1, 1]]),
                 moistureFitnessScale = np.array([[0, 0], [0.2, 0.5], [0.5, 0.5], [1, 1]])):
        self.row = row
        self.colon = colon
        self.reproductionRate = reproductionRate
        self.lifeLength = lifeLength
        self.age = 0

        self.elevationFitnessScale = elevationFitnessScale
        self.temperatureFitnessScale = temperatureFitnessScale
        self.moistureFitnessScale = moistureFitnessScale

        self.elevationFitnessInterpolator = interpolate.interp1d(x=self.elevationFitnessScale[:, 0],
                                                                 y = self.elevationFitnessScale[:, 1],
                                                                 kind = 'linear',
                                                                 fill_value=(0, 1))
        self.temperatureFitnessInterpolator = interpolate.interp1d(x=self.temperatureFitnessScale[:, 0],
                                                                   y = self.temperatureFitnessScale[:, 1],
                                                                   kind = 'linear',
                                                                   fill_value=(0, 1))
        self.moistureFitnessInterpolator = interpolate.interp1d(x=self.moistureFitnessScale[:, 0],
                                                                y = self.moistureFitnessScale[:, 1],
                                                                kind = 'linear',
                                                                fill_value=(0, 1))

        self.fitness = self.CalculateFitness()

    def CalculateFitness(self, row=None, colon=None):
        if row == None: row = self.row
        if colon == None: colon = self.colon

        elevationFitness = self.elevationFitnessInterpolator(self.mainProgram.world.elevation[row, colon])
        temperatureFitness = self.temperatureFitnessInterpolator(self.mainProgram.world.temperature[row, colon])
        moistureFitness = self.moistureFitnessInterpolator(self.mainProgram.world.moisture[row, colon])

        return (elevationFitness + temperatureFitness + moistureFitness)/3

    def Step(self):
        self.age += 1
        if self.age == self.lifeLength:
            self.Die()

        self.Reproduce()

    def Die(self):
        print('The plant should die')
        pass

    def Reproduce(self):
        print('The plant should reproduce')

    @classmethod
    def Initialize(cls, mainProgram):
        cls.mainProgram = mainProgram
        cls.plants = [[None for colon in range(cls.mainProgram.settings.N_COLONS)]
                      for row in range(cls.mainProgram.settings.N_ROWS)]
        return cls.plants

class Grass(Plant):
    def __init__(self,
                 row,
                 colon,
                 reproductionRate = 0.5,
                 lifeLength = 10,
                 elevationFitnessScale = np.array([[0, 0], [0.2, 0.2], [0.5, 0.5], [1, 1]]),
                 temperatureFitnessScale = np.array([[0, 0], [0.2, 0.2], [0.5, 0.5], [1, 1]]),
                 moistureFitnessScale = np.array([[0, 0], [0.2, 0.2], [0.5, 0.5], [1, 1]])):
        super().__init__(row,
                         colon,
                         reproductionRate,
                         lifeLength,
                         elevationFitnessScale=elevationFitnessScale,
                         temperatureFitnessScale=temperatureFitnessScale,
                         moistureFitnessScale=moistureFitnessScale)





