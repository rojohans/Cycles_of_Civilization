import panda3d.core as p3d

class SingleFeature():
    def __init__(self, parentNode, model, position, rotation, scale):

        self.node = parentNode.attachNewNode('featureNode')

        model.copyTo(self.node)

        self.node.setPos(p3d.LPoint3(position[0], position[1], position[2]))

        self.node.set_hpr(rotation[0], rotation[1], position[2])
        #self.node.set_hpr(self.node, 0, 0, rotation[2])

        self.node.setScale(scale, scale, scale)
        self.node.setTransparency(p3d.TransparencyAttrib.MAlpha)






