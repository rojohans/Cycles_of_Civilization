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
    def __init__(self, parent, backupRoot, positionOffset, rotation, featureTemplate, iTile, triangleCorners = None):
        self.parent = parent

        self.template = featureTemplate


        self.node = backupRoot.attachNewNode('featureNode')
        if len(featureTemplate.models) > 0:
            nFeatures = featureTemplate.nObjects
            triangleDivisions = featureTemplate.triangleDivisions

            v, f = World.SphericalWorld.SubdivideTriangle(triangleCorners, divisions=triangleDivisions,onlyGetSize=False)
            fc = World.SphericalWorld.CalculateFaceCoordinates(v, f)
            if nFeatures > np.size(fc, axis = 0):
                nFeatures = np.size(fc, axis = 0)
            iSubFaces = np.random.choice(np.size(fc, axis=0), nFeatures, replace=False)

            iComponent = np.random.choice(range(featureTemplate.numberOfComponents), nFeatures, p=featureTemplate.weights)
            if featureTemplate.orientationMode == 'uniform':
                orientationAngle = 360*np.random.rand()

            modelNodes = []
            for iObject in range(nFeatures):
                model = featureTemplate.models[iComponent[iObject]]
                scaleRange = featureTemplate.scaleRange[iComponent[iObject]]
                scale = scaleRange[0] + np.random.rand()*(scaleRange[1]-scaleRange[0])

                modelNodes.append(self.node.attachNewNode('modelNode'))
                model.copyTo(modelNodes[-1])

                modelNodes[-1].setPos(p3d.LPoint3(fc[iSubFaces[iObject], 0]+positionOffset[0],
                                             fc[iSubFaces[iObject], 1]+positionOffset[1],
                                             fc[iSubFaces[iObject], 2]+positionOffset[2]))
                if featureTemplate.orientationMode == 'random':
                    orientationAngle = 360 * np.random.rand()
                modelNodes[-1].set_hpr(rotation[0], rotation[1], orientationAngle)
                modelNodes[-1].setScale(scale, scale, scale)
                modelNodes[-1].setTransparency(p3d.TransparencyAttrib.MAlpha)
            self.node.flattenStrong()
        self.parentedNode = parent.node.attachNewNode('featureNode')

    def AttachToParent(self):
        self.parentedNode = self.parent.node.attachNewNode('featureNode')
        self.node.copyTo(self.parentedNode)

    def Delete(self):
        self.node.removeNode()


class FeatureCluster():
    def __init__(self, parent, position, renderDistance):
        self.parent = parent

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

        self.childrenTiles = []

class FeatureInteractivity():
    def __init__(self, mainProgram):
        self.mainProgram = mainProgram

    def AddFeature(self, status):
        if status == 1:
            self.mainProgram.interface.frames['addFeatureMenu'].node.show()
        else:
            self.mainProgram.interface.frames['addFeatureMenu'].node.hide()


    def RemoveFeature(self, status):
        if status == 1:


            if len(self.mainProgram.featureList[self.mainProgram.selectedTile]) > 0:
                clusterNode = self.mainProgram.featureList[self.mainProgram.selectedTile][0].parent

                # Removes all features from the tile
                for feature in self.mainProgram.featureList[self.mainProgram.selectedTile]:
                    if feature.template.textureKey != None:
                        self.mainProgram.planet.textureUpdatedStatus = False
                    feature.Delete()
                self.mainProgram.featureList[self.mainProgram.selectedTile] = []

                # Recreates the feature nodes.
                clusterNode.node.removeNode()
                clusterNode.node = clusterNode.parent.attachNewNode("forestRootNode")
                for childrenTile in clusterNode.childrenTiles:
                    for feature in self.mainProgram.featureList[childrenTile]:
                        feature.AttachToParent()
                clusterNode.node.clearModelNodes()
                clusterNode.node.flattenStrong()
                clusterNode.node.reparentTo(clusterNode.LODNodePath)

                '''
                # Recalculate texture coordinates of the globe.
                textureCoordinates = p3d.GeomVertexWriter(self.mainProgram.planet.vertexData, 'texcoord')
                for iTile in range(np.size(self.mainProgram.world.f, axis = 0)):
                    textureKey = self.mainProgram.planet.DetermineTextureKey(iTile)

                    rIndices = self.mainProgram.closeTexture.textureIndices[textureKey]
                    textureCoordinates .addData2f(rIndices[0], 0)
                    textureCoordinates .addData2f(rIndices[1], 0)
                    textureCoordinates .addData2f((rIndices[0] + rIndices[1]) / 2, np.sqrt(3) / 2)
                '''

                if self.mainProgram.buildingList[self.mainProgram.selectedTile] != None:
                    self.mainProgram.buildingList[self.mainProgram.selectedTile] = None
                    self.mainProgram.transport.RecalculateInputDictionay()






        self.mainProgram.interface.buttons['addFeature'].node["indicatorValue"] = False
        self.mainProgram.interface.buttons['addFeature'].node.setIndicatorValue()
        self.mainProgram.interface.buttons['removeFeature'].node["indicatorValue"] = False
        self.mainProgram.interface.buttons['removeFeature'].node.setIndicatorValue()

    def PlaceFeature(self, featureKey):
        iCluster = self.mainProgram.clusterBelonging[self.mainProgram.selectedTile]
        cluster = self.mainProgram.featureNodeClusters[iCluster]

        theta = 180 * np.arctan(self.mainProgram.world.faceCoordinates[self.mainProgram.selectedTile, 2] / np.sqrt(
            self.mainProgram.world.faceCoordinates[self.mainProgram.selectedTile, 0] ** 2 + self.mainProgram.world.faceCoordinates[self.mainProgram.selectedTile, 1] ** 2)) / np.pi
        phi = 180 * np.arctan(self.mainProgram.world.faceCoordinates[self.mainProgram.selectedTile, 1] / self.mainProgram.world.faceCoordinates[self.mainProgram.selectedTile, 0]) / np.pi
        if self.mainProgram.world.faceCoordinates[self.mainProgram.selectedTile, 0] > 0:
            phi += 180

        self.mainProgram.featureList[self.mainProgram.selectedTile]\
            .append(TileFeature(parent=cluster,
                                backupRoot=self.mainProgram.featureBackupRoot,
                                positionOffset = -cluster.position,
                                rotation=[90 + phi, theta, 0],
                                triangleCorners=self.mainProgram.world.v[self.mainProgram.world.f[self.mainProgram.selectedTile, 1:]],
                                featureTemplate=self.mainProgram.featureTemplate[featureKey],
                                iTile = self.mainProgram.selectedTile))
        if self.mainProgram.featureTemplate[featureKey].buildingTemplate != None:

            newBuilding = self.mainProgram.featureTemplate[featureKey].buildingTemplate()
            self.mainProgram.buildingList[self.mainProgram.selectedTile] = newBuilding
            for resource in newBuilding.inputBuffert.type:
                self.mainProgram.transport.buildingsInput[resource].append(newBuilding)

        if self.mainProgram.featureTemplate[featureKey].textureKey != None:
            self.mainProgram.planet.textureUpdatedStatus = False

        cluster.node.removeNode()
        cluster.node = cluster.parent.attachNewNode("forestRootNode")
        for childrenTile in cluster.childrenTiles:
            for feature in self.mainProgram.featureList[childrenTile]:
                feature.AttachToParent()
        cluster.node.clearModelNodes()
        cluster.node.flattenStrong()
        cluster.node.reparentTo(cluster.LODNodePath)


