import numpy as np
import queue

import Library.TileClass as TileClass


class MapGraph():
    def __init__(self):
        self.edges = {}
        self.cost = {}

    def GetConnections(self, ID):
        return self.edges[ID]

    def GetCost(self, fromNode, toNode):
        for i, node in enumerate(self.edges[fromNode]):
            if node == toNode:
                return self.cost[fromNode][i]

    def CreateEdgesSimple(self, N_ROWS, N_COLONS):
        for x in range(N_COLONS):
            for y in range(N_ROWS):
                iTile = TileClass.TileClass.CoordinateToIndex(y, x)
                if y == 0:
                    # Southern border
                    self.edges[TileClass.TileClass.CoordinateToIndex(y, x)] = \
                        [TileClass.TileClass.CoordinateToIndex(y, (x - 1)%N_COLONS),
                         TileClass.TileClass.CoordinateToIndex(y, (x + 1)%N_COLONS),
                         TileClass.TileClass.CoordinateToIndex(y + 1, (x - 1)%N_COLONS),
                         TileClass.TileClass.CoordinateToIndex(y + 1, x%N_COLONS),
                         TileClass.TileClass.CoordinateToIndex(y + 1, (x + 1)%N_COLONS)]
                    self.cost[TileClass.TileClass.CoordinateToIndex(y, x)] = [1,
                                                                              1,
                                                                              1.5,
                                                                              1,
                                                                              1.5]
                elif y == N_ROWS-1:
                    # Northern border
                    self.edges[TileClass.TileClass.CoordinateToIndex(y, x)] = \
                        [TileClass.TileClass.CoordinateToIndex(y, (x - 1)%N_COLONS),
                         TileClass.TileClass.CoordinateToIndex(y, (x + 1)%N_COLONS),
                         TileClass.TileClass.CoordinateToIndex(y - 1, (x - 1)%N_COLONS),
                         TileClass.TileClass.CoordinateToIndex(y - 1, x%N_COLONS),
                         TileClass.TileClass.CoordinateToIndex(y - 1, (x + 1)%N_COLONS)]
                    self.cost[TileClass.TileClass.CoordinateToIndex(y, x)] = [1,
                                                                              1,
                                                                              1.5,
                                                                              1,
                                                                              1.5]
                else:
                    self.edges[TileClass.TileClass.CoordinateToIndex(y, x)] = \
                        [TileClass.TileClass.CoordinateToIndex(y, (x - 1)%N_COLONS),
                         TileClass.TileClass.CoordinateToIndex(y, (x + 1)%N_COLONS),
                         TileClass.TileClass.CoordinateToIndex(y - 1, (x - 1) % N_COLONS),
                         TileClass.TileClass.CoordinateToIndex(y - 1, x % N_COLONS),
                         TileClass.TileClass.CoordinateToIndex(y - 1, (x + 1) % N_COLONS),
                         TileClass.TileClass.CoordinateToIndex(y + 1, (x - 1)%N_COLONS),
                         TileClass.TileClass.CoordinateToIndex(y + 1, x%N_COLONS),
                         TileClass.TileClass.CoordinateToIndex(y + 1, (x + 1)%N_COLONS)]
                    self.cost[TileClass.TileClass.CoordinateToIndex(y, x)] = [1,
                                                                              1,
                                                                              1.5,
                                                                              1,
                                                                              1.5,
                                                                              1.5,
                                                                              1,
                                                                              1.5]
    def CreateEdges(self, N_ROWS, N_COLONS):
        for x in range(N_COLONS):
            for y in range(N_ROWS):
                iTile = TileClass.TileClass.CoordinateToIndex(y, x)
                if y == 0:
                    # Southern border
                    self.edges[TileClass.TileClass.CoordinateToIndex(y, x)] = \
                        [TileClass.TileClass.CoordinateToIndex(y, (x - 1)%N_COLONS),
                         TileClass.TileClass.CoordinateToIndex(y, (x + 1)%N_COLONS),
                         TileClass.TileClass.CoordinateToIndex(y + 1, (x - 1)%N_COLONS),
                         TileClass.TileClass.CoordinateToIndex(y + 1, x%N_COLONS),
                         TileClass.TileClass.CoordinateToIndex(y + 1, (x + 1)%N_COLONS)]
                    self.cost[iTile] = [self.DetermineCost(iTile, self.edges[iTile][0]),
                                        self.DetermineCost(iTile, self.edges[iTile][1]),
                                        self.DetermineCost(iTile, self.edges[iTile][2]),
                                        self.DetermineCost(iTile, self.edges[iTile][3]),
                                        self.DetermineCost(iTile, self.edges[iTile][4])]
                elif y == N_ROWS-1:
                    # Northern border
                    self.edges[TileClass.TileClass.CoordinateToIndex(y, x)] = \
                        [TileClass.TileClass.CoordinateToIndex(y, (x - 1)%N_COLONS),
                         TileClass.TileClass.CoordinateToIndex(y, (x + 1)%N_COLONS),
                         TileClass.TileClass.CoordinateToIndex(y - 1, (x - 1)%N_COLONS),
                         TileClass.TileClass.CoordinateToIndex(y - 1, x%N_COLONS),
                         TileClass.TileClass.CoordinateToIndex(y - 1, (x + 1)%N_COLONS)]
                    self.cost[iTile] = [self.DetermineCost(iTile, self.edges[iTile][0]),
                                        self.DetermineCost(iTile, self.edges[iTile][1]),
                                        self.DetermineCost(iTile, self.edges[iTile][2]),
                                        self.DetermineCost(iTile, self.edges[iTile][3]),
                                        self.DetermineCost(iTile, self.edges[iTile][4])]
                else:
                    self.edges[TileClass.TileClass.CoordinateToIndex(y, x)] = \
                        [TileClass.TileClass.CoordinateToIndex(y, (x - 1)%N_COLONS),
                         TileClass.TileClass.CoordinateToIndex(y, (x + 1)%N_COLONS),
                         TileClass.TileClass.CoordinateToIndex(y - 1, (x - 1) % N_COLONS),
                         TileClass.TileClass.CoordinateToIndex(y - 1, x % N_COLONS),
                         TileClass.TileClass.CoordinateToIndex(y - 1, (x + 1) % N_COLONS),
                         TileClass.TileClass.CoordinateToIndex(y + 1, (x - 1)%N_COLONS),
                         TileClass.TileClass.CoordinateToIndex(y + 1, x%N_COLONS),
                         TileClass.TileClass.CoordinateToIndex(y + 1, (x + 1)%N_COLONS)]
                    self.cost[iTile] = [self.DetermineCost(iTile, self.edges[iTile][0]),
                                        self.DetermineCost(iTile, self.edges[iTile][1]),
                                        self.DetermineCost(iTile, self.edges[iTile][2]),
                                        self.DetermineCost(iTile, self.edges[iTile][3]),
                                        self.DetermineCost(iTile, self.edges[iTile][4]),
                                        self.DetermineCost(iTile, self.edges[iTile][5]),
                                        self.DetermineCost(iTile, self.edges[iTile][6]),
                                        self.DetermineCost(iTile, self.edges[iTile][7])]

    @classmethod
    def DetermineCost(cls, tile1ID, tile2ID):
        '''
        Returns the movement cost between two tiles.
        '''
        tile1 = cls.mainProgram.tileList[tile1ID]
        tile2 = cls.mainProgram.tileList[tile2ID]
        leftTileID = TileClass.TileClass.CoordinateToIndex(tile1.row, (tile1.colon - 1) % cls.mainProgram.settings.N_COLONS)
        rightTileID = TileClass.TileClass.CoordinateToIndex(tile1.row, (tile1.colon + 1) % cls.mainProgram.settings.N_COLONS)
        underTileID = TileClass.TileClass.CoordinateToIndex(tile1.row - 1, tile1.colon % cls.mainProgram.settings.N_COLONS)
        upperTileID = TileClass.TileClass.CoordinateToIndex(tile1.row + 1, tile1.colon % cls.mainProgram.settings.N_COLONS)

        lowerLeftTileID = TileClass.TileClass.CoordinateToIndex(tile1.row-1, (tile1.colon - 1) % cls.mainProgram.settings.N_COLONS)
        lowerRightTileID = TileClass.TileClass.CoordinateToIndex(tile1.row - 1, (tile1.colon + 1) % cls.mainProgram.settings.N_COLONS)
        upperLeftTileID = TileClass.TileClass.CoordinateToIndex(tile1.row+1, (tile1.colon - 1) % cls.mainProgram.settings.N_COLONS)
        upperRightTileID = TileClass.TileClass.CoordinateToIndex(tile1.row + 1, (tile1.colon + 1) % cls.mainProgram.settings.N_COLONS)

        if tile2ID == leftTileID or tile2ID == rightTileID or tile2ID == underTileID or tile2ID == upperTileID:
            # Vertical or horisontal alignment
            cost = 1
        else:
            # Diagonal alignment
            cost = 1.5

        elevationDifference = np.abs(tile1.elevation - tile2.elevation)
        if elevationDifference == 0:
            elevationCostModifier = 0
        elif elevationDifference == 1:
            elevationCostModifier = 1
        else:
            elevationCostModifier = 100000000
        if tile2ID == lowerLeftTileID:
            row1, colon1 = TileClass.TileClass.IndexToCoordinate(leftTileID)
            row2, colon2 = TileClass.TileClass.IndexToCoordinate(underTileID)
            elvDiff = np.abs(cls.mainProgram.world.elevation[row1, colon1]-cls.mainProgram.world.elevation[row2, colon2])
            if elvDiff >=2:elevationCostModifier = 100000000

        elif tile2ID == lowerRightTileID:
            row1, colon1 = TileClass.TileClass.IndexToCoordinate(rightTileID)
            row2, colon2 = TileClass.TileClass.IndexToCoordinate(underTileID)
            elvDiff = np.abs(cls.mainProgram.world.elevation[row1, colon1]-cls.mainProgram.world.elevation[row2, colon2])
            if elvDiff >=2:elevationCostModifier = 100000000

        elif tile2ID == upperLeftTileID:
            row1, colon1 = TileClass.TileClass.IndexToCoordinate(leftTileID)
            row2, colon2 = TileClass.TileClass.IndexToCoordinate(upperTileID)
            elvDiff = np.abs(cls.mainProgram.world.elevation[row1, colon1]-cls.mainProgram.world.elevation[row2, colon2])
            if elvDiff >=2:elevationCostModifier = 100000000

        elif tile2ID == upperRightTileID:
            row1, colon1 = TileClass.TileClass.IndexToCoordinate(upperTileID)
            row2, colon2 = TileClass.TileClass.IndexToCoordinate(rightTileID)
            elvDiff = np.abs(cls.mainProgram.world.elevation[row1, colon1]-cls.mainProgram.world.elevation[row2, colon2])
            if elvDiff >=2:elevationCostModifier = 100000000

        cost += elevationCostModifier

        featureCostModifier = 0 + (len(tile1.features) + len(tile2.features))/2
        cost += featureCostModifier

        roughnessCostModifier = 0 +(cls.mainProgram.world.topographyRoughness[tile1.row, tile1.colon] +
                                    cls.mainProgram.world.topographyRoughness[tile2.row, tile2.colon])/2
        cost += roughnessCostModifier

        if tile1.isWater or tile2.isWater:
            cost += 100000000

        return cost

    def CreateEdgesFromElevationMap(self, elevationMap, N_ROWS, N_COLONS):
        for row in range(N_ROWS):
            for colon in range(N_COLONS):
                iTile = colon + row * N_COLONS

                adjacentCross = np.zeros((8, 2), dtype=int)
                adjacentCross[:, 0] = int(self.row) + self.ADJACENT_TILES_TEMPLATE[:, 0]
                adjacentCross[:, 1] = np.mod(int(self.colon) + self.ADJACENT_TILES_TEMPLATE[:, 1], self.N_COLONS)

    @classmethod
    def Initialize(cls, mainProgram):
        cls.mainProgram = mainProgram

def SimplePathfinding(startNode, endNode, graph):
    '''
    A simple pathfinding algorithm which uses a sort of flood-fill approach to explore paths. The function stops when
    the desired endNode has been reached. The path found is NOT necessarily the shortest one.
    :param startNode:
    :param endNode:
    :param graph:
    :return:
    '''
    border = queue.Queue()
    border.put(startNode)

    came_from = {}
    came_from[startNode] = None

    # Step through all nodes.
    while not border.empty():
        current = border.get()
        for next in graph.edges[current]:
            if next not in came_from:
                border.put(next)
                came_from[next] = current
                if next == endNode:
                    break
            if next == endNode:
                break


    # Retrace back to the start node.
    current = endNode
    path = []
    while current != startNode:
        path.append(int(current))
        current = came_from[current]
    path.append(int(startNode))
    path.reverse()

    return path

def AStar(startNode, endNode, graph):
    '''
    The A* algorithm finds the shortest path between the start node and the end node. The method do not utilize an
    early exit to ensure that the shortest path is indeed found. Performance might be improved by saving calculated
    paths in a look up table. Returns None if no path could be found.
    :param startNode:
    :param endNode:
    :param graph:
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
        for next in graph.edges[current]:

            stepCost = graph.GetCost(current, next)
            newCost = cost_so_far[current] + stepCost

            #if next not in cost_so_far or newCost < cost_so_far[next]:
            if (next not in cost_so_far or newCost < cost_so_far[next]) and newCost < 10000000:
                border.put(next, newCost)
                came_from[next] = current
                cost_so_far[next] = newCost

    if endNode not in came_from:
        print('no path exists')
        return None
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


