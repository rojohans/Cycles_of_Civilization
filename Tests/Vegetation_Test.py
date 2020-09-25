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

        Vegetation_Templates.NormalGrass.InitializeFitnessInterpolators()
        Vegetation_Templates.Jungle.InitializeFitnessInterpolators()
        Vegetation_Templates.SpruceForest.InitializeFitnessInterpolators()
        Vegetation_Templates.PineForest.InitializeFitnessInterpolators()
        Vegetation_Templates.BroadleafForest.InitializeFitnessInterpolators()

        #Vegetation.Plant.SeedWorld(1000, Vegetation_Templates.NormalGrass, minFitness=0.2)
        #Vegetation.Plant.SeedWorld(100, Vegetation_Templates.Jungle, minFitness=0.2)
        #Vegetation.Plant.SeedWorld(200, Vegetation_Templates.SpruceForest, minFitness=0.2)
        #Vegetation.Plant.SeedWorld(100, Vegetation_Templates.PineForest, minFitness=0.2)
        #Vegetation.Plant.SeedWorld(200, Vegetation_Templates.BroadleafForest, minFitness=0.2)
        Vegetation.Plant.SeedWorld(200, Vegetation_Templates.NormalGrass, minFitness=0.2)
        Vegetation.Plant.SeedWorld(50, Vegetation_Templates.Jungle, minFitness=0.2)
        Vegetation.Plant.SeedWorld(50, Vegetation_Templates.SpruceForest, minFitness=0.2)
        Vegetation.Plant.SeedWorld(50, Vegetation_Templates.PineForest, minFitness=0.2)
        Vegetation.Plant.SeedWorld(50, Vegetation_Templates.BroadleafForest, minFitness=0.2)

        NSteps = 100

        forestImage = Vegetation.Plant.GetImage()
        vegetationImageObject = plt.imshow(forestImage)
        for iStep in range(NSteps):
            for plantRow in self.plants:
                for plant in plantRow:
                    if plant:
                        plant.Step()
            forestImage = Vegetation.Plant.GetImage()
            vegetationImageObject.set_array(forestImage)
            plt.pause(0.0001)

        self.world.VisualizeMaps([self.world.elevation, self.world.temperature, self.world.moisture])

        plt.show()


Main()
print('Program done')


