import numpy as np
import cProfile, pstats, io
from pstats import SortKey


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
            self.buildingsInput[resource] = [None for i in range(self.mainProgram.world.nTriangles)]

    def RecalculateInputDictionay(self):
        self.InitializeInputDictionary()
        for iTriangle, building in enumerate(self.mainProgram.buildingList):
            if building != None:
                for resource in building.inputBuffert.type:
                    self.buildingsInput[resource][iTriangle] = building

    def __call__(self, *args, **kwargs):
        for building in self.mainProgram.buildingList:
            if building != None:

                # Check if the range area should be re calculated.

                recalculateAStarMap = False
                for resource in building.outputBuffert.type:
                    if building.destinationAmount[resource] < building.destinationLimit or building.turnsSinceTransportLinkUpdate >= self.mainProgram.settings.transportLinkUpdateInterval:
                        recalculateAStarMap = True
                if recalculateAStarMap:
                    # Calculate range area.
                    building.tilesInRange = None
                    building.tilesInRange, building.came_from, building.cost_so_far = self.mainProgram.movementGraph.AStar(
                        startNode=building.iTile, maximumCost=self.mainProgram.settings.defaultMovementRange)

                updateLinks = False
                if building.turnsSinceTransportLinkUpdate >= self.mainProgram.settings.transportLinkUpdateInterval:
                    updateLinks = True
                    building.turnsSinceTransportLinkUpdate = 0

                for resource in building.outputBuffert.type:
                    if building.destinationAmount[resource] < building.destinationLimit or updateLinks or (resource == 'labor' and building.unusedLabor > 0.5):
                        #Connect to destination buildings
                        #building.tilesInRange = None
                        building.ResetDestinations(resource=resource)

                        #building.tilesInRange, building.came_from, building.cost_so_far = self.mainProgram.movementGraph.AStar(
                        #    startNode=building.iTile, maximumCost=self.mainProgram.settings.defaultMovementRange)

                        possibleDestinations = []
                        for tileInRange in building.tilesInRange:
                            if self.buildingsInput[resource][tileInRange] != None:
                                possibleDestinations.append(self.mainProgram.buildingList[tileInRange])

                        if len(possibleDestinations) > 0:
                            destinationWeights = np.empty((len(possibleDestinations), 1))


                            for i, possibleDestination in enumerate(possibleDestinations):
                                satisfactionweight = 1/(1+possibleDestination.inputBuffert.smoothedSatisfaction[resource])
                                inputLinksWeight = 1/(1+possibleDestination.inputLinkAmount[resource])
                                distanceWeight = 1/(1 + building.cost_so_far[possibleDestination.iTile])

                                destinationWeights[i, 0] = 0.5*inputLinksWeight + distanceWeight + satisfactionweight

                            destinationIndicesSorted = np.argsort(destinationWeights, axis = 0)
                            destinationIndicesSorted = np.flip(destinationIndicesSorted)

                            for i, iDestination in enumerate(destinationIndicesSorted[:, 0]):
                                iLinkedBuilding = possibleDestinations[iDestination].iTile
                                self.buildingsInput[resource][iLinkedBuilding].inputLinks[resource].append(building)

                                building.destinations[resource].append(self.buildingsInput[resource][iLinkedBuilding])
                                building.destinationAmount[resource] += 1
                                self.buildingsInput[resource][iLinkedBuilding].inputLinkAmount[resource] += 1
                                if i >= building.destinationLimit-1:
                                    break

                        if building.linkNode != None:
                            # When the links are recomputed the link node should be removed.
                            building.linkNode.removeNode()
                            building.linkNode = None
                        #print('Transport link updated')


                    # Resources are transported to destination buildings.
                    # The weights are used to give destination buildings with a lower satisfaction value more resources.
                    if building.outputBuffert.amount[resource] > 0:
                        amountToMoveTotal = building.outputBuffert.amount[resource]
                        nRecievingBuildings = building.destinationAmount[resource]

                        satisfactionWeights = np.empty((nRecievingBuildings, 1))
                        for i, recievingBuilding in enumerate(building.destinations[resource]):
                            satisfactionWeights[i] = 0.01 + 1-recievingBuilding.inputBuffert.smoothedSatisfaction[resource]
                        satisfactionWeights /= np.sum(satisfactionWeights, axis=0)

                        amountToMove = satisfactionWeights * amountToMoveTotal
                        for i, recievingBuilding in enumerate(building.destinations[resource]):
                            #amountToMove = satisfactionWeights[i, 0] * amountToMoveTotal
                            recievingSpace = recievingBuilding.inputBuffert.limit[resource] - recievingBuilding.inputBuffert.amount[resource]
                            amountToMove[i, 0] = np.min((recievingSpace, amountToMove[i, 0]))

                            building.outputBuffert.amount[resource] -= amountToMove[i, 0]
                            recievingBuilding.inputBuffert.amount[resource] += amountToMove[i, 0]

                        amountToMoveTotal -= np.sum(amountToMove, axis=0)[0]
                        for i, recievingBuilding in enumerate(building.destinations[resource]):
                            if amountToMoveTotal > 0:
                                amountToMove = amountToMoveTotal
                                recievingSpace = recievingBuilding.inputBuffert.limit[resource] - recievingBuilding.inputBuffert.amount[resource]
                                amountToMove = np.min((recievingSpace, amountToMove))
                                amountToMoveTotal -= amountToMove

                                building.outputBuffert.amount[resource] -= amountToMove
                                recievingBuilding.inputBuffert.amount[resource] += amountToMove
                        # Calculates unused labor for households.
                        if resource == 'labor':
                            building.unusedLabor = building.outputBuffert.amount['labor'] / building.population
                    '''
                    if building.outputBuffert.amount[resource] > 0:
                        amountToMoveTotal = building.outputBuffert.amount[resource]
                        nRecievingBuildings = building.destinationAmount[resource]
                        for recievingBuilding in building.destinations[resource]:
                            amountToMove = amountToMoveTotal / nRecievingBuildings
                            recievingSpace = recievingBuilding.inputBuffert.limit[resource] - \
                                             recievingBuilding.inputBuffert.amount[resource]
                            amountToMove = np.min((recievingSpace, amountToMove))

                            building.outputBuffert.amount[resource] -= amountToMove
                            recievingBuilding.inputBuffert.amount[resource] += amountToMove
                    '''

                if building.turnsSinceTransportLinkUpdate <= self.mainProgram.settings.transportLinkUpdateInterval:
                    building.turnsSinceTransportLinkUpdate += 1

import queue
class MovementGraph():
    def __init__(self, mainProgram):
        self.mainProgram = mainProgram
        self.edges = {}
        self.cost = {}
        self.upToDate = False

    def GetConnections(self, ID):
        return self.edges[ID]

    def GetCost(self, fromNode, toNode):
        for i, node in enumerate(self.edges[fromNode]):
            if node == toNode:
                return self.cost[fromNode][i]

    def GetCostSimple(self, fromNode, iToNode):
        return self.cost[fromNode][iToNode]

    def InitializeStandard(self):
        '''
        Initializes the world as if it was all standard.
        :return:
        '''
        for iFace in range(np.size(self.mainProgram.world.f, 0)):
            if self.mainProgram.worldProperties.isWater[iFace] == False:
                edges = []
                costs = []
                for adjacentTile in self.mainProgram.world.faceConnections[iFace]:
                    #print(self.mainProgram.worldProperties.isWater[adjacentTile])
                    if self.mainProgram.worldProperties.isWater[adjacentTile] == False:
                        edges.append(adjacentTile)
                        costs.append(self.mainProgram.settings.defaultMovementCost)
                if len(edges) > 0:
                    self.edges[iFace] = edges
                    self.cost[iFace] = costs
                else:
                    self.edges[iFace] = []
                    self.cost[iFace] = []
        self.upToDate = True

    def RecalculateGraph(self):
        '''
        Creates the graph with costs based on tile features.
        This code assumes
        :return:
        '''
        for iFace in range(np.size(self.mainProgram.world.f, 0)):
            if self.mainProgram.worldProperties.isWater[iFace] == False:
                edges = []
                costs = []
                tileCost = None
                if len(self.mainProgram.featureList[iFace]) > 0:
                    tileCost = self.mainProgram.featureList[iFace][0].template.movementCost
                if tileCost == None:
                    tileCost = self.mainProgram.settings.defaultMovementCost

                for adjacentTile in self.mainProgram.world.faceConnections[iFace]:
                    if self.mainProgram.worldProperties.isWater[adjacentTile] == False:
                        edges.append(adjacentTile)

                        adjacentTileCost = None
                        if len(self.mainProgram.featureList[adjacentTile]) > 0:
                            adjacentTileCost = self.mainProgram.featureList[adjacentTile][0].template.movementCost
                        if adjacentTileCost == None:
                            adjacentTileCost = self.mainProgram.settings.defaultMovementCost

                        costs.append((tileCost+adjacentTileCost)/2)
                if len(edges) > 0:
                    self.edges[iFace] = edges
                    self.cost[iFace] = costs
                else:
                    self.edges[iFace] = []
                    self.cost[iFace] = []
        self.upToDate = True

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
        border = [startNode]
        i = 0

        came_from = {}
        came_from[startNode] = None

        cost_so_far = {}
        cost_so_far[startNode] = 0
        # Step through all nodes.
        while i < len(border):
            current = border[i]
            for iAdjacent, next in enumerate(self.edges[current]):

                #stepCost = self.GetCost(current, next)
                stepCost = self.GetCostSimple(current, iAdjacent)
                newCost = cost_so_far[current] + stepCost

                if (next not in cost_so_far or newCost < cost_so_far[next]) and newCost < maximumCost:
                    border.append(next)
                    came_from[next] = current
                    cost_so_far[next] = newCost
            i += 1

        tilesInRange = []
        for i, key in enumerate(came_from):
            if i > 0:
                tilesInRange.append(key)

        return tilesInRange, came_from, cost_so_far

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

    @classmethod
    def RetracePath(cls, graph, startNode):
        path = [startNode]
        nextNode = graph[startNode]
        while nextNode != None:
            path.append(nextNode)
            nextNode = graph[nextNode]
        return path