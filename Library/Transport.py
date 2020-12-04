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
                        building.tilesInRange = None
                        building.ResetDestinations(resource=resource)

                        building.tilesInRange, building.came_from, building.cost_so_far = self.mainProgram.movementGraph.AStar(
                            startNode=building.iTile, maximumCost=self.mainProgram.settings.defaultMovementRange)

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

import queue
class MovementGraph():
    def __init__(self, mainProgram):
        self.mainProgram = mainProgram
        self.edges = {}
        self.cost = {}

    def GetConnections(self, ID):
        return self.edges[ID]

    def GetCost(self, fromNode, toNode):
        for i, node in enumerate(self.edges[fromNode]):
            if node == toNode:
                return self.cost[fromNode][i]

    def InitializeStandard(self):
        '''
        Initializes the world as if it was all standard.
        :return:
        '''
        for iFace in range(np.size(self.mainProgram.world.f, 0)):
            if self.mainProgram.worldProperties.isWater[iFace] == False:
                edges = []
                cost = []
                for adjacentTile in self.mainProgram.world.faceConnections[iFace]:
                    #print(self.mainProgram.worldProperties.isWater[adjacentTile])
                    if self.mainProgram.worldProperties.isWater[adjacentTile] == False:
                        edges.append(adjacentTile)
                        cost.append(self.mainProgram.settings.defaultMovementCost)
                if len(edges) > 0:
                    self.edges[iFace] = edges
                    self.cost[iFace] = cost

    def AStar(self, startNode, maximumCost):
        '''
        The A* algorithm finds the shortest path between the start node and the end node. The method do not utilize an
        early exit to ensure that the shortest path is indeed found. Performance might be improved by saving calculated
        paths in a look up table. Returns None if no path could be found.
        :param startNode:
        :param endNode:
        :param maximumCost: Determines the maximum movement range in which to check.
        :return:
        '''
        border = queue.PriorityQueue()
        border.put(startNode, 0)

        came_from = {}
        came_from[startNode] = None

        cost_so_far = {}
        cost_so_far[startNode] = 0

        # Step through all nodes.
        while not border.empty():
            current = border.get()
            for next in self.edges[current]:

                stepCost = self.GetCost(current, next)
                newCost = cost_so_far[current] + stepCost

                #if next not in cost_so_far or newCost < cost_so_far[next]:
                if (next not in cost_so_far or newCost < cost_so_far[next]) and newCost < maximumCost:
                    border.put(next, newCost)
                    came_from[next] = current
                    cost_so_far[next] = newCost

        tilesInRange = []
        for i, key in enumerate(came_from):
            if i > 0:
                tilesInRange.append(key)

        return tilesInRange, came_from, cost_so_far
        #print(tilesInRange)
        #print(came_from)
        #print(cost_so_far)

        '''
        else:
            # Retrace back to the start node.
            current = endNode
            path = []
            while current != startNode:
                path.append(int(current))
                current = came_from[current]
            path.append(int(startNode))
            path.reverse()

            return path
        '''