from direct.showbase.ShowBase import ShowBase
import panda3d.core as p3d
import numpy as np

import Library.TileClass as TileClass
import Library.Light as Light
import Data.Dictionaries.FeatureTemplateDictionary as FeatureTemplateDictionary
import Root_Directory


class Game(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        p3d.PStatClient.connect()

        #print(cpMgr)

        self.N_ROWS = 128
        self.N_COLONS = 128
        self.MODEL_RESOLUTION = 30
        self.ELEVATION_SCALE = 0.3

        self.FEATURE_RENDER_RADIUS = 12
        self.FEATURE_RENDER_CAPACITY = 2000
        self.FEATURE_RENDER_MAX_SPEED = 2 # The maximum #features to add each frame.

        self.RENDER_CIRCLE = []
        for row in np.linspace(-self.FEATURE_RENDER_RADIUS, self.FEATURE_RENDER_RADIUS, self.FEATURE_RENDER_RADIUS * 2 + 1):
            for colon in np.linspace(-self.FEATURE_RENDER_RADIUS, self.FEATURE_RENDER_RADIUS, self.FEATURE_RENDER_RADIUS * 2 + 1):
                if np.sqrt(row**2 + colon**2) <= self.FEATURE_RENDER_RADIUS:
                    self.RENDER_CIRCLE.append([colon, row])
        self.RENDER_CIRCLE = np.array(self.RENDER_CIRCLE)

        self.featureRoot = render.attachNewNode("featureRoot")
        self.tileList = []

        self.tilesToRender = []
        self.tilesBeingRendered = []


        TileClass.TileClass.Initialize(self.N_ROWS, self.N_COLONS,
                                       tileList = self.tileList,
                                       elevationMap = None,
                                       ADJACENT_TILES_TEMPLATE= None,
                                       TILE_CENTER_WIDTH=None,
                                       grassProbabilityMap=None,
                                       desertProbabilityMap=None,
                                       tundraProbabilityMap=None,
                                       modelResolution=self.MODEL_RESOLUTION,
                                       textureResolution=None,
                                       pandaProgram = self)

        self.featureTemplateDictionary = FeatureTemplateDictionary.GetFeatureTemplateDictionary()

        TileClass.FeatureClass.Initialize(featureTemplates = self.featureTemplateDictionary, pandaProgram = self)

        for row in range(self.N_ROWS):
            for colon in range(self.N_COLONS):
                self.tileList.append(TileClass.TileClass(row, colon, 0))
                self.tileList[-1].topography = np.zeros((self.MODEL_RESOLUTION, self.MODEL_RESOLUTION))

        for row in range(self.N_ROWS):
            for colon in range(self.N_COLONS):
                iTile = colon + row * self.N_COLONS
                r = np.random.rand()
                #self.tileList[iTile].features.append(TileClass.FeatureClass(parentTile=self.tileList[iTile],
                #                                                            type='8_bit_test',
                #                                                            numberOfcomponents=20))
                #self.tileList[iTile].features.append(TileClass.FeatureClass(parentTile=self.tileList[iTile],
                #                                                            type='temperate_forest',
                #                                                            numberOfcomponents=20))
                if r< 0.5:
                    self.tileList[iTile].features.append(TileClass.FeatureClass(parentTile=self.tileList[iTile],
                                                                                type='jungle',
                                                                                numberOfcomponents=20))
                else:
                    self.tileList[iTile].features.append(TileClass.FeatureClass(parentTile=self.tileList[iTile],
                                                                                type='town',
                                                                                numberOfcomponents=20,
                                                                                distributionType='grid',
                                                                                distributionValue=7,
                                                                                gridAlignedHPR=True
                                                                                ))
                self.tileList[iTile].features[0].node.removeNode()


        base.setFrameRateMeter(True)

        self.lightObject = Light.LightClass()

        import Library.Camera as Camera
        Camera.CameraClass.Initialize(mainProgram = self)
        self.cameraObject = Camera.CameraClass()

        self.key_down = {}
        # mouse1 : left mouse button
        # mouse2 : middle mouse button
        # mouse3 : right mouse button
        self.inputDictionary = {'arrow_left': False,
                                'arrow_down': False,
                                'arrow_right': False,
                                'arrow_up': False,
                                'a': False,
                                's': False,
                                'd': False,
                                'w': False,
                                'mouse1': False,
                                'mouse2': False,
                                'mouse3': False,
                                'escape': False,
                                'mouse4': False}

        for key, value in self.inputDictionary.items():
            print(key)
            self.accept(key, self.UpdateKeyDictionary, [key, True])
            self.accept(key + '-up', self.UpdateKeyDictionary, [key, False])

        self.leftMouseClickCooldown = 0
        self.leftMouseClickCooldownMax = 0.1
        #self.LeftMouseButtonFunction = self.StandardClicker
        #self.add_task(self.MouseClickTask, 'mouse_click')
        #self.add_task(self.AnimationTask, 'animation_task')
        #self.debugTask = taskMgr.add(self.DebugPicker, 'debugTask')

        self.add_task(self.cameraObject.AttachDetachNodes, 'Attach_Detach_Nodes')

    def UpdateKeyDictionary(self, key, status):
        self.inputDictionary[key] = status


game = Game()
game.run()

