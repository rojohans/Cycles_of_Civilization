import pyvista as pv
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.colors import ListedColormap
import time

import Library.World as World
import Library.Erosion as Erosion

class Main():
    def __init__(self):
        shape = {'latitude':256, 'longitude':512}

        longitude = np.linspace(0, 2*np.pi*(1-1/shape['longitude']), shape['longitude'])
        latitude = np.linspace(-np.pi/2 + np.pi/(2*shape['latitude']),np.pi/2 - np.pi/(2*shape['latitude']), shape['latitude'])
        longitude, latitude = np.meshgrid(longitude, latitude)

        deltaLatitude = np.pi/shape['latitude']
        deltaLongitude = 2*np.pi/shape['longitude']

        radius = shape['latitude']/np.pi #The radius is chosen such that the latitudinal delta value is 1.

        latitudeScaled = radius * latitude
        longitudeScaled = radius * longitude

        deltaLatitudeScaled = radius * deltaLatitude
        deltaLongitudeScaled = radius * np.cos(latitude)*deltaLongitude

        x = np.cos(longitude) * np.cos(latitude)
        y = np.sin(longitude) * np.cos(latitude)
        z = np.sin(latitude)

        vertices = np.concatenate((np.reshape(x, (shape['longitude']*shape['latitude'], 1)),
                                   np.reshape(y, (shape['longitude']*shape['latitude'], 1)),
                                   np.reshape(z, (shape['longitude']*shape['latitude'], 1))), axis=1)

        oceanLevel = 0.4
        oceanFilter = World.SphericalWorld.PerlinNoise(vertices=vertices, octaves=6, persistence=0.4)

        oceanFilter -= oceanLevel
        oceanFilter[oceanFilter<0] = 0
        oceanFilter /= 1 - oceanLevel
        oceanFilter = np.sqrt(oceanFilter)

        initialElevation = radius + oceanFilter*(
                shape['latitude']/10*World.SphericalWorld.PerlinNoise(vertices=vertices, octaves=6, persistence=0.4)**3+
                shape['latitude']/15*World.SphericalWorld.PerlinNoise(vertices=vertices, octaves=6, persistence=0.6)**2+
                shape['latitude']/25*World.SphericalWorld.PerlinNoise(vertices=vertices, octaves=6, persistence=0.9)**2)
        initialElevation = np.reshape(initialElevation, (shape['latitude'], shape['longitude']))

        self.elevation = np.zeros((shape['latitude'], shape['longitude'], 2))
        self.elevation[:, :, 0] = initialElevation

        matplotlibVisualization = False
        pyvistaVisualization = True
        profile = False
        NSimulationItterations = 450
        # waterVisibilityDepth = 3
        waterVisibilityDepth = 1
        sedimentVisibilityDepth = 1

        if pyvistaVisualization:
            X = np.arange(0, shape['longitude'], 1)
            Y = np.arange(0, shape['latitude'], 1)
            X, Y = np.meshgrid(X, Y)

            def CoordinatesToIndex(x, y):
                return x + y * shape['longitude']

            NPoints = shape['latitude'] * shape['longitude']
            terrainPoints = np.zeros((NPoints, 3))
            terrainPoints[:, 0] = np.reshape(longitudeScaled, (NPoints, 1))[:, 0]
            terrainPoints[:, 1] = np.reshape(latitudeScaled, (NPoints, 1))[:, 0]
            terrainPoints[:, 2] = np.reshape(self.elevation[:, :, 0], (NPoints, 1))[:, 0]

            sedimentPoints = np.zeros((NPoints, 3))
            sedimentPoints[:, 0] = np.reshape(longitudeScaled, (NPoints, 1))[:, 0]
            sedimentPoints[:, 1] = np.reshape(latitudeScaled, (NPoints, 1))[:, 0]
            sedimentPoints[:, 2] = np.reshape(np.sum(self.elevation, axis=2), (NPoints, 1))[:, 0]

            waterPoints = np.zeros((NPoints, 3))
            waterPoints[:, 0] = np.reshape(longitudeScaled, (NPoints, 1))[:, 0]
            waterPoints[:, 1] = np.reshape(latitudeScaled, (NPoints, 1))[:, 0]
            waterPoints[:, 2] = np.reshape(np.zeros((shape['latitude'], shape['longitude'])), (NPoints, 1))[:, 0]

            faces = []
            for x in range(shape['longitude'] - 1):
                for y in range(shape['latitude'] - 1):
                    faces.append(
                        [4, CoordinatesToIndex(x, y), CoordinatesToIndex(x + 1, y), CoordinatesToIndex(x + 1, y + 1),
                         CoordinatesToIndex(x, y + 1)])
            faces = np.hstack(faces)

            if False:
                h = radius + np.reshape(initialElevation, (NPoints, 1))
                vertices[:, 0] *= h[:, 0]
                vertices[:, 1] *= h[:, 0]
                vertices[:, 2] *= h[:, 0]

                terrainMesh = pv.PolyData(vertices, faces)
                sedimentMesh = pv.PolyData(vertices, faces)
                waterMesh = pv.PolyData(vertices, faces)
            else:
                terrainMesh = pv.PolyData(terrainPoints, faces)
                sedimentMesh = pv.PolyData(sedimentPoints, faces)
                waterMesh = pv.PolyData(waterPoints, faces)

            waterDepth = np.reshape(np.zeros((shape['latitude'], shape['longitude'])), (NPoints, 1))
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
            plotter.add_mesh(terrainMesh, color=[0.3, 0.3, 0.35], smooth_shading=True)
            plotter.add_mesh(sedimentMesh, color=[0.6, 0.5, 0.5], smooth_shading=True)
            plotter.add_mesh(waterMesh, scalars=waterDepth, cmap=my_colormap)

            plotter.enable_eye_dome_lighting()
            plotter.enable_terrain_style()
            plotter.show(auto_close=False)

            #deltaLatitudeScaled /= deltaLatitudeScaled
            #deltaLongitudeScaled /= deltaLongitudeScaled

            #self.elevation *= 0

            print('Amount of material before simulation: ', np.sum(np.sum(np.sum(self.elevation))))

            Erosion.HydrolicErosion.InitializeRainDropTemplates(maximumRainDropRadius=20)
            Erosion.HydrolicErosionScaled.InitializeRainDropTemplates(maximumRainDropRadius=20)
            self.hydrolicErosion = Erosion.HydrolicErosionScaled(terrain=self.elevation,
                                                           evaporationRate=0.02,
                                                           deltaT=0.1,
                                                           flowSpeed=1,
                                                           sedimentFlowSpeed=1,
                                                           gridLength=1,
                                                           carryCapacityLimit=3.5,
                                                           erosionRate=[0.5, 0.5],
                                                           depositionRate=0.1,
                                                           maximumErosionDepth=10,
                                                                 deltaLatitude=deltaLatitudeScaled,
                                                                 deltaLongitude=deltaLongitudeScaled)
            self.thermalErosion = Erosion.ThermalErosionScaled(terrain=self.elevation,
                                                         maximumSlope=[30, 30],
                                                         flowSpeed=1,
                                                         deltaT=0.1,
                                                               deltaLatitude=deltaLatitudeScaled,
                                                               deltaLongitude=deltaLongitudeScaled)

            self.thermalWeathering = Erosion.ThermalWeatheringScaled(terrain=self.elevation,
                                                               weatheringRate=[1, 1],
                                                                     deltaLatitude=deltaLatitudeScaled,
                                                                     deltaLongitude=deltaLongitudeScaled)

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

                if i > 400:
                    rainAmount = 0
                else:
                    # if i%50 == 0:
                    #    rainAmount = 1
                    # else:
                    #
                    #    rainAmount = 0
                    # if i%10 == 0:
                    #    rainAmount = 0.1 * (1 + np.sin(np.pi*(i / 15))) / 2
                    # else:
                    #    rainAmount = 0
                    # rainAmount = 0.01 * (1 + np.sin(i / 15)) / 2
                    rainAmount = 0.005 * (1 + np.sin(2*np.pi*(i / 40))) / 2
                    #rainAmount = 0.01 * (1 + np.sin(i / 15)) / 2
                    # rainAmount = 0.02 * (1 + np.sin(i / 15)) / 2
                    # self.hydrolicErosion.Rain(numberOfDrops=1, radius=3, dropSize=10000, application='drop')
                #self.hydrolicErosion.Rain(numberOfDrops=1, radius=3, dropSize=10000, application='drop')
                #self.hydrolicErosion.Rain(numberOfDrops=1, radius=3, dropSize=1000, application='drop')
                #    self.hydrolicErosion.Rain(numberOfDrops=1, radius=10, dropSize=rainAmount, application='even')
                #self.hydrolicErosion.Rain(numberOfDrops=1, radius=10, rainMap=2*rainAmount * np.random.rand(shape['latitude'], shape['longitude']), application='map')
                #    self.hydrolicErosion()

                #self.hydrolicErosion.UpdateFlow()
                #self.hydrolicErosion.UpdateWaterHeight()
                #self.hydrolicErosion.Evaporation()

                if True:
                    if i < 400:
                        # self.thermalWeathering.Weather(0.002)
                        self.thermalWeathering.Weather(0.02)
                        # self.thermalWeathering.Weather(0.04)
                    # if i%10 == 0:
                    self.thermalErosion()

                if pyvistaVisualization:
                    z = self.elevation[:, :, 0].copy()
                    terrainPoints[:, -1] = np.reshape(z, (NPoints, 1))[:, 0]

                    z = np.sum(self.elevation, axis=2)
                    z -= 0.2
                    sedimentPoints[:, -1] = np.reshape(z, (NPoints, 1))[:, 0]

                    z = np.sum(self.elevation, axis=2) + self.hydrolicErosion.water[:, :, 0].copy()
                    waterPoints[:, -1] = np.reshape(z, (NPoints, 1))[:, 0]
                    waterDepth = self.hydrolicErosion.water[:, :, 0].copy()
                    waterDepth /= waterVisibilityDepth
                    waterDepth[waterDepth > 1] = 1
                    waterDepth = np.reshape(waterDepth, (NPoints, 1))

                    plotter.update_coordinates(points=terrainPoints, mesh=terrainMesh)
                    plotter.update_coordinates(points=sedimentPoints, mesh=sedimentMesh)
                    plotter.update_coordinates(points=waterPoints, mesh=waterMesh)

                    # plotter.update_scalars(sedimentDepth[:, 0], mesh=sedimentMesh, render=False)
                    plotter.update_scalars(waterDepth[:, 0], mesh=waterMesh, render=False)

                    terrainMesh.compute_normals(point_normals=True, inplace=True)
                    sedimentMesh.compute_normals(point_normals=True, inplace=True)
                    waterMesh.compute_normals(point_normals=True, inplace=True)
                    plotter.render()
                    # plt.imshow(self.heightMap[:, :, 1])
                    # plt.pause(0.00001)

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

            print('Amount of material after simulation: ', np.sum(np.sum(np.sum(self.elevation))) + np.sum(
                np.sum(self.hydrolicErosion.suspendedSediment[:, :, 0])))
            toc = time.time()
            print('Total erosion time: ', toc - tic)


            # ---------------------------------------------------------------------------------------------------------
            # Save topography to file.
            world = World.SphericalWorld()

            from scipy import interpolate

            elevationTotal = np.reshape(np.sum(self.elevation, axis=2), (shape['latitude'] * shape['longitude'], 1))

            interpolator = interpolate.NearestNDInterpolator(vertices, elevationTotal)

            v = world.v.copy()
            v[:, 0] /= world.vertexRadius
            v[:, 1] /= world.vertexRadius
            v[:, 2] /= world.vertexRadius

            a = interpolator(v)

            v[:, 0] *= a[:, 0]
            v[:, 1] *= a[:, 0]
            v[:, 2] *= a[:, 0]

            world.v = v
            world.vertexRadius = world.CalculateVertexRadius(world.v)
            world.faceRadius = world.CalculateFaceRadius(world.v, world.f)

            import pickle
            import Root_Directory
            pickle.dump(world, open(Root_Directory.Path() + '/Data/tmp_Data/worldRock.pkl', "wb"))

            # Save water to file.
            world = World.SphericalWorld()


            elevationTotal += np.reshape(self.hydrolicErosion.water[:, :, 0], (shape['latitude'] * shape['longitude'], 1))-0.1

            interpolator = interpolate.NearestNDInterpolator(vertices, elevationTotal)

            v = world.v.copy()
            v[:, 0] /= world.vertexRadius
            v[:, 1] /= world.vertexRadius
            v[:, 2] /= world.vertexRadius

            a = interpolator(v)

            v[:, 0] *= a[:, 0]
            v[:, 1] *= a[:, 0]
            v[:, 2] *= a[:, 0]

            world.v = v
            world.vertexRadius = world.CalculateVertexRadius(world.v)
            world.faceRadius = world.CalculateFaceRadius(world.v, world.f)

            pickle.dump(world, open(Root_Directory.Path() + '/Data/tmp_Data/worldWater.pkl', "wb"))
            # ---------------------------------------------------------------------------------------------------------

            if pyvistaVisualization:
                plotter.show(auto_close=False)

                elevationRock = np.reshape(self.elevation[:, :, 0], (shape['latitude'] * shape['longitude'], 1))
                elevationTotal = np.reshape(np.sum(self.elevation, axis = 2), (shape['latitude']*shape['longitude'], 1))
                water = np.reshape(self.hydrolicErosion.water[:, :, 0], (shape['latitude']*shape['longitude'], 1))

                rockVertices = vertices.copy()
                sedimentVertices = vertices.copy()
                waterVertices = vertices.copy()

                rockVertices[:, 0:1] *= elevationRock
                rockVertices[:, 1:2] *= elevationRock
                rockVertices[:, 2:3] *= elevationRock

                sedimentVertices[:, 0:1] *= elevationTotal - 0.2
                sedimentVertices[:, 1:2] *= elevationTotal - 0.2
                sedimentVertices[:, 2:3] *= elevationTotal - 0.2

                waterVertices[:, 0:1] *= water+elevationTotal
                waterVertices[:, 1:2] *= water+elevationTotal
                waterVertices[:, 2:3] *= water+elevationTotal

                waterDepth = self.hydrolicErosion.water[:, :, 0].copy()
                waterDepth /= waterVisibilityDepth
                waterDepth[waterDepth > 1] = 1
                waterDepth = np.reshape(waterDepth, (NPoints, 1))

                globeRockMesh = pv.PolyData(rockVertices, np.hstack(faces))
                globeSedimentMesh = pv.PolyData(sedimentVertices, np.hstack(faces))
                globeWaterMesh = pv.PolyData(waterVertices, np.hstack(faces))

                plotter = pv.Plotter()
                plotter.add_mesh(globeRockMesh, color=[0.3, 0.3, 0.35], smooth_shading=True)
                plotter.add_mesh(globeSedimentMesh, color=[0.6, 0.5, 0.5], smooth_shading=True)
                plotter.add_mesh(globeWaterMesh, scalars=waterDepth, cmap=my_colormap)

                plotter.enable_eye_dome_lighting()
                plotter.show(auto_close=False)


            if matplotlibVisualization:
                plt.show()







Main()
