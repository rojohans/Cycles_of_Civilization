import numpy as np
from matplotlib import pyplot as plt
import matplotlib
import System_Information
if System_Information.OPERATING_SYSTEM == 'windows':
    matplotlib.use('TkAgg')
import time

import perlin_numpy


import Settings
import Library.World as World
import Library.Erosion as Erosion


class Main():
    def __init__(self):
        self.settings = Settings.SettingsClass()

        if True:
            tic = time.time()
            World.WorldClass.Initialize(mainProgram = self)
            #self.world = World.WorldClass()
            toc = time.time()
            print('World creation time: ', toc-tic)

            shape = (256, 512)
            self.heightMap = perlin_numpy.generate_fractal_noise_2d(shape, (2, 4), octaves=8, lacunarity=2, persistence=0.5, tileable=(False, True))
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
            self.heightMap *= 512/5
        else:
            h = np.linspace(0, 512, 512)
            h = np.reshape(h, (1, 512))
            self.heightMap = np.repeat(h, 256, axis=0)



            #self.heightMap = np.zeros((self.settings.N_ROWS*self.settings.MODEL_RESOLUTION, self.settings.N_COLONS*self.settings.MODEL_RESOLUTION))
            #self.heightMap[100, 100] = 1000
            #self.heightMap[100, 101] = 1000
            #self.heightMap[101, 100] = 1000
            #self.heightMap[101, 101] = 1000
            #self.heightMap[100:110, 100:110] = 100
            #self.heightMap[:, 300:310] = 100

        matplotlibVisualization = True
        pyvistaVisualization = False

        if pyvistaVisualization:
            X = np.arange(0, 512, 1)
            Y = np.arange(0, 256, 1)
            X, Y = np.meshgrid(X, Y)

            import pyvista as pv

            def CoordinatesToIndex(x, y):
                return x + y*shape[1]

            NPoints = shape[0]*shape[1]
            terrainPoints = np.zeros((NPoints, 3))
            terrainPoints[:, 0] = np.reshape(X, (NPoints, 1))[:, 0]
            terrainPoints[:, 1] = np.reshape(Y, (NPoints, 1))[:, 0]
            terrainPoints[:, 2] = np.reshape(self.heightMap, (NPoints, 1))[:, 0]

            waterPoints = np.zeros((NPoints, 3))
            waterPoints[:, 0] = np.reshape(X, (NPoints, 1))[:, 0]
            waterPoints[:, 1] = np.reshape(Y, (NPoints, 1))[:, 0]
            waterPoints[:, 2] = np.reshape(np.zeros((shape[0], shape[1])), (NPoints, 1))[:, 0]

            faces = []
            for x in range(shape[1]-1):
                for y in range(shape[0]-1):
                    faces.append([4, CoordinatesToIndex(x, y), CoordinatesToIndex(x+1, y), CoordinatesToIndex(x+1, y+1), CoordinatesToIndex(x, y+1)])
            faces = np.hstack(faces)

            terrainMesh = pv.PolyData(terrainPoints, faces)
            waterMesh = pv.PolyData(waterPoints, faces)



            plotter = pv.Plotter()
            # , scalars = grid.points[:, -1]
            # opacity=1+waterPoints[:, -1]
            plotter.add_mesh(terrainMesh, scalars = terrainPoints[:, -1], smooth_shading=True)
            plotter.add_mesh(waterMesh, smooth_shading=True, color = [0.1, 0.3, 0.6], opacity=0.5)
            plotter.enable_3_lights()
            #waterMesh = plotter.add_mesh(mesh = waterGrid, color=[0.1, 0.4, 0.8], smooth_shading=True, show_edges=False)
            plotter.enable_terrain_style()
            plotter.show(auto_close=False)

            #https: // github.com / BartheG / Orvisu
            #https: // github.com / OpenGeoVis / PVGeo

        Erosion.HydrolicErosion.InitializeRainDropTemplates(maximumRainDropRadius=20)
        #self.terrainHardness
        self.hydrolicErosion = Erosion.HydrolicErosion(terrain = self.heightMap,
                                                       terrainHardness = None,
                                                                evaporationRate=0.1,
                                                                deltaT=0.1,
                                                                flowSpeed=2,
                                                       sedimentFlowSpeed=0.5,
                                                                gridLength=1,
                                                                carryCapacityLimit=2,
                                                                erosionRate=0.1,
                                                                depositionRate=0.1,
                                                                maximumErosionDepth=10)

        self.thermalErosion = Erosion.ThermalErosion(terrain = self.heightMap,
                                                              maximumSlope=30,
                                                              flowSpeed=1,
                                                              deltaT=1)

        #          USEFUL PAPERS
        #https: // github.com / bshishov / UnityTerrainErosionGPU
        #https://old.cescg.org/CESCG-2011/papers/TUBudapest-Jako-Balazs.pdf
        #https://hal.inria.fr/inria-00402079/document
        #http: // www - cg.cis.iwate - u.ac.jp / lab / graphite06.pdf
        #https://matthias-research.github.io/pages/publications/SPHShallow.pdf
        #https://dl.acm.org/doi/pdf/10.1145/97880.97884
        #

        tic = time.time()
        for i in range(600):
            print(i)
            #self.hydrolicErosion.Rain(numberOfDrops=10, radius=10, dropSize=0.01, application='even')


            if i>400:
                rainAmount = 0
            else:
                rainAmount = 0.03 * (1 + np.sin(i / 20)) / 2

            #self.hydrolicErosion.Rain(numberOfDrops=1, radius=10, dropSize=0.02, application='even')
            self.hydrolicErosion.Rain(numberOfDrops=1, radius=10, dropSize=rainAmount, application='even')
            '''
            if i > 100:
                #self.hydrolicErosion.Rain(numberOfDrops=100, radius=2, dropSize=100, application='drop')
                if np.mod(i, 10) == 0:
                    #self.hydrolicErosion.Rain(numberOfDrops=200, radius=2, dropSize=100, application='drop')
                    self.hydrolicErosion.Rain(numberOfDrops=1, radius=10, dropSize=0.1, application='even')
            else:
                #self.hydrolicErosion.Rain(numberOfDrops=100, radius=2, dropSize=100, application='drop')
                if np.mod(i, 20) == 0:
                    self.hydrolicErosion.Rain(numberOfDrops=1, radius=10, dropSize=0.2, application='even')
            '''

            #self.hydrolicErosion.Rain(numberOfDrops=10, radius=20, dropSize=100, application='drop')
            #if np.mod(i, 50) == 0:
            #    self.hydrolicErosion.Rain(numberOfDrops=1, radius=10, dropSize=2, application='even')
            self.hydrolicErosion()
            #self.hydrolicErosion.UpdateSlope()

            #self.hydrolicErosion.UpdateFlow()
            #self.hydrolicErosion.UpdateWaterHeight()
            #self.hydrolicErosion.UpdateVelocity()

            if i%20 == 0:
                pass
                #self.thermalErosion()
            #self.thermalErosion()

            #print(np.min(self.heightMap))
            #print(np.max(self.heightMap))

            #self.thermalErosion()
            #self.thermalErosion()

            if pyvistaVisualization:
                z = self.heightMap.copy()
                z[:, 0] = -10
                z[:, -1] = -10
                z[0, :] = -10
                z[-1, :] = -10
                terrainPoints[:, -1] = np.reshape(z, (NPoints, 1))[:, 0]

                z = self.heightMap.copy()+self.hydrolicErosion.water[:, :, 0].copy()
                z[self.hydrolicErosion.water[:, :, 0] < 1] = 0
                z[:, 0] = -10
                z[:, -1] = -10
                z[0, :] = -10
                z[-1, :] = -10
                waterPoints[:, -1] = np.reshape(z, (NPoints, 1))[:, 0]

                print(np.max(waterPoints[:, -1]))

                plotter.update_coordinates(points=terrainPoints, mesh=terrainMesh)
                plotter.update_coordinates(points=waterPoints, mesh = waterMesh)

                #plotter.update_coordinates(points=pts, render=False)
                #plotter.update_coordinates(waterPts, render=False)
                plotter.update_scalars(terrainPoints[:, -1], mesh=terrainMesh, render=False)
                plotter.mesh.compute_normals(cell_normals=False, inplace=True)
                plotter.render()


            if matplotlibVisualization:
                self.hydrolicErosion.Visualize()
                plt.pause(0.000001)
        toc = time.time()
        print('Total erosion time: ', toc-tic)
        if pyvistaVisualization:
            plotter.show(auto_close=False)
        if matplotlibVisualization:
            plt.show()

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