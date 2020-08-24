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
        self.tileList = TileClass.TileClass(0, 0, 0)
        self.tileList.topography = np.zeros((self.settings.MODEL_RESOLUTION, self.settings.MODEL_RESOLUTION))
        self.tileList.node = loader.loadModel(Root_Directory.Path(style='unix') + "/Data/Models/simple_tile.dae")
        self.tileList.node.set_hpr(0, 90, 0)
        self.tileList.node.setPos(0.5, 0.5, 0)
        self.tileList.node.reparentTo(render)

        self.featureTemplateDictionary = FeatureTemplateDictionary.GetFeatureTemplateDictionary()
        TileClass.FeatureClass.Initialize(featureTemplates = self.featureTemplateDictionary, pandaProgram = self)

        self.tileList.features.append(TileClass.FeatureClass(parentTile=self.tileList,
                                                                    type='8_bit_test',
                                                                    numberOfcomponents=20))

        base.setFrameRateMeter(True)

        self.lightObject = Light.LightClass(shadowsEnabled=True)

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

    def UpdateKeyDictionary(self, key, status):
        self.inputDictionary[key] = status


game = Game()
game.run()


