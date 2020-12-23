import Library.GUI as GUI
import Library.Graphics as Graphics
import Library.Transport as Transport

class FeatureInformation():
    def __init__(self, mainProgram):
        self.mainProgram = mainProgram

    def Initialize(self, interface):
        interface.frames['featureInformation'] = GUI.CustomFrame(
            position=self.mainProgram.settings.featureInformationFramePosition,
            size=self.mainProgram.settings.featureInformationFrameSize,
            color=(1, 1, 1, 1))
        interface.frames['featureInformation'].node.hide()
        interface.labels['featureInformation'] = GUI.CustomLabel(position=(
        self.mainProgram.settings.featureInformationFrameSize[0] + self.mainProgram.settings.featureInformationMargin[
            0],
        0,
        self.mainProgram.settings.featureInformationFrameSize[3] - self.mainProgram.settings.featureInformationMargin[
            1] - 0.05),
                                                        text=" TEST ",
                                                        parent=interface.frames['featureInformation'].node)
        interface.buttons['buildingRange'] = GUI.CustomCheckButton(parent=interface.frames['featureInformation'].node,
                                                          images=['building_range.png', 'building_range_pressed.png'],
                                                          callbackFunction=self.VisualizeBuildingRange,
                                                          position=(
                                                          self.mainProgram.settings.featureInformationFrameSize[1] -
                                                          self.mainProgram.settings.featureInformationMargin[0] - 0.1,
                                                          0,
                                                          self.mainProgram.settings.featureInformationFrameSize[2] +
                                                          self.mainProgram.settings.featureInformationMargin[1] + 0.05),
                                                          scale=0.07)
        interface.buttons['buildingLinks'] = GUI.CustomCheckButton(parent=interface.frames['featureInformation'].node,
                                                          images=['building_links.png', 'building_links_pressed.png'],
                                                          callbackFunction=self.VisualizeBuildingLinks,
                                                          position=(
                                                          self.mainProgram.settings.featureInformationFrameSize[1] -
                                                          self.mainProgram.settings.featureInformationMargin[0] - 0.2,
                                                          0,
                                                          self.mainProgram.settings.featureInformationFrameSize[2] +
                                                          self.mainProgram.settings.featureInformationMargin[1] + 0.05),
                                                          scale=0.07)

    def VisualizeBuildingRange(self, status):
        if status == 1:
            building = self.mainProgram.buildingList[self.mainProgram.selectedTile]
            if building.tilesInRange == None:
                # The tiles within range are calculated.
                building.tilesInRange, building.came_from, building.cost_so_far = self.mainProgram.movementGraph.AStar(startNode=building.iTile, maximumCost=self.mainProgram.settings.defaultMovementRange)
            Graphics.WorldMesh.Highlight(building.tilesInRange, self.mainProgram.planet, self.mainProgram.water)

        else:
            Graphics.WorldMesh.Highlight([], self.mainProgram.planet, self.mainProgram.water)
            self.mainProgram.interface.buttons['buildingRange'].node["indicatorValue"] = False
            self.mainProgram.interface.buttons['buildingRange'].node.setIndicatorValue()

    def VisualizeBuildingLinks(self, status):
        '''
        Will visualize lines between this building and all it's destination buildings.
        :param status:
        :return:
        '''
        if status == 1:
            building = self.mainProgram.buildingList[self.mainProgram.selectedTile]

            if building.linkNode != None:
                building.linkNode.show()
            else:
                '''
                # Create line graphics object.
                pointIndices = [self.mainProgram.selectedTile]
                lines = []
                i = 0
                for resource in building.outputBuffert.type:
                    for destination in building.destinations[resource]:
                        i += 1
                        pointIndices.append(destination.iTile)
                        lines.append([0, i])
                pointCoordinates = Graphics.LineSegments.IndicesToCoordinates(indices=pointIndices, mainProgram=self.mainProgram)

                building.linkNode = Graphics.LineSegments.LineSegments(coordinates=pointCoordinates, lineIndices=lines, coordinateMultiplier=1.01)
                building.linkNode.show()
                '''

                pointIndices = [self.mainProgram.selectedTile]
                lines = []
                paths = []
                i = 0
                for resource in building.outputBuffert.type:
                    for destination in building.destinations[resource]:
                        i += 1
                        pointIndices.append(destination.iTile)
                        path = Transport.MovementGraph.RetracePath(building.came_from, destination.iTile)
                        paths.append(path)
                        #lines.append([0, i])
                pointCoordinates = Graphics.LineSegments.IndicesToCoordinates(indices=paths, mainProgram=self.mainProgram)

                building.linkNode = Graphics.LineSegments.LineStrips(coordinates=pointCoordinates, coordinateMultiplier=1.01)
                building.linkNode.show()
        else:
            if self.mainProgram.selectedTile != None:
                building = self.mainProgram.buildingList[self.mainProgram.selectedTile]
                if building != None:
                    if building.linkNode != None:
                        building.linkNode.hide()
            self.mainProgram.interface.buttons['buildingLinks'].node["indicatorValue"] = False
            self.mainProgram.interface.buttons['buildingLinks'].node.setIndicatorValue()













