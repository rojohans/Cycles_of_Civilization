import numpy as np
from matplotlib import pyplot as plt

import Settings
import Library.World as World
import Library.Ecosystem as Ecosystem
import Data.Templates.Vegetation_Templates as Vegetation_Templates
import Data.Templates.Animal_Templates as Animal_Templates

class Main():
    def __init__(self):
        self.settings = Settings.SettingsClass()

        World.WorldClass.Initialize(mainProgram = self)
        self.world = World.WorldClass()

        self.plants = Ecosystem.Vegetation.Initialize(mainProgram=self)
        self.animals = Ecosystem.Animal.Initialize(mainProgram=self)

        Vegetation_Templates.NormalGrass.InitializeFitnessInterpolators()
        Vegetation_Templates.Jungle.InitializeFitnessInterpolators()
        Vegetation_Templates.SpruceForest.InitializeFitnessInterpolators()
        Vegetation_Templates.PineForest.InitializeFitnessInterpolators()
        Vegetation_Templates.BroadleafForest.InitializeFitnessInterpolators()

        #Animal_Templates.NormalBrowser.InitializeFitnessInterpolators()
        Animal_Templates.Boar.InitializeFitnessInterpolators()
        Animal_Templates.Turkey.InitializeFitnessInterpolators()
        Animal_Templates.Deer.InitializeFitnessInterpolators()
        Animal_Templates.Caribou.InitializeFitnessInterpolators()
        Animal_Templates.Bison.InitializeFitnessInterpolators()
        Animal_Templates.Horse.InitializeFitnessInterpolators()


        Ecosystem.Vegetation.SeedWorld(200, Vegetation_Templates.NormalGrass, minFitness=0.2)
        Ecosystem.Vegetation.SeedWorld(20, Vegetation_Templates.Jungle, minFitness=0.2)
        Ecosystem.Vegetation.SeedWorld(50, Vegetation_Templates.SpruceForest, minFitness=0.2)
        Ecosystem.Vegetation.SeedWorld(40, Vegetation_Templates.PineForest, minFitness=0.2)
        Ecosystem.Vegetation.SeedWorld(50, Vegetation_Templates.BroadleafForest, minFitness=0.2)

        for iStep in range(5):
            for plantRow in self.plants:
                for plant in plantRow:
                    if plant:
                        plant.Step()

        Ecosystem.Animal.SeedWorld(30, Animal_Templates.Boar, minFitness=0.2)
        Ecosystem.Animal.SeedWorld(20, Animal_Templates.Turkey, minFitness=0.2)
        Ecosystem.Animal.SeedWorld(50, Animal_Templates.Deer, minFitness=0.2)
        Ecosystem.Animal.SeedWorld(50, Animal_Templates.Caribou, minFitness=0.2)
        Ecosystem.Animal.SeedWorld(50, Animal_Templates.Bison, minFitness=0.2)
        Ecosystem.Animal.SeedWorld(50, Animal_Templates.Horse, minFitness=0.2)


        #migrate, predator, slope


        NSteps = 100

        forestImage = Ecosystem.Vegetation.GetImage()
        animalImage = Ecosystem.Vegetation.GetImage()

        fig, axs = plt.subplots(2)
        #fig.suptitle('Vertically stacked subplots')
        vegetationImageObject = axs[0].imshow(forestImage)
        animalImageObject = axs[1].imshow(animalImage)

        for iStep in range(NSteps):
            for animalRow in self.animals:
                for animal in animalRow:
                    if animal:
                        animal.Step()
            for plantRow in self.plants:
                for plant in plantRow:
                    if plant:
                        plant.Step()

            forestImage = Ecosystem.Vegetation.GetImage()
            animalImage = Ecosystem.Animal.GetImage()
            vegetationImageObject.set_array(forestImage)
            animalImageObject.set_array(animalImage)
            plt.pause(0.0001)

        self.world.VisualizeMaps([self.world.elevation, self.world.temperature, self.world.moisture])

        plt.show()


Main()
print('Program done')


