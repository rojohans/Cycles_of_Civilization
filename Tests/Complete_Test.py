from direct.showbase.ShowBase import ShowBase
import panda3d.core as p3d
import numpy as np
import time

import Library.TileClass as TileClass
import Library.Light as Light
import Library.Camera as Camera
import Library.World as World
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
        self.collidableRoot = render.attachNewNode('collidableRoot')
        self.tileRoot = self.collidableRoot.attachNewNode("squareRoot")

        World.WorldClass.Initialize(mainProgram = self)
        self.world = World.WorldClass()

        self.SetupTiles()

        self.SetupFeatures()

        # --------------------------------------------------------------------------------------------------------------
        # --------------------------------------------------------------------------------------------------------------

        base.setFrameRateMeter(True)

        self.lightObject = Light.LightClass(shadowsEnabled = False)

        Camera.CameraClass.Initialize(mainProgram = self)
        self.cameraObject = Camera.CameraClass()
        self.cameraObject.cameraUpdateFunctions.append(self.cameraObject.UpdateFeatureRender)

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

    def SetupFeatures(self):
        self.tilesToRender = []
        self.tilesBeingRendered = []

        self.featureTemplateDictionary = FeatureTemplateDictionary.GetFeatureTemplateDictionary()
        TileClass.FeatureClass.Initialize(featureTemplates = self.featureTemplateDictionary, pandaProgram = self)
        for row in range(self.settings.N_ROWS):
            for colon in range(self.settings.N_COLONS):
                iTile = colon + row * self.settings.N_COLONS
                r = np.random.rand()
                if r < 0.2:
                    self.tileList[iTile].features.append(TileClass.FeatureClass(parentTile=self.tileList[iTile],
                                                                                type='jungle',
                                                                                numberOfcomponents=20))
                elif r < 0.4:
                    self.tileList[iTile].features.append(TileClass.FeatureClass(parentTile=self.tileList[iTile],
                                                                                type='town',
                                                                                numberOfcomponents=20,
                                                                                distributionType='grid',
                                                                                distributionValue=7,
                                                                                gridAlignedHPR=True
                                                                                ))
                elif r < 0.6:
                    self.tileList[iTile].features.append(TileClass.FeatureClass(parentTile=self.tileList[iTile],
                                                                                type='farm',
                                                                                numberOfcomponents=1,
                                                                                distributionType='random'))
                elif r < 0.8:
                    self.tileList[iTile].features.append(TileClass.FeatureClass(parentTile=self.tileList[iTile],
                                                                                type='conifer_forest',
                                                                                numberOfcomponents=20))
                else:
                    self.tileList[iTile].features.append(TileClass.FeatureClass(parentTile=self.tileList[iTile],
                                                                                type='temperate_forest',
                                                                                numberOfcomponents=20))
                self.tileList[iTile].features[0].node.removeNode()

    def SetupTiles(self):
        self.tileList = []
        TileClass.TileClass.Initialize(self.settings.N_ROWS, self.settings.N_COLONS,
                                       tileList = self.tileList,
                                       pandaProgram = self)


        tic = time.time()
        # Initializes the tiles
        for row in range(self.settings.N_ROWS):
            for colon in range(self.settings.N_COLONS):
                self.tileList.append(TileClass.TileClass(row, colon, self.world.elevation[row, colon]))
        toc = time.time()
        print('object creation time: {}'.format(toc - tic))

        tic = time.time()
        # Creates the tile models.

        for row in range(self.settings.N_ROWS):
            for colon in range(self.settings.N_COLONS):
                iTile = colon + row * self.settings.N_COLONS
                #self.tileList[iTile].TopographyTile()
                self.tileList[iTile].ApplyTopography()


        toc = time.time()
        print('TopographyTile: {}'.format(toc - tic))

        tic = time.time()
        self.tileList[0].TopographyCleanUp()
        toc = time.time()
        print('TopographyCleanUp: {}'.format(toc - tic))


        tic = time.time()
        for row in range(self.settings.N_ROWS):
            for colon in range(self.settings.N_COLONS):
                iTile = colon + row * self.settings.N_COLONS
                self.tileList[iTile].CreateNormals()
        toc = time.time()
        print('CreateNormals: {}'.format(toc - tic))

        tic = time.time()
        self.tileList[0].NormalsCleanup()
        toc = time.time()
        print('NormalsCleanup: {}'.format(toc - tic))

        tic = time.time()
        for row in range(self.settings.N_ROWS):
            for colon in range(self.settings.N_COLONS):
                iTile = colon + row * self.settings.N_COLONS
                # self.tileList[iTile].CreateNode()

                self.tileList[iTile].CreateNodeExperimental()
        toc = time.time()
        print('CreateNodeExperimental: {}'.format(toc - tic))

        #TileClass.UnitClass.CreateUnit(row=7, colon=13, elevation=self.z[7, 13], type='unit_test')
        #TileClass.UnitClass.CreateUnit(row=5, colon=5, elevation=self.z[5, 5], type='unit_test')
        # TileClass.UnitClass.CreateUnit(row = 8, colon = 61, elevation = self.z[8, 61], type = 'unit_test')

        for row in range(self.settings.N_ROWS):
            for colon in range(self.settings.N_COLONS):
                iTile = colon + row * self.settings.N_COLONS

                self.tileList[iTile].ApplyTexture()
                #self.tileList[iTile].TextureTile()

                self.tileList[iTile].node.reparentTo(self.tileRoot)
                self.tileList[iTile].node.setScale(1, 1, self.settings.ELEVATION_SCALE)
                self.tileList[iTile].node.setTag('square', str(iTile))
                self.tileList[iTile].node.setTag('row', str(row))
                self.tileList[iTile].node.setTag('colon', str(colon))
                self.tileList[iTile].node.setTag('type', 'tile')

                # Creates a duplicate of the tiles which are within the HORIZONTAL_WRAP_BUFFER distance from the map edge.
                # This makes it so that the user do not see an edge when scrolling over the edge.
                if colon < self.settings.HORIZONTAL_WRAP_BUFFER:
                    self.tileList[iTile].Wrap('right')
                if colon > (self.settings.N_COLONS - self.settings.HORIZONTAL_WRAP_BUFFER):
                    self.tileList[iTile].Wrap('left')


game = Game()
game.run()

