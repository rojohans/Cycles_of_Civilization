import numpy as np
from matplotlib import pyplot as plt

import Settings
import Library.World as World
import Library.Vegetation as Vegetation
import Data.Templates.Vegetation_Templates as Vegetation_Templates

class Main():
    def __init__(self):
        self.settings = Settings.SettingsClass()

        World.WorldClass.Initialize(mainProgram = self)
        self.world = World.WorldClass()

        self.plants = Vegetation.Plant.Initialize(mainProgram=self)

        g = Vegetation_Templates.NormalGrass(0, 0)



        #print(self.plants)
        #print(np.shape(self.plants))
        #print(self.plants[4][8])

        import scipy.interpolate as interpolate

        x = np.linspace(0, 8, 70)
        y = g.elevationFitnessInterpolator(x)
        plt.plot(x, y)
        plt.show()


Main()
print('Program done')


