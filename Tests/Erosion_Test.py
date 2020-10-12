import numpy as np
from matplotlib import pyplot as plt
import time

import perlin_numpy


import Settings
import Library.World as World
import Library.Erosion as Erosion


class Main():
    def __init__(self):
        self.settings = Settings.SettingsClass()

        if False:
            #import noise


            #help(noise)
            shape = (256, 512)
            world = perlin_numpy.generate_fractal_noise_2d(shape, (2, 4), octaves=8, lacunarity=2, persistence=0.7, tileable=(False, True))

            '''
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
            '''

            plt.imshow(world)
            #fig, axs = plt.subplots(1, 2)
            #axs[0].imshow(world)
            #axs[1].imshow(world1)
            plt.show()
            quit()




        if True:
            tic = time.time()
            World.WorldClass.Initialize(mainProgram = self)
            #self.world = World.WorldClass()
            toc = time.time()
            print('World creation time: ', toc-tic)

            shape = (256, 512)
            self.heightMap = perlin_numpy.generate_fractal_noise_2d(shape, (2, 4), octaves=8, lacunarity=2, persistence=0.65, tileable=(False, True))
            self.terrainHardness = perlin_numpy.generate_fractal_noise_2d(shape, (2, 4), octaves=8, lacunarity=2,
                                                                    persistence=0.8, tileable=(False, True))
            self.terrainHardness -= np.min(self.terrainHardness)
            self.terrainHardness /= np.max(self.terrainHardness)

            h = np.cos(np.linspace(-np.pi, np.pi, 512))
            h = np.reshape(h, (1, 512))
            h *= 120
            self.heightMap -= np.min(self.heightMap)
            self.heightMap /= np.max(self.heightMap)
            #self.heightMap = 10*self.heightMap + np.repeat(h, 256, axis=0)

            #h = np.cos(np.linspace(-np.pi, np.pi, self.settings.N_COLONS*self.settings.MODEL_RESOLUTION))
            #h = np.reshape(h, (1, self.settings.N_COLONS*self.settings.MODEL_RESOLUTION))
            #h *= 120
            #self.heightMap = 10*self.heightMap + np.repeat(h, self.settings.N_ROWS*self.settings.MODEL_RESOLUTION, axis=0)

            #self.heightMap -= np.min(self.heightMap)
            #self.heightMap /= np.max(self.heightMap)
            self.heightMap *= 8*30
        else:
            self.heightMap = np.zeros((self.settings.N_ROWS*self.settings.MODEL_RESOLUTION, self.settings.N_COLONS*self.settings.MODEL_RESOLUTION))
        #self.heightMap[100, 100] = 1000
        #self.heightMap[100, 101] = 1000
        #self.heightMap[101, 100] = 1000
        #self.heightMap[101, 101] = 1000

        Erosion.HydrolicErosion.InitializeRainDropTemplates(maximumRainDropRadius=20)
        self.hydrolicErosion = Erosion.HydrolicErosion(terrain = self.heightMap,
                                                       terrainHardness = self.terrainHardness,
                                                                evaporationRate=0.02,
                                                                deltaT=1,
                                                                flowSpeed=0.2,
                                                                gridLength=1,
                                                                carryCapacityLimit=.5,
                                                                erosionRate=0.25,
                                                                depositionRate=0.5,
                                                                maximumErosionDepth=10)

        #self.thermalErosion = Erosion.ThermalErosion(terrain = self.heightMap,
        #                                                      maximumSlope=50,
        #                                                      flowSpeed=0.01,
        #                                                      deltaT=0.1)

        tic = time.time()
        for i in range(600):
            print(i)
            #self.hydrolicErosion.Rain(numberOfDrops=10, radius=10, dropSize=0.01, application='even')



            if i > 100:
                self.hydrolicErosion.Rain(numberOfDrops=100, radius=2, dropSize=100, application='drop')
            else:
                self.hydrolicErosion.Rain(numberOfDrops=100, radius=2, dropSize=100, application='drop')
                #self.hydrolicErosion.Rain(numberOfDrops=1, radius=10, dropSize=0.2, application='even')

            #self.hydrolicErosion.Rain(numberOfDrops=10, radius=20, dropSize=100, application='drop')
            #if np.mod(i, 50) == 0:
            #    self.hydrolicErosion.Rain(numberOfDrops=1, radius=10, dropSize=2, application='even')
            self.hydrolicErosion()

            self.hydrolicErosion.Visualize()
            plt.pause(0.000001)
        toc = time.time()
        print('Total erosion time: ', toc-tic)

        #scaledHeightMap = self.world.ApplyDistributionFilter(self.heightMap, self.settings.ELEVATION_DISTRIBUTION)
        scaledHeightMap = self.heightMap.copy()
        scaledHeightMap -= np.min(scaledHeightMap)
        scaledHeightMap /= np.max(scaledHeightMap)
        scaledHeightMap *= 8
        plt.figure()
        plt.imshow(scaledHeightMap)

        from scipy import interpolate
        interpolator = interpolate.interp2d(np.linspace(-0.5, self.settings.N_COLONS-0.5, self.settings.N_COLONS*self.settings.MODEL_RESOLUTION),
                             np.linspace(-0.5, self.settings.N_ROWS-0.5, self.settings.N_ROWS*self.settings.MODEL_RESOLUTION),
                             self.heightMap)
        tileElevation = interpolator(range(self.settings.N_COLONS), range(self.settings.N_ROWS))
        plt.figure()
        plt.imshow(tileElevation)
        plt.show()

Main()
print('Erosion test finished')