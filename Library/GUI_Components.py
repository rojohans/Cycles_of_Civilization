import panda3d.core as p3d
import sys
import numpy as np

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
                pointIndices = [self.mainProgram.selectedTile]
                paths = []
                i = 0
                for resource in building.outputBuffert.type:
                    for destination in building.destinations[resource]:
                        i += 1
                        pointIndices.append(destination.iTile)
                        path = Transport.MovementGraph.RetracePath(building.came_from, destination.iTile)
                        paths.append(path)
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

class ToolMenu():
    def __init__(self, mainProgram):
        self.mainProgram = mainProgram

    def Initialize(self, interface):
        interface.frames['toolMenu'] = GUI.CustomFrame(
            position=(0, 0, 0),
            size=(-1.0, 0.5, 0.9, 1.0),
            color=(1, 1, 1, 1))

        #interface.frames['statisticsGraphWindow'] = GUI.CustomFrame(
        #    position=(0, 0, 0),
        #    size=(-1.0, 1.0, -1.0, 0.9),
        #    color=(1, 1, 1, 1))
        interface.frames['statisticsGraphWindow'] = GUI.CustomFrame(
            textureImage=None,
            position=(0, 0, 0),
            size=(-1.0, 1.0, -1.0, 0.9),
            color=(0.9, 0.8, 0.5, 1))
        interface.frames['statisticsGraphWindow'].node.hide()

        interface.buttons['openStatisticsGraphWindow'] = \
            GUI.CustomCheckButton(parent=interface.frames['toolMenu'].node,
                                  images=['statistics_graph.png',
                                          'statistics_graph_pressed.png'],
                                  callbackFunction=self.OpenStatisticsGraphWindow,
                                  position=(-0.9, 0, 0.95),
                                  scale=0.05)
        interface.frames['statisticsGraphBackground'] = GUI.CustomFrame(textureImage='graph_background.png',
            position=self.mainProgram.settings.statisticsGraphPosition,
            size=self.mainProgram.settings.statisticsGraphSize,
            color=(1, 1, 1, 1))
        interface.frames['statisticsGraphBackground'].node.reparentTo(interface.frames['statisticsGraphWindow'].node)
        self.plot = None # The node used to visualize graph lines.
        self.plotMode = ['demand']

        interface.buttons['statisticsGraphPriority'] = \
            GUI.CustomRadioButton(parent=interface.frames['statisticsGraphBackground'].node,
                                  images=['toggle_off.png', 'toggle_on.png'],
                                  callbackFunction=self.UpdateStatisticsGraph,
                                  position=(0.2 + self.mainProgram.settings.statisticsGraphSize[0], 0,
                                            0.05 + self.mainProgram.settings.statisticsGraphSize[3]),
                                  scale=0.05,
                                  text='PRIORITY',
                                  variable=self.plotMode,
                                  value='priority')
        interface.buttons['statisticsGraphDemand'] = \
            GUI.CustomRadioButton(parent=interface.frames['statisticsGraphBackground'].node,
                                  images=['toggle_off.png', 'toggle_on.png'],
                                  callbackFunction=self.UpdateStatisticsGraph,
                                  position=(0.2+self.mainProgram.settings.statisticsGraphSize[0], 0, 0.15+self.mainProgram.settings.statisticsGraphSize[3]),
                                  scale=0.05,
                                  text='DEMAND',
                                  variable = self.plotMode,
                                  value = 'demand')
        interface.buttons['statisticsGraphProduction'] = \
            GUI.CustomRadioButton(parent=interface.frames['statisticsGraphBackground'].node,
                                  images=['toggle_off.png', 'toggle_on.png'],
                                  callbackFunction=self.UpdateStatisticsGraph,
                                  position=(0.2+self.mainProgram.settings.statisticsGraphSize[0], 0, 0.25+self.mainProgram.settings.statisticsGraphSize[3]),
                                  scale=0.05,
                                  text='PRODUCTION',
                                  variable = self.plotMode,
                                  value = 'production')
        interface.buttons['statisticsGraphConsumption'] = \
            GUI.CustomRadioButton(parent=interface.frames['statisticsGraphBackground'].node,
                                  images=['toggle_off.png', 'toggle_on.png'],
                                  callbackFunction=self.UpdateStatisticsGraph,
                                  position=(0.2+self.mainProgram.settings.statisticsGraphSize[0], 0, 0.35+self.mainProgram.settings.statisticsGraphSize[3]),
                                  scale=0.05,
                                  text='CONSUMPTION',
                                  variable = self.plotMode,
                                  value = 'consumption')
        interface.buttons['statisticsGraphPopulation'] = \
            GUI.CustomRadioButton(parent=interface.frames['statisticsGraphBackground'].node,
                                  images=['toggle_off.png', 'toggle_on.png'],
                                  callbackFunction=self.UpdateStatisticsGraph,
                                  position=(0.2+self.mainProgram.settings.statisticsGraphSize[0], 0, 0.45+self.mainProgram.settings.statisticsGraphSize[3]),
                                  scale=0.05,
                                  text='POPULATION',
                                  variable = self.plotMode,
                                  value = 'population')
        radioButtons = [interface.buttons['statisticsGraphPriority'].node, interface.buttons['statisticsGraphDemand'].node, interface.buttons['statisticsGraphProduction'].node, interface.buttons['statisticsGraphConsumption'].node, interface.buttons['statisticsGraphPopulation'].node]
        for button in radioButtons:
            button.setOthers(radioButtons)
        #interface.buttons['statisticsGraphDemand'].node.setOthers(radioButtons)
        #interface.buttons['statisticsGraphProduction'].node.setOthers(radioButtons)
        #interface.buttons['statisticsGraphPopulation'].node.setOthers(radioButtons)

        self.plotResourceList = {}
        nResources = len(self.mainProgram.resources.resources)
        for iResource, resource in enumerate(self.mainProgram.resources.resources):
            self.plotResourceList[resource] = True
            interface.labels['statisticsGraphResource_' + resource] = GUI.CustomLabel(position=(0.8, 0, 0.7*(1 - 2*iResource/(nResources-1))),
                                                         text='{:>20}'.format(resource),
                                                         parent=interface.frames['statisticsGraphWindow'].node,
                                                                                      frameColour=self.mainProgram.resources.colour[resource],
                                                                                      textAlign=p3d.TextNode.ARight)
            interface.buttons['statisticsGraphResource_' + resource] = \
                GUI.CustomCheckButton(parent=interface.frames['statisticsGraphWindow'].node,
                                      images=['toggle_off.png',
                                              'toggle_on.png'],
                                      callbackFunction=self.UpdateStatisticsGraphResourceToggle,
                                      position=(0.9, 0, 0.7*(1 - 2*iResource/(nResources-1))),
                                      scale=0.05,
                                      commandInput=[resource])
            interface.buttons['statisticsGraphResource_' + resource].node["indicatorValue"] = 1
            interface.buttons['statisticsGraphResource_' + resource].node.setIndicatorValue()

        interface.buttons['quitButton'] = GUI.CustomButton(parent = interface.frames['toolMenu'].node,
                                                           images = ["quit_button.png", "quit_button.png"],
                                                           scale = self.mainProgram.settings.buttonSize,
                                                           position = (0.4, 0.0, 0.95),
                                                           callbackFunction=sys.exit)

    def OpenStatisticsGraphWindow(self, status):
        if status == 1:
            self.mainProgram.interface.frames['statisticsGraphWindow'].node.show()
            self.UpdateStatisticsGraph()
        elif status == 0:
            self.mainProgram.interface.frames['statisticsGraphWindow'].node.hide()

    def UpdateStatisticsGraph(self):
        nTimeSteps = len(self.mainProgram.resources.demandHistory['labor'])
        if nTimeSteps > 1:
            if self.plot != None:
                self.plot.remove_node()

            xWindowSpan = self.mainProgram.settings.statisticsGraphSize[1]-self.mainProgram.settings.statisticsGraphSize[0]
            x = xWindowSpan * np.linspace(0, 1, nTimeSteps) - xWindowSpan/2
            x *= self.mainProgram.interface.windowRatio
            yWindowSpan = self.mainProgram.settings.statisticsGraphSize[3] - \
                          self.mainProgram.settings.statisticsGraphSize[2]

            if self.plotMode[0] == 'priority':
                resourcesToPlot = []
                for resource in self.plotResourceList:
                    if self.plotResourceList[resource]:
                        resourcesToPlot.append(resource)
                coordinates = [np.zeros((nTimeSteps, 2)) for resource in resourcesToPlot]
                colours = np.empty((len(resourcesToPlot), 4))
                yBoundaries = [self.mainProgram.resources.minPriority-0.1, self.mainProgram.resources.maxPriority+0.1]
                ySpan = yBoundaries[1] - yBoundaries[0]

                for iResource, resource in enumerate(resourcesToPlot):
                    coordinates[iResource][:, 0] = x
                    coordinates[iResource][:, -1] = self.mainProgram.settings.statisticsGraphSize[2]+yWindowSpan*(np.array(self.mainProgram.resources.priorityHistory[resource])-yBoundaries[0])/ySpan
                    colours[iResource, :] = self.mainProgram.resources.colour[resource][:]
                self.plot = Graphics.LineSegments.Plot(coordinates=coordinates, plotWindow=self.mainProgram.interface.frames['statisticsGraphBackground'].node, colour=colours, lineThickness=2)
            elif self.plotMode[0] == 'demand':
                resourcesToPlot = []
                for resource in self.plotResourceList:
                    if self.plotResourceList[resource]:
                        resourcesToPlot.append(resource)
                coordinates = [np.zeros((nTimeSteps, 2)) for resource in resourcesToPlot]
                colours = np.empty((len(resourcesToPlot), 4))
                yBoundaries = [self.mainProgram.resources.minDemand-0.1, self.mainProgram.resources.maxDemand+0.1]
                ySpan = yBoundaries[1] - yBoundaries[0]

                for iResource, resource in enumerate(resourcesToPlot):
                    coordinates[iResource][:, 0] = x
                    coordinates[iResource][:, -1] = self.mainProgram.settings.statisticsGraphSize[2]+yWindowSpan*(np.array(self.mainProgram.resources.demandHistory[resource])-yBoundaries[0])/ySpan
                    colours[iResource, :] = self.mainProgram.resources.colour[resource][:]
                self.plot = Graphics.LineSegments.Plot(coordinates=coordinates, plotWindow=self.mainProgram.interface.frames['statisticsGraphBackground'].node, colour=colours, lineThickness=2)
            elif self.plotMode[0] == 'production':
                resourcesToPlot = []
                for resource in self.plotResourceList:
                    if self.plotResourceList[resource]:
                        resourcesToPlot.append(resource)
                coordinates = [np.zeros((nTimeSteps, 2)) for resource in resourcesToPlot]
                colours = np.empty((len(resourcesToPlot), 4))
                yBoundaries = [self.mainProgram.resources.minProduction-0.1, self.mainProgram.resources.maxProduction+0.1]
                ySpan = yBoundaries[1] - yBoundaries[0]

                for iResource, resource in enumerate(resourcesToPlot):
                    coordinates[iResource][:, 0] = x
                    coordinates[iResource][:, -1] = self.mainProgram.settings.statisticsGraphSize[2]+yWindowSpan*(np.array(self.mainProgram.resources.productionHistory[resource])-yBoundaries[0])/ySpan
                    colours[iResource, :] = self.mainProgram.resources.colour[resource][:]
                self.plot = Graphics.LineSegments.Plot(coordinates=coordinates, plotWindow=self.mainProgram.interface.frames['statisticsGraphBackground'].node, colour=colours, lineThickness=2)
            elif self.plotMode[0] == 'consumption':
                resourcesToPlot = []
                for resource in self.plotResourceList:
                    if self.plotResourceList[resource]:
                        resourcesToPlot.append(resource)
                coordinates = [np.zeros((nTimeSteps, 2)) for resource in resourcesToPlot]
                colours = np.empty((len(resourcesToPlot), 4))
                yBoundaries = [self.mainProgram.resources.minConsumption-0.1, self.mainProgram.resources.maxConsumption+0.1]
                ySpan = yBoundaries[1] - yBoundaries[0]

                for iResource, resource in enumerate(resourcesToPlot):
                    coordinates[iResource][:, 0] = x
                    coordinates[iResource][:, -1] = self.mainProgram.settings.statisticsGraphSize[2]+yWindowSpan*(np.array(self.mainProgram.resources.consumptionHistory[resource])-yBoundaries[0])/ySpan
                    colours[iResource, :] = self.mainProgram.resources.colour[resource][:]
                self.plot = Graphics.LineSegments.Plot(coordinates=coordinates, plotWindow=self.mainProgram.interface.frames['statisticsGraphBackground'].node, colour=colours, lineThickness=2)
            elif self.plotMode[0] == 'population':
                coordinates = [np.zeros((nTimeSteps, 2))]
                yBoundaries = [self.mainProgram.populationStatistics.historicalMin - 0.1, self.mainProgram.populationStatistics.historicalMax + 0.1]
                ySpan = yBoundaries[1] - yBoundaries[0]

                coordinates[0][:, 0] = x
                coordinates[0][:, -1] = self.mainProgram.settings.statisticsGraphSize[2] + yWindowSpan * (
                            np.array(self.mainProgram.populationStatistics.history) - yBoundaries[0]) / ySpan
                self.plot = Graphics.LineSegments.Plot(coordinates=coordinates,
                                                       plotWindow=self.mainProgram.interface.frames[
                                                           'statisticsGraphBackground'].node,
                                                       lineThickness=2)
            print('Statistics graph updating')

    def UpdateStatisticsGraphResourceToggle(self, status, resource):
        if status == 1:
            self.plotResourceList[resource] = True
        elif status == 0:
            self.plotResourceList[resource] = False
        self.UpdateStatisticsGraph()


class MapFilterMenu():
    def __init__(self, mainProgram):
        self.mainProgram = mainProgram

    def Initialize(self, interface):
        NotImplemented







