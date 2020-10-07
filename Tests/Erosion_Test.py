import numpy as np
from matplotlib import pyplot as plt
import time

import Settings
import Library.World as World
import Library.Erosion as Erosion


class Main():
    def __init__(self):
        self.settings = Settings.SettingsClass()

        if True:
            import noise

            #help(noise)
            shape = (512, 1024)
            scale = 1024
            octaves = 10
            persistence = 0.7
            lacunarity = 2.0

            world = np.zeros(shape)
            for i in range(shape[0]):
                for j in range(shape[1]):
                    world[i][j] = noise.pnoise2(i / scale,
                                                j / scale,
                                                octaves=octaves,
                                                persistence=persistence,
                                                lacunarity=lacunarity,
                                                repeatx=0.5,
                                                repeaty=1,
                                                base=0)
            world = np.concatenate((world, world), axis=0)
            world = np.concatenate((world, world), axis=1)

            np.random.seed(42)

            import random
            random.seed(42)
            #np.random.seed(42)
            world1 = np.zeros(shape)
            for i in range(shape[0]):
                for j in range(shape[1]):
                    world1[i][j] = noise.pnoise2(i / scale,
                                                j / scale,
                                                octaves=octaves,
                                                persistence=persistence,
                                                lacunarity=lacunarity,
                                                repeatx=0.5,
                                                repeaty=1,
                                                base=0)
            world1 = np.concatenate((world1, world1), axis=0)
            world1 = np.concatenate((world1, world1), axis=1)

            plt.imshow(world)
            plt.figure()
            plt.imshow(world1)
            plt.show()
            quit()




        if False:
            tic = time.time()
            World.WorldClass.Initialize(mainProgram = self)
            self.world = World.WorldClass()
            toc = time.time()
            print('World creation time: ', toc-tic)

            self.heightMap = self.world.elevationInterpolated
            #self.heightMap = self.world.elevation

            h = np.cos(np.linspace(-np.pi, np.pi, self.settings.N_COLONS*self.settings.MODEL_RESOLUTION))
            h = np.reshape(h, (1, self.settings.N_COLONS*self.settings.MODEL_RESOLUTION))
            h *= 100

            #self.heightMap = 10*self.heightMap + np.repeat(h, self.settings.N_ROWS*self.settings.MODEL_RESOLUTION, axis=0)
            self.heightMap *= 30
        else:
            self.heightMap = np.zeros((self.settings.N_ROWS*self.settings.MODEL_RESOLUTION, self.settings.N_COLONS*self.settings.MODEL_RESOLUTION))
        #self.heightMap[100, 100] = 1000
        #self.heightMap[100, 101] = 1000
        #self.heightMap[101, 100] = 1000
        #self.heightMap[101, 101] = 1000

        Erosion.HydrolicErosion.InitializeRainDropTemplates(maximumRainDropRadius=10)
        self.hydrolicErosion = Erosion.HydrolicErosion(terrain = self.heightMap,
                                                                evaporationRate=0.02,
                                                                deltaT=1,
                                                                flowSpeed=0.2,
                                                                gridLength=1,
                                                                carryCapacityLimit=5,
                                                                erosionRate=0.05,
                                                                depositionRate=0.1,
                                                                maximumErosionDepth=10)

        self.thermalErosion = Erosion.ThermalErosion(terrain = self.heightMap,
                                                              maximumSlope=50,
                                                              flowSpeed=0.01,
                                                              deltaT=0.1)

        self.hydrolicErosion.Rain(numberOfDrops=1, radius=10, dropSize=100, application='even')

        tic = time.time()
        for i in range(1000):
            print(i)
            #self.hydrolicErosion.Rain(numberOfDrops=10, radius=10, dropSize=0.01, application='even')


            if i > 100:
                self.hydrolicErosion.Rain(numberOfDrops=100, radius=10, dropSize=100, application='drop')
                #if np.mod(i, 10) == 0:
                #    self.hydrolicErosion.Rain(numberOfDrops=1, radius=10, dropSize=0.5, application='even')


            self.hydrolicErosion.UpdateFlow()
            self.hydrolicErosion.UpdateWaterHeight()
            self.hydrolicErosion.UpdateVelocity()

            self.hydrolicErosion.UpdateSlope()

            self.hydrolicErosion.UpdateCarryCapacity()
            self.hydrolicErosion.Erode()
            self.hydrolicErosion.Deposit()
            self.hydrolicErosion.SedimentTransportation()
            self.hydrolicErosion.Evaporation()



            #self.thermalErosion.UpdateSlope()
            #self.thermalErosion.UpdateFlow()
            #self.thermalErosion.UpdateTerrainHeight()
            #self.hydrolicErosion.slope = self.thermalErosion.flow[:, :, 0]

            self.hydrolicErosion.Visualize()
            plt.pause(0.000001)
        toc = time.time()
        print('Total erosion time: ', toc-tic)
        plt.show()

Main()
print('Erosion test finished')