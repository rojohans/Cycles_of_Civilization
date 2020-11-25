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

import Data.Dictionaries.FeatureTemplateDictionary as FeatureTemplateDictionary
import Data.Templates.Vegetation_Templates as Vegetation_Templates
import Data.Templates.Animal_Templates as Animal_Templates
import pickle

import Settings
import Root_Directory

class Game(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        p3d.PStatClient.connect()
        base.setFrameRateMeter(True)
        base.setBackgroundColor(0.1, 0.1, 0.15)

        self.settings = Settings.GlobeSettings()

        fileToOpen = '11'

        self.closeTexture = Texture.Texture({'water': image.imread(Root_Directory.Path() + "/Data/Tile_Data/water_2.png"),
                                     'shallow_water': image.imread(Root_Directory.Path() + "/Data/Tile_Data/water_shallow.png"),
                                     'grass': image.imread(Root_Directory.Path() + "/Data/Tile_Data/soil_fertility_2.png"),
                                     'forest': image.imread(Root_Directory.Path() + "/Data/Tile_Data/forest_floor_terrain.png"),
                                     'rock': image.imread(Root_Directory.Path() + "/Data/Tile_Data/rock_terrain.png"),
                                     'tundra': image.imread(Root_Directory.Path() + "/Data/Tile_Data/tundra.png"),
                                     'snow': image.imread(Root_Directory.Path() + "/Data/Tile_Data/snow_terrain.png")})
        self.farTexture = Texture.Texture({'water': image.imread(Root_Directory.Path() + "/Data/Tile_Data/water_2.png"),
                                     'shallow_water': image.imread(Root_Directory.Path() + "/Data/Tile_Data/water_shallow.png"),
                                     'grass': image.imread(Root_Directory.Path() + "/Data/Tile_Data/soil_fertility_2.png"),
                                     'forest': image.imread(Root_Directory.Path() + "/Data/Tile_Data/forest_canopy_terrain.png"),
                                     'rock': image.imread(Root_Directory.Path() + "/Data/Tile_Data/rock_terrain.png"),
                                     'tundra': image.imread(Root_Directory.Path() + "/Data/Tile_Data/tundra.png"),
                                     'snow': image.imread(Root_Directory.Path() + "/Data/Tile_Data/snow_terrain.png")})
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

        forestPerlin = World.SphericalWorld.PerlinNoise(self.world.unscaledFaceCoordinates, octaves=6, persistence=1.1)
        self.isForest = [] # Determines which tiles got forests
        self.temperature = world.faceTemperature.copy()

        h = self.world.faceRadius - self.waterWorld.minRadius
        w = self.waterWorld.faceRadius - self.waterWorld.minRadius
        self.elevation = h.copy()
        self.elevation[w > h] = w[w > h]


        # getV3n3c4t2() : vertices3, normals3, colours4, textureCoordinates2
        # v3n3t2 : vertices3, normals3, textureCoordinates2
        #vertex_format = p3d.GeomVertexFormat.get_v3n3t2()
        vertex_format = p3d.GeomVertexFormat.getV3n3c4t2()

        # vertex_format = p3d.GeomVertexFormat.get_v3t2()
        self.planet_vertex_data = p3d.GeomVertexData("triangle_data", vertex_format, p3d.Geom.UH_static)

        pos_writer = p3d.GeomVertexWriter(self.planet_vertex_data, "vertex")
        normal_writer = p3d.GeomVertexWriter(self.planet_vertex_data, "normal")
        colour_writer = p3d.GeomVertexWriter(self.planet_vertex_data, 'color')
        tex_writer = p3d.GeomVertexWriter(self.planet_vertex_data, 'texcoord')

        for iFace in range(np.size(world.f, 0)):
            vertices = world.v[world.f[iFace, 1:]]
            pos_writer.add_data3(vertices[0, 0], vertices[0, 1], vertices[0, 2])
            pos_writer.add_data3(vertices[1, 0], vertices[1, 1], vertices[1, 2])
            pos_writer.add_data3(vertices[2, 0], vertices[2, 1], vertices[2, 2])

            colour_writer.add_data4(1, 1, 1, 1)
            colour_writer.add_data4(1, 1, 1, 1)
            colour_writer.add_data4(1, 1, 1, 1)

            #vertices /= np.sqrt(vertices[0]**2 + vertices[1]**2 + vertices[2]**2)
            normal = world.faceNormals[iFace, :]
            normal /= np.sqrt(normal[0]**2 + normal[1]**2 + normal[2]**2)



            vertices = np.sum(vertices, axis=0) / 3
            vertices /= np.sqrt(vertices[0] ** 2 + vertices[1] ** 2 + vertices[2] ** 2)

            #print(normal)
            #print(vertices)

            #print(np.sqrt(vertices[0]**2 + vertices[1]**2 + vertices[2]**2))
            #print(np.sqrt(normal[0]**2 + normal[1]**2 + normal[2]**2))
            #print('  ')

            self.terrainAngles[iFace] = 180/np.pi*np.arccos( (vertices[0]*normal[0] + vertices[1]*normal[1] + vertices[2]*normal[2]))
            isForest = False
            if self.world.faceRadius[iFace] > self.waterWorld.faceRadius[iFace]:
                if self.terrainAngles[iFace] <= 30 and self.world.faceTemperature[iFace, 0] >= 0.4:
                    #r = np.random.rand()
                    #if r < 0.5:
                    if forestPerlin[iFace] < self.settings.forestPerlinThreshold:
                        isForest = True
            self.isForest.append(isForest)

            temperature = world.faceTemperature[iFace, 0]

            if self.terrainAngles[iFace] >30:
                if temperature < 0.1:
                    r = 'snow'
                else:
                    r = 'rock'
            else:
                if temperature < 0.3:
                    r = 'snow'
                elif temperature < 0.4:
                    r = 'tundra'
                else:
                    if self.isForest[iFace]:
                        r = 'forest'
                    else:
                        r = 'grass'
            #print('  ')

            #r = np.random.choice(['water', 'grass', 'rock', 'snow'])
            #r = 'grass'
            rIndices = self.closeTexture.textureIndices[r]
            tex_writer.addData2f(rIndices[0], 0)
            tex_writer.addData2f(rIndices[1], 0)
            tex_writer.addData2f((rIndices[0] + rIndices[1])/2, np.sqrt(3)/2)

        tri = p3d.GeomTriangles(p3d.Geom.UH_static)

        # Creates the triangles.
        n = 0
        for iFace in range(np.size(world.f, 0)):
            #tri.add_vertices(world.f[iFace, 0], world.f[iFace, 1], world.f[iFace, 2])
            tri.add_vertices(n, n+1, n+2)
            n += 3

        # Assigns a normal to each vertex.
        for iFace in range(np.size(world.f, 0)):
            #normal_writer.add_data3(p3d.Vec3(self.normals[y, x, 0], self.normals[y, x, 1], self.normals[y, x, 2]))

            #vertices = world.v[world.f[iFace, 1:]]
            #v0 = vertices[1, :] - vertices[0, :]
            #v1 = vertices[2, :] - vertices[0, :]
            #normal = [v0[1]*v1[2] - v1[1]*v0[2], v0[0]*v1[2] - v1[0]*v0[2], v0[0]*v1[1] - v1[0]*v0[1]]

            normal = world.faceNormals[iFace, :]

            #normal_writer.add_data3(p3d.Vec3(0, 0, 1))
            #normal_writer.add_data3(p3d.Vec3(0, 0, 1))
            #normal_writer.add_data3(p3d.Vec3(0, 0, 1))
            normal_writer.add_data3(p3d.Vec3(normal[0], normal[1], normal[2]))
            normal_writer.add_data3(p3d.Vec3(normal[0], normal[1], normal[2]))
            normal_writer.add_data3(p3d.Vec3(normal[0], normal[1], normal[2]))

        geom = p3d.Geom(self.planet_vertex_data)
        geom.add_primitive(tri)

        node = p3d.GeomNode("Planet")
        node.add_geom(geom)
        self.planet = p3d.NodePath(node)

        self.planet.reparentTo(render)
        self.planet.setTexture(self.closeTexture.stitchedTexture)
        self.planet.setTransparency(p3d.TransparencyAttrib.MAlpha)
        #self.planet.setTexture(texture.whiteTexture)
        #self.planet.setTag('iFace', 'THE PLANET')



        #-------------------------------------------------------------

        # v3n3t2 : vertices3, normals3, textureCoordinates2
        vertex_format = p3d.GeomVertexFormat.get_v3n3c4t2()
        # vertex_format = p3d.GeomVertexFormat.get_v3t2()
        self.water_vertex_data = p3d.GeomVertexData("triangle_data", vertex_format, p3d.Geom.UH_static)

        pos_writer = p3d.GeomVertexWriter(self.water_vertex_data, "vertex")
        normal_writer = p3d.GeomVertexWriter(self.water_vertex_data, "normal")
        colour_writer = p3d.GeomVertexWriter(self.water_vertex_data, 'color')
        tex_writer = p3d.GeomVertexWriter(self.water_vertex_data, 'texcoord')

        for iFace in range(np.size(worldWater.f, 0)):
            vertices = worldWater.v[worldWater.f[iFace, 1:]]
            pos_writer.add_data3(vertices[0, 0], vertices[0, 1], vertices[0, 2])
            pos_writer.add_data3(vertices[1, 0], vertices[1, 1], vertices[1, 2])
            pos_writer.add_data3(vertices[2, 0], vertices[2, 1], vertices[2, 2])

            colour_writer.add_data4(1, 1, 1, 1)
            colour_writer.add_data4(1, 1, 1, 1)
            colour_writer.add_data4(1, 1, 1, 1)

            r = np.random.choice(['water', 'grass', 'rock', 'snow'])
            #r = 'water'
            waterHeight = worldWater.faceRadius[iFace] - world.faceRadius[iFace]

            temperature = world.faceTemperature[iFace, 0]
            if temperature < 0.1:
                r = 'snow'
            else:
                if waterHeight < 1.2:
                    r = 'shallow_water'
                else:
                    r = 'water'
            rIndices = self.closeTexture.textureIndices[r]
            tex_writer.addData2f(rIndices[0], 0)
            tex_writer.addData2f(rIndices[1], 0)
            tex_writer.addData2f((rIndices[0] + rIndices[1])/2, np.sqrt(3)/2)

        tri = p3d.GeomTriangles(p3d.Geom.UH_static)

        # Creates the triangles.
        n = 0
        for iFace in range(np.size(worldWater.f, 0)):
            #tri.add_vertices(world.f[iFace, 0], world.f[iFace, 1], world.f[iFace, 2])
            tri.add_vertices(n, n+1, n+2)
            n += 3

        # Assigns a normal to each vertex.
        for iFace in range(np.size(worldWater.f, 0)):
            #normal_writer.add_data3(p3d.Vec3(self.normals[y, x, 0], self.normals[y, x, 1], self.normals[y, x, 2]))

            vertices = worldWater.v[worldWater.f[iFace, 1:]]
            v0 = vertices[1, :] - vertices[0, :]
            v1 = vertices[2, :] - vertices[0, :]
            normal = [v0[1]*v1[2] - v1[1]*v0[2], -v0[0]*v1[2] + v1[0]*v0[2], v0[0]*v1[1] - v1[0]*v0[1]]

            #normal_writer.add_data3(p3d.Vec3(0, 0, 1))
            #normal_writer.add_data3(p3d.Vec3(0, 0, 1))
            #normal_writer.add_data3(p3d.Vec3(0, 0, 1))
            normal_writer.add_data3(p3d.Vec3(normal[0], normal[1], normal[2]))
            normal_writer.add_data3(p3d.Vec3(normal[0], normal[1], normal[2]))
            normal_writer.add_data3(p3d.Vec3(normal[0], normal[1], normal[2]))

        geom = p3d.Geom(self.water_vertex_data)
        geom.add_primitive(tri)

        node = p3d.GeomNode("Water")
        node.add_geom(geom)
        self.water = p3d.NodePath(node)

        # This material adds some shine to the water surface.
        waterMaterial = p3d.Material()
        waterMaterial.setShininess(128.0)
        waterMaterial.setSpecular((0.2, 0.2, 0.2, 1))

        self.water.reparentTo(render)
        #self.water.setMaterial(waterMaterial)
        self.water.setTexture(self.closeTexture.stitchedTexture)
        self.water.setTransparency(p3d.TransparencyAttrib.MAlpha)
        self.water.setShaderAuto()



        import Library.Collision_Detection as Collision_Detection
        self.tilePicker = Collision_Detection.TilePicker(mainProgram=self)
        self.selectedTile = None


        import Library.GUI as GUI
        self.interface = GUI.Interface(base=base, mainProgram=self)





        self.sunAngle = 0
        self.sunOrbitTime = 100
        self.add_task(self.RotateSun, 'sunRotation')




        # Adds a GUI button for toggling of terrain textures
        self.windowSize = (base.win.getXSize(), base.win.getYSize())
        self.windowRatio = self.windowSize[0] / self.windowSize[1]
        GUIDataDirectoryPath = Root_Directory.Path(style='unix') + '/Data/GUI/'

        self.displayFeaturesPositionRelative = [1.95, 0, 0.1]#[1.85, 0, 0.45]
        self.displayFeaturesPosition = (self.displayFeaturesPositionRelative[0]*self.windowRatio,
                                        0,
                                        self.displayFeaturesPositionRelative[2]*self.windowRatio)
        self.displayFeaturesButton = DirectCheckButton(boxImage=(GUIDataDirectoryPath + "feature_toggle.png",
                                                           GUIDataDirectoryPath + "feature_toggle_pressed.png",
                                                           GUIDataDirectoryPath + "feature_toggle.png",
                                                           GUIDataDirectoryPath + "feature_toggle.png"),
                                                 scale=0.1,
                                                 pos=self.displayFeaturesPosition,
                                                 relief=None,
                                                 boxRelief=None,
                                                 boxPlacement='right',
                                                 parent=base.a2dBottomLeft,
                                                 command=self.TextureToggleCallback)
        self.displayFeaturesButton.setTransparency(TransparencyAttrib.MAlpha)


        profile = False
        tic = time.time()
        if profile:
            import cProfile, pstats, io
            from pstats import SortKey
            pr = cProfile.Profile()
            pr.enable()
        self.InitializeForest(farDistance = self.farDistance)
        if profile:
            pr.disable()
            s = io.StringIO()
            sortby = SortKey.CUMULATIVE
            ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
            ps.print_stats()
            print(s.getvalue())
            quit()
        toc = time.time()
        print('Initialize forest: ', toc-tic)

        self.camera = Camera.GlobeCamera(mainProgram=self,
                                         zoomRange = [1.1*world.minRadius, 7*world.minRadius],
                                         zoomSpeed=0.03,
                                         minRadius = world.minRadius,
                                         rotationSpeedRange=[np.pi/1000, np.pi/120])
        print(self.camera.focalPoint.getPos())
        print(self.camera.camera.getPos())

    def TextureToggleCallback(self, value):
        if value == 1:
            self.planet.setTexture(self.closeTexture.whiteTexture)
        elif value == 0:
            self.planet.setTexture(self.closeTexture.stitchedTexture)

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
        import Library.Feature as Feature

        self.nodeWorld = World.SphericalWorld(nDivisions=8)
        self.nForestNodes = np.size(self.nodeWorld.v, axis=0)
        self.nodeWorld.v = self.nodeWorld.unscaledVertices * self.world.minRadius

        self.featureRoot = render.attachNewNode("featureRoot")
        self.forestRoot = self.featureRoot.attachNewNode("forestRoot")

        self.featureList = [[] for i in range(self.world.nTriangles)]

        pineModel = loader.loadModel(Root_Directory.Path(style='unix') + "/Data/Models/pine_1.bam")
        kapokModel = loader.loadModel(Root_Directory.Path(style='unix') + "/Data/Models/kapok_2.bam")
        palmModel = loader.loadModel(Root_Directory.Path(style='unix') + "/Data/Models/palm_2.bam")

        #self.forestRootNodes = [self.forestRoot.attachNewNode("forestRootNode") for i in range(self.nForestNodes)]

        self.forestNodeClusters = []
        for iNode in range(self.nForestNodes):
            #nodePos = np.mean(
            #    self.world.faceCoordinates[int(np.floor(iNode * self.world.nTriangles / self.nForestNodes)):
            #                               int(np.floor((iNode + 1) * self.world.nTriangles / self.nForestNodes) - 1),
            #    :], axis=0)
            nodePos = self.nodeWorld.v[iNode, :]
            self.forestNodeClusters.append(Feature.FeatureCluster(parent=self.forestRoot, position=nodePos, renderDistance=farDistance))

        kdTree = sp.spatial.cKDTree(self.nodeWorld.v)

        r, featureiNode = kdTree.query(self.world.faceCoordinates)

        for iFace in range(self.world.nTriangles):
            if self.isForest[iFace]:
                theta = 180*np.arctan(self.world.faceCoordinates[iFace, 2] / np.sqrt(self.world.faceCoordinates[iFace, 0]**2 + self.world.faceCoordinates[iFace, 1]**2))/np.pi
                phi = 180*np.arctan(self.world.faceCoordinates[iFace, 1]/self.world.faceCoordinates[iFace, 0])/np.pi
                if self.world.faceCoordinates[iFace, 0] > 0:
                    phi += 180

                iNode = featureiNode[iFace]

                #iNode = int(np.floor(iFace * self.nForestNodes / self.world.nTriangles))
                #self.featureList[iFace].append(Feature.SingleFeature(parentNode=forestNodeClusters[iNode].node,
                #                                                     model=model,
                #                                                     position=self.world.faceCoordinates[iFace, :]-forestNodeClusters[iNode].position,
                #                                                     rotation=[90+phi, theta, 0],
                #                                                     scale=10))

                temperature = self.world.faceTemperature[iFace, 0]
                if temperature < 0.8:
                    model = pineModel
                    scale = 3.5
                elif temperature < 1.2:
                    model = kapokModel
                    scale = 1.5
                else:
                    model = palmModel
                    scale = 4.5

                self.featureList[iFace].append(Feature.TileFeature(parentNode=self.forestNodeClusters[iNode].node,
                                                                   model=model,
                                                                   positionOffset=-self.forestNodeClusters[iNode].position,
                                                                   rotation=[90+phi, theta, 0],
                                                                   scale=scale,
                                                                   triangleCorners=self.world.v[self.world.f[iFace, 1:]],
                                                                   triangleDivisions=2,
                                                                   nFeatures=5))# 2# 7

        for iNode in range(self.nForestNodes):
            self.forestNodeClusters[iNode].node.clearModelNodes()
            self.forestNodeClusters[iNode].node.flattenStrong()
            self.forestNodeClusters[iNode].node.reparentTo(self.forestNodeClusters[iNode].LODNodePath)

        #render.analyze()

game = Game()
game.run()

