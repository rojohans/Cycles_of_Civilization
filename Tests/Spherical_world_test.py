from direct.showbase.ShowBase import ShowBase
import panda3d.core as p3d
from direct.gui.DirectGui import *
from panda3d.core import TransparencyAttrib
from matplotlib import image
import numpy as np
import scipy as sp
import time

import Library.TileClass as TileClass
import Library.Light as Light
import Library.Camera as Camera
import Library.World as World
import Library.Pathfinding as Pathfinding
import Library.Animation as Animation
import Library.Ecosystem as Ecosystem
import Library.Texture as Texture
import Library.Feature as Feature

import Data.Dictionaries.FeatureTemplateDictionary as FeatureTemplateDictionary
import Data.Templates.Vegetation_Templates as Vegetation_Templates
import Data.Templates.Animal_Templates as Animal_Templates
import pickle

import Settings
import Root_Directory

class Game(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        #p3d.PStatClient.connect()
        base.setFrameRateMeter(True)
        base.setBackgroundColor(0.1, 0.1, 0.15)

        self.settings = Settings.GlobeSettings()

        fileToOpen = '11' # 11: ca 50 000,     12: ca 200 000

        self.closeTexture = Texture.Texture({'water': image.imread(Root_Directory.Path() + "/Data/Tile_Data/water_2.png"),
                                     'shallow_water': image.imread(Root_Directory.Path() + "/Data/Tile_Data/water_shallow.png"),
                                     'grass': image.imread(Root_Directory.Path() + "/Data/Tile_Data/soil_fertility_2.png"),
                                     'forest': image.imread(Root_Directory.Path() + "/Data/Tile_Data/forest_floor_terrain.png"),
                                     'rock': image.imread(Root_Directory.Path() + "/Data/Tile_Data/rock_terrain.png"),
                                     'tundra': image.imread(Root_Directory.Path() + "/Data/Tile_Data/tundra.png"),
                                     'snow': image.imread(Root_Directory.Path() + "/Data/Tile_Data/snow_terrain.png"),
                                             'farm_field': image.imread(Root_Directory.Path() + "/Data/Tile_Data/farm_field_terrain_2.png"),
                                             'road': image.imread(Root_Directory.Path() + "/Data/Tile_Data/road_terrain.png"),
                                             'stone_road': image.imread(Root_Directory.Path() + "/Data/Tile_Data/cobble_stone_road_terrain.png"),
                                             'tuber_farm_field': image.imread(Root_Directory.Path() + "/Data/Tile_Data/farm_field_terrain_3.png")})
        self.farTexture = Texture.Texture({'water': image.imread(Root_Directory.Path() + "/Data/Tile_Data/water_2.png"),
                                     'shallow_water': image.imread(Root_Directory.Path() + "/Data/Tile_Data/water_shallow.png"),
                                     'grass': image.imread(Root_Directory.Path() + "/Data/Tile_Data/soil_fertility_2.png"),
                                     'forest': image.imread(Root_Directory.Path() + "/Data/Tile_Data/forest_canopy_terrain.png"),
                                     'rock': image.imread(Root_Directory.Path() + "/Data/Tile_Data/rock_terrain.png"),
                                     'tundra': image.imread(Root_Directory.Path() + "/Data/Tile_Data/tundra.png"),
                                     'snow': image.imread(Root_Directory.Path() + "/Data/Tile_Data/snow_terrain.png"),
                                           'farm_field': image.imread(Root_Directory.Path() + "/Data/Tile_Data/farm_field_terrain_2.png"),
                                           'road': image.imread(Root_Directory.Path() + "/Data/Tile_Data/road_terrain.png"),
                                           'stone_road': image.imread(Root_Directory.Path() + "/Data/Tile_Data/cobble_stone_road_terrain.png"),
                                           'tuber_farm_field': image.imread(Root_Directory.Path() + "/Data/Tile_Data/farm_field_terrain_3.png")})
        #self.lightObject = Light.LightClass(shadowsEnabled=False)
        self.sunLight = Light.Sun(shadowsEnabled=False)
        self.cameraLight = Light.CameraLight()
        if False:
            world = World.SphericalWorld()
        else:
            world = pickle.load(open(Root_Directory.Path() + '/Data/tmp_Data/worldRock_' + fileToOpen + '.pkl', "rb"))
            world.nTriangles = np.size(world.f, 0)
            self.world = world
            #world = pickle.load(open(Root_Directory.Path() + '/Data/tmp_Data/worldRock.pkl', "rb"))
            '''
            world.v[:, 0] /= world.vertexRadius
            world.v[:, 1] /= world.vertexRadius
            world.v[:, 2] /= world.vertexRadius
            world.vertexRadius = world.Smooth(world.v, world.f, world.vertexRadius, world.faceRadius)
            world.v[:, 0] *= world.vertexRadius
            world.v[:, 1] *= world.vertexRadius
            world.v[:, 2] *= world.vertexRadius
            '''
            world.minRadius = np.min(world.faceRadius)

        self.world.faceCoordinates[:, 0] = self.world.unscaledFaceCoordinates[:, 0]*self.world.faceRadius
        self.world.faceCoordinates[:, 1] = self.world.unscaledFaceCoordinates[:, 1]*self.world.faceRadius
        self.world.faceCoordinates[:, 2] = self.world.unscaledFaceCoordinates[:, 2]*self.world.faceRadius

        self.world.faceConnections = self.world.CalculateFaceConnections(self.world.faceCoordinates)

        self.terrainAngles = np.zeros((self.world.nTriangles, 1))

        print('# faces : ', np.size(world.f, 0))

        world.faceNormals = world.CalculateFaceNormals(world.v, world.f)
        world.faceTemperature = world.CalculateFaceTemperature(world.v, world.f, world.faceRadius)

        self.farDistance = 3 * self.world.minRadius

        if False:
            worldWater = World.SphericalWorld()
        else:
            worldWater = pickle.load(open(Root_Directory.Path() + '/Data/tmp_Data/worldWater_' + fileToOpen +'.pkl', "rb"))
            #worldWater = pickle.load(open(Root_Directory.Path() + '/Data/tmp_Data/worldWater.pkl', "rb"))
            worldWater.minRadius = np.min(worldWater.faceRadius)
        self.waterWorld = worldWater

        worldWater.faceNormals = worldWater.CalculateFaceNormals(worldWater.v, worldWater.f)
        waterHeight = worldWater.faceRadius - world.faceRadius

        self.temperature = world.faceTemperature.copy()
        h = self.world.faceRadius - self.waterWorld.minRadius
        w = self.waterWorld.faceRadius - self.waterWorld.minRadius
        self.elevation = h.copy()
        self.elevation[w > h] = w[w > h]

        self.terrainAngles = np.zeros((np.size(world.f, 0), 1))
        for iFace in range(np.size(world.f, 0)):
            vertices = world.v[world.f[iFace, 1:]]

            normal = world.faceNormals[iFace, :]
            normal /= np.sqrt(normal[0]**2 + normal[1]**2 + normal[2]**2)

            vertices = np.sum(vertices, axis=0) / 3
            vertices /= np.sqrt(vertices[0] ** 2 + vertices[1] ** 2 + vertices[2] ** 2)

            self.terrainAngles[iFace] = 180 / np.pi * np.arccos(
            (vertices[0] * normal[0] + vertices[1] * normal[1] + vertices[2] * normal[2]))


        self.worldProperties = World.WorldProperties(mainProgram=self, temperature=self.temperature, elevation=self.elevation, slope = self.terrainAngles)
        self.worldProperties.DetermineWater()

        #-------------------------------------------------------------






        self.featureInteractivity = Feature.FeatureInteractivity(mainProgram=self)


        import Library.Collision_Detection as Collision_Detection
        self.tilePicker = Collision_Detection.TilePicker(mainProgram=self)
        self.selectedTile = None

        import Library.Industry as Industry
        Industry.Building.Initialize(mainProgram=self)
        self.featureTemplate = FeatureTemplateDictionary.GetFeatureTemplateDictionaryGlobe(mainProgram=self)

        import Library.Resources as Resources
        self.resources = Resources.Resources(mainProgram=self,
                                             resources=['labor', 'spent_labor', 'grain', 'wood', 'tuber', 'flour', 'bread', 'stone', 'iron ore', 'coal', 'steel', 'tools'])

        import Library.GUI as GUI
        self.interface = GUI.Interface(base=base, mainProgram=self)

        self.featureList = [[] for i in range(self.world.nTriangles)]
        self.buildingList = [None for i in range(self.world.nTriangles)]


        import Library.Transport as Transport
        self.transport = Transport.Transport(mainProgram=self, resources=['labor', 'spent_labor', 'grain', 'wood', 'tuber', 'flour', 'bread', 'stone', 'iron ore', 'coal', 'steel', 'tools'])
        self.movementGraph = Transport.MovementGraph(mainProgram=self)
        self.movementGraph.RecalculateGraph()

        tic = time.time()
        self.InitializeForest(farDistance = self.farDistance)
        toc = time.time()
        print('Initialize forest: ', toc-tic)

        import Library.Graphics as Graphics
        tic = time.time()
        self.planet = Graphics.WorldMesh(mainProgram = self, vertices = world.v, faces = world.f,
                                         faceNormals = world.faceNormals, type = 'land')
        toc = time.time()
        print('Initialize planet: ', toc - tic)

        tic = time.time()
        self.water = Graphics.WorldMesh(mainProgram=self, vertices=worldWater.v, faces=worldWater.f,
                                        faceNormals=worldWater.faceNormals, type='water', waterHeight=waterHeight)
        toc = time.time()
        print('Initialize water: ', toc - tic)


        self.sunAngle = 0
        self.sunOrbitTime = 100
        self.add_task(self.RotateSun, 'sunRotation')

        self.camera = Camera.GlobeCamera(mainProgram=self,
                                         zoomRange = [1.1*world.minRadius, 7*world.minRadius],
                                         zoomSpeed=0.03,
                                         minRadius = world.minRadius,
                                         rotationSpeedRange=[np.pi/1000, np.pi/120])

        self.turn = 0

    def Turn(self, status):
        if status == 1:
            ticTurn = time.time()
            self.interface.buttons['end_turn'].node["indicatorValue"] = 1
            self.interface.buttons['end_turn'].node.setIndicatorValue()
            base.graphicsEngine.renderFrame()
            base.graphicsEngine.renderFrame()

            if self.movementGraph.upToDate == False:
                tic = time.time()
                self.movementGraph.RecalculateGraph()
                for building in self.buildingList:
                    if building != None:
                        building.tilesInRange = None
                toc = time.time()
                print('Movement graph calculation time : ', toc - tic)

            tic = time.time()
            # The buildings process their input into output. Households grow/starve.
            for building in self.buildingList:
                if building != None:
                    building()
            toc = time.time()
            print('Building operation time : ', toc-tic)

            tic = time.time()
            # Resources are moved.
            profile = False
            if profile:
                import cProfile, pstats, io
                from pstats import SortKey
                pr = cProfile.Profile()
                pr.enable()

            self.transport()

            if profile:
                pr.disable()
                s = io.StringIO()
                sortby = SortKey.CUMULATIVE
                ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
                ps.print_stats()
                print(s.getvalue())
                #quit()
            toc = time.time()
            print('Transport time : ', toc - tic)

            tic = time.time()
            self.resources()
            toc = time.time()
            print('Resource operation time : ', toc-tic)

            self.interface.buttons['end_turn'].node["indicatorValue"] = 0
            self.interface.buttons['end_turn'].node.setIndicatorValue()

            self.turn += 1
            self.interface.labels['end_turn'].node.setText('TURN : ' + str(self.turn))

            # Update the GUI text.
            if self.selectedTile != None:
                tileInformationText = ""
                tileInformationText += 'ID : ' + str(self.selectedTile) + '\n'
                tileInformationText += 'Elevation : ' + "{:.3f}".format(self.elevation[self.selectedTile]) + '\n'
                tileInformationText += 'Temperature : ' + "{:.3f}".format(self.temperature[self.selectedTile, 0]) + '\n'
                tileInformationText += 'Slope : ' + "{:.3f}".format(self.worldProperties.slope[self.selectedTile, 0]) + '\n'
                for i, feature in enumerate(self.featureList[self.selectedTile]):
                    if i == 0:
                        tileInformationText += 'Features : '
                    else:
                        tileInformationText += '         : '
                    tileInformationText += feature.template.GUILabel + '\n'

                if self.buildingList[self.selectedTile] != None:
                    #tileInformationText += str(self.buildingList[self.selectedTile])

                    featureInformationText = ''
                    featureInformationText += self.featureList[self.selectedTile][0].template.GUILabel + '\n'
                    featureInformationText += self.buildingList[
                        self.selectedTile].GetDetailedText()
                    self.interface.labels['featureInformation'].node.setText(featureInformationText)
                self.interface.labels['tileInformation'].node.setText(tileInformationText)


            self.interface.featureInformation.VisualizeBuildingLinks(self.interface.buttons['buildingLinks'].node["indicatorValue"])


            base.graphicsEngine.renderFrame()
            tocTurn = time.time()
            print('TURN TIME : ', tocTurn-ticTurn)
            print(' ')


    def RotateSun(self, Task):
        dt = globalClock.get_dt()
        self.sunAngle += dt%self.sunOrbitTime
        sunx = 5*self.world.minRadius*np.cos(-2 * np.pi * self.sunAngle / self.sunOrbitTime)
        suny = 5*self.world.minRadius*np.sin(-2 * np.pi * self.sunAngle / self.sunOrbitTime)
        #self.sunLight.light.setDirection(p3d.LVector3(sunx, suny, 0))
        self.sunLight.SetPosition(sunx, suny, 0)
        #self.sunLight.sun.setPos(sunx, suny, 0)
        return Task.cont

    def InitializeForest(self, farDistance):

        forestPerlin = World.SphericalWorld.PerlinNoise(self.world.unscaledFaceCoordinates, octaves=6,persistence=1.1)
        isForestList = []
        for iFace in range(self.world.nTriangles):
            isForest = False
            if self.world.faceRadius[iFace] > self.waterWorld.faceRadius[iFace]:
                if self.worldProperties.slope[iFace] <= 30 and self.worldProperties.temperature[iFace, 0] >= 0.4:
                    if forestPerlin[iFace] < self.settings.forestPerlinThreshold:
                        isForest = True
            isForestList.append(isForest)


        self.nodeWorld = World.SphericalWorld(nDivisions=8)
        self.nForestNodes = np.size(self.nodeWorld.v, axis=0)
        self.nodeWorld.v = self.nodeWorld.unscaledVertices * self.world.minRadius

        self.featureRoot = render.attachNewNode("featureRoot")
        self.forestRoot = self.featureRoot.attachNewNode("forestRoot")

        self.featureBackupRoot = render.attachNewNode("featureBackupRoot")
        self.featureBackupRoot .hide()

        self.featureNodeClusters = []
        for iNode in range(self.nForestNodes):
            nodePos = self.nodeWorld.v[iNode, :]
            self.featureNodeClusters.append(Feature.FeatureCluster(parent=self.forestRoot, position=nodePos, renderDistance=farDistance))

        kdTree = sp.spatial.cKDTree(self.nodeWorld.v)

        r, self.clusterBelonging = kdTree.query(self.world.faceCoordinates)

        for iNode, featureID in enumerate(self.clusterBelonging):
            self.featureNodeClusters[featureID].childrenTiles.append(iNode)

        for iFace in range(self.world.nTriangles):





            if False:
                # Initializes some basic buildings (towns and farms).
                if np.random.rand() < 0.9 and self.worldProperties.isWater[iFace] == False:
                    theta = 180 * np.arctan(self.world.faceCoordinates[iFace, 2] / np.sqrt(
                        self.world.faceCoordinates[iFace, 0] ** 2 + self.world.faceCoordinates[iFace, 1] ** 2)) / np.pi
                    phi = 180 * np.arctan(self.world.faceCoordinates[iFace, 1] / self.world.faceCoordinates[iFace, 0]) / np.pi
                    if self.world.faceCoordinates[iFace, 0] > 0:
                        phi += 180

                    iNode = self.clusterBelonging[iFace]

                    r = np.random.rand()
                    if r < 0.2:
                        featureKey = 'town'
                    elif r < 0.3:
                        featureKey = 'farm'
                    elif r < 0.4:
                        featureKey = 'bakery'
                    elif r < 0.5:
                        featureKey = 'windmill'
                    elif r < 0.6:
                        featureKey = 'lumbermill'
                    elif r < 0.7:
                        featureKey = 'storage_hall'
                    else:
                        featureKey = 'stone_road'


                    self.featureList[iFace] \
                        .append(Feature.TileFeature(parent=self.featureNodeClusters[iNode],
                                            backupRoot=self.featureBackupRoot,
                                            positionOffset=-self.featureNodeClusters[iNode].position,
                                            rotation=[90 + phi, theta, 0],
                                            triangleCorners=self.world.v[
                                                self.world.f[iFace, 1:]],
                                            featureTemplate=self.featureTemplate[featureKey],
                                            iTile=iFace))

                    if self.featureTemplate[featureKey].buildingTemplate != None:
                        newBuilding = self.featureTemplate[featureKey].buildingTemplate(iFace)
                        self.buildingList[iFace] = newBuilding
                        for resource in newBuilding.inputBuffert.type:
                            self.transport.buildingsInput[resource][iFace] = newBuilding
                self.movementGraph.upToDate = False





            if isForestList[iFace]:
                theta = 180*np.arctan(self.world.faceCoordinates[iFace, 2] / np.sqrt(self.world.faceCoordinates[iFace, 0]**2 + self.world.faceCoordinates[iFace, 1]**2))/np.pi
                phi = 180*np.arctan(self.world.faceCoordinates[iFace, 1]/self.world.faceCoordinates[iFace, 0])/np.pi
                if self.world.faceCoordinates[iFace, 0] > 0:
                    phi += 180

                iNode = self.clusterBelonging[iFace]


                temperature = self.world.faceTemperature[iFace, 0]
                if temperature < 0.8:
                    featureTemplate = self.featureTemplate['pine_forest']
                elif temperature < 1.2:
                    featureTemplate = self.featureTemplate['temperate_forest']
                    #featureTemplate = self.featureTemplate['town']
                else:
                    featureTemplate = self.featureTemplate['jungle']
                    #featureTemplate = self.featureTemplate['conifer_forest']



                self.featureList[iFace].append(Feature.TileFeature(parent=self.featureNodeClusters[iNode],
                                                                   backupRoot=self.featureBackupRoot,
                                                                   positionOffset=-self.featureNodeClusters[iNode].position,
                                                                   rotation=[90+phi, theta, 0],
                                                                   triangleCorners=self.world.v[self.world.f[iFace, 1:]],
                                                                   featureTemplate = featureTemplate,
                                                                   iTile = iFace))

        for iFace in range(self.world.nTriangles):
            for feature in self.featureList[iFace]:
                feature.AttachToParent()
        for iNode in range(self.nForestNodes):
            self.featureNodeClusters[iNode].node.clearModelNodes()
            self.featureNodeClusters[iNode].node.flattenStrong()
            self.featureNodeClusters[iNode].node.reparentTo(self.featureNodeClusters[iNode].LODNodePath)

        n = 0
        for building in self.buildingList:
            if building != None:
                n += 1
        print('#buildings : ', n)
        #render.analyze()

game = Game()
game.run()

