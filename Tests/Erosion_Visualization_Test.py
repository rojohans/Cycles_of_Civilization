from direct.showbase.ShowBase import ShowBase
import panda3d.core as p3d
import numpy as np
import time
import perlin_numpy
import matplotlib.pyplot as plt

import Library.Erosion as Erosion
import Library.Camera as Camera
import Library.Light as Light

import Settings
import Root_Directory

class Game(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        base.setFrameRateMeter(True)

        self.settings = Settings.SettingsClass()

        #Camera.CameraClass.Initialize(self)
        #self.cameraObject = Camera.CameraClass()
        #self.camera.cameraUpdateFunctions.append(self.camera.UpdateFeatureRender)
        self.light = Light.LightClass(shadowsEnabled=False)

        self.tilesToRender = []
        self.tilesBeingRendered = []

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

        shape = (256, 512)
        self.heightMap = perlin_numpy.generate_fractal_noise_2d(shape, (2, 4), octaves=8, lacunarity=2, persistence=0.8,
                                                                tileable=(False, True))
        self.heightMap -= np.min(self.heightMap)
        self.heightMap /= np.max(self.heightMap)
        #self.heightMap *= 10
        hMap = np.zeros((shape[0], shape[1], 4))
        hMap[:, :, 0] = self.heightMap
        hMap[:, :, 1] = self.heightMap
        hMap[:, :, 2] = self.heightMap
        hMap[:, :, 2] = self.heightMap
        print(np.shape(hMap))
        print(type(hMap))
        plt.imsave(Root_Directory.Path() + '/Data/tmp_Data/' + 'heightMap.png', self.heightMap)

        self.terrain = p3d.GeoMipTerrain('terrain')
        #self.terrain = world.myGeoMipTerrain('terrain')
        self.terrain.setHeightfield(Root_Directory.Path() + '/Data/tmp_Data/' + 'heightMap.png')



        self.terrain.setBlockSize(32)
        #self.terrain.setNear(40)
        #self.terrain.setFar(100)
        #self.terrain.setMinLevel(2)
        #self.terrain.setBruteforce(False)
        #self.terrain.setAutoFlatten(self.terrain.AFMOff)
        #self.terrain.setFocalPoint(base.camera)

        root = self.terrain.getRoot()
        root.reparentTo(render)
        root.setSz(5)

        self.terrain.generate()

        def updateTask(task):
            self.heightMap = perlin_numpy.generate_fractal_noise_2d(shape, (2, 4), octaves=8, lacunarity=2,
                                                                    persistence=0.8,
                                                                    tileable=(False, True))
            self.heightMap -= np.min(self.heightMap)
            self.heightMap /= np.max(self.heightMap)
            plt.imsave(Root_Directory.Path() + '/Data/tmp_Data/' + 'heightMap.png', self.heightMap)
            self.terrain.setHeightfield(Root_Directory.Path() + '/Data/tmp_Data/' + 'heightMap.png')

            self.terrain.update()
            return task.cont

        taskMgr.add(updateTask, "update")

        '''
        # Set up the GeoMipTerrain
        terrain = GeoMipTerrain("myDynamicTerrain")
        terrain.setHeightfield("yourHeightField.png")

        # Set terrain properties
        terrain.setBlockSize(32)
        terrain.setNear(40)
        terrain.setFar(100)
        terrain.setFocalPoint(base.camera)

        # Store the root NodePath for convenience
        root = terrain.getRoot()
        root.reparentTo(render)
        root.setSz(100)

        # Generate it.
        terrain.generate()

        # Add a task to keep updating the terrain
        def updateTask(task):
            terrain.update()
            return task.cont

        taskMgr.add(updateTask, "update")
        '''
    def UpdateKeyDictionary(self, key, status):
        self.inputDictionary[key] = status

game = Game()
game.run()
