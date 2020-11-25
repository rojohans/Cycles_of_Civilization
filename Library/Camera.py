from direct.showbase.ShowBase import ShowBase
import panda3d.core as p3d
import Library.TileClass as TileClass
import numpy as np

class CameraClass():
    def __init__(self):

        self.camera_node = render.attach_new_node('camera_node')
        self.camera_focal_node = self.camera_node.attach_new_node('gimbal')

        camera_offset = (0, -3, 3)
        camera.set_pos(self.camera_focal_node, camera_offset)
        camera.look_at(self.camera_focal_node)
        camera.wrt_reparent_to(self.camera_node)
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
        self.mainProgram.accept('wheel_up', self.zoom_control, [-0.55])
        self.mainProgram.accept('wheel_down', self.zoom_control, [0.55])

        self.camera_zoom_limit = (0, 30)
        self.camera_zoom_value = 0.5
        camera.look_at(self.camera_focal_node)

        self.last_mouse_pos = None

        self.mainProgram.add_task(self.camera_update, 'camera_update')

        self.mainProgram.disableMouse()

        self.cameraUpdateFunctions = []

        self.timeSinceFeatureUpdate = 0
        self.featureUpdateInterval = 1

    @classmethod
    def Initialize(cls, mainProgram):
        cls.mainProgram = mainProgram

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

    def zoom_control(self, amount):
        self.zoom = amount

    def camera_update(self, task):
        '''This function is a task run each frame,
           it controls the camera movement/rotation/zoom'''

        dt = globalClock.get_dt()

        self.timeSinceFeatureUpdate += dt

        if self.mainProgram.mouseWatcherNode.has_mouse():
            # let's see where the mouse cursor is now
            mouse_pos = self.mainProgram.mouseWatcherNode.get_mouse()
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
                distance = camera.get_distance(self.camera_node)

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

                self.mainProgram.camera.look_at(self.camera_focal_node)

                if self.zoom >= 0.0:
                    self.zoom -= dt * self.camera_zoom_damping
                    if self.zoom < 0: self.zoom = 0
                else:
                    self.zoom += dt * self.camera_zoom_damping
                    if self.zoom > 0: self.zoom = 0

            if self.mainProgram.inputDictionary['mouse4'] or self.mainProgram.inputDictionary['mouse2']:
                # Rotate camera.
                h = self.camera_node.get_h() - mouse_delta.x * self.camera_rotation_speed
                self.camera_node.set_h(h)

        self.camera_move_speed = self.Get_Camera_Move_Speed(self.camera_zoom_value)
        if self.mainProgram.inputDictionary['arrow_up'] or self.mainProgram.inputDictionary['w']:
            self.camera_node.set_pos(self.camera_node,
                                     self.camera_forward_vector * 0.01 * self.camera_move_speed * dt / 0.03)
        elif self.mainProgram.inputDictionary['arrow_down'] or self.mainProgram.inputDictionary['s']:
            self.camera_node.set_pos(self.camera_node,
                                     -self.camera_forward_vector * 0.01 * self.camera_move_speed * dt / 0.03)
        if self.mainProgram.inputDictionary['arrow_left'] or self.mainProgram.inputDictionary['a']:
            self.camera_node.set_pos(self.camera_node,
                                     -self.camera_right_vector * 0.01 * self.camera_move_speed * dt / 0.03)
        elif self.mainProgram.inputDictionary['arrow_right'] or self.mainProgram.inputDictionary['d']:
            self.camera_node.set_pos(self.camera_node,
                                     self.camera_right_vector * 0.01 * self.camera_move_speed * dt / 0.03)

        if self.timeSinceFeatureUpdate > self.featureUpdateInterval:
            for cameraUpdateFunction in self.cameraUpdateFunctions:
                cameraUpdateFunction()
            self.timeSinceFeatureUpdate -= self.featureUpdateInterval

        # When the camera traverses over the edge (west or east) it wraps around to the other side.
        cameraPosition = self.camera_node.get_pos()
        if cameraPosition[0] < 0:
            self.camera_node.set_pos((cameraPosition[0] + self.mainProgram.settings.N_COLONS, cameraPosition[1], cameraPosition[2]))
        if cameraPosition[0] > self.mainProgram.settings.N_COLONS:
            self.camera_node.set_pos((cameraPosition[0] - self.mainProgram.settings.N_COLONS, cameraPosition[1], cameraPosition[2]))

        return task.cont

    def UpdateFeatureRender(self):
        '''
        Checks which, if any, new tiles should be rendered.
        :return:
        '''
        renderCircle = self.GetRenderCircle()
        for tilePos in renderCircle:
            if tilePos[1] >= 0 and tilePos[1] < self.mainProgram.settings.N_ROWS:
                iTile = TileClass.TileClass.CoordinateToIndex(tilePos[1], tilePos[0])

                if self.mainProgram.tilesBeingRendered.count(iTile) == 1:
                    # already exists
                    self.mainProgram.tilesBeingRendered.remove(iTile)
                    self.mainProgram.tilesBeingRendered.insert(0, iTile)
                elif self.mainProgram.tilesToRender.count(iTile) == 1:
                    pass
                else:
                    #self.mainProgram.tilesToRender.append(iTile)
                    self.mainProgram.tilesToRender.insert(0, iTile)

    def GetRenderCircle(self):
        '''
        Return the render circle around the cameras current position.
        :return:
        '''
        position = self.camera_node.get_pos()
        position = np.floor(position)
        position = position[0:2]

        renderCircle = self.mainProgram.RENDER_CIRCLE.copy()
        renderCircle[:, 0] += position[0]
        renderCircle[:, 1] += position[1]

        renderCircle[:, 0] = (renderCircle[:, 0]+self.mainProgram.settings.N_COLONS) % self.mainProgram.settings.N_COLONS
        return renderCircle

    def AttachDetachNodes(self, task):
        '''
        Dynamically attaches (reparentTo()) and detaches (detachNode()) to reduce memory usage.
        :param task:
        :return:
        '''

        for i in range(self.mainProgram.settings.FEATURE_RENDER_MAX_SPEED):
            if len(self.mainProgram.tilesToRender) > 0:
                # Add node
                tileToRender = self.mainProgram.tilesToRender.pop(0)
                self.mainProgram.tilesBeingRendered.insert(0, tileToRender)
                for feature in self.mainProgram.tileList[tileToRender].features:
                    feature.CreateNodes()
                #self.mainProgram.tileList[tileToRender].features[0].CreateNodes()

            if len(self.mainProgram.tilesBeingRendered) > self.mainProgram.settings.FEATURE_RENDER_CAPACITY:
                # Remove node
                tileToRemove = self.mainProgram.tilesBeingRendered.pop()
                for feature in self.mainProgram.tileList[tileToRemove].features:
                    feature.node.removeNode()
                #self.mainProgram.tileList[tileToRemove].features[0].node.removeNode()
        return task.cont

class GlobeCamera():
    def __init__(self, mainProgram, zoomRange = [1.1, 2], zoomSpeed = 0.05, minRadius = 1, rotationSpeedRange = [np.pi/50, np.pi/10]):
        self.mainProgram = mainProgram
        self.zoomRange = zoomRange
        self.minRadius = minRadius
        self.rotationSpeedRange = rotationSpeedRange
        self.zoomSpeed = zoomSpeed
        self.zoomAmount = 0

        self.featureNodeUpdateTimer = 0

        #self.camera = render.attach_new_node('camera_node')
        #self.focalPoint = self.camera.attach_new_node('gimbal')

        self.focalPoint = render.attach_new_node('gimbal')
        self.camera = render.attach_new_node('camera_node')

        self.zoom = 1

        self.focalPosition = {'longitude':np.pi/2, 'latitude':0, 'x':0, 'y':self.minRadius, 'z':0}
        self.cameraPosition = {'x':self.focalPosition['x']*(self.zoomRange[0] + self.zoom*(self.zoomRange[1]-self.zoomRange[0]))/self.minRadius,
                               'y':self.focalPosition['y']*(self.zoomRange[0] + self.zoom*(self.zoomRange[1]-self.zoomRange[0]))/self.minRadius,
                               'z':self.focalPosition['z']*(self.zoomRange[0] + self.zoom*(self.zoomRange[1]-self.zoomRange[0]))/self.minRadius}

        #camera_offset = (0, -3, 3)
        self.focalPoint.set_pos(self.focalPosition['x'], self.focalPosition['y'], self.focalPosition['z'])
        #self.camera.set_pos(100, 0, 0)
        #camera.set_pos(self.focalPoint, camera_offset)
        #camera.set_pos(self.focalPoint, (0, self.zoomRange[1]-self.zoomRange[0], 0))
        #camera.look_at(self.focalPoint)
        camera.wrt_reparent_to(self.camera)
        self.camera.set_pos(self.cameraPosition['x'], self.cameraPosition['y'], self.cameraPosition['z'])
        self.camera.look_at(self.focalPoint)

        #self.camera_direction_angle = 0
        #self.camera_forward_vector = p3d.Vec3(np.sin(self.camera_direction_angle), np.cos(self.camera_direction_angle),0)
        #self.camera_right_vector = p3d.Vec3(np.cos(self.camera_direction_angle), np.sin(self.camera_direction_angle), 0)

        #self.camera_rotation_speed = 100.0
        #self.camera_move_speed = 10.0
        #self.camera_zoom_speed = 10.0
        #self.camera_zoom_damping = 2.0
        #self.camera_p_limit = p3d.Vec2(-65, 10)
        #self.zoom_limit = [3, 20]

        #self.mainProgram.accept('wheel_up', self.zoom_control, [-0.55])
        #self.mainProgram.accept('wheel_down', self.zoom_control, [0.55])

        #self.camera_zoom_limit = (0, 30)
        #self.camera_zoom_value = 0.5
        camera.look_at(self.focalPoint)

        #self.last_mouse_pos = None

        #self.mainProgram.add_task(self.camera_update, 'camera_update')

        self.mainProgram.disableMouse()

        #self.cameraUpdateFunctions = []

        #self.timeSinceFeatureUpdate = 0
        #self.featureUpdateInterval = 1


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
            self.mainProgram.accept(key, self.UpdateKeyDictionary, [key, True])
            self.mainProgram.accept(key + '-up', self.UpdateKeyDictionary, [key, False])

        self.mainProgram.accept('mouse1', self.LeftMouseClick)
        self.mainProgram.accept('mouse3', self.RightMouseClick)

        self.mainProgram.accept('wheel_up', self.zoom_control, [-zoomSpeed])
        self.mainProgram.accept('wheel_down', self.zoom_control, [zoomSpeed])

        self.mainProgram.add_task(self.CameraTask, 'camera_update')

    def zoom_control(self, amount):
        #self.zoom += (0.1+np.sqrt(self.zoom))*amount#(self.zoom+0.1)/1.1*amount
        #self.zoom = np.max((0, self.zoom))
        #self.zoom = np.min((1, self.zoom))
        self.zoomAmount = amount

    def UpdateKeyDictionary(self, key, status):
        self.inputDictionary[key] = status

    def CameraTask(self, Task):
        dt = globalClock.get_dt()

        # camera zoom
        if self.zoom != 0.0:
            pass
            #print(self.zoom)

        updateCamera = False

        if self.zoomAmount != 0:
            self.zoom += (0.1 + np.sqrt(self.zoom)) * self.zoomAmount  # (self.zoom+0.1)/1.1*amount
            self.zoom = np.max((0, self.zoom))
            self.zoom = np.min((1, self.zoom))
            self.zoomAmount = 0
            updateCamera = True

        dAngle = self.rotationSpeedRange[0] + self.zoom * (self.rotationSpeedRange[1]-self.rotationSpeedRange[0]) * 60*dt

        if self.inputDictionary['arrow_up'] or self.inputDictionary['w']:
            self.focalPosition['latitude'] += dAngle
            self.focalPosition['latitude'] = np.min((np.pi/2, self.focalPosition['latitude']))
            updateCamera = True
        elif self.inputDictionary['arrow_down'] or self.inputDictionary['s']:
            self.focalPosition['latitude'] -= dAngle
            self.focalPosition['latitude'] = np.max((-np.pi/2, self.focalPosition['latitude']))
            updateCamera = True
        if self.inputDictionary['arrow_left'] or self.inputDictionary['a']:
            self.focalPosition['longitude'] -= dAngle
            self.focalPosition['longitude'] = (self.focalPosition['longitude']+2*np.pi)%(2*np.pi)
            updateCamera = True
        elif self.inputDictionary['arrow_right'] or self.inputDictionary['d']:
            self.focalPosition['longitude'] += dAngle
            self.focalPosition['longitude'] = (self.focalPosition['longitude'] + 2*np.pi) % (2*np.pi)
            updateCamera = True
        if updateCamera:
            self.focalPosition['x'] = self.minRadius*np.cos(self.focalPosition['longitude'])*np.cos(self.focalPosition['latitude'])
            self.focalPosition['y'] = self.minRadius*np.sin(self.focalPosition['longitude'])*np.cos(self.focalPosition['latitude'])
            self.focalPosition['z'] = self.minRadius*np.sin(self.focalPosition['latitude'])
            self.focalPoint.set_pos(self.focalPosition['x'], self.focalPosition['y'], self.focalPosition['z'])

            self.cameraPosition['x'] = self.focalPosition['x']*(self.zoomRange[0] + self.zoom*(self.zoomRange[1]-self.zoomRange[0]))/self.minRadius
            self.cameraPosition['y'] = self.focalPosition['y']*(self.zoomRange[0] + self.zoom*(self.zoomRange[1]-self.zoomRange[0]))/self.minRadius
            self.cameraPosition['z'] = self.focalPosition['z']*(self.zoomRange[0] + self.zoom*(self.zoomRange[1]-self.zoomRange[0]))/self.minRadius
            self.camera.set_pos(self.cameraPosition['x'], self.cameraPosition['y'], self.cameraPosition['z'])

            self.camera.look_at(self.focalPoint)

        self.featureNodeUpdateTimer += dt
        if self.featureNodeUpdateTimer >= 1:
            self.featureNodeUpdateTimer -= 1
            # Updates the visible/hidden state of the feature nodes depending on angle.
            for featureNode in self.mainProgram.forestNodeClusters:
                #print(np.abs(featureNode.longitude - self.focalPosition['longitude']))
                #if np.abs(featureNode.longitude - self.focalPosition['longitude']) < 0.5:


                longitudeDifference = abs((featureNode.longitude + 2 * np.pi) % (2 * np.pi) - (
                            self.focalPosition['longitude'] + 2 * np.pi) % (2 * np.pi))
                longitudeDifference = np.min([longitudeDifference, 2*np.pi-longitudeDifference])
                latitudeDifference = abs(featureNode.latitude - self.focalPosition['latitude'])

                totalAngleDifference = np.sqrt(longitudeDifference**2 + latitudeDifference**2)

                if totalAngleDifference < np.pi/3:
                    featureNode.LODNodePath.show()
                else:
                    featureNode.LODNodePath.hide()


            # Updates visible/hidden state of the features nodes depending on distance. Textures are also updated.
            if np.sqrt(self.cameraPosition['x']**2 + self.cameraPosition['y']**2 + self.cameraPosition['z']**2) < self.mainProgram.farDistance:
                # CLOSE
                self.mainProgram.planet.setTexture(self.mainProgram.closeTexture.stitchedTexture)
                self.mainProgram.water.setTexture(self.mainProgram.closeTexture.stitchedTexture)
                self.mainProgram.featureRoot.show()
            else:
                # FAR
                self.mainProgram.planet.setTexture(self.mainProgram.farTexture.stitchedTexture)
                self.mainProgram.water.setTexture(self.mainProgram.farTexture.stitchedTexture)
                self.mainProgram.featureRoot.hide()

        return Task.cont

    def LeftMouseClick(self):
        '''
        A tile is selected and highlighted.
        :return:
        '''

        iTile = self.mainProgram.tilePicker()

        planetColor = p3d.GeomVertexWriter(self.mainProgram.planet_vertex_data, 'color')
        waterColor = p3d.GeomVertexWriter(self.mainProgram.water_vertex_data, 'color')

        if iTile != None:
            i = 0
            while not planetColor.isAtEnd():
                #if i < 3 * 5000:
                if i >= 3*iTile and i <= 3*iTile+2:
                    planetColor.setData4(1, 0, 0, 1)
                    waterColor.setData4(1, 0, 0, 1)
                else:
                    planetColor.setData4(1, 1, 1, 1)
                    waterColor.setData4(1, 1, 1, 1)
                i += 1
            self.mainProgram.selectedTile = iTile

            self.mainProgram.interface.frames['tileInformation'].node.show()
            self.mainProgram.interface.frames['tileAction'].node.show()

            tileInformationText = ""
            tileInformationText += 'ID : ' + str(iTile) + '\n'
            tileInformationText += 'Elevation : ' + "{:.3f}".format(self.mainProgram.elevation[iTile]) + '\n'
            tileInformationText += 'Temperature : ' + "{:.3f}".format(self.mainProgram.temperature[iTile, 0]) + '\n'
            if self.mainProgram.isForest[iTile]:
                tileInformationText += 'Features : ' + 'FOREST' + '\n'

            self.mainProgram.interface.labels['tileInformation'].node.setText(tileInformationText)

        print('Tile clicked : ', iTile)

    def RightMouseClick(self):
        '''
        Deselects the selected tile, removing the highlight.
        :return:
        '''
        if self.mainProgram.selectedTile != None:
            planetColor = p3d.GeomVertexWriter(self.mainProgram.planet_vertex_data, 'color')
            waterColor = p3d.GeomVertexWriter(self.mainProgram.water_vertex_data, 'color')
            while not planetColor.isAtEnd():
                planetColor.setData4(1, 1, 1, 1)
                waterColor.setData4(1, 1, 1, 1)
            self.mainProgram.selectedTile = None

            self.mainProgram.interface.frames['tileInformation'].node.hide()
            self.mainProgram.interface.frames['tileAction'].node.hide()

