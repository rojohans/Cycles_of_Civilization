import numpy as np
from matplotlib import pyplot as plt
import time

import Settings
import Library.World as World
import Library.Ecosystem as Ecosystem
import Data.Templates.Vegetation_Templates as Vegetation_Templates
import Data.Templates.Animal_Templates as Animal_Templates

class Main():
    def __init__(self):
        self.settings = Settings.SettingsClass()

        def SinGrowth(value, maxValue):
            #maxValue*(1+np.sin((n/maxValue-0.5)*np.pi))/2
            #return np.cos((value/maxValue -0.5)*np.pi)*np.pi/2

            return np.cos(value*np.pi / (2*maxValue)) * np.pi / 2
        '''
        xGrowth = 1.5

        yFoodEaten = 1.4
        yFoodEfficiency = 0.6
        yMortality = 0.6

        zFoodEaten = 0.2
        zFoodEfficiency = 0.2
        zMortality = 0.2
        '''

        '''
        xGrowth = 1.5

        yFoodEaten = 0.4
        yMaxFoodEaten = 3
        yFoodEfficiency = 0.25
        yMortality = 0.1

        zFoodEaten = 0.5
        zFoodEfficiency = 0.05
        zMortality = 0.2

        N = 5000

        dt = 0.1

        XMax = 20
        YMax = 1
        x = [10]
        y = [5.0]
        z = [0]
        #t = range(N)
        tic = time.time()
        for i in range(N-1):
            #r = 1+0.2*(np.random.rand()-0.5)
            #x.append(x[i] + dt * (x[i] * xGrowth * SinGrowth(x[i], XMax) - np.min([yFoodEaten*y[i], 9999*x[i]])))
            x.append(x[i] + dt * (x[i] * xGrowth * SinGrowth(x[i], XMax) - np.min([yFoodEaten * y[i]*x[i], yMaxFoodEaten*y[i]])))
            #y.append(y[i] + dt * (np.min([yFoodEaten*y[i], 9999*x[i]])*yFoodEfficiency - y[i] * yMortality - zFoodEaten * y[i]*z[i]))
            y.append(y[i] + dt * (np.min([yFoodEaten * y[i]*x[i], yMaxFoodEaten*y[i]]) * yFoodEfficiency - y[i] * yMortality - np.min([zFoodEaten*z[i], y[i]])))

            z.append(z[i] + dt * (zFoodEaten * z[i] * y[i] * zFoodEfficiency - z[i] * zMortality))
            if y[-1] < 0 or x[-1]<0 or z[-1]<0:
                break
        '''

        '''
        xGrowth = .5

        yGrowth = .1

        zFoodEaten = 0.5
        zFoodEfficiency = 0.05
        zMortality = 0.2

        N = 5000

        dt = 0.1

        XMax = 20
        YMax = 1
        x = [10]
        y = [5]
        z = [0]
        #t = range(N)
        tic = time.time()
        for i in range(N-1):
            x.append(x[i] + dt * x[i]*( xGrowth*(1-x[i]/XMax) - y[i]*0.75/(x[i]+1) ))

            y.append(y[i] + dt * y[i]*( yGrowth*(1-2*y[i]/x[i]) ))

            z.append(z[i] + dt * (zFoodEaten * z[i] * y[i] * zFoodEfficiency - z[i] * zMortality))
            if y[-1] < 0 or x[-1]<0 or z[-1]<0:
                break
        '''
        if False:
            xGrowth = .1

            yGrowth = .1
            #yMortality = 0.05# Sustainable
            yMortality = 0.05

            zGrowth = 0.05
            zMortality = 0.01

            N = 50000

            dt = 0.1

            XMax = 20
            YMax = 1
            x = [10]
            y = [5]
            z = [0]
            #t = range(N)
            tic = time.time()
            for i in range(N-1):
                r1 = 1 + 5.6 * (np.random.rand() - 0.5)
                r2 = 1 + 5.6 * (np.random.rand() - 0.5)
                r3 = 1 + 5.6 * (np.random.rand() - 0.5)
                x.append(x[i] + dt * r1 * x[i]*( xGrowth*(1-x[i]/XMax) - 0.5*y[i]*0.75/(x[i]+10) ))

                #y.append(y[i] + dt * y[i]*( yGrowth*(1-2*y[i]/x[i]) - z[i]*0.01/(y[i]+1)))
                y.append(y[i] + dt * r2 * y[i]*( 0.5*x[i]*0.3/(x[i]+10) - yMortality   - 0.7*z[i]*0.55/(y[i]+10)))

                z.append(z[i] + dt * r3 * z[i]*(0.7*y[i]*0.1/(y[i]+10) - zMortality))
                if y[-1] < 0 or x[-1]<0 or z[-1]<0:
                    break

            toc = time.time()
            print('time elapsed: ', toc-tic)
            fig, axs = plt.subplots(2)
            axs[0].plot(x)
            axs[0].plot(y)
            axs[0].plot(z)
            axs[0].legend(['Plant', 'Animal', 'Predator'])
            axs[1].plot(y, z)
            plt.show()
            quit()


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

        #Ecosystem.Vegetation.SeedWorld(5, Vegetation_Templates.NormalGrass, minFitness=0.2)
        Ecosystem.Vegetation.SeedWorld(200, Vegetation_Templates.NormalGrass, minFitness=0.2)
        Ecosystem.Vegetation.SeedWorld(20, Vegetation_Templates.Jungle, minFitness=0.2)
        #Ecosystem.Vegetation.SeedWorld(50, Vegetation_Templates.SpruceForest, minFitness=0.2)
        #Ecosystem.Vegetation.SeedWorld(40, Vegetation_Templates.PineForest, minFitness=0.2)
        #Ecosystem.Vegetation.SeedWorld(50, Vegetation_Templates.BroadleafForest, minFitness=0.2)

        forestImage = Ecosystem.Vegetation.GetImage(densityScaling=True)
        animalImage = Ecosystem.Animal.GetImage()
        predatorImage = Ecosystem.Predator.GetImage()
        fig, axs = plt.subplots(3)
        #fig.suptitle('Vertically stacked subplots')
        vegetationImageObject = axs[0].imshow(forestImage)
        animalImageObject = axs[1].imshow(animalImage)
        predatorImageObject = axs[2].imshow(predatorImage)
        plt.pause(3)

        for iStep in range(30):
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
            plt.pause(0.001)

        Ecosystem.Animal.SeedWorld(30, Animal_Templates.Boar, minFitness=0.2)
        #Ecosystem.Animal.SeedWorld(20, Animal_Templates.Turkey, minFitness=0.2)
        #Ecosystem.Animal.SeedWorld(50, Animal_Templates.Deer, minFitness=0.2)
        #Ecosystem.Animal.SeedWorld(50, Animal_Templates.Caribou, minFitness=0.2)
        Ecosystem.Animal.SeedWorld(50, Animal_Templates.Bison, minFitness=0.2)
        #Ecosystem.Animal.SeedWorld(50, Animal_Templates.Horse, minFitness=0.2)

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
            forestImage = Ecosystem.Vegetation.GetImage(densityScaling=True)
            animalImage = Ecosystem.Animal.GetImage(densityScaling=True)
            predatorImage = Ecosystem.Predator.GetImage()
            vegetationImageObject.set_array(forestImage)
            animalImageObject.set_array(animalImage)
            predatorImageObject.set_array(predatorImage)
            plt.pause(0.0001)

        NSteps = 100
        Ecosystem.Predator.SeedWorld(10, Animal_Templates.Wolf, minFitness=0.2)


        for iStep in range(NSteps):
            plants = self.plants.copy()
            animals = self.animals.copy()
            for row in range(self.settings.N_ROWS):
                for colon in range(self.settings.N_COLONS):
                    plant = plants[row][colon]
                    animal = animals[row][colon]
                    if animal:
                        animal.Step()
                    if plant:
                        plant.Step()

            '''        
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
            '''

            forestImage = Ecosystem.Vegetation.GetImage(densityScaling=True)
            animalImage = Ecosystem.Animal.GetImage(densityScaling=True)
            predatorImage = Ecosystem.Predator.GetImage()
            vegetationImageObject.set_array(forestImage)
            animalImageObject.set_array(animalImage)
            predatorImageObject.set_array(predatorImage)
            plt.pause(0.0001)

        self.world.VisualizeMaps([self.world.elevation, self.world.temperature, self.world.moisture])

        plt.show()


Main()
print('Program done')


