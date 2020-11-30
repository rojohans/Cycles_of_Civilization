
import Data.Dictionaries.FeatureTemplateDictionary as FeatureTemplateDictionary


class BuildingFeatureProperties(FeatureTemplateDictionary.GlobeFeatureProperties):
    def __init__(self, models, weights, scaleRange, triangleDivisions, nObjects, orientationMode, GUILabel, textureKey, buildingTemplate):
        super().__init__(models, weights, scaleRange, triangleDivisions, nObjects, orientationMode, GUILabel, textureKey)

        self.buildingTemplate = buildingTemplate


class Building():
    def __init__(self, inputBuffert, outputBuffert):
        self.inputBuffert = inputBuffert
        self.outputBuffert = outputBuffert

    def __call__(self, *args, **kwargs):
        pass

    def __str__(self):
        text = ''
        for i, resource in enumerate(self.inputBuffert.type):
            text += resource + ' : ' + "{:.0f}".format(self.inputBuffert.amount[resource]) + '/' + "{:.0f}".format(self.inputBuffert.limit[resource]) + '\n'
        for i, resource in enumerate(self.outputBuffert.type):
            text += resource + ' : ' + "{:.0f}".format(self.outputBuffert.amount[resource]) + '/' + "{:.0f}".format(self.outputBuffert.limit[resource]) + '\n'

        return text

class ProductionBuilding(Building):
    def __init__(self, inputBuffert, outputBuffert, laborLimit = 50):
        super().__init__(inputBuffert, outputBuffert)
        self.laborLimit = laborLimit # The max amount of labor that can be used each day.

    def __call__(self, *args, **kwargs):
        for amount in self.outputBuffert.amount:
            amount += 10

class LivingBuilding(Building):
    def __init__(self, inputBuffert, outputBuffert, population = 10, populationInHouse = 10, maxPopulation = 100):
        super().__init__(inputBuffert, outputBuffert)
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


