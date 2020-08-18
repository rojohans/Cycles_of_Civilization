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
                if y == 0:
                    # Southern border
                    self.edges[TileClass.TileClass.CoordinateToIndex(y, x)] = \
                        [TileClass.TileClass.CoordinateToIndex(y, (x - 1)%N_COLONS),
                         TileClass.TileClass.CoordinateToIndex(y, (x + 1)%N_COLONS),
                         TileClass.TileClass.CoordinateToIndex(y + 1, (x - 1)%N_COLONS),
                         TileClass.TileClass.CoordinateToIndex(y + 1, x%N_COLONS),
                         TileClass.TileClass.CoordinateToIndex(y + 1, (x + 1)%N_COLONS)]
                    #self.cost[]
                    self.cost[TileClass.TileClass.CoordinateToIndex(y, x)] = [1, 1, 1.5, 1, 1.5]
                elif y == N_ROWS-1:
                    # Northern border
                    self.edges[TileClass.TileClass.CoordinateToIndex(y, x)] = \
                        [TileClass.TileClass.CoordinateToIndex(y, (x - 1)%N_COLONS),
                         TileClass.TileClass.CoordinateToIndex(y, (x + 1)%N_COLONS),
                         TileClass.TileClass.CoordinateToIndex(y - 1, (x - 1)%N_COLONS),
                         TileClass.TileClass.CoordinateToIndex(y - 1, x%N_COLONS),
                         TileClass.TileClass.CoordinateToIndex(y - 1, (x + 1)%N_COLONS)]
                    self.cost[TileClass.TileClass.CoordinateToIndex(y, x)] = [1, 1, 1.5, 1, 1.5]
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
                    self.cost[TileClass.TileClass.CoordinateToIndex(y, x)] = [1, 1, 1.5, 1, 1.5, 1.5, 1, 1.5]

    def CreateEdgesFromElevationMap(self, elevationMap, N_ROWS, N_COLONS):
        for row in range(N_ROWS):
            for colon in range(N_COLONS):
                iTile = colon + row * N_COLONS

                adjacentCross = np.zeros((8, 2), dtype=int)
                adjacentCross[:, 0] = int(self.row) + self.ADJACENT_TILES_TEMPLATE[:, 0]
                adjacentCross[:, 1] = np.mod(int(self.colon) + self.ADJACENT_TILES_TEMPLATE[:, 1], self.N_COLONS)

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
    paths in a look up table.
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

            if next not in cost_so_far or newCost < cost_so_far[next]:
                border.put(next, newCost)
                came_from[next] = current
                cost_so_far[next] = newCost

    # Retrace back to the start node.
    current = endNode
    path = []
    while current != startNode:
        path.append(int(current))
        current = came_from[current]
    path.append(int(startNode))
    path.reverse()

    return path

