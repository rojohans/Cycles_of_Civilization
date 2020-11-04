from panda3d.core import AmbientLight, DirectionalLight, LightAttrib, LVector3, Spotlight, Vec4, Point3, PointLight
from direct.showbase.ShowBase import ShowBase

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


