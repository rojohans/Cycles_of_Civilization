from panda3d.core import AmbientLight, DirectionalLight, LightAttrib, LVector3

from direct.showbase.ShowBase import ShowBase

class LightClass():
    def __init__(self):
        ambientLight = AmbientLight("ambientLight")
        ambientLight.setColor((.1, .1, .1, 1))
        directionalLight = DirectionalLight("directionalLight")
        directionalLight.setDirection(LVector3(-100, 100, -75))
        directionalLight.setColor((1, 1, 0.9, 1))

        directionalLight2 = DirectionalLight("directionalLight")
        directionalLight2.setDirection(LVector3(100, 0, -45))
        directionalLight2.setColor((0.1, 0.1, 0.15, 1))

        directionalLight3 = DirectionalLight("directionalLight")
        directionalLight3.setDirection(LVector3(0, -100, -45))
        directionalLight3.setColor((0.1, 0.1, 0.15, 1))

        directionalLight4 = DirectionalLight("directionalLight")
        directionalLight4.setDirection(LVector3(-100, 100, -45))
        directionalLight4.setColor((0.2, 0.1, 0, 1))
        '''
        directionalLight5 = DirectionalLight("directionalLight")
        directionalLight5.setDirection(LVector3(-100, 100, 10))
        directionalLight5.setColor((0.025, 0.025, 0.05, 1))
        '''
        render.setLight(render.attachNewNode(directionalLight))
        render.setLight(render.attachNewNode(directionalLight2))
        render.setLight(render.attachNewNode(directionalLight3))
        render.setLight(render.attachNewNode(directionalLight4))
        #render.setLight(render.attachNewNode(directionalLight5))
        render.setLight(render.attachNewNode(ambientLight))