from direct.showbase.ShowBase import ShowBase
import panda3d.core as p3d
import numpy as np
import time

import Library.TileClass as TileClass
import Library.Light as Light
import Library.Camera as Camera
import Library.World as World
import Library.Pathfinding as Pathfinding
import Library.Animation as Animation
import Library.Ecosystem as Ecosystem

import Data.Dictionaries.FeatureTemplateDictionary as FeatureTemplateDictionary
import Data.Templates.Vegetation_Templates as Vegetation_Templates
import Data.Templates.Animal_Templates as Animal_Templates

import Settings
import Root_Directory


class Game(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        p3d.PStatClient.connect()

        self.settings = Settings.SettingsClass()

        import Library.GUI as GUI
        self.GUIObject = GUI.GUIClass(base, debugText = True, mainProgram = self)
        self.add_task(self.GUIObject.window_task, 'window_update')

        self.RENDER_CIRCLE = []
        for row in np.linspace(-self.settings.FEATURE_RENDER_RADIUS, self.settings.FEATURE_RENDER_RADIUS, self.settings.FEATURE_RENDER_RADIUS * 2 + 1):
            for colon in np.linspace(-self.settings.FEATURE_RENDER_RADIUS, self.settings.FEATURE_RENDER_RADIUS, self.settings.FEATURE_RENDER_RADIUS * 2 + 1):
                if np.sqrt(row**2 + colon**2) <= self.settings.FEATURE_RENDER_RADIUS:
                    self.RENDER_CIRCLE.append([colon, row])
        self.RENDER_CIRCLE = np.array(self.RENDER_CIRCLE)
        # --------------------------------------------------------------------------------------------------------------
        # --------------------------------------------------------------------------------------------------------------
        self.featureRoot = render.attachNewNode("featureRoot")
        self.wildlifeRoot = render.attachNewNode("wildlifeRoot")
        self.collidableRoot = render.attachNewNode('collidableRoot')
        self.tileRoot = self.collidableRoot.attachNewNode("squareRoot")
        self.unitRoot = self.collidableRoot.attachNewNode('unitRoot')

        self.lightObject = Light.LightClass(shadowsEnabled = False)

        Camera.CameraClass.Initialize(mainProgram = self)
        self.cameraObject = Camera.CameraClass()
        self.cameraObject.cameraUpdateFunctions.append(self.cameraObject.UpdateFeatureRender)

        tic = time.time()
        World.WorldClass.Initialize(mainProgram = self)
        self.world = World.WorldClass(numberOfErosionIterations=350)
        toc = time.time()
        print('World creation time: ', format(toc-tic))


        tic = time.time()
        self.plants = Ecosystem.Vegetation.Initialize(mainProgram=self)
        self.animals = Ecosystem.Animal.Initialize(mainProgram=self)

        Vegetation_Templates.NormalGrass.InitializeFitnessInterpolators()
        Vegetation_Templates.Jungle.InitializeFitnessInterpolators()
        Vegetation_Templates.SpruceForest.InitializeFitnessInterpolators()
        Vegetation_Templates.PineForest.InitializeFitnessInterpolators()
        Vegetation_Templates.BroadleafForest.InitializeFitnessInterpolators()

        # Animal_Templates.NormalBrowser.InitializeFitnessInterpolators()
        Animal_Templates.Boar.InitializeFitnessInterpolators()
        Animal_Templates.Turkey.InitializeFitnessInterpolators()
        Animal_Templates.Deer.InitializeFitnessInterpolators()
        Animal_Templates.Caribou.InitializeFitnessInterpolators()
        Animal_Templates.Bison.InitializeFitnessInterpolators()
        Animal_Templates.Horse.InitializeFitnessInterpolators()

        Ecosystem.Vegetation.SeedWorld(300, Vegetation_Templates.NormalGrass, minFitness=0.2)
        Ecosystem.Vegetation.SeedWorld(40, Vegetation_Templates.Jungle, minFitness=0.2)
        Ecosystem.Vegetation.SeedWorld(100, Vegetation_Templates.SpruceForest, minFitness=0.2)
        Ecosystem.Vegetation.SeedWorld(90, Vegetation_Templates.PineForest, minFitness=0.2)
        Ecosystem.Vegetation.SeedWorld(100, Vegetation_Templates.BroadleafForest, minFitness=0.2)

        for iStep in range(5):
            for plantRow in self.plants:
                for plant in plantRow:
                    if plant:
                        plant.Step()

        Ecosystem.Animal.SeedWorld(30, Animal_Templates.Boar, minFitness=0.2)
        Ecosystem.Animal.SeedWorld(20, Animal_Templates.Turkey, minFitness=0.2)
        Ecosystem.Animal.SeedWorld(50, Animal_Templates.Deer, minFitness=0.2)
        Ecosystem.Animal.SeedWorld(10, Animal_Templates.Caribou, minFitness=0.2)
        Ecosystem.Animal.SeedWorld(10, Animal_Templates.Bison, minFitness=0.2)
        Ecosystem.Animal.SeedWorld(10, Animal_Templates.Horse, minFitness=0.2)

        # migrate, predator, slope

        NSteps = 100

        forestImage = Ecosystem.Vegetation.GetImage()
        animalImage = Ecosystem.Vegetation.GetImage()

        for iStep in range(NSteps):
            for animalRow in self.animals:
                for animal in animalRow:
                    if animal:
                        animal.Step()
            for plantRow in self.plants:
                for plant in plantRow:
                    if plant:
                        plant.Step()

        toc = time.time()
        print('Ecosystem simulation: ', format(toc-tic))
        self.Ecosystem = Ecosystem



        self.selected_tile_ID = None
        self.selected_unit_ID = None
        self.SetupPicker()

        import matplotlib.pyplot as plt
        plt.imshow(self.world.topography)

        self.SetupTiles()
        plt.figure()
        plt.imshow(self.world.topography)
        plt.show()

        tic = time.time()
        self.SetupFeatures(empty = False)
        toc = time.time()
        print('Setup features: ', toc-tic)
        self.GUIObject.tileFrame.ConstructionMenuFunction = TileClass.FeatureClass.ConstructionMenuFunction
        self.GUIObject.tileFrame.RemoveFeatureFunction = TileClass.FeatureClass.RemoveFeatureFunction
        self.GUIObject.minimap.minimapFilter[0] = 'elevation'
        self.GUIObject.minimap.UpdateMinimap()

        Animation.AnimationClass.Initialize(self.settings.ELEVATION_SCALE, self)

        self.SetupUnits()

        # --------------------------------------------------------------------------------------------------------------
        # --------------------------------------------------------------------------------------------------------------

        base.setFrameRateMeter(True)

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

        self.leftMouseClickCooldown = 0
        self.leftMouseClickCooldownMax = 0.1
        self.LeftMouseButtonFunction = self.StandardClicker
        self.add_task(self.MouseClickTask, 'mouse_click')
        self.add_task(self.AnimationTask, 'animation_task')
        self.add_task(self.cameraObject.AttachDetachNodes, 'Attach_Detach_Nodes')

    def AnimationTask(self, task):
        Animation.AnimationClass.AnimationTaskFunction()
        return task.cont

    def UpdateKeyDictionary(self, key, status):
        self.inputDictionary[key] = status

    def SetupFeatures(self, empty = False):
        self.tilesToRender = []
        self.tilesBeingRendered = []

        self.featureTemplateDictionary = FeatureTemplateDictionary.GetFeatureTemplateDictionary()
        TileClass.FeatureClass.Initialize(featureTemplates = self.featureTemplateDictionary, pandaProgram = self)
        if empty == False:
            for row in range(self.settings.N_ROWS):
                for colon in range(self.settings.N_COLONS):
                    iTile = colon + row * self.settings.N_COLONS
                    if self.tileList[iTile].isWater:
                        pass
                    else:
                        if self.plants[row][colon]:
                            if self.plants[row][colon].featureTemplate:
                                self.tileList[iTile].features.append(TileClass.FeatureClass(parentTile=self.tileList[iTile],
                                                                                            type=self.plants[row][colon].featureTemplate,
                                                                                            numberOfcomponents=int(np.ceil(self.plants[row][colon].fitness*20)),
                                                                                            parentNode = self.featureRoot))
                                #self.tileList[iTile].features[0].node.removeNode()
                        if self.animals[row][colon]:
                            if self.animals[row][colon].featureTemplate:
                                self.tileList[iTile].features.append(TileClass.FeatureClass(parentTile=self.tileList[iTile],
                                                                                            type=self.animals[row][colon].featureTemplate,
                                                                                            numberOfcomponents=int(np.ceil(self.animals[row][colon].fitness*20)),
                                                                                            parentNode = self.wildlifeRoot))
                                #self.tileList[iTile].features[0].node.removeNode()
                        for feature in self.tileList[iTile].features:
                            feature.node.removeNode()

                        '''
                        r = np.random.rand()
                        a = False
                        if r < 0.2:
                            self.tileList[iTile].features.append(TileClass.FeatureClass(parentTile=self.tileList[iTile],
                                                                                        type='jungle',
                                                                                        numberOfcomponents=20))
                            self.tileList[iTile].features[0].node.removeNode()

                        elif r < 0.4:
                            self.tileList[iTile].features.append(TileClass.FeatureClass(parentTile=self.tileList[iTile],
                                                                                        type='conifer_forest',
                                                                                        numberOfcomponents=20))
                            self.tileList[iTile].features[0].node.removeNode()
                        elif r < 0.6:
                            self.tileList[iTile].features.append(TileClass.FeatureClass(parentTile=self.tileList[iTile],
                                                                                        type='temperate_forest',
                                                                                        numberOfcomponents=20))
                            self.tileList[iTile].features[0].node.removeNode()
                        '''


    def SetupTiles(self):
        self.tileList = []
        TileClass.TileClass.Initialize(self.settings.N_ROWS, self.settings.N_COLONS,
                                       tileList = self.tileList,
                                       pandaProgram = self)

        Pathfinding.MapGraph.Initialize(mainProgram=self)
        self.mapGraph = Pathfinding.MapGraph()
        self.mapGraph.CreateEdgesSimple(self.settings.N_ROWS, self.settings.N_COLONS)

        tic = time.time()
        # Initializes the tiles
        for row in range(self.settings.N_ROWS):
            for colon in range(self.settings.N_COLONS):
                self.tileList.append(TileClass.TileClass(row, colon, self.world.elevation[row, colon]))
        toc = time.time()
        print('object creation time: {}'.format(toc - tic))

        #from scipy import interpolate
        #extentedElevation = np.concatenate((self.world.elevation[:, self.settings.N_COLONS-2:self.settings.N_COLONS],
        #                                    self.world.elevation,
        #                                    self.world.elevation[:, 0:2]),
        #                                   axis=1)
        #self.elevationInterpolator = interpolate.interp2d(np.linspace(-2, self.settings.N_COLONS-1+2, self.settings.N_COLONS+4),
        #                                                  np.linspace(0, self.settings.N_ROWS-1, self.settings.N_ROWS),
        #                                                  extentedElevation, kind='cubic', fill_value=0)
        #self.elevationInterpolator = self.world.elevationInterpolated
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
                self.tileList[iTile].ApplyNormals()
                #self.tileList[iTile].CreateNormals()
                self.tileList[iTile].NormalizeNormals()
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
                self.tileList[iTile].NormalizeNormals()
        toc = time.time()
        print('Normalize normals: {}'.format(toc - tic))

        tic = time.time()
        '''
        import cProfile, pstats, io
        from pstats import SortKey
        pr = cProfile.Profile()
        pr.enable()
        '''
        for row in range(self.settings.N_ROWS):
            for colon in range(self.settings.N_COLONS):
                iTile = colon + row * self.settings.N_COLONS
                # self.tileList[iTile].CreateNode()
                #self.tileList[iTile].ApplyNode()
                self.tileList[iTile].CreateNodeExperimental()
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
        print('CreateNodeExperimental: {}'.format(toc - tic))

        for row in range(self.settings.N_ROWS):
            for colon in range(self.settings.N_COLONS):
                if self.world.elevation[row, colon] <= self.settings.OCEAN_HEIGHT:
                    iTile = colon + row * self.settings.N_COLONS
                    #isOcean = self.world.elevation[row, colon] <= 1
                    self.tileList[iTile].CreateWater(isOcean = True)

        tic = time.time()
        for row in range(self.settings.N_ROWS):
            for colon in range(self.settings.N_COLONS):
                #if self.world.elevation[row, colon] <= 1:
                iTile = colon + row * self.settings.N_COLONS
                if self.tileList[iTile].isWater or self.tileList[iTile].isShore:
                    self.tileList[iTile].CreateWaterNode()
                    self.tileList[iTile].ApplyWaterTexture()
        toc = time.time()
        print('Create water nodes: {}'.format(toc - tic))

        tic = time.time()
        for row in range(self.settings.N_ROWS):
            for colon in range(self.settings.N_COLONS):
                iTile = colon + row * self.settings.N_COLONS
                #self.tileList[iTile].CreateTextureArrayDebug()
                self.tileList[iTile].CreateTextureArray()
                #self.tileList[iTile].AddSlopeTexture()
        toc = time.time()
        print('Create texture array (slopes included): {}'.format(toc - tic))

        for row in range(self.settings.N_ROWS):
            for colon in range(self.settings.N_COLONS):
                iTile = colon + row * self.settings.N_COLONS
                self.tileList[iTile].ApplyTexture()

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
        self.tileMarker = loader.loadModel(Root_Directory.Path(style = 'unix') + "/Data/Models/tile_select_marker_3.dae")
        self.tileMarker.setPos(p3d.LPoint3(0, 0, 0))
        self.tileMarker.set_hpr(0, 90, 0)
        self.tileMarker.set_scale((0.5, 1, 0.5))

        tic = time.time()
        TileClass.TileClass.SaveDictionariesToFile()
        toc = time.time()
        print('Save dictionaries to file: {}'.format(toc - tic))

    def SetupUnits(self):
        self.units = {}
        TileClass.UnitClass.Initialize(unitRoot = self.unitRoot,
                                       ELEVATION_SCALE = self.settings.ELEVATION_SCALE,
                                       unitDictionary = self.units,
                                       tileList = self.tileList,
                                       standardClicker= self.StandardClicker,
                                       ChessboardDemo = self)
        self.unitMarker = loader.loadModel(Root_Directory.Path(style = 'unix') + "/Data/Models/unit_select_marker.dae")
        self.unitMarker.setPos(p3d.LPoint3(0, 0, 0))
        self.unitMarker.set_hpr(0, 90, 0)

        Pathfinding.MapGraph.Initialize(mainProgram=self)
        self.movementGraph = Pathfinding.MapGraph()
        self.movementGraph.CreateEdges(self.settings.N_ROWS, self.settings.N_COLONS)

    def SetupPicker(self):
        # Since we are using collision detection to do picking, we set it up like
        # any other collision detection system with a traverser and a handler
        self.picker = p3d.CollisionTraverser()  # Make a traverser
        self.pq = p3d.CollisionHandlerQueue()  # Make a handler
        # Make a collision node for our picker ray
        self.pickerNode = p3d.CollisionNode('mouseRay')
        # Attach that node to the camera since the ray will need to be positioned
        # relative to it
        self.pickerNP = camera.attachNewNode(self.pickerNode)
        # Everything to be picked will use bit 1. This way if we were doing other
        # collision we could separate it
        self.pickerNode.setFromCollideMask(p3d.GeomNode.getDefaultCollideMask())
        self.pickerRay = p3d.CollisionRay()  # Make our ray
        # Add it to the collision node
        self.pickerNode.addSolid(self.pickerRay)
        # Register the ray as something that can cause collisions
        self.picker.addCollider(self.pickerNP, self.pq)

    def MouseClickTask(self, task):
        if self.leftMouseClickCooldown < 0:
            if self.inputDictionary['mouse1']:
                self.leftMouseClickCooldown = self.leftMouseClickCooldownMax
                self.LeftMouseButtonFunction()
        else:
            dt = globalClock.get_dt()
            self.leftMouseClickCooldown -= dt

        # On right-click
        if self.inputDictionary['escape'] or self.inputDictionary['mouse3']:

            if self.selected_unit_ID:
                print(self.units[self.selected_unit_ID].isSelected)
                self.units[self.selected_unit_ID].isSelected = False
                print(self.units[self.selected_unit_ID].isSelected)
                print(print('---------'))

            self.selected_tile_ID = None
            self.selected_unit_ID = None
            self.unitMarker.detachNode()
            self.tileMarker.detachNode()

            self.GUIObject.unitFrame.frame.hide()
            self.GUIObject.tileFrame.frame.hide()
            self.GUIObject.tileFrame.constructionMenu.hide()

            TileClass.UnitClass.AddUnitButtonFunction(0)
            self.GUIObject.add_unit_button['indicatorValue'] = False
            self.GUIObject.add_unit_button.setIndicatorValue()

            #for buttonKey in self.GUIObject.unitFrame.buttons:
            #    print(buttonKey)
            #    button = self.GUIObject.unitFrame.buttons[buttonKey]
            #    button['indicatorValue'] = False
            #    button.setIndicatorValue()

            TileClass.UnitClass.AddUnitButtonFunction(0)
            #self.GUIObject.add_unit_button['indicatorValue'] = False
            #self.GUIObject.add_unit_button.setIndicatorValue()

            TileClass.UnitClass.MoveUnitButtonFunction(0)
            self.GUIObject.unitFrame.buttons['move']['indicatorValue'] = False
            self.GUIObject.unitFrame.buttons['move'].setIndicatorValue()

            self.LeftMouseButtonFunction = self.StandardClicker

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
        print('This is located in StandardPicker()')
        print(tileID)
        print(unitID)
        print(' ')
        return tileID, unitID

    def StandardClicker(self):
        tileID, unitID = self.StandardPicker()

        if tileID:
            self.SelectTile(tileID)

        elif unitID is not None:
            self.SelectUnit(unitID)

    def SelectTileClicker(self):
        tileID, unitID = self.StandardPicker()
        if tileID:
            self.SelectTile(tileID)


    def SelectUnitClicker(self):
        tileID, unitID = self.StandardPicker()
        if unitID is not None:
            self.SelectUnit(unitID)

    def SelectTile(self, tileID):
        self.GUIObject.tileFrame.UnToggleButtons()

        self.selected_tile_ID = tileID

        self.tileMarker.setPos(self.tileList[tileID].colon + 0.5, self.tileList[tileID].row + 0.5,
                               self.settings.ELEVATION_SCALE * (self.tileList[tileID].elevation + 0.1))
        self.tileMarker.reparentTo(render)

        self.GUIObject.tileFrame.frame.show()
        self.LeftMouseButtonFunction = self.SelectTileClicker

    def SelectUnit(self, unitID):
        self.GUIObject.unitFrame.UnToggleButtons()

        self.selected_unit_ID = unitID
        self.selected_tile_ID = None

        self.units[unitID].isSelected = True

        self.unitMarker.setPos(self.units[unitID].colon + 0.5, self.units[unitID].row + 0.5,
                               self.settings.ELEVATION_SCALE * (self.units[unitID].elevation + 0.1))
        self.unitMarker.reparentTo(render)

        self.GUIObject.unitFrame.frame.show()
        self.GUIObject.unitFrame.DestroyUnitFunction = self.units[unitID].Destroy
        self.GUIObject.unitFrame.MoveUnitFunction = self.units[unitID].MoveUnitButtonFunction

        self.LeftMouseButtonFunction = self.SelectUnitClicker


game = Game()
game.run()

