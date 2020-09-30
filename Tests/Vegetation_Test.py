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

        import time
        tic = time.time()
        World.WorldClass.Initialize(mainProgram = self)
        self.world = World.WorldClass()
        toc = time.time()
        print('World creation time: ', toc-tic)

        self.plants = Ecosystem.Vegetation.Initialize(mainProgram=self)
        self.animals = Ecosystem.Animal.Initialize(mainProgram=self)
        self.predators = Ecosystem.Predator.Initialize(mainProgram=self)

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

        Animal_Templates.Wolf.InitializeFitnessInterpolators()

        Ecosystem.Vegetation.SeedWorld(200, Vegetation_Templates.NormalGrass, minFitness=0.2)
        Ecosystem.Vegetation.SeedWorld(20, Vegetation_Templates.Jungle, minFitness=0.2)
        Ecosystem.Vegetation.SeedWorld(50, Vegetation_Templates.SpruceForest, minFitness=0.2)
        Ecosystem.Vegetation.SeedWorld(40, Vegetation_Templates.PineForest, minFitness=0.2)
        Ecosystem.Vegetation.SeedWorld(50, Vegetation_Templates.BroadleafForest, minFitness=0.2)

        for iStep in range(5):
            for plantRow in self.plants.copy():
                for plant in plantRow:
                    if plant:
                        plant.Step()

        Ecosystem.Animal.SeedWorld(30, Animal_Templates.Boar, minFitness=0.2)
        Ecosystem.Animal.SeedWorld(20, Animal_Templates.Turkey, minFitness=0.2)
        Ecosystem.Animal.SeedWorld(50, Animal_Templates.Deer, minFitness=0.2)
        Ecosystem.Animal.SeedWorld(50, Animal_Templates.Caribou, minFitness=0.2)
        Ecosystem.Animal.SeedWorld(50, Animal_Templates.Bison, minFitness=0.2)
        Ecosystem.Animal.SeedWorld(50, Animal_Templates.Horse, minFitness=0.2)

        NSteps = 30
        for iStep in range(NSteps):
            for animalRow in self.animals.copy():
                for animal in animalRow:
                    if animal:
                        animal.Step()
            for plantRow in self.plants.copy():
                for plant in plantRow:
                    if plant:
                        plant.Step()
        NSteps = 100
        Ecosystem.Predator.SeedWorld(10, Animal_Templates.Wolf, minFitness=0.2)

        forestImage = Ecosystem.Vegetation.GetImage()
        animalImage = Ecosystem.Vegetation.GetImage()
        predatorImage = Ecosystem.Predator.GetImage()

        fig, axs = plt.subplots(3)
        #fig.suptitle('Vertically stacked subplots')
        vegetationImageObject = axs[0].imshow(forestImage)
        animalImageObject = axs[1].imshow(animalImage)
        predatorImageObject = axs[2].imshow(predatorImage)

        for iStep in range(NSteps):
            for predatorRow in self.predators.copy():
                for predator in predatorRow:
                    if predator:
                        pass
                        #predator.Step()
            for animalRow in self.animals.copy():
                for animal in animalRow:
                    if animal:
                        animal.Step()
            for plantRow in self.plants.copy():
                for plant in plantRow:
                    if plant:
                        plant.Step()

            forestImage = Ecosystem.Vegetation.GetImage(densityScaling=True)
            animalImage = Ecosystem.Animal.GetImage()
            predatorImage = Ecosystem.Predator.GetImage()
            vegetationImageObject.set_array(forestImage)
            animalImageObject.set_array(animalImage)
            predatorImageObject.set_array(predatorImage)
            plt.pause(0.0001)

        self.world.VisualizeMaps([self.world.elevation, self.world.temperature, self.world.moisture])

        plt.show()


Main()
print('Program done')


