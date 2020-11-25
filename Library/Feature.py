import panda3d.core as p3d
import numpy as np

import Library.World as World

class SingleFeature():
    def __init__(self, parentNode, model, position, rotation, scale):

        self.node = parentNode.attachNewNode('featureNode')
        model.copyTo(self.node)

        self.node.setPos(p3d.LPoint3(position[0], position[1], position[2]))
        self.node.set_hpr(rotation[0], rotation[1], position[2])
        self.node.setScale(scale, scale, scale)
        self.node.setTransparency(p3d.TransparencyAttrib.MAlpha)

class TileFeature():
    def __init__(self, parentNode, model, positionOffset, rotation, scale, triangleCorners = None, triangleDivisions = 0, nFeatures = 1):

        self.node = parentNode.attachNewNode('featureNode')
        if triangleDivisions == 0:
            model.copyTo(self.node)

            self.node.setPos(p3d.LPoint3(position[0], position[1], position[2]))
            self.node.set_hpr(rotation[0], rotation[1], position[2])
            self.node.setScale(scale, scale, scale)
            self.node.setTransparency(p3d.TransparencyAttrib.MAlpha)
        else:
            v, f = World.SphericalWorld.SubdivideTriangle(triangleCorners, divisions=triangleDivisions,onlyGetSize=False)
            fc = World.SphericalWorld.CalculateFaceCoordinates(v, f)
            if nFeatures > np.size(fc, axis = 0):
                nFeatures = np.size(fc, axis = 0)
            iSubFaces = np.random.choice(np.size(fc, axis=0), nFeatures, replace=False)

            modelNodes = []
            for iModel in range(nFeatures):
                modelNodes.append(self.node.attachNewNode('modelNode'))
                model.copyTo(modelNodes[-1])

                modelNodes[-1].setPos(p3d.LPoint3(fc[iSubFaces[iModel], 0]+positionOffset[0],
                                             fc[iSubFaces[iModel], 1]+positionOffset[1],
                                             fc[iSubFaces[iModel], 2]+positionOffset[2]))
                modelNodes[-1].set_hpr(rotation[0], rotation[1], 360*np.random.rand())
                modelNodes[-1].setScale(scale, scale, scale)
                modelNodes[-1].setTransparency(p3d.TransparencyAttrib.MAlpha)
            self.node.flattenStrong()



class FeatureCluster():
    def __init__(self, parent, position, renderDistance):

        self.LODNode = p3d.LODNode('LOD node')
        self.LODNodePath = p3d.NodePath(self.LODNode)
        self.LODNodePath.reparentTo(parent)

        self.LODNodePath.setPos( p3d.LPoint3(position[0], position[1], position[2]) )
        self.LODNode.addSwitch(renderDistance, 0.0)

        self.node = parent.attachNewNode("forestRootNode")
        #self.node.reparentTo(self.LODNodePath)

        self.position = position

        self.latitude = np.arctan(self.position[2] / np.sqrt(self.position[0] ** 2 + self.position[1] ** 2))
        self.longitude = np.arctan(self.position[1] / self.position[0])
        if self.position[0] < 0:
            self.longitude += np.pi






