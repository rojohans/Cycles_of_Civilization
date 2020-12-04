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

                    if building.destinationAmount[resource] < building.destinationLimit or building.turnsSinceTransportLinkUpdate >= self.mainProgram.settings.transportLinkUpdateInterval:
                        #Connect to destination buildings

                        building.ResetDestinations(resource=resource)

                        possibleDestinations = self.buildingsInput[resource]
                        if len(possibleDestinations) > 0:
                            destinationWeights = np.empty((len(possibleDestinations), 1))
                            for i, possibleDestination in enumerate(possibleDestinations):
                                destinationWeights[i, 0] = np.random.rand()#1/(1+possibleDestination.inputLinkAmount[resource])

                            destinationIndicesSorted = np.argsort(destinationWeights, axis = 0)
                            destinationIndicesSorted = np.flip(destinationIndicesSorted)

                            for i, iDestination in enumerate(destinationIndicesSorted[:, 0]):
                                self.buildingsInput[resource][iDestination].inputLinks[resource].append(building)

                                building.destinations[resource].append(self.buildingsInput[resource][iDestination])
                                building.destinationAmount[resource] += 1
                                self.buildingsInput[resource][iDestination].inputLinkAmount[resource] += 1
                                if i >= building.destinationLimit-1:
                                    break

                        if building.linkNode != None:
                            # When the links are recomputed the link node should be removed.
                            building.linkNode.removeNode()
                            building.linkNode = None
                        #print('Transport link updated')

                    #print(resource)
                    #print(len(building.destinations[resource]))

                    if building.outputBuffert.amount[resource] > 0:
                        amountToMoveTotal = building.outputBuffert.amount[resource]
                        nRecievingBuildings = building.destinationAmount[resource]
                        for recievingBuilding in building.destinations[resource]:
                            amountToMove = amountToMoveTotal/nRecievingBuildings
                            recievingSpace = recievingBuilding.inputBuffert.limit[resource] - recievingBuilding.inputBuffert.amount[resource]
                            amountToMove = np.min((recievingSpace, amountToMove))

                            building.outputBuffert.amount[resource] -= amountToMove
                            recievingBuilding.inputBuffert.amount[resource] += amountToMove

                if building.turnsSinceTransportLinkUpdate >= self.mainProgram.settings.transportLinkUpdateInterval:
                    building.turnsSinceTransportLinkUpdate = 0
                else:
                    building.turnsSinceTransportLinkUpdate += 1

