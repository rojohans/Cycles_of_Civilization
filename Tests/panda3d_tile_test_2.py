

from direct.showbase.ShowBase import ShowBase
import panda3d.core as p3d
import configparser
from panda3d.core import CollisionTraverser, CollisionNode
from panda3d.core import CollisionHandlerQueue, CollisionRay
from panda3d.core import AmbientLight, DirectionalLight, LightAttrib
from panda3d.core import TextNode
from panda3d.core import LPoint3, LVector3, BitMask32, GeomNode, TextureStage
from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectGui import *

from direct.showbase.DirectObject import DirectObject
from direct.task.Task import Task
import sys

import time
import numpy as np

import Library.TileClass as TileClass
import Library.Animation as Animation
import Library.Pathfinding as Pathfinding
import Root_Directory

# First we define some constants for the colors
WHITE = (1, 1, 1, 1)
HIGHLIGHT = (1, 0, 0, 1)

#N_ROWS = 8
#N_COLONS = 16
N_ROWS = 32
N_COLONS = 32
#N_ROWS = 32
#N_COLONS = 128
#N_ROWS = 150
#N_COLONS = 150

# 16*64 = 600 + 40 + 360 + 24 = 1024
# 150*150 = 10 000 + 5000 + 5000 + 2500 = 22 500

TILE_CENTER_WIDTH = 0.5
#TILE_CENTER_WIDTH = 0.1

HORIZONTAL_WRAP_BUFFER = 20

#ELEVATION_SCALE = 0.05
ELEVATION_SCALE = 0.2
#ELEVATION_SCALE = 0.6
MODEL_RESOLUTION = 30
TEXTURE_RESOLUTION = 128

# [1, -1]      [1, 0]       [1, 1]         7  6  5
# [0, -1]    [row, colon]   [0, 1]         0     4
# [-1, -1]     [-1, 0]      [-1, 1]        1  2  3
ADJACENT_TILES_TEMPLATE = np.array([[0, -1], [-1, -1], [-1, 0], [-1, 1], [0, 1], [1, 1], [1, 0], [1, -1]], dtype = int)


def CalculateTriangleNormal(p0, p1, p2):
    # The points p0, p1, p2 needs to be given in counter clockwise order.

    v0 = np.array(p1)-np.array(p0)
    v1 = np.array(p2)-np.array(p0)

    c = np.cross(v0, v1)
    c /= np.sqrt(c[0]**2 + c[1]**2 + c[2]**2)

    return p3d.Vec3(c[0], c[1], c[2])

def DiscretizeElevationMap(zMap, N_ELEVATION_LAYERS):
    zMap = np.abs(np.round((N_ELEVATION_LAYERS-1) * zMap))
    return zMap

class ChessboardDemo(ShowBase):
    def __init__(self):
        # Initialize the ShowBase class from which we inherit, which will
        # create a window and set up everything we need for rendering into it.
        ShowBase.__init__(self)

        # Changes the background colour of the scene.
        base.setBackgroundColor(0.0, 0.0, 0.0)

        self.N_ROWS = N_ROWS
        self.N_COLONS = N_COLONS
        self.TILE_CENTER_WIDTH = TILE_CENTER_WIDTH
        self.HORIZONTAL_WRAP_BUFFER = HORIZONTAL_WRAP_BUFFER
        self.ELEVATION_SCALE = ELEVATION_SCALE
        self.MODEL_RESOLUTION = MODEL_RESOLUTION
        self.TEXTURE_RESOLUTION = TEXTURE_RESOLUTION

        import Library.GUI as GUI
        self.GUIObject = GUI.GUIClass(base, debugText = True)
        self.add_task(self.GUIObject.window_task, 'window_update')


        # We will attach all of the squares to their own root. This way we can do the
        # collision pass just on the squares and save the time of checking the rest
        # of the scene
        self.collidableRoot = render.attachNewNode('collidableRoot')
        self.squareRoot = self.collidableRoot.attachNewNode("squareRoot")
        self.unitRoot = self.collidableRoot.attachNewNode('unitRoot')
        #self.GUIRoot = self.collidableRoot.attachNewNode('GUIRoot')
        self.GUIRoot = self.render.attachNewNode('GUIRoot')

        self.featureRoot = render.attachNewNode("featureRoot")



        #"panda3d-master/samples/chessboard/models/red_128.jpg"
        #b.setTag('type', 'GUI')
        #,parent = base.a2dTopLeft
        #b.reparentTo(self.GUIRoot)
        #b.reparentTo(self.render)



        self.selected_tile_ID = None
        self.selected_unit_ID = None

        #self.accept('escape', sys.exit)  # Escape quits
        #self.disableMouse()  # Disble mouse camera control
        #camera.setPosHpr(0, -12, 8, 0, -35, 0)  # Set the camera

        #self.setupLights()  # Setup default lighting
        import Library.Light as Light
        self.lights = Light.LightClass()


        # Since we are using collision detection to do picking, we set it up like
        # any other collision detection system with a traverser and a handler
        self.picker = CollisionTraverser()  # Make a traverser
        self.pq = CollisionHandlerQueue()  # Make a handler
        # Make a collision node for our picker ray
        self.pickerNode = CollisionNode('mouseRay')
        # Attach that node to the camera since the ray will need to be positioned
        # relative to it
        self.pickerNP = camera.attachNewNode(self.pickerNode)
        # Everything to be picked will use bit 1. This way if we were doing other
        # collision we could separate it
        self.pickerNode.setFromCollideMask(GeomNode.getDefaultCollideMask())
        self.pickerRay = CollisionRay()  # Make our ray
        # Add it to the collision node
        self.pickerNode.addSolid(self.pickerRay)
        # Register the ray as something that can cause collisions
        self.picker.addCollider(self.pickerNP, self.pq)
        #self.picker.showCollisions(render)

        # Now we create the chess board and its pieces

        import Library.Noise as Noise

        gridSize = 128
        points = np.zeros((N_ROWS* N_COLONS, 3))
        for row in range(N_ROWS):
            for colon in range(N_COLONS):
                #points[colon + row * N_COLONS, 0] = gridSize/2 + 0.9*(gridSize/2) * np.cos(2*np.pi*colon/N_COLONS)
                #points[colon + row * N_COLONS, 1] = gridSize/2 + 0.9*(gridSize/2) * np.sin(2*np.pi*colon/N_COLONS)
                #points[colon + row * N_COLONS, 2] = (gridSize) * row/N_ROWS
                points[colon + row * N_COLONS, 0] = 1*np.cos(2*np.pi*colon/N_COLONS)
                points[colon + row * N_COLONS, 1] = 1*np.sin(2*np.pi*colon/N_COLONS)
                points[colon + row * N_COLONS, 2] = 2*row/N_ROWS
        numberOfInitialIterationsToSkip = 1
        amplitudeScaling = 1.2

        print(points)

        z = Noise.PerlinNoiseSpherical(gridSize, points, numberOfInitialIterationsToSkip, amplitudeScaling)
        grassPropabilityList = Noise.PerlinNoiseSpherical(gridSize, points, numberOfInitialIterationsToSkip, amplitudeScaling=1.0)
        desertPropabilityList = Noise.PerlinNoiseSpherical(gridSize, points, numberOfInitialIterationsToSkip, amplitudeScaling=1.0)
        tundraProbabilityList = Noise.PerlinNoiseSpherical(gridSize, points, numberOfInitialIterationsToSkip, amplitudeScaling=1.0)

        self.z = np.zeros((N_ROWS, N_COLONS))
        for row in range(N_ROWS):
            for colon in range(N_COLONS):
                self.z[row, colon] = z[colon + row * N_COLONS]
        self.z -= np.min(np.min(self.z))
        self.z /= np.max(np.max(self.z))
        print(np.min(np.min(self.z)))
        print(np.max(np.max(self.z)))

        grassProbabilityMap = np.zeros((N_ROWS, N_COLONS))
        for row in range(N_ROWS):
            for colon in range(N_COLONS):
                grassProbabilityMap[row, colon] = grassPropabilityList[colon + row * N_COLONS]
        grassProbabilityMap -= np.min(np.min(grassProbabilityMap))
        grassProbabilityMap /= np.max(np.max(grassProbabilityMap))

        desertProbabilityMap = np.zeros((N_ROWS, N_COLONS))
        for row in range(N_ROWS):
            for colon in range(N_COLONS):
                desertProbabilityMap[row, colon] = desertPropabilityList[colon + row * N_COLONS]
        desertProbabilityMap -= np.min(np.min(desertProbabilityMap))
        desertProbabilityMap /= np.max(np.max(desertProbabilityMap))

        tundraProbabilityMap = np.zeros((N_ROWS, N_COLONS))
        for row in range(N_ROWS):
            for colon in range(N_COLONS):
                tundraProbabilityMap[row, colon] = tundraProbabilityList[colon + row * N_COLONS]
        tundraProbabilityMap -= np.min(np.min(tundraProbabilityMap))
        tundraProbabilityMap /= np.max(np.max(tundraProbabilityMap))

        N_ELEVATION_LAYERS = 10
        #self.z*=10
        self.z = DiscretizeElevationMap(self.z, N_ELEVATION_LAYERS)

        print(np.min(np.min(self.z)))
        print(np.max(np.max(self.z)))

        # For each square
        self.squares = [None for i in range(N_ROWS*N_COLONS)]
        self.tileList = []
        treeList = []
        self.units = {}

        TileClass.TileClass.Initialize(N_ROWS, N_COLONS,
                                       tileList = self.tileList,
                                       elevationMap = self.z,
                                       ADJACENT_TILES_TEMPLATE= ADJACENT_TILES_TEMPLATE,
                                       TILE_CENTER_WIDTH=TILE_CENTER_WIDTH,
                                       grassProbabilityMap=grassProbabilityMap,
                                       desertProbabilityMap=desertProbabilityMap,
                                       tundraProbabilityMap=tundraProbabilityMap,
                                       modelResolution=MODEL_RESOLUTION,
                                       textureResolution=TEXTURE_RESOLUTION,
                                       pandaProgram = self)

        TileClass.UnitClass.Initialize(unitRoot = self.unitRoot,
                                       ELEVATION_SCALE = ELEVATION_SCALE,
                                       unitDictionary = self.units,
                                       tileList = self.tileList,
                                       standardClicker= self.StandardClicker,
                                       ChessboardDemo = self)
        import Data.Dictionaries.FeatureTemplateDictionary as FeatureTemplateDictionary
        self.featureTemplateDictionary = FeatureTemplateDictionary.GetFeatureTemplateDictionary()

        TileClass.FeatureClass.Initialize(featureTemplates = self.featureTemplateDictionary, pandaProgram = self)

        tic = time.time()
        # Initializes the tiles
        for row in range(N_ROWS):
            for colon in range(N_COLONS):
                self.tileList.append(TileClass.TileClass(row, colon, self.z[row, colon]))
        toc = time.time()
        print('object creation time: {}'.format(toc-tic))

        tic = time.time()
        for row in range(N_ROWS):
            for colon in range(N_COLONS):
                iTile = colon + row * N_COLONS
                self.tileList[iTile].DetermineTileFeatures()

                self.tileList[iTile].textureCodeSimple = self.tileList[iTile].CreateTextureCodeSimple()
        toc = time.time()
        print('DetermineTileFeatures and CreateTextureCodeSimple: {}'.format(toc-tic))

        tic = time.time()
        # Creates the tile models.

        '''
        import cProfile, pstats, io
        from pstats import SortKey
        pr = cProfile.Profile()
        pr.enable()
        '''
        for row in range(N_ROWS):
            for colon in range(N_COLONS):
                iTile = colon + row * N_COLONS
                self.tileList[iTile].TopographyTile()
        '''
        pr.disable()
        s = io.StringIO()
        sortby = SortKey.CUMULATIVE
        ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
        ps.print_stats()
        print(s.getvalue())
        quit()
        '''


        toc = time.time()
        print('TopographyTile: {}'.format(toc-tic))

        tic = time.time()
        self.tileList[0].TopographyCleanUp()
        toc = time.time()
        print('TopographyCleanUp: {}'.format(toc-tic))

        #self.tileList[0].TopographyCleanUp()

        tic = time.time()
        for row in range(N_ROWS):
            for colon in range(N_COLONS):
                iTile = colon + row * N_COLONS
                self.tileList[iTile].CreateNormals()
        toc = time.time()
        print('CreateNormals: {}'.format(toc-tic))

        tic = time.time()
        self.tileList[0].NormalsCleanup()
        toc = time.time()
        print('NormalsCleanup: {}'.format(toc-tic))

        tic = time.time()
        for row in range(N_ROWS):
            for colon in range(N_COLONS):
                iTile = colon + row * N_COLONS
                #self.tileList[iTile].CreateNode()


                self.tileList[iTile].CreateNodeExperimental()
                #self.tileList[iTile].node = loader.loadModel("panda3d-master/samples/chessboard/models/tile_simple.dae")
                #self.tileList[iTile].node.setPos(self.tileList[iTile].node, LPoint3(colon, row, 0.4 * self.tileList[0].elevationMap[row, colon]))
                #self.tileList[iTile].node.set_hpr(0, 90, 0)
        toc = time.time()
        print('CreateNodeExperimental: {}'.format(toc-tic))

        TileClass.UnitClass.CreateUnit(row = 7, colon = 13, elevation=self.z[7, 13], type='unit_test')
        TileClass.UnitClass.CreateUnit(row = 5, colon = 5, elevation = self.z[5, 5], type = 'unit_test')
        #TileClass.UnitClass.CreateUnit(row = 8, colon = 61, elevation = self.z[8, 61], type = 'unit_test')

        tic = time.time()
        for row in range(N_ROWS):
            for colon in range(N_COLONS):
                iTile = colon + row * N_COLONS

                self.tileList[iTile].TextureTile()
                self.tileList[iTile].node.reparentTo(self.squareRoot)
                self.tileList[iTile].node.setScale(1, 1, ELEVATION_SCALE)
                self.tileList[iTile].node.setTag('square', str(iTile))
                self.tileList[iTile].node.setTag('row', str(row))
                self.tileList[iTile].node.setTag('colon', str(colon))
                self.tileList[iTile].node.setTag('type', 'tile')
                

                # Creates a duplicate of the tiles which are within the HORIZONTAL_WRAP_BUFFER distance from the map edge.
                # This makes it so that the user do not see an edge when scrolling over the edge.
                if colon < HORIZONTAL_WRAP_BUFFER:
                    self.tileList[iTile].Wrap('right')
                if colon > (N_COLONS-HORIZONTAL_WRAP_BUFFER):
                    self.tileList[iTile].Wrap('left')


                rootModel = (loader.loadModel(Root_Directory.Path(style = 'unix') + "/Data/Models/8_bit_test.bam"))
                rootModel.reparentTo(self.featureRoot)
                models = []

                if True:
                    if False:
                        if True:
                            self.tileList[iTile].features.append(TileClass.FeatureClass(parentTile=self.tileList[iTile],
                                                                                        type='jungle',
                                                                                        numberOfcomponents=20))
                        else:
                            for i in range(20):
                                #models.append(loader.loadModel("panda3d-master/samples/chessboard/models/8_bit_test.bam"))

                                #models.append(loader.loadModel("panda3d-master/samples/chessboard/models/oak_1.bam"))
                                #models[-1].setPos(p3d.LPoint3(colon + 0.5, row + 0.5, 5.0))
                                #models[-1].reparentTo(self.featureRoot)

                                models.append(self.featureRoot.attachNewNode("Placeholder"))
                                models[-1].setPos(p3d.LPoint3(colon + 0.5, row + 0.5, 5.0))
                                rootModel.instanceTo(models[-1])


                        # 8_bit_test
                        #self.tileList[iTile].features.append(TileClass.FeatureClass(parentTile=self.tileList[iTile],
                        #                                                            type='town',
                        #                                                            numberOfcomponents=10,
                        #                                                            distributionType = 'grid',
                        #                                                            distributionValue = 7))
                        #pass

                    else:
                        r = np.random.rand()
                        if r<0.2:
                            self.tileList[iTile].features.append(TileClass.FeatureClass(parentTile=self.tileList[iTile],
                                                                                        type='jungle',
                                                                                        numberOfcomponents=20,
                                                                                        distributionType = 'random'))
                        elif r<0.4:
                            self.tileList[iTile].features.append(TileClass.FeatureClass(parentTile=self.tileList[iTile],
                                                                                        type='temperate_forest',
                                                                                        numberOfcomponents=20,
                                                                                        distributionType = 'random'))
                        elif r<0.6:
                            self.tileList[iTile].features.append(TileClass.FeatureClass(parentTile=self.tileList[iTile],
                                                                                        type='conifer_forest',
                                                                                        numberOfcomponents=20,
                                                                                        distributionType = 'random'))
                        elif r < 0.7:
                            self.tileList[iTile].features.append(TileClass.FeatureClass(parentTile=self.tileList[iTile],
                                                                                        type='town',
                                                                                        numberOfcomponents=20,
                                                                                        distributionType='grid',
                                                                                        distributionValue = 7,
                                                                                        gridAlignedHPR = True))

                else:
                    r = np.random.rand()
                    if r < 0.1:
                        self.tileList[iTile].features.append(TileClass.FeatureClass(parentTile=self.tileList[iTile],
                                                                                    type='spruce_forest',
                                                                                    numberOfcomponents=20))
                    elif r < 0.3:
                        self.tileList[iTile].features.append(TileClass.FeatureClass(parentTile=self.tileList[iTile],
                                                                                    type='birch_forest',
                                                                                    numberOfcomponents=20))
                    elif r < 0.5:
                        self.tileList[iTile].features.append(TileClass.FeatureClass(parentTile=self.tileList[iTile],
                                                                                    type='oak_forest',
                                                                                    numberOfcomponents=5))
                        #self.tileList[iTile].features.append(TileClass.FeatureClass(parentTile=self.tileList[iTile],
                        #                                                            type='town',
                        #                                                            hprValue = [360*np.random.rand(), 90, 0],
                        #                                                            components=10,
                        #                                                            distribution = 'even'))
                    elif r < 0.6:
                        self.tileList[iTile].features.append(TileClass.FeatureClass(parentTile=self.tileList[iTile],
                                                                                    type='temperate_forest',
                                                                                    numberOfcomponents=20))
                    elif r < 0.7:
                        self.tileList[iTile].features.append(TileClass.FeatureClass(parentTile=self.tileList[iTile],
                                                                                    type='jungle',
                                                                                    numberOfcomponents=20))
                    elif r < 0.8:
                        self.tileList[iTile].features.append(TileClass.FeatureClass(parentTile=self.tileList[iTile],
                                                                                    type='palm_forest',
                                                                                    numberOfcomponents=20))
                    elif r < 0.9:
                        self.tileList[iTile].features.append(TileClass.FeatureClass(parentTile=self.tileList[iTile],
                                                                                    type='jungle_trees',
                                                                                    numberOfcomponents=20))
                    else:
                        self.tileList[iTile].features.append(TileClass.FeatureClass(parentTile=self.tileList[iTile],
                                                                                    type='pine_forest',
                                                                                    numberOfcomponents=20))
                        # scaleRange = [0.8, 1.2]



        #self.featureRoot.flattenStrong()
        #self.featureRoot.flattenMedium()


        toc = time.time()
        print('TextureTile and other objects: {}'.format(toc-tic))


        self.movementGraph = Pathfinding.MapGraph()
        self.movementGraph.CreateEdgesSimple(N_ROWS, N_COLONS)

        TileClass.TileClass.SaveDictionariesToFile()

        self.unitMarker = loader.loadModel(Root_Directory.Path(style = 'unix') + "/Data/Models/unit_select_marker.dae")
        self.unitMarker.setPos(LPoint3(0 + 0.5, 0 + 0.5, ELEVATION_SCALE * (0.1 + self.z[0, 0])))
        self.unitMarker.set_hpr(0, 90, 0)
        #unitMarker.wrt_reparent_to(render)

        Animation.AnimationClass.Initialize(ELEVATION_SCALE, self)



        '''
        # Detaches all but a few nodes.
        for row in range(N_ROWS):
            for colon in range(N_COLONS):
                iTile = colon + row * N_COLONS
                if row > 5 or colon > 5:
                    self.tileList[iTile].features[0].node.detachNode()
        '''



        # This will represent the index of the currently highlighted square
        self.hiSq = False
        self.pickedUnit = False
        # This wil represent the index of the square where currently dragged piece
        # was grabbed from
        self.dragging = False

        #--------------------------------------------------------------------------------------------------------------
        #--------------------------------------------------------------------------------------------------------------
        # we will control the camera using a rig of 2 nodes
        # the 'node' will be the point in space where the camera looks at
        # the 'gimbal' will act as an arm that the camera is attached to
        #self.camera_node = self.render.attach_new_node('camera_node')
        #self.camera_gimbal = self.camera_node.attach_new_node('gimbal')

        self.camera_node = self.render.attach_new_node('camera_node')
        self.camera_focal_node = self.camera_node.attach_new_node('gimbal')

        # the camera will orbit around the camera_node, here we'll set
        # how far that orbit is from the focus point
        camera_offset = (0, -3, 3)
        #self.camera.set_pos(self.render, camera_offset)
        self.camera.set_pos(self.camera_focal_node, camera_offset)
        self.camera.look_at(self.camera_focal_node)
        # we use 'wrt_reparent_to' to keep the offset we just set
        self.camera.wrt_reparent_to(self.camera_node)
        #self.camera.reparent_to(self.camera_gimbal)
        # with the setup done, we want to move the camera to a different spot
        self.camera_node.set_pos(10, 10, 5)
        # and rotate 180
        #self.camera_node.set_h(180)

        self.camera_direction_angle = 0
        self.camera_forward_vector = p3d.Vec3(np.sin(self.camera_direction_angle), np.cos(self.camera_direction_angle), 0)
        self.camera_right_vector = p3d.Vec3(np.cos(self.camera_direction_angle), np.sin(self.camera_direction_angle), 0)

        # configuration time
        # how fast can the camera rotate?
        self.camera_rotation_speed = 100.0
        # how fast can the camera move?
        self.camera_move_speed = 10.0
        # how fast can the camera zoom?
        self.camera_zoom_speed = 10.0
        self.camera_zoom_damping = 2.0
        # how much can the camera tilt? (change 'p' in HPR sense)
        self.camera_p_limit = p3d.Vec2(-65, 10)
        # how much can the camera zoom in or out?
        self.zoom_limit = [3, 20]
        # controls:
        # we'll read the keys from an .ini file
        # I'm not using the default .prc PAnda3D configuration file format
        # because most players will not even recognize .prc as a human readable,
        # configuration file, .ini on the other hand are common in games
        #key_config = configparser.ConfigParser()
        #key_config.read('panda3d-master/samples/chessboard/models/keys.ini')
        # we want mouse wheel to control zoom
        # the way the mouse wheel works is just like a button
        # it just fires the 'wheel_up' or 'wheel_down' events when the wheel is spun
        # we will zoom in (or out) some amount whenever the wheel is moved
        # self.zoom will tell us how much we still need to move and in what direction
        # the actual moving of the camera will happen in the camera_update task
        self.zoom = 0
        # the 'accept' function tells the underlying DirectObject to listen to some event
        # and run some function (method) when it happens
        # in this case the event is "key_config['camera_zoom']['zoom_in']" - and that should be just
        # "key_config['camera_zoom']['zoom_in']" should just be 'wheel_up'
        # our function is 'self.zoom_control'
        # the last argument is a list of ... em arguments passed to our function
        # in other words:
        # when a player spins the mouse wheel, panda3d will send a event named 'wheel_up'
        # and our class will respond to it by calling 'self.zoom_control(1.0)'
        #self.accept(key_config['camera_zoom']['zoom_in'], self.zoom_control, [-0.5])
        #self.accept(key_config['camera_zoom']['zoom_out'], self.zoom_control, [0.5])
        self.accept('wheel_up', self.zoom_control, [-0.55])
        self.accept('wheel_down', self.zoom_control, [0.55])
        # for other keys we want to know if the player is holding down a key
        # self.key_down will be a dict that will have the names of events as keys
        # and True as the value if a key is pressed else False
        self.key_down = {}
        '''
        for event, key in key_config['camera_keys'].items():
            self.key_down[event] = False
            self.accept(key, self.key_down.__setitem__, [event, True])
            # the keys can me 'compound' like 'shift-mouse1' or 'alt-mouse1'
            # the problem is - there is no -up event for such key-combos
            # we will have to react just to the first key
            # if we'd have a key bind on shift things would break :(
            if '-' in key:
                self.accept(key.split('-')[0] + '-up', self.key_down.__setitem__, [event, False])
            else:
                self.accept(key + '-up', self.key_down.__setitem__, [event, False])
        '''
        # we'll later check if this set None and skip moving the mouse
        # until we have a valid value
        self.last_mouse_pos = None

        # mouse1 : left mouse button
        # mouse2 : middle mouse button
        # mouse3 : right mouse button
        self.inputDictionary = {'arrow_left' : False,
                                'arrow_down' : False,
                                'arrow_right' : False,
                                'arrow_up' : False,
                                'a': False,
                                's': False,
                                'd': False,
                                'w': False,
                                'mouse1': False,
                                'mouse2' : False,
                                'mouse3' : False,
                                'escape' : False,
                                'mouse4' : False}

        for key, value in self.inputDictionary.items():
            print(key)
            self.accept(key, self.UpdateKeyDictionary, [key, True])
            self.accept(key + '-up', self.UpdateKeyDictionary, [key, False])


        # our App class inherits from the BaseApp class..
        # BaseApp inherits from ShowBase...
        # ShowBase inherits from DirectObject...
        # ...so we can use DirectObject methods like add_task()
        # The alternative is using taskMgr.add() and that's what
        # DirectObject is actually doing, but this is nicer (?)
        # A task is simply a function called auto-magically each frame
        self.add_task(self.camera_update, 'camera_update')

        self.leftMouseClickCooldown = 0
        self.leftMouseClickCooldownMax = 0.1
        self.LeftMouseButtonFunction = self.StandardClicker
        self.add_task(self.MouseClickTask, 'mouse_click')
        self.add_task(self.AnimationTask, 'animation_task')
        #self.add_task(self.StandardClicker, 'standard_picker')
        self.debugTask = taskMgr.add(self.DebugPicker, 'debugTask')
        self.disableMouse()

        self.camera_zoom_limit = (0, 30)
        #self.camera_zoom_value = (self.camera_zoom_limit[0] + self.camera_zoom_limit[1] ) / 2
        self.camera_zoom_value = 0.5
        #self.camera_node.set_pos(self.camera_node, 0, self.Camera_Zoom_Scaling('y', self.camera_zoom_value)-10, self.Camera_Zoom_Scaling('z', self.camera_zoom_value))
        self.camera.look_at(self.camera_focal_node)

        #self.squareRoot.flattenStrong()
        #self.featureRoot.flattenStrong()

        self.fpsTime = 0
        self.fpsCounter = 0


        # Camera zoom scaling visualization.
        '''
        import matplotlib.pyplot as plt

        n = np.linspace(0, 1, 100)
        xVector = np.linspace(0, 1, 100)
        yVector = np.linspace(0, 1, 100)
        for i, x in enumerate(xVector):
            xVector[i] = self.Camera_Zoom_Scaling('y', n[i])
            yVector[i] = self.Camera_Zoom_Scaling('z', n[i])

        plt.plot(xVector, yVector)
        plt.show()
        '''
        render.analyze()
        p3d.PStatClient.connect()


    def Camera_Zoom_Scaling(self, axis, zoom):
        if axis == 'x':
            pass
        elif axis == 'y':
            #return 18*(2-(zoom+1)) / (2*(zoom+1))
            #return 38*(2-(zoom+1)) / (2*(zoom+1))

            return 2*(1 - zoom**1)
            #y0 = 4
            #y1 = 6
            #c = 0.3
            #return (y0-y1)/c**2*(zoom-c)**2 + y1
        elif axis == 'z':
            #return 3+27*zoom
            #return 1 + 15 * zoom
            return 0.5 + 18 * (zoom)**1

    def Get_Camera_Move_Speed(self, zoom):
        return 6 + 16*zoom

    def UpdateKeyDictionary(self, key, status):
        self.inputDictionary[key] = status

    def zoom_control(self, amount):
        self.zoom = amount

    def camera_update(self, task):
        '''This function is a task run each frame,
           it controls the camera movement/rotation/zoom'''
        # dt is 'delta time' - how much time elapsed since the last time the task ran
        # we will use it to keep the motion independent from the framerate
        dt = globalClock.get_dt()

        self.fpsTime += dt
        self.fpsCounter += 1
        if self.fpsTime > 1:
            self.fpsTime -= 1
            #self.GUIObject.fpsCounter.setText('FPS : ' + str(round(1 / dt)))
            self.GUIObject.fpsCounter.setText('FPS : ' + str(self.fpsCounter))
            self.fpsCounter = 0


        # we'll be tracking the mouse
        # first we need to check if the cursor is in the window
        if self.mouseWatcherNode.has_mouse():
            # let's see where the mouse cursor is now
            mouse_pos = self.mouseWatcherNode.get_mouse()
            # let's see how much it moved from last time, or if this is the first frame
            if self.last_mouse_pos is None:
                self.last_mouse_pos = p3d.Vec2(mouse_pos)
                return task.again
            mouse_delta = mouse_pos - self.last_mouse_pos
            # and let's remember where it is this frame so we can
            # check next frame where it was
            self.last_mouse_pos = p3d.Vec2(mouse_pos)
            # camera zoom
            if self.zoom != 0.0:
                # let's see how far the camera is from the pivot point
                distance = self.camera.get_distance(self.camera_node)
                # we don't want it to be too close nor to far away
                #if (distance > self.zoom_limit[0] and self.zoom > 0.0) or \
                #        (distance < self.zoom_limit[1] and self.zoom < 0.0):
                    # move the camera away or closer to the pivot point
                    # we do that by moving the camera relative to itself
                    #self.camera.set_y(self.camera, self.zoom * dt * self.camera_zoom_speed)

                self.zoom *= 0.1

                #self.camera_zoom_value = min(max(self.camera_zoom_value + self.zoom, self.camera_zoom_limit[0]), self.camera_zoom_limit[1])
                self.camera_zoom_value = min(max(self.camera_zoom_value + 30*dt*self.zoom, 0), 1)

                #self.camera_node.set_pos(self.camera_focal_node, 0, -self.Camera_Zoom_Scaling('y', self.camera_zoom_value), self.Camera_Zoom_Scaling('z', self.camera_zoom_value))

                self.camera_focal_node.set_pos(self.camera_node, 0, self.Camera_Zoom_Scaling('y', self.camera_zoom_value), -self.Camera_Zoom_Scaling('z', self.camera_zoom_value))
                cameraPositon = self.camera_node.get_pos()
                self.camera_node.set_pos(cameraPositon[0], cameraPositon[1], self.Camera_Zoom_Scaling('z', self.camera_zoom_value))

                #self.camera_gimbal.set_pos(self.camera_node, 0, self.Camera_Zoom_Scaling('y', self.camera_zoom_value)-10, self.Camera_Zoom_Scaling('z', self.camera_zoom_value))
                self.camera.look_at(self.camera_focal_node)
                #print(self.zoom)

                if self.zoom >= 0.0:
                    self.zoom -= dt * self.camera_zoom_damping
                    if self.zoom < 0:self.zoom = 0
                else:
                    self.zoom += dt * self.camera_zoom_damping
                    if self.zoom > 0: self.zoom = 0
                #else:
                #    self.zoom = 0.0

            if self.inputDictionary['mouse2']:
                self.selected_tile_ID = None
                self.selected_unit_ID = None
                self.unitMarker.detachNode()
            #if self.inputDictionary['mouse3']:
            if self.inputDictionary['mouse4']:
                h = self.camera_node.get_h() - mouse_delta.x * self.camera_rotation_speed
                self.camera_node.set_h(h)
                #self.squares[i].detachNode()


                #print('mouse 3')
            #if self.inputDictionary['mouse1'] and self.inputDictionary['mouse3']:


        self.camera_move_speed = self.Get_Camera_Move_Speed(self.camera_zoom_value)
        if self.inputDictionary['arrow_up'] or self.inputDictionary['w']:
            self.camera_node.set_pos(self.camera_node, self.camera_forward_vector *0.01* self.camera_move_speed*dt/0.03)
        elif self.inputDictionary['arrow_down'] or self.inputDictionary['s']:
            self.camera_node.set_pos(self.camera_node, -self.camera_forward_vector *0.01* self.camera_move_speed*dt/0.03)
        if self.inputDictionary['arrow_left'] or self.inputDictionary['a']:
            self.camera_node.set_pos(self.camera_node, -self.camera_right_vector * 0.01 * self.camera_move_speed*dt/0.03)
        elif self.inputDictionary['arrow_right'] or self.inputDictionary['d']:
            self.camera_node.set_pos(self.camera_node, self.camera_right_vector * 0.01 * self.camera_move_speed*dt/0.03)

        if self.inputDictionary['escape'] or self.inputDictionary['mouse3']:

            if self.selected_unit_ID:
                print(self.units[self.selected_unit_ID].isSelected)
                self.units[self.selected_unit_ID].isSelected = False
                print(self.units[self.selected_unit_ID].isSelected)
                print(print('---------'))

            self.selected_tile_ID = None
            self.selected_unit_ID = None
            self.unitMarker.detachNode()

            self.GUIObject.myFrame.hide()

            TileClass.UnitClass.AddUnitButtonFunction(0)
            self.GUIObject.add_unit_button['indicatorValue'] = False
            self.GUIObject.add_unit_button.setIndicatorValue()

            TileClass.UnitClass.MoveUnitButtonFunction(0)
            self.GUIObject.move_button['indicatorValue'] = False
            self.GUIObject.move_button.setIndicatorValue()

        # When the camera traverses over the edge (west or east) it wraps around to the other side.
        cameraPosition = self.camera_node.get_pos()
        if cameraPosition[0] < 0:
            self.camera_node.set_pos((cameraPosition[0] + N_COLONS, cameraPosition[1], cameraPosition[2]))
        if cameraPosition[0]>N_COLONS:
            self.camera_node.set_pos((cameraPosition[0] - N_COLONS, cameraPosition[1], cameraPosition[2]))

        return task.cont
        #--------------------------------------------------------------------------------------------------------------
        #--------------------------------------------------------------------------------------------------------------

    def MouseClickTask(self, task):
        if self.leftMouseClickCooldown < 0:
            if self.inputDictionary['mouse1']:
                self.leftMouseClickCooldown = self.leftMouseClickCooldownMax
                self.LeftMouseButtonFunction()
        else:
            dt = globalClock.get_dt()
            self.leftMouseClickCooldown -= dt
        return task.cont

    def AnimationTask(self, task):
        Animation.AnimationClass.AnimationTaskFunction()
        return task.cont

    def StandardPicker(self):
        tileID = None
        unitID = None
        if self.inputDictionary['mouse1']:
            if self.mouseWatcherNode.hasMouse():
                # get the mouse position
                mpos = self.mouseWatcherNode.getMouse()

                # Set the position of the ray based on the mouse position
                self.pickerRay.setFromLens(self.camNode, mpos.getX(), mpos.getY())

                self.picker.traverse(self.collidableRoot)
                if self.pq.getNumEntries() > 0:
                    # if we have hit something, sort the hits so that the closest
                    # is first, and highlight that node
                    self.pq.sortEntries()
                    pickedObj = self.pq.getEntry(0).getIntoNodePath()
                    if pickedObj.getNetTag('type') == 'tile':
                        tileID = int(pickedObj.getNetTag('square'))
                    elif pickedObj.getNetTag('type') == 'unit':
                        unitID = int(pickedObj.getNetTag('ID'))
        return tileID, unitID

    def StandardClicker(self):
        tileID, unitID = self.StandardPicker()

        if tileID:
            self.selected_tile_ID = tileID
        elif unitID:
            self.selected_unit_ID = unitID
            self.selected_tile_ID = None

            self.units[unitID].isSelected = True

            self.unitMarker.setPos(self.units[unitID].colon + 0.5, self.units[unitID].row + 0.5,
                                   ELEVATION_SCALE * (self.units[unitID].elevation + 0.1))
            self.unitMarker.reparentTo(render)

            self.GUIObject.myFrame.show()
            self.GUIObject.DestroyUnitFunction = self.units[unitID].Destroy
            self.GUIObject.MoveUnitFunction = self.units[unitID].MoveUnitButtonFunction


        '''
        if self.inputDictionary['mouse1']:
            if self.mouseWatcherNode.hasMouse():
                # get the mouse position
                mpos = self.mouseWatcherNode.getMouse()

                # Set the position of the ray based on the mouse position
                self.pickerRay.setFromLens(self.camNode, mpos.getX(), mpos.getY())

                self.picker.traverse(self.collidableRoot)
                if self.pq.getNumEntries() > 0:
                    # if we have hit something, sort the hits so that the closest
                    # is first, and highlight that node
                    self.pq.sortEntries()
                    pickedObj = self.pq.getEntry(0).getIntoNodePath()

                    if pickedObj.getNetTag('type') == 'tile':
                        i = int(pickedObj.getNetTag('square'))
                        self.selected_tile_ID = i
                    elif pickedObj.getNetTag('type') == 'unit':
                        unitID = int(pickedObj.getNetTag('ID'))

                        self.selected_unit_ID = unitID
                        self.selected_tile_ID = None

                        self.unitMarker.setPos(self.units[unitID].colon + 0.5, self.units[unitID].row + 0.5,
                                               ELEVATION_SCALE * (self.units[unitID].elevation + 0.1))
                        self.unitMarker.reparentTo(render)

                        self.GUIObject.myFrame.show()
                        self.GUIObject.DestroyUnitFunction = self.units[unitID].Destroy
        '''


    def DebugPicker(self, task):
        # This task deals with the highlighting and dragging based on the mouse

        # First, clear the current highlight
        if self.hiSq is not False:
            if self.hiSq == 0:
                #self.triangle.setColor(WHITE)
                self.tileList[self.hiSq].node.setColor(WHITE)
                if self.tileList[self.hiSq].wrapperNode is not None:
                    self.tileList[self.hiSq].wrapperNode.setColor(WHITE)
            else:
                self.tileList[self.hiSq].node.setColor(WHITE)
                if self.tileList[self.hiSq].wrapperNode is not None:
                    self.tileList[self.hiSq].wrapperNode.setColor(WHITE)
            self.hiSq = False
        if self.pickedUnit is not False:
            #self.units[self.pickedUnit].node.setColor(WHITE)
            self.units[self.pickedUnit].node.setColorScale(WHITE)
            self.pickedUnit = False

        # Check to see if we can access the mouse. We need it to do anything
        # else
        if self.mouseWatcherNode.hasMouse():
            # get the mouse position
            mpos = self.mouseWatcherNode.getMouse()

            # Set the position of the ray based on the mouse position
            self.pickerRay.setFromLens(self.camNode, mpos.getX(), mpos.getY())

            # Do the actual collision pass (Do it only on the squares for
            # efficiency purposes)
            #self.picker.traverse(self.squareRoot)
            self.picker.traverse(self.collidableRoot)
            if self.pq.getNumEntries() > 0:
                # if we have hit something, sort the hits so that the closest
                # is first, and highlight that node
                self.pq.sortEntries()
                pickedObj = self.pq.getEntry(0).getIntoNodePath()

                if pickedObj.getNetTag('type') == 'tile':
                    i = int(pickedObj.getNetTag('square'))
                    #print('i = ', i)

                    row = int(pickedObj.getNetTag('row'))
                    colon = int(pickedObj.getNetTag('colon'))

                    self.GUIObject.selectedTileText.setText('Row : ' + str(row) + '\nColon : ' + str(colon) + '\nElevation : ' + str(self.z[row, colon]) + '\nTerrain : ' + self.tileList[i].terrain)

                    #i = int(self.pq.getEntry(0).getIntoNode().getTag('square'))
                    # Set the highlight on the picked square
                    if i == 0:
                        #self.triangle.setColor(HIGHLIGHT)
                        self.tileList[i].node.setColor(HIGHLIGHT)
                        if self.tileList[i].wrapperNode is not None:
                            self.tileList[i].wrapperNode.setColor(HIGHLIGHT)
                    else:
                        self.tileList[i].node.setColor(HIGHLIGHT)
                        if self.tileList[i].wrapperNode is not None:
                            self.tileList[i].wrapperNode.setColor(HIGHLIGHT)
                    self.hiSq = i
                elif pickedObj.getNetTag('type') == 'unit':
                    unitID = int(pickedObj.getNetTag('ID'))
                    #self.units[unitID].node.setColor(HIGHLIGHT)
                    self.units[unitID].node.setColorScale(HIGHLIGHT)
                    self.pickedUnit = unitID

                # detachNode() removes the current node from the tile root node.
                #self.squares[i].detachNode()
                #time.sleep(5)
                #self.squares[i].reparentTo(self.squareRoot)

        return Task.cont

    def setupLights(self):  # This function sets up some default lighting
        ambientLight = AmbientLight("ambientLight")
        ambientLight.setColor((.1, .1, .1, 1))
        directionalLight = DirectionalLight("directionalLight")
        directionalLight.setDirection(LVector3(-100, 100, -75))
        directionalLight.setColor((1, 1, 0.9, 1))

        directionalLight2 = DirectionalLight("directionalLight")
        directionalLight2.setDirection(LVector3(100, 0, -45))
        directionalLight2.setColor((0.1, 0.1, 0.15, 1))

        directionalLight3 = DirectionalLight("directionalLight")
        directionalLight3.setDirection(LVector3(0, -100, -45))
        directionalLight3.setColor((0.1, 0.1, 0.15, 1))

        directionalLight4 = DirectionalLight("directionalLight")
        directionalLight4.setDirection(LVector3(-100, 100, -45))
        directionalLight4.setColor((0.2, 0.1, 0, 1))
        '''
        directionalLight5 = DirectionalLight("directionalLight")
        directionalLight5.setDirection(LVector3(-100, 100, 10))
        directionalLight5.setColor((0.025, 0.025, 0.05, 1))
        '''
        render.setLight(render.attachNewNode(directionalLight))
        render.setLight(render.attachNewNode(directionalLight2))
        render.setLight(render.attachNewNode(directionalLight3))
        render.setLight(render.attachNewNode(directionalLight4))
        #render.setLight(render.attachNewNode(directionalLight5))
        render.setLight(render.attachNewNode(ambientLight))

# Do the main initialization and start 3D rendering
demo = ChessboardDemo()
demo.run()
