import numpy as np
from matplotlib import pyplot as plt
import matplotlib
import System_Information
if System_Information.OPERATING_SYSTEM == 'windows':
    matplotlib.use('TkAgg')
import time
import pyvista as pv
from matplotlib.colors import ListedColormap
import System_Information
if System_Information.OPERATING_SYSTEM == 'windows':
    import cupy as cp
from numba import jit

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
            self.rockMap = perlin_numpy.generate_fractal_noise_2d(shape, (2, 4), octaves=8, lacunarity=2, persistence=0.4, tileable=(False, True))
            roughNoise = perlin_numpy.generate_fractal_noise_2d(shape, (2, 4), octaves=8, lacunarity=2,persistence=0.8, tileable=(False, True))

            h = np.cos(np.linspace(-np.pi, np.pi, 512))
            h = np.reshape(h, (1, 512))
            h *= 120
            self.rockMap -= np.min(self.rockMap)
            self.rockMap /= np.max(self.rockMap)

            roughNoise -= np.min(roughNoise)
            roughNoise /= np.max(roughNoise)

            #self.heightMap = 10*self.heightMap + np.repeat(h, 256, axis=0)

            #h = np.cos(np.linspace(-np.pi, np.pi, self.settings.N_COLONS*self.settings.MODEL_RESOLUTION))
            #h = np.reshape(h, (1, self.settings.N_COLONS*self.settings.MODEL_RESOLUTION))
            #h *= 120
            #self.heightMap = 10*self.heightMap + np.repeat(h, self.settings.N_ROWS*self.settings.MODEL_RESOLUTION, axis=0)

            #self.heightMap -= np.min(self.heightMap)
            #self.heightMap /= np.max(self.heightMap)
            #self.rockMap *= 512/15
            #self.rockMap += 5 * roughNoise

            self.rockMap *= 512/10
            self.rockMap += 10 * roughNoise
            #self.rockMap *= 512/5
            #self.rockMap += 25 * roughNoise

            self.heightMap = np.zeros((shape[0], shape[1], 3))
            self.heightMap[:, :, 0] = self.rockMap
            #self.heightMap[:, :, 1] += 0.5
            #self.heightMap[100:110, 100:110, 1] += 100
        else:
            #h = np.linspace(0, 512, 512)
            #h = np.reshape(h, (1, 512))
            #self.heightMap = np.repeat(h, 256, axis=0)



            self.heightMap = np.zeros((self.settings.N_ROWS*self.settings.MODEL_RESOLUTION, self.settings.N_COLONS*self.settings.MODEL_RESOLUTION))
            #self.heightMap[100, 100] = 1000
            #self.heightMap[100, 101] = 1000
            #self.heightMap[101, 100] = 1000
            #self.heightMap[101, 101] = 1000
            self.heightMap[100:110, 100:110] = 50
            #self.heightMap[:, 300:310] = 100

        '''
        x = np.arange(10000).reshape(100, 100)

        @jit(nopython=True)
        def go_fast(a):  # Function is compiled and runs in machine code
            trace = 0.0
            for i in range(a.shape[0]):
                trace += np.tanh(a[i, i])
            return a + trace

        # DO NOT REPORT THIS... COMPILATION TIME IS INCLUDED IN THE EXECUTION TIME!
        start = time.time()
        a = go_fast(x)
        end = time.time()
        print("Elapsed (with compilation) = %s" % (end - start))

        # NOW THE FUNCTION IS COMPILED, RE-TIME IT EXECUTING FROM CACHE
        start = time.time()
        b = go_fast(x)
        end = time.time()
        print("Elapsed (after compilation) = %s" % (end - start))
        print(a)
        print(b)
        quit()
        '''

        '''
        #shape = (512, 1024)
        shape = (2**13, 2**14)
        print(shape)

        ### Numpy and CPU
        s = time.time()
        x_cpu = np.ones(shape)
        e = time.time()
        print(e - s)
        ### CuPy and GPU
        s = time.time()
        x_gpu = cp.ones(shape)
        cp.cuda.Stream.null.synchronize()
        e = time.time()
        print(e - s)

        print('-------------------')
        ### Numpy and CPU
        s = time.time()
        x_cpu *= 5
        e = time.time()
        print(e - s)
        ### CuPy and GPU
        s = time.time()
        x_gpu *= 5
        cp.cuda.Stream.null.synchronize()
        e = time.time()
        print(e - s)

        print('-------------------')
        ### Numpy and CPU
        s = time.time()
        x_cpu *= 5
        x_cpu *= x_cpu
        x_cpu += x_cpu
        e = time.time()
        print(e - s)
        ### CuPy and GPU
        s = time.time()
        x_gpu *= 5
        x_gpu *= x_gpu
        x_gpu += x_gpu
        cp.cuda.Stream.null.synchronize()
        e = time.time()
        print(e - s)

        quit()
        '''

        matplotlibVisualization = False
        pyvistaVisualization = True
        profile = False
        NSimulationItterations = 500
        #waterVisibilityDepth = 3
        waterVisibilityDepth = 1
        sedimentVisibilityDepth = 1

        if pyvistaVisualization:
            X = np.arange(0, shape[1], 1)
            Y = np.arange(0, shape[0], 1)
            X, Y = np.meshgrid(X, Y)

            def CoordinatesToIndex(x, y):
                return x + y*shape[1]

            NPoints = shape[0]*shape[1]
            terrainPoints = np.zeros((NPoints, 3))
            terrainPoints[:, 0] = np.reshape(X, (NPoints, 1))[:, 0]
            terrainPoints[:, 1] = np.reshape(Y, (NPoints, 1))[:, 0]
            terrainPoints[:, 2] = np.reshape(self.heightMap[:, :, 0], (NPoints, 1))[:, 0]

            sedimentPoints = np.zeros((NPoints, 3))
            sedimentPoints[:, 0] = np.reshape(X, (NPoints, 1))[:, 0]
            sedimentPoints[:, 1] = np.reshape(Y, (NPoints, 1))[:, 0]
            sedimentPoints[:, 2] = np.reshape(np.sum(self.heightMap, axis = 2), (NPoints, 1))[:, 0]

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
            sedimentMesh = pv.PolyData(sedimentPoints, faces)
            waterMesh = pv.PolyData(waterPoints, faces)

            sedimentDepth = 0*np.reshape(self.heightMap[:, :, 1]/sedimentVisibilityDepth, (NPoints, 1))
            sedimentMapping = np.linspace(0, 1.0, 256)
            sedimentNewcolors = np.empty((256, 4))
            #sedimentNewcolors[sedimentMapping >= 1.0] = np.array([0.2, 0.5, 0.1, 1])
            #sedimentNewcolors[sedimentMapping < 1.0] = np.array([0.35, 0.3, 0.1, 1])
            #sedimentNewcolors[sedimentMapping < 0.2] = np.array([0.35, 0.3, 0.1, 1])
            sedimentNewcolors[sedimentMapping >= 1.0] = np.array([0.5, 0.4, 0.4, 1])
            sedimentNewcolors[sedimentMapping < 1.0] = np.array([0.5, 0.4, 0.4, 1])
            sedimentNewcolors[sedimentMapping < 0.2] = np.array([0.5, 0.4, 0.4, 1])
            sedimentColormap = ListedColormap(sedimentNewcolors)

            waterDepth = np.reshape(np.zeros((shape[0], shape[1])), (NPoints, 1))
            mapping = np.linspace(0, 1, 256)
            newcolors = np.empty((256, 4))
            newcolors[mapping >= 1] = np.array([0.1, 0.1, 0.3, 1])
            newcolors[mapping < 1.0] = np.array([0.1, 0.2, 0.4, 1])
            newcolors[mapping < 0.75] = np.array([0.1, 0.4, 0.6, 1])
            newcolors[mapping < 0.5] = np.array([0.05, 0.65, 0.8, 1])
            newcolors[mapping < 0.25] = np.array([0.05, 0.9, 1.0, 1])
            newcolors[mapping < 0.1] = np.array([1.0, 1.0, 1.0, 0])
            my_colormap = ListedColormap(newcolors)

            plotter = pv.Plotter()
            # , scalars = grid.points[:, -1]
            # opacity=1+waterPoints[:, -1]
            #plotter.add_mesh(terrainMesh, scalars = terrainPoints[:, -1], smooth_shading=True)
            plotter.add_mesh(terrainMesh, color = [0.3, 0.3, 0.35], smooth_shading=True)

            #plotter.add_mesh(sedimentMesh, scalars=sedimentDepth, cmap=sedimentColormap, smooth_shading=True)
            #plotter.add_mesh(sedimentMesh, scalars=sedimentDepth, cmap=sedimentColormap)
            plotter.add_mesh(sedimentMesh, color = [0.6, 0.5, 0.5], smooth_shading=True)
            #plotter.add_mesh(sedimentMesh, scalars=sedimentDepth)
            #plotter.add_mesh(sedimentMesh, color = [1, 0, 0], opacity=0.5)
            #plotter.add_mesh(sedimentMesh, color = [1, 0, 0], smooth_shading=True)

            #plotter.add_mesh(waterMesh, smooth_shading=True, color = [0.1, 0.3, 0.4], opacity=0.5, specular=1, specular_power=15)
            #plotter.add_mesh(waterMesh, scalars=waterDepth, smooth_shading=True, color=[0.1, 0.3, 0.4], opacity='sigmoid', specular=1)

            #plotter.add_mesh(waterMesh, scalars=waterDepth, cmap=my_colormap, specular=1, specular_power=10)
            plotter.add_mesh(waterMesh, scalars=waterDepth, cmap=my_colormap)

            #plotter.enable_3_lights()
            plotter.enable_eye_dome_lighting()
            #waterMesh = plotter.add_mesh(mesh = waterGrid, color=[0.1, 0.4, 0.8], smooth_shading=True, show_edges=False)
            plotter.enable_terrain_style()
            plotter.show(auto_close=False)

        '''
        from numba import int32, float32  # import the types

        spec = [
            ('value', int32),  # a simple scalar field
            ('array', float32[:]),  # an array field
        ]

        import numba
        @numba.jitclass(spec)
        class Bag(object):
            def __init__(self, value):
                self.value = value
                self.array = np.zeros(value, dtype=np.float32)

            @property
            def size(self):
                return self.array.size

            def increment(self, val):
                for i in range(self.size):
                    self.array[i] += val
                return self.array

        n = 21
        mybag = Bag(n)
        print(mybag)
        quit()
        '''
        #fig = pyplot.figure(figsize=(11, 7), dpi=100)
        #pyplot.quiver(X[::3, ::3], Y[::3, ::3], u[::3, ::3], v[::3, ::3]);

        #fig = pyplot.figure(figsize=(11, 7), dpi=100)
        #pyplot.quiver(X, Y, u, v);

        #self.heightMap[:, :, -1] += 10

        self.heightMap = self.heightMap[:, :, 0:2]

        Erosion.HydrolicErosion.InitializeRainDropTemplates(maximumRainDropRadius=20)
        Erosion.HydrolicErosion2.InitializeRainDropTemplates(maximumRainDropRadius=20)
        if True:
            self.hydrolicErosion = Erosion.HydrolicErosion(terrain = self.heightMap,
                                                            evaporationRate=0.1,
                                                            deltaT=0.1,
                                                            flowSpeed=3,
                                                            sedimentFlowSpeed=1,
                                                            gridLength=1,
                                                            carryCapacityLimit=2,
                                                            erosionRate=[0.05, 0.5],
                                                            depositionRate=0.1,
                                                            maximumErosionDepth=10)
            #self.hydrolicErosion = Erosion.HydrolicErosion2(terrain = self.heightMap,
            #                                                evaporationRate=0.1,
            #                                                deltaT=0.01,
            #                                                flowSpeed=1500,
            #                                                sedimentFlowSpeed=0.5,
            #                                                gridLength=1,
            #                                                carryCapacityCoefficient=0.0001,
            #                                                erosionRate=0.005,
            #                                                disolveRate = 5,
            #                                                depositionRate=0.1,
            #                                                maximumErosionDepth=0.5,
            #                                                bedrockHardness=20000)
            #self.hydrolicErosion = Erosion.HydrolicErosion(terrain = self.heightMap,
            #                                                evaporationRate=0.15,
            #                                                deltaT=0.02,
            #                                                flowSpeed=300,
            #                                                sedimentFlowSpeed=1,
            #                                                gridLength=1,
            #                                                carryCapacityLimit=1,
            #                                                erosionRate=[0.01, 0.1],
            #                                                depositionRate=0.1,
            #                                                maximumErosionDepth=10)
            self.thermalErosion = Erosion.ThermalErosion(terrain=self.heightMap,
                                                         maximumSlope=[90, 30],
                                                         flowSpeed=1,
                                                         deltaT=0.1)
        else:
            self.hydrolicErosion = Erosion.HydrolicErosionNumba(terrain = self.heightMap,
                                                                evaporationRate=0.1,
                                                                deltaT=0.1,
                                                                flowSpeed=3,
                                                                sedimentFlowSpeed=1,
                                                                gridLength=1,
                                                                carryCapacityLimit=4,
                                                                erosionRate=[0.05, 0.5],
                                                                depositionRate=0.1,
                                                                maximumErosionDepth=10)
            self.thermalErosion = Erosion.ThermalErosionNumba(terrain = self.heightMap,
                                                              NRows=np.size(self.heightMap, 0),
                                                              NColons=np.size(self.heightMap, 1),
                                                              NLayers=np.size(self.heightMap, 2),
                                                              maximumSlope=[90, 30],
                                                              flowSpeed=1,
                                                              deltaT=0.1,
                                                              gridLength=1)

        self.thermalWeathering = Erosion.ThermalWeathering(terrain=self.heightMap,
                                                           weatheringRate=[1, 1])

        #
        #         VISUALIZATION LIBRARIES
        # https: // github.com / BartheG / Orvisu
        # https: // github.com / OpenGeoVis / PVGeo
        #
        #          USEFUL PAPERS
        # https: // github.com / bshishov / UnityTerrainErosionGPU
        # https://old.cescg.org/CESCG-2011/papers/TUBudapest-Jako-Balazs.pdf
        # https://hal.inria.fr/inria-00402079/document
        # http: // www - cg.cis.iwate - u.ac.jp / lab / graphite06.pdf
        # https://matthias-research.github.io/pages/publications/SPHShallow.pdf
        # https://dl.acm.org/doi/pdf/10.1145/97880.97884
        #


        if profile:
            import cProfile, pstats, io
            from pstats import SortKey
            pr = cProfile.Profile()
            pr.enable()

        tic = time.time()
        for i in range(NSimulationItterations):
            print(i)

            if i>400:
                rainAmount = 0
            else:
                #if i%50 == 0:
                #    rainAmount = 1
                #else:
                #
                #    rainAmount = 0
                #if i%10 == 0:
                #    rainAmount = 0.1 * (1 + np.sin(np.pi*(i / 15))) / 2
                #else:
                #    rainAmount = 0
                #rainAmount = 0.01 * (1 + np.sin(i / 15)) / 2
                #rainAmount = 0.01 * (1 + np.sin(2*np.pi*(i / 40))) / 2
                rainAmount = 0.01 * (1 + np.sin(i / 15)) / 2
                #rainAmount = 0.02 * (1 + np.sin(i / 15)) / 2
                #self.hydrolicErosion.Rain(numberOfDrops=1, radius=3, dropSize=10000, application='drop')
            self.hydrolicErosion.Rain(numberOfDrops=1, radius=10, dropSize=rainAmount, application='even')
            self.hydrolicErosion()

            #self.hydrolicErosion.UpdateTotalTerrain()
            #self.hydrolicErosion.UpdateSlope()

            #self.hydrolicErosion.UpdateFlow()
            #self.hydrolicErosion.UpdateWaterHeight()
            #self.hydrolicErosion.Evaporation()
            #self.hydrolicErosion.UpdateVelocity()

            if True:
                if i < 400:
                    #self.thermalWeathering.Weather(0.002)
                    self.thermalWeathering.Weather(0.02)
                    #self.thermalWeathering.Weather(0.04)
                #if i%10 == 0:
                self.thermalErosion()


            if pyvistaVisualization:
                z = self.heightMap[:, :, 0].copy()
                terrainPoints[:, -1] = np.reshape(z, (NPoints, 1))[:, 0]

                z = np.sum(self.heightMap, axis=2)
                z -= 0.2
                sedimentPoints[:, -1] = np.reshape(z, (NPoints, 1))[:, 0]

                z = np.sum(self.heightMap, axis=2)+self.hydrolicErosion.water[:, :, 0].copy()
                waterPoints[:, -1] = np.reshape(z, (NPoints, 1))[:, 0]
                waterDepth = self.hydrolicErosion.water[:, :, 0].copy()
                waterDepth /= waterVisibilityDepth
                waterDepth[waterDepth > 1] = 1
                waterDepth = np.reshape(waterDepth, (NPoints, 1))

                plotter.update_coordinates(points=terrainPoints, mesh=terrainMesh)
                plotter.update_coordinates(points=sedimentPoints, mesh=sedimentMesh)
                #plotter.update_coordinates(points=waterPoints, mesh = waterMesh)

                #plotter.update_scalars(sedimentDepth[:, 0], mesh=sedimentMesh, render=False)
                #plotter.update_scalars(waterDepth[:, 0], mesh=waterMesh, render=False)

                terrainMesh.compute_normals(point_normals=True, inplace=True)
                sedimentMesh.compute_normals(point_normals=True, inplace=True)
                waterMesh.compute_normals(point_normals=True, inplace=True)
                plotter.render()
                #plt.imshow(self.heightMap[:, :, 1])
                #plt.pause(0.00001)

            if matplotlibVisualization:
                self.hydrolicErosion.Visualize()
                plt.pause(0.000001)
        if profile:
            pr.disable()
            s = io.StringIO()
            sortby = SortKey.CUMULATIVE
            ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
            ps.print_stats()
            print(s.getvalue())
            quit()

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