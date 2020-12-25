import numpy as np


import Data.Dictionaries.FeatureTemplateDictionary as FeatureTemplateDictionary


class BuildingFeatureProperties(FeatureTemplateDictionary.GlobeFeatureProperties):
    def __init__(self, models, weights, scaleRange, triangleDivisions, nObjects, orientationMode, GUILabel, textureKey, buildingTemplate):
        super().__init__(models, weights, scaleRange, triangleDivisions, nObjects, orientationMode, GUILabel, textureKey)

        self.buildingTemplate = buildingTemplate


class Building():
    def __init__(self, iTile, inputBuffert, outputBuffert):
        self.inputBuffert = inputBuffert
        self.outputBuffert = outputBuffert
        self.iTile = iTile

        self.inputLinks = {}
        self.inputLinkAmount = {} # The amount of linked buildings, used as a sort of "satisfaction" value.
        self.destinationLimit = 3 # The maximum number of destinations per resource.
        self.destinationAmount = {} # The number of linked destinations per resource.
        self.destinations = {} # The linked destinations.
        for inputResource in self.inputBuffert.type:
            self.inputLinkAmount[inputResource] = 0
            self.inputLinks[inputResource] = []
        for outputResource in self.outputBuffert.type:
            self.destinationAmount[outputResource] = 0
            self.destinations[outputResource] = []

        self.turnsSinceTransportLinkUpdate = 0

        self.linkNode = None # Used for visualizing the links.

        # Used for range dependent destination links.
        self.tilesInRange = None
        self.came_from = None
        self.cost_so_far = None

        # This building doesn't affect its tiles movement cost.
        self.movementCost = None

    def ResetDestinations(self, resource):
        # Links should be removed from destinations

        for destination in self.destinations[resource]:
            destination.inputLinkAmount[resource] -= 1

        self.destinationAmount[resource] = 0
        self.destinations[resource] = []

    def Delete(self):
        for inputResource in self.inputBuffert.type:
            for link in self.inputLinks[inputResource]:
                link.ResetDestinations(inputResource)
                if link.linkNode != None:
                    # When the links are recomputed the link node should be removed.
                    link.linkNode.removeNode()
                    link.linkNode = None
        if self.linkNode != None:
            # When the links are recomputed the link node should be removed.
            self.linkNode.removeNode()
            self.linkNode = None

    def __call__(self, *args, **kwargs):
        pass

    def __str__(self):
        text = ''
        for i, resource in enumerate(self.inputBuffert.type):
            text += resource + ' : ' + "{:.0f}".format(self.inputBuffert.amount[resource]) + '/' + "{:.0f}".format(self.inputBuffert.limit[resource]) + '\n'
        for i, resource in enumerate(self.outputBuffert.type):
            text += resource + ' : ' + "{:.0f}".format(self.outputBuffert.amount[resource]) + '/' + "{:.0f}".format(self.outputBuffert.limit[resource]) + '\n'

        return text

    def GetInputOutputText(self):
        text = ''
        text += 'INPUT\n'
        for i, resource in enumerate(self.inputBuffert.type):
            text += '   ' + resource + ' : ' + "{:.0f}".format(self.inputBuffert.amount[resource]) + '/' + "{:.0f}".format(self.inputBuffert.limit[resource]) + '  ' + "{:.0f}".format(100*self.inputBuffert.smoothedSatisfaction[resource]) + '%' + '\n'
        text += 'OUTPUT\n'
        for i, resource in enumerate(self.outputBuffert.type):
            text += '   ' + resource + ' : ' + "{:.0f}".format(self.outputBuffert.amount[resource]) + '/' + "{:.0f}".format(self.outputBuffert.limit[resource]) + '\n'
        return text

    def GetDetailedText(self):
        text = self.GetInputOutputText()
        return text

    @classmethod
    def Initialize(cls, mainProgram):
        cls.mainProgram = mainProgram

class ProductionBuilding(Building):
    def __init__(self, iTile, inputBuffert, outputBuffert, laborLimit = 50, recipy = None):
        super().__init__(iTile, inputBuffert, outputBuffert)
        self.laborLimit = laborLimit # The max amount of labor that can be used each day.
        self.recipy = recipy

    def __call__(self, *args, **kwargs):
        for amount in self.outputBuffert.amount:
            amount += 10

class LivingBuilding(Building):
    def __init__(self, iTile, inputBuffert, outputBuffert, population = 10, populationInHouse = 10, maxPopulation = 100):
        super().__init__(iTile, inputBuffert, outputBuffert)
        self.population = population
        self.populationInHouse = populationInHouse
        self.maxPopulation = maxPopulation
        self.unusedLabor = 0

    def __call__(self, *args, **kwargs):
        pass

    def __str__(self):
        text = ''
        for i, resource in enumerate(self.inputBuffert.type):
            text += resource + ' : ' + "{:.0f}".format(self.inputBuffert.amount[resource]) + '/' + "{:.0f}".format(self.inputBuffert.limit[resource]) + '\n'
        for i, resource in enumerate(self.outputBuffert.type):
            text += resource + ' : ' + "{:.0f}".format(self.outputBuffert.amount[resource]) + '/' + "{:.0f}".format(self.outputBuffert.limit[resource]) + '\n'
        text += 'Population : ' + "{:.0f}".format(self.population) + '/' + "{:.0f}".format(self.maxPopulation) + '\n'
        return text

    def GetDetailedText(self):
        text = self.GetInputOutputText()
        text += 'POPULATION\n'
        text += '   ' + "{:.0f}".format(self.population) + '/' + "{:.0f}".format(self.maxPopulation) + '\n'
        return text



class ResourceBuffert():
    def __init__(self, types, amounts, limits, satisfaction = None):
        self.type = types
        self.amount = {}
        self.limit = {}
        if satisfaction != None:
            self.satisfaction = {}
            self.smoothedSatisfaction = {}
        for i, type in enumerate(types):
            self.amount[type] = amounts[i]
            self.limit[type] = limits[i]
            if satisfaction != None:
                self.satisfaction[type] = satisfaction[i]
                self.smoothedSatisfaction[type] = satisfaction[i]

    def GetSatisfaction(self):
        '''
        Satisfaction is defined as the sum of all the resource amounts/limits.
        :return:
        '''

        sumAmount = 0
        for key in self.amount:
            sumAmount += self.amount[key]
        sumLimit = 0
        for key in self.limit:
            sumLimit += self.limit[key]
        return (sumAmount, sumLimit)

class Recipy():
    def __init__(self, building, laborLimit, input, output):
        '''
        All recipies are "manned"; they require labor as input. This could be made more general if need be.
        '''
        self.building = building
        self.laborLimit = laborLimit
        self.input = input
        self.output = output

    def __call__(self, *args, **kwargs):
        laborOutputSpace = self.building.outputBuffert.limit['spent_labor'] - self.building.outputBuffert.amount['spent_labor']
        usedLabor = np.min((self.building.inputBuffert.amount['labor'], self.laborLimit, laborOutputSpace))
        laborEfficiency = usedLabor / self.laborLimit
        self.building.inputBuffert.satisfaction['labor'] = laborEfficiency
        self.building.inputBuffert.smoothedSatisfaction['labor'] = (self.building.inputBuffert.smoothedSatisfaction[
                                                               'labor'] + laborEfficiency) / 2
        self.building.inputBuffert.amount['labor'] -= usedLabor
        self.building.outputBuffert.amount['spent_labor'] += usedLabor

        if usedLabor > 0:
            resourceEfficiency = []
            for inputResource in self.input:
                resourceEfficiency.append(np.min((1, self.building.inputBuffert.amount[inputResource]/self.input[inputResource])))
                self.building.inputBuffert.satisfaction[inputResource] = resourceEfficiency[-1]
                self.building.inputBuffert.smoothedSatisfaction[inputResource] = (self.building.inputBuffert.smoothedSatisfaction[
                                                                       inputResource] + resourceEfficiency[-1]) / 2
            resourceEfficiency.append(laborEfficiency)
            totalEfficiency = np.min(resourceEfficiency)

            for inputResource in self.input:
                self.building.inputBuffert.amount[inputResource] -= self.input[inputResource]*totalEfficiency

            for outputResource in self.output:
                self.building.outputBuffert.amount[outputResource] += totalEfficiency*self.output[outputResource]
                self.building.outputBuffert.amount[outputResource] = np.min((self.building.outputBuffert.amount[outputResource], self.building.outputBuffert.limit[outputResource]))







