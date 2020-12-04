
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

    def __call__(self, *args, **kwargs):
        pass

    def __str__(self):
        text = ''
        for i, resource in enumerate(self.inputBuffert.type):
            text += resource + ' : ' + "{:.0f}".format(self.inputBuffert.amount[resource]) + '/' + "{:.0f}".format(self.inputBuffert.limit[resource]) + '\n'
        for i, resource in enumerate(self.outputBuffert.type):
            text += resource + ' : ' + "{:.0f}".format(self.outputBuffert.amount[resource]) + '/' + "{:.0f}".format(self.outputBuffert.limit[resource]) + '\n'

        return text

    def GetDetailedText(self):
        text = ''
        text += 'INPUT\n'
        for i, resource in enumerate(self.inputBuffert.type):
            text += '   ' + resource + ' : ' + "{:.0f}".format(self.inputBuffert.amount[resource]) + '/' + "{:.0f}".format(self.inputBuffert.limit[resource]) + '\n'
        text += 'OUTPUT\n'
        for i, resource in enumerate(self.outputBuffert.type):
            text += '   ' + resource + ' : ' + "{:.0f}".format(self.outputBuffert.amount[resource]) + '/' + "{:.0f}".format(self.outputBuffert.limit[resource]) + '\n'
        return text

class ProductionBuilding(Building):
    def __init__(self, iTile, inputBuffert, outputBuffert, laborLimit = 50):
        super().__init__(iTile, inputBuffert, outputBuffert)
        self.laborLimit = laborLimit # The max amount of labor that can be used each day.

    def __call__(self, *args, **kwargs):
        for amount in self.outputBuffert.amount:
            amount += 10

class LivingBuilding(Building):
    def __init__(self, iTile, inputBuffert, outputBuffert, population = 10, populationInHouse = 10, maxPopulation = 100):
        super().__init__(iTile, inputBuffert, outputBuffert)
        self.population = population
        self.populationInHouse = populationInHouse
        self.maxPopulation = maxPopulation

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
        text = ''
        text += 'INPUT\n'
        for i, resource in enumerate(self.inputBuffert.type):
            text += '   ' + resource + ' : ' + "{:.0f}".format(self.inputBuffert.amount[resource]) + '/' + "{:.0f}".format(self.inputBuffert.limit[resource]) + '\n'
        text += 'OUTPUT\n'
        for i, resource in enumerate(self.outputBuffert.type):
            text += '   ' + resource + ' : ' + "{:.0f}".format(self.outputBuffert.amount[resource]) + '/' + "{:.0f}".format(self.outputBuffert.limit[resource]) + '\n'
        text += 'POPULATION\n'
        text += '   ' + "{:.0f}".format(self.population) + '/' + "{:.0f}".format(self.maxPopulation) + '\n'
        return text



class ResourceBuffert():
    def __init__(self, types, amounts, limits):
        self.type = types
        self.amount = {}
        self.limit = {}
        for i, type in enumerate(types):
            self.amount[type] = amounts[i]
            self.limit[type] = limits[i]

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


