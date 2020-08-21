from direct.showbase.ShowBase import ShowBase
import panda3d.core as p3d
import numpy as np

import Library.TileClass as TileClass
import Library.Light as Light
import Library.Camera as Camera
import Data.Dictionaries.FeatureTemplateDictionary as FeatureTemplateDictionary
import Settings
import Root_Directory


class Game(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        p3d.PStatClient.connect()

        #print(cpMgr)

        self.settings = Settings.SettingsClass()

        self.RENDER_CIRCLE = []
        for row in np.linspace(-self.settings.FEATURE_RENDER_RADIUS, self.settings.FEATURE_RENDER_RADIUS, self.settings.FEATURE_RENDER_RADIUS * 2 + 1):
            for colon in np.linspace(-self.settings.FEATURE_RENDER_RADIUS, self.settings.FEATURE_RENDER_RADIUS, self.settings.FEATURE_RENDER_RADIUS * 2 + 1):
                if np.sqrt(row**2 + colon**2) <= self.settings.FEATURE_RENDER_RADIUS:
                    self.RENDER_CIRCLE.append([colon, row])
        self.RENDER_CIRCLE = np.array(self.RENDER_CIRCLE)
        # --------------------------------------------------------------------------------------------------------------
        # --------------------------------------------------------------------------------------------------------------
        self.featureRoot = render.attachNewNode("featureRoot")
        self.tileList = []

        self.tilesToRender = []
        self.tilesBeingRendered = []

        TileClass.TileClass.Initialize(self.settings.N_ROWS, self.settings.N_COLONS,
                                       tileList = self.tileList,
                                       elevationMap = None,
                                       ADJACENT_TILES_TEMPLATE= None,
                                       TILE_CENTER_WIDTH=None,
                                       grassProbabilityMap=None,
                                       desertProbabilityMap=None,
                                       tundraProbabilityMap=None,
                                       modelResolution=self.settings.MODEL_RESOLUTION,
                                       textureResolution=None,
                                       pandaProgram = self)
        for row in range(self.settings.N_ROWS):
            for colon in range(self.settings.N_COLONS):
                self.tileList.append(TileClass.TileClass(row, colon, 0))
                self.tileList[-1].topography = np.zeros((self.settings.MODEL_RESOLUTION, self.settings.MODEL_RESOLUTION))

        self.featureTemplateDictionary = FeatureTemplateDictionary.GetFeatureTemplateDictionary()
        TileClass.FeatureClass.Initialize(featureTemplates = self.featureTemplateDictionary, pandaProgram = self)
        for row in range(self.settings.N_ROWS):
            for colon in range(self.settings.N_COLONS):
                iTile = colon + row * self.settings.N_COLONS
                r = np.random.rand()
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
        # --------------------------------------------------------------------------------------------------------------
        # --------------------------------------------------------------------------------------------------------------

        base.setFrameRateMeter(True)

        self.lightObject = Light.LightClass()

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

