from panda3d.core import AmbientLight, DirectionalLight, LightAttrib, LVector3, Spotlight, Vec4, Point3, PointLight
from direct.showbase.ShowBase import ShowBase
import numpy as np

class LightClass():
    def __init__(self, shadowsEnabled = False):
        ambientLight = AmbientLight("ambientLight")
        ambientLight.setColor((0.1, 0.1, .15, 1))
        directionalLight = DirectionalLight("directionalLight")
        directionalLight.setDirection(LVector3(25, 25, -45))
        directionalLight.setColor((0.1, 0.1, 0.2, 1))
        #directionalLight.setColor((0, 0, 0.05, 1))

        directionalLight2 = DirectionalLight("directionalLight")
        directionalLight2.setDirection(LVector3(50, 0, -45))
        directionalLight2.setColor((0.1, 0.1, 0.2, 1))
        #directionalLight2.setColor((0, 0, 0.05, 1))

        directionalLight3 = DirectionalLight("directionalLight")
        directionalLight3.setDirection(LVector3(0, 50, -45))
        directionalLight3.setColor((0.1, 0.1, 0.2, 1))
        #directionalLight3.setColor((0, 0, 0.05, 1))

        directionalLight4 = DirectionalLight("directionalLight")
        directionalLight4.setDirection(LVector3(-25, -25, -45))
        directionalLight4.setColor((0.1, 0.1, 0.2, 1))
        #directionalLight4.setColor((0, 0, 0.05, 1))

        #render.setLight(render.attachNewNode(directionalLight))
        #render.setLight(render.attachNewNode(directionalLight2))
        #render.setLight(render.attachNewNode(directionalLight3))
        #render.setLight(render.attachNewNode(directionalLight4))

        #render.setLight(render.attachNewNode(ambientLight))



        '''
        directionalLight = render.attachNewNode(DirectionalLight("directionalLight"))
        directionalLight.node().setScene(render)
        directionalLight.node().setShadowCaster(True, 512, 512)
        directionalLight.node().showFrustum()
        directionalLight.node().getLens().setNearFar(0.001, 200)
        directionalLight.node().getLens().setFilmSize(16, 16)
        #directionalLight.node().setDirection(LVector3(-100, 100, -75))
        directionalLight.node().setDirection(LVector3(-1, 0, -1))
        directionalLight.node().setColor((1, 1, 0.9, 1))
        render.setLight(directionalLight)
        '''

        if shadowsEnabled:
            dLight = DirectionalLight('dLight')
            dLight.setColor(Vec4(1, 1, 0.8, 1))
            dLightNP = render.attachNewNode(dLight)
            dLightNP.setHpr(90, -22.5, 0)
            dLightNP.setPos(260, 16, 100)

            #dLightNP.setHpr(45, -22.5, 0)
            #dLightNP.setPos(140, -140, 100)
            if shadowsEnabled:
                #dLight.setShadowCaster(True, 16384, 16384)
                #dLight.setShadowCaster(True, 8192, 8192)
                dLight.setShadowCaster(True, 4096, 4096)
                dLight.showFrustum()
                dLight.getLens().setFilmSize(64, 16)
                dLight.getLens().setNearFar(1, 500.0)
                render.setShaderAuto()
            render.setLight(dLightNP)
        else:
            directionalLightSun = DirectionalLight("directionalLight")
            directionalLightSun.setDirection(LVector3(-0, 1, 0))
            directionalLightSun.setColor((0.7, 0.7, 0.5, 1))
            self.sun = render.attachNewNode(directionalLightSun)
            render.setLight(self.sun)

            directionalLightSunReverse = PointLight('plight')
            #directionalLightSunReverse = DirectionalLight("directionalLight")
            #directionalLightSunReverse.setDirection(LVector3(25, -25, 45))
            directionalLightSunReverse.setColor((0.3, 0.3, 0.5, 1))
            #render.setLight(render.attachNewNode(directionalLightSunReverse))
            render.setLight(camera.attachNewNode(directionalLightSunReverse))



        '''
        self.light = render.attachNewNode(Spotlight("Spot"))
        self.light.node().setScene(render)
        self.light.node().setShadowCaster(True)
        self.light.node().showFrustum()
        self.light.node().getLens().setFov(40)
        self.light.node().getLens().setNearFar(10, 100)
        render.setLight(self.light)
        '''


        #directionalLight.setShadowCaster(True, 512, 512)
        render.setShaderAuto()

class CameraLight():
    def __init__(self):
        self.cameraLight = PointLight('camera light')
        # directionalLightSunReverse = DirectionalLight("directionalLight")
        # directionalLightSunReverse.setDirection(LVector3(25, -25, 45))
        self.cameraLight.setColor((0.3, 0.3, 0.5, 1))
        # render.setLight(render.attachNewNode(directionalLightSunReverse))
        render.setLight(camera.attachNewNode(self.cameraLight))

class Sun():
    def __init__(self, position = [1, 0, 0], shadowsEnabled = False):
        self.position = position
        self.shadowsEnabled = shadowsEnabled

        # point
        #self.light = PointLight('camera light')
        #self.light.setColor((0.7, 0.7, 0.5, 1))

        # direction
        self.light = DirectionalLight("directionalLight")
        self.light.setDirection(LVector3(-self.position[0], -self.position[1], -self.position[2]))
        self.light.setColor((0.7, 0.7, 0.5, 1))

        if self.shadowsEnabled:
            #self.light.setShadowCaster(True, 16384, 16384)
            #self.light.setShadowCaster(True, 8192, 8192)
            self.light.setShadowCaster(True, 4096, 4096)

            #self.light.showFrustum()
            #self.light.getLens().setFilmSize(64, 16)
            #self.light.getLens().setNearFar(1, 500.0)
            #render.setShaderAuto()
        self.sun = render.attachNewNode(self.light)
        self.sun.setPos(position[0], position[1], position[2])
        render.setLight(self.sun)

    def SetPosition(self, x, y, z):
        self.position = [x, y, z]
        #self.sun.setPos(self.position[0], self.position[1], self.position[2])
        self.light.setDirection(LVector3(-self.position[0], -self.position[1], -self.position[2]))
