from direct.showbase.ShowBase import ShowBase
import panda3d.core as p3d
import numpy as np

import Library.TileClass as TileClass
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

        self.renderCircle = []
        for row in np.linspace(-self.FEATURE_RENDER_RADIUS, self.FEATURE_RENDER_RADIUS, self.FEATURE_RENDER_RADIUS * 2 + 1):
            for colon in np.linspace(-self.FEATURE_RENDER_RADIUS, self.FEATURE_RENDER_RADIUS, self.FEATURE_RENDER_RADIUS * 2 + 1):
                if np.sqrt(row**2 + colon**2) <= self.FEATURE_RENDER_RADIUS:
                    self.renderCircle.append([colon, row])
        self.renderCircle = np.array(self.renderCircle)

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

        #rootModel = (loader.loadModel(Root_Directory.Path(style='unix') + "/Data/Models/8_bit_test.bam"))
        #rootModel.reparentTo(self.featureRoot)
        models = []

        for row in range(self.N_ROWS):
            for colon in range(self.N_COLONS):
                iTile = colon + row * self.N_COLONS
                if True:
                    #self.tileList[iTile].features.append(TileClass.FeatureClass(parentTile=self.tileList[iTile],
                    #                                                            type='8_bit_test',
                    #                                                            numberOfcomponents=20))
                    #self.tileList[iTile].features.append(TileClass.FeatureClass(parentTile=self.tileList[iTile],
                    #                                                            type='temperate_forest',
                    #                                                            numberOfcomponents=20))
                    self.tileList[iTile].features.append(TileClass.FeatureClass(parentTile=self.tileList[iTile],
                                                                                type='town',
                                                                                numberOfcomponents=20,
                                                                                distributionType='grid',
                                                                                distributionValue=7,
                                                                                gridAlignedHPR=True
                                                                                ))
                    self.tileList[iTile].features[0].node.removeNode()

                else:

                    for i in range(20):
                        # models.append(loader.loadModel("panda3d-master/samples/chessboard/models/8_bit_test.bam"))

                        #models.append(loader.loadModel("panda3d-master/samples/chessboard/models/oak_1.bam"))


                        models.append(self.featureRoot.attachNewNode('featureNode'))

                        #self.featureTemplateDictionary['8_bit_test'].models[0].copyTo(models[-1])
                        self.featureTemplateDictionary['8_bit_test'].models[0].instanceTo(models[-1])

                        rowOffset, colonOffset = np.random.randint(0, self.MODEL_RESOLUTION,2)/self.MODEL_RESOLUTION
                        models[-1].setPos(p3d.LPoint3(colon + colonOffset, row + rowOffset, 0))
                        models[-1].set_hpr(360 * np.random.rand(), 90, 0)
                        models[-1].setScale(2.2, 2.2, 2.2)
                        models[-1].setTransparency(p3d.TransparencyAttrib.MAlpha)
                        models[-1].clearModelNodes()


        base.setFrameRateMeter(True)






        self.camera_node = self.render.attach_new_node('camera_node')
        self.camera_focal_node = self.camera_node.attach_new_node('gimbal')

        camera_offset = (0, -3, 3)
        self.camera.set_pos(self.camera_focal_node, camera_offset)
        self.camera.look_at(self.camera_focal_node)
        self.camera.wrt_reparent_to(self.camera_node)
        self.camera_node.set_pos(10, 10, 5)

        self.camera_direction_angle = 0
        self.camera_forward_vector = p3d.Vec3(np.sin(self.camera_direction_angle), np.cos(self.camera_direction_angle), 0)
        self.camera_right_vector = p3d.Vec3(np.cos(self.camera_direction_angle), np.sin(self.camera_direction_angle), 0)

        self.camera_rotation_speed = 100.0
        self.camera_move_speed = 10.0
        self.camera_zoom_speed = 10.0
        self.camera_zoom_damping = 2.0
        self.camera_p_limit = p3d.Vec2(-65, 10)
        self.zoom_limit = [3, 20]
        self.zoom = 0
        self.accept('wheel_up', self.zoom_control, [-0.55])
        self.accept('wheel_down', self.zoom_control, [0.55])
        self.key_down = {}


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


        self.add_task(self.camera_update, 'camera_update')

        self.leftMouseClickCooldown = 0
        self.leftMouseClickCooldownMax = 0.1
        #self.LeftMouseButtonFunction = self.StandardClicker
        #self.add_task(self.MouseClickTask, 'mouse_click')
        #self.add_task(self.AnimationTask, 'animation_task')
        #self.debugTask = taskMgr.add(self.DebugPicker, 'debugTask')
        self.disableMouse()

        self.camera_zoom_limit = (0, 30)
        self.camera_zoom_value = 0.5
        self.camera.look_at(self.camera_focal_node)

        self.last_mouse_pos = None

        self.add_task(self.AttachDetachNodes, 'Attach_Detach_Nodes')

    def Camera_Zoom_Scaling(self, axis, zoom):
        if axis == 'x':
            pass
        elif axis == 'y':
            # return 18*(2-(zoom+1)) / (2*(zoom+1))
            # return 38*(2-(zoom+1)) / (2*(zoom+1))

            return 2 * (1 - zoom ** 1)
            # y0 = 4
            # y1 = 6
            # c = 0.3
            # return (y0-y1)/c**2*(zoom-c)**2 + y1
        elif axis == 'z':
            # return 3+27*zoom
            # return 1 + 15 * zoom
            return 0.5 + 18 * (zoom) ** 1

    def Get_Camera_Move_Speed(self, zoom):
        return 6 + 16 * zoom

    def UpdateKeyDictionary(self, key, status):
        self.inputDictionary[key] = status

    def zoom_control(self, amount):
        self.zoom = amount

    def camera_update(self, task):
        '''This function is a task run each frame,
           it controls the camera movement/rotation/zoom'''

        dt = globalClock.get_dt()

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
                distance = self.camera.get_distance(self.camera_node)

                self.zoom *= 0.1

                # self.camera_zoom_value = min(max(self.camera_zoom_value + self.zoom, self.camera_zoom_limit[0]), self.camera_zoom_limit[1])
                self.camera_zoom_value = min(max(self.camera_zoom_value + 30 * dt * self.zoom, 0), 1)

                # self.camera_node.set_pos(self.camera_focal_node, 0, -self.Camera_Zoom_Scaling('y', self.camera_zoom_value), self.Camera_Zoom_Scaling('z', self.camera_zoom_value))

                self.camera_focal_node.set_pos(self.camera_node, 0,
                                               self.Camera_Zoom_Scaling('y', self.camera_zoom_value),
                                               -self.Camera_Zoom_Scaling('z', self.camera_zoom_value))
                cameraPositon = self.camera_node.get_pos()
                self.camera_node.set_pos(cameraPositon[0], cameraPositon[1],
                                         self.Camera_Zoom_Scaling('z', self.camera_zoom_value))

                self.camera.look_at(self.camera_focal_node)

                if self.zoom >= 0.0:
                    self.zoom -= dt * self.camera_zoom_damping
                    if self.zoom < 0: self.zoom = 0
                else:
                    self.zoom += dt * self.camera_zoom_damping
                    if self.zoom > 0: self.zoom = 0

            if self.inputDictionary['mouse4']:
                h = self.camera_node.get_h() - mouse_delta.x * self.camera_rotation_speed
                self.camera_node.set_h(h)

        self.camera_move_speed = self.Get_Camera_Move_Speed(self.camera_zoom_value)
        if self.inputDictionary['arrow_up'] or self.inputDictionary['w']:
            self.camera_node.set_pos(self.camera_node,
                                     self.camera_forward_vector * 0.01 * self.camera_move_speed * dt / 0.03)
        elif self.inputDictionary['arrow_down'] or self.inputDictionary['s']:
            self.camera_node.set_pos(self.camera_node,
                                     -self.camera_forward_vector * 0.01 * self.camera_move_speed * dt / 0.03)
        if self.inputDictionary['arrow_left'] or self.inputDictionary['a']:
            self.camera_node.set_pos(self.camera_node,
                                     -self.camera_right_vector * 0.01 * self.camera_move_speed * dt / 0.03)
        elif self.inputDictionary['arrow_right'] or self.inputDictionary['d']:
            self.camera_node.set_pos(self.camera_node,
                                     self.camera_right_vector * 0.01 * self.camera_move_speed * dt / 0.03)
        if self.inputDictionary['arrow_up'] or \
                self.inputDictionary['w'] or \
                self.inputDictionary['arrow_down'] or \
                self.inputDictionary['s'] or \
                self.inputDictionary['arrow_left'] or \
                self.inputDictionary['a'] or \
                self.inputDictionary['arrow_right'] or \
                self.inputDictionary['d']:
            renderCircle = self.GetRenderCircle()
            for tilePos in renderCircle:
                if tilePos[1] >= 0 and tilePos[1] < self.N_ROWS:
                    iTile = TileClass.TileClass.CoordinateToIndex(tilePos[1], tilePos[0])

                    if self.tilesBeingRendered.count(iTile) == 1:
                        # already exists
                        self.tilesBeingRendered.remove(iTile)
                        self.tilesBeingRendered.insert(0, iTile)
                    elif self.tilesToRender.count(iTile) == 1:
                        pass
                    else:
                        self.tilesToRender.append(iTile)

                    '''
                    if self.tileList[iTile].featureDuration < 0:
                        self.tileList[iTile].featureDuration = self.FEATURE_RENDER_DURATION
                    else:
                        self.tileList[iTile].featureDuration = self.FEATURE_RENDER_DURATION - 1
                    '''


        # When the camera traverses over the edge (west or east) it wraps around to the other side.
        cameraPosition = self.camera_node.get_pos()
        if cameraPosition[0] < 0:
            self.camera_node.set_pos((cameraPosition[0] + self.N_COLONS, cameraPosition[1], cameraPosition[2]))
        if cameraPosition[0] > self.N_COLONS:
            self.camera_node.set_pos((cameraPosition[0] - self.N_COLONS, cameraPosition[1], cameraPosition[2]))

        return task.cont
        # --------------------------------------------------------------------------------------------------------------
        # --------------------------------------------------------------------------------------------------------------

    def GetRenderCircle(self):
        position = self.camera_node.get_pos()
        position = np.floor(position)
        position = position[0:2]


        renderCircle = self.renderCircle.copy()
        renderCircle[:, 0] += position[0]
        renderCircle[:, 1] += position[1]

        renderCircle[:, 0] = (renderCircle[:, 0]+self.N_COLONS) % self.N_COLONS
        return renderCircle

    def AttachDetachNodes(self, task):
        '''
        Dynamically attaches (reparentTo()) and detaches (detachNode()) to reduce memory usage.
        :param task:
        :return:
        '''

        for i in range(self.FEATURE_RENDER_MAX_SPEED):
            if len(self.tilesToRender) > 0:
                # Add node
                tileToRender = self.tilesToRender.pop(0)
                self.tilesBeingRendered.insert(0, tileToRender)
                #self.tileList[tileToRender].features.append(TileClass.FeatureClass(parentTile=self.tileList[tileToRender],
                #                                                            type='town',
                #                                                            numberOfcomponents=20,
                #                                                            distributionType='grid',
                #                                                            distributionValue=7,
                #                                                            gridAlignedHPR=True
                #d                                                            ))
                self.tileList[tileToRender].features[0].CreateNodes()

            if len(self.tilesBeingRendered) > self.FEATURE_RENDER_CAPACITY:
                # Remove node
                tileToRemove = self.tilesBeingRendered.pop()
                self.tileList[tileToRemove].features[0].node.removeNode()

        return task.cont


game = Game()
game.run()