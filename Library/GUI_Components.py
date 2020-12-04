import Library.GUI as GUI
import Library.Graphics as Graphics

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
        print('building range should be visualized')

    def VisualizeBuildingLinks(self, status):
        building = self.mainProgram.buildingList[self.mainProgram.selectedTile]
        if status == 1:
            print('building links should be visualized')

            if building.linkNode != None:
                building.linkNode.show()
            else:
                # Create line graphics object.
                #pointIndices = [[[self.mainProgram.selectedTile, destination.iTile] for destination in building.destinations[resource]] for resource in building.outputBuffert.type]

                pointIndices = [self.mainProgram.selectedTile]
                lines = []
                i = 0
                for resource in building.outputBuffert.type:
                    for destination in building.destinations[resource]:
                        i += 1
                        pointIndices.append(destination.iTile)
                        lines.append([0, i])

                pointCoordinates = Graphics.LineSegments.IndicesToCoordinates(indices=pointIndices, mainProgram=self.mainProgram)
                print(pointIndices)
                print(lines)
                print(pointCoordinates)

                building.linkNode = Graphics.LineSegments.LineSegments(coordinates=pointCoordinates, lineIndices=lines, coordinateMultiplier=1.01)
                building.linkNode.show()
        else:
            if building.linkNode != None:
                building.linkNode.hide()













