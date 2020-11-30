import numpy as np



class Transport():
    def __init__(self, mainProgram, resources):
        '''
        buildingsInput is a dictionary with a key for every resource. Each field contains a list of the buildings which
         has that resource as input.
        :param mainProgram:
        :param resources:
        '''
        self.mainProgram = mainProgram
        self.resources = resources
        self.InitializeInputDictionary()

    def InitializeInputDictionary(self):
        self.buildingsInput = {}
        for resource in self.resources:
            self.buildingsInput[resource] = []

    def RecalculateInputDictionay(self):
        self.InitializeInputDictionary()
        for building in self.mainProgram.buildingList:
            if building != None:
                for resource in building.inputBuffert.type:
                    self.buildingsInput[resource].append(building)

    def __call__(self, *args, **kwargs):
        for building in self.mainProgram.buildingList:
            if building != None:
                for resource in building.outputBuffert.type:
                    if building.outputBuffert.amount[resource] > 0:
                        amountToMoveTotal = building.outputBuffert.amount[resource]
                        nRecievingBuildings = len(self.buildingsInput[resource])
                        for recievingBuilding in self.buildingsInput[resource]:
                            amountToMove = amountToMoveTotal/nRecievingBuildings
                            recievingSpace = recievingBuilding.inputBuffert.limit[resource] - recievingBuilding.inputBuffert.amount[resource]
                            amountToRecieve = np.min((recievingSpace, amountToMove))
                            amountToMove -= amountToRecieve
                            building.outputBuffert.amount[resource] -= amountToRecieve
                            recievingBuilding.inputBuffert.amount[resource] += amountToRecieve



