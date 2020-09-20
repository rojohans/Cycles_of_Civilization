import panda3d.core as p3d
from direct.task.Task import Task

from matplotlib import image
import pickle
import numpy as np

import Library.Pathfinding as Pathfinding
import Library.Animation as Animation

import Root_Directory

import Data.Dictionaries.FeatureTemplateDictionary as FeatureTemplateDictionary

class Entity():
    def __init__(self, row, colon, elevation):
        self.row = row
        self.colon = colon
        self.elevation = elevation
        self.node = None
        self.wrapperNode = None

class TileClass(Entity):
    def __init__(self, row, colon, elevation):
        '''
        terrain: A terrain is something like grassland, desert or rocky.
        topography: A numpy array containing the elevation map added on top of the standard tile elevation.

        :param row:
        :param colon:
        :param elevation:
        '''
        super().__init__(row, colon, elevation)
        self.terrain = None
        self.normals = None
        self.topography = None
        self.topographyBase = None
        self.topographyTop = None
        self.textureCodeSimple = None
        self.textureCode = None

        self.isWater = False
        self.isShore = False
        self.isOcean = False

        self.waterNode = None

        # The unit is a reference to the unit object which is located on the tile, if any exists.
        self.unit = None

        # A list of references to the features occupying the tile. A feature could be; any kind of forest, a river or a
        # road.
        self.features = []


    def CalculateTriangleNormal(self, p0, p1, p2):
        # The points p0, p1, p2 needs to be given in counter clockwise order.

        v0 = np.array(p1) - np.array(p0)
        v1 = np.array(p2) - np.array(p0)

        c = np.cross(v0, v1)
        c /= np.sqrt(c[0] ** 2 + c[1] ** 2 + c[2] ** 2)

        return p3d.Vec3(c[0], c[1], c[2])

    def CreateNodeExperimental(self):
        '''

        :return:
        '''


        tileSlopeWidth = (1 - self.pandaProgram.settings.TILE_CENTER_WIDTH) / 2
        if self.row > 0 and self.row < self.N_ROWS - 1:
            tileElevation = self.pandaProgram.world.elevation[self.row, self.colon]

            adjacentCross = np.zeros((8, 2), dtype=int)
            adjacentCross[:, 0] = int(self.row) + self.pandaProgram.settings.ADJACENT_TILES_TEMPLATE[:, 0]
            adjacentCross[:, 1] = np.mod(int(self.colon) + self.pandaProgram.settings.ADJACENT_TILES_TEMPLATE[:, 1], self.N_COLONS)
            adjacentZValues = self.pandaProgram.world.elevation[adjacentCross[:, 0], adjacentCross[:, 1]]

            adjacentZValues -= tileElevation

            # v3n3t2 : vertices3, normals3, textureCoordinates2
            vertex_format = p3d.GeomVertexFormat.get_v3n3t2()
            #vertex_format = p3d.GeomVertexFormat.get_v3t2()
            vertex_data = p3d.GeomVertexData("triangle_data", vertex_format, p3d.Geom.UH_static)

            pos_writer = p3d.GeomVertexWriter(vertex_data, "vertex")
            normal_writer = p3d.GeomVertexWriter(vertex_data, "normal")
            tex_writer = p3d.GeomVertexWriter(vertex_data, 'texcoord')

            # Indices of the vertices and triangles
            # 12 --- 15 ------ 8 --- 11
            #  :\  12 : 11  /  : 9  / :
            #  :  \   :   /    :  /   :
            #  : 13 \ : /  10  :/  8  :
            # 13 -- 14,19 --- 9,18 --- 10
            #  :\  14 :  16 /  :\  7  :
            #  :  \   :   /    :  \   :
            #  : 15 \ : /  17  : 6  \ :
            #  0 --- 3,16 --- 4,17 ---- 7
            #  : 0  / :  2  /  : \ 5  :
            #  :   /  :   /    :   \  :
            #  : /  1 : /   3  : 4  \ :
            #  1 ---- 2 ------ 5 ---- 6
            #

            points = []

            # Creates the vertices.
            for y in np.linspace(0, 1, self.pandaProgram.settings.MODEL_RESOLUTION):
                for x in np.linspace(0, 1, self.pandaProgram.settings.MODEL_RESOLUTION):
                    a = self.topography[int(np.round((1-y)*(self.pandaProgram.settings.MODEL_RESOLUTION-1))),
                                        int(np.round(x*(self.pandaProgram.settings.MODEL_RESOLUTION-1)))]
                    #z += 0.1*a/255
                    #z += a/255

                    #z += a
                    z = a
                    #z = a

                    #z += a / 65025

                    points.append(np.array((self.colon+x, self.row+y, z)))
                    pos_writer.add_data3(self.colon + x, self.row + y, z)
                    tex_writer.addData2f(x, y)

            tri = p3d.GeomTriangles(p3d.Geom.UH_static)

            # Creates the triangles.
            for y in range(self.pandaProgram.settings.MODEL_RESOLUTION - 1):
                for x in range(self.pandaProgram.settings.MODEL_RESOLUTION - 1):
                    i = x + y * self.pandaProgram.settings.MODEL_RESOLUTION
                    tri.add_vertices(i, i + self.pandaProgram.settings.MODEL_RESOLUTION + 1, i + self.pandaProgram.settings.MODEL_RESOLUTION)
                    tri.add_vertices(i, i + 1, i + self.pandaProgram.settings.MODEL_RESOLUTION + 1)

            # Assigns a normal to each vertex.
            for y in range(self.pandaProgram.settings.MODEL_RESOLUTION):
                for x in range(self.pandaProgram.settings.MODEL_RESOLUTION):
                    '''
                    i = x + y * self.MODEL_RESOLUTION
                    #print(x)
                    #print(y)
                    #print(i)
                    #print('   ')
                    if x == 0:
                        diffx = points[i + 1] - points[i]
                    elif x == self.MODEL_RESOLUTION-1:
                        #diffx = points[i + 1] - points[i - 1]
                        diffx = points[i] - points[i - 1]
                    else:
                        diffx = points[i + 1] - points[i - 1]

                    if y == 0:
                        diffy = points[i + self.MODEL_RESOLUTION] - points[i]
                    elif y == self.MODEL_RESOLUTION-1:
                        #diffy = points[i + self.MODEL_RESOLUTION] - points[i - self.MODEL_RESOLUTION]
                        diffy = points[i] - points[i - self.MODEL_RESOLUTION]
                    else:
                        #diffy = points[i] - points[i - self.MODEL_RESOLUTION]
                        diffy = points[i + self.MODEL_RESOLUTION] - points[i - self.MODEL_RESOLUTION]
                    #diffx /= np.sqrt(diffx[0]**2 + diffx[1]**2 + diffx[2]**2)
                    #diffy /= np.sqrt(diffy[0]**2 + diffy[1]**2 + diffy[2]**2)

                    normal_writer.add_data3(p3d.Vec3(diffx[1]*diffy[2] - diffx[2]*diffy[1],
                                                     diffx[2]*diffy[0] - diffx[0]*diffy[2],
                                                     diffx[0]*diffy[1] - diffx[1]*diffy[0]))
                    '''
                    normal_writer.add_data3(p3d.Vec3(self.normals[y, x, 0], self.normals[y, x, 1], self.normals[y, x, 2]))

            geom = p3d.Geom(vertex_data)
            geom.add_primitive(tri)

            node = p3d.GeomNode("Tile")
            node.add_geom(geom)
            tile = p3d.NodePath(node)

        else:
            tileElevation = self.pandaProgram.world.elevation[self.row, self.colon]

            vertex_format = p3d.GeomVertexFormat.get_v3n3()
            vertex_data = p3d.GeomVertexData("triangle_data", vertex_format, p3d.Geom.UH_static)

            pos_writer = p3d.GeomVertexWriter(vertex_data, "vertex")
            normal_writer = p3d.GeomVertexWriter(vertex_data, "normal")
            normal = p3d.Vec3(0., 0., 1.)

            pos_writer.add_data3(self.colon, self.row, tileElevation)
            pos_writer.add_data3(self.colon + 1, self.row, tileElevation)
            pos_writer.add_data3(self.colon + 1, self.row + 1, tileElevation)
            pos_writer.add_data3(self.colon, self.row + 1, tileElevation)
            for _ in range(4):
                normal_writer.add_data3(normal)

            tri0 = p3d.GeomTriangles(p3d.Geom.UH_static)
            tri0.add_next_vertices(3)
            tri0.add_vertices(0, 1, 2)
            tri1 = p3d.GeomTriangles(p3d.Geom.UH_static)
            tri1.add_next_vertices(3)
            tri1.add_vertices(3, 0, 2)

            geom = p3d.Geom(vertex_data)
            geom.add_primitive(tri0)
            geom.add_primitive(tri1)
            node = p3d.GeomNode("my_triangle")
            node.add_geom(geom)
            tile = p3d.NodePath(node)
        self.node = tile

    def CreateWaterNode(self):
        if self.isOcean:
            waterLevel = 1 + self.pandaProgram.settings.WATER_HEIGHT
        else:
            waterLevel = self.elevation + self.pandaProgram.settings.WATER_HEIGHT

        vertex_format = p3d.GeomVertexFormat.get_v3n3t2()
        vertex_data = p3d.GeomVertexData("water_data", vertex_format, p3d.Geom.UH_static)

        pos_writer = p3d.GeomVertexWriter(vertex_data, "vertex")
        normal_writer = p3d.GeomVertexWriter(vertex_data, "normal")
        tex_writer = p3d.GeomVertexWriter(vertex_data, 'texcoord')
        normal = p3d.Vec3(0., 0., 1.)

        pos_writer.add_data3(self.colon, self.row, waterLevel)
        tex_writer.addData2f(0, 0)
        pos_writer.add_data3(self.colon + 1, self.row, waterLevel)
        tex_writer.addData2f(1, 0)
        pos_writer.add_data3(self.colon + 1, self.row + 1, waterLevel)
        tex_writer.addData2f(1, 1)
        pos_writer.add_data3(self.colon, self.row + 1, waterLevel)
        tex_writer.addData2f(0, 1)
        for _ in range(4):
            normal_writer.add_data3(normal)

        tri0 = p3d.GeomTriangles(p3d.Geom.UH_static)
        tri0.add_next_vertices(3)
        tri0.add_vertices(0, 1, 2)
        tri1 = p3d.GeomTriangles(p3d.Geom.UH_static)
        tri1.add_next_vertices(3)
        tri1.add_vertices(3, 0, 2)

        geom = p3d.Geom(vertex_data)
        geom.add_primitive(tri0)
        geom.add_primitive(tri1)
        node = p3d.GeomNode("water_square")
        node.add_geom(geom)
        self.waterNode = p3d.NodePath(node)

        self.waterNode.reparentTo(self.pandaProgram.tileRoot)
        self.waterNode.setTransparency(p3d.TransparencyAttrib.MAlpha)

        self.waterNode.setScale(1, 1, self.pandaProgram.settings.ELEVATION_SCALE)
        self.waterNode.setTag('square', str(self.CoordinateToIndex(self.row, self.colon)))
        self.waterNode.setTag('row', str(self.row))
        self.waterNode.setTag('colon', str(self.colon))
        self.waterNode.setTag('type', 'tile')


    def ApplyTopography(self):
        '''
        The topography_roughness value is -1 where there is water. So at that place the flat topography will be used.
        :return:
        '''
        self.topographyBase = self.CreateBaseTopography()

        if self.pandaProgram.world.topographyRoughness[self.row, self.colon] >=0:
            self.topographyTop = self.terrainTopography['topography_roughness_' + str(self.pandaProgram.world.topographyRoughness[self.row, self.colon])]
        else:
            self.topographyTop = self.terrainTopography[
                'topography_roughness_0']


        self.topography = self.topographyBase + self.topographyTop

    def TopographyTile(self):
        if self.row > 0 and self.row < self.N_ROWS - 1:

                adjacentCross = np.zeros((8, 2), dtype=int)
                adjacentCross[:, 0] = int(self.row) + self.ADJACENT_TILES_TEMPLATE[:, 0]
                adjacentCross[:, 1] = np.mod(int(self.colon) + self.ADJACENT_TILES_TEMPLATE[:, 1], self.N_COLONS)
                adjacentZValues = self.elevationMap[adjacentCross[:, 0], adjacentCross[:, 1]]

                adjacentZValues -= self.elevation

                topographyCode = self.CreateTextureCode()
                keyFound = False
                for key, value in self.topographyDictionary.items():
                    if key == topographyCode:
                        keyFound = True
                        # Load an existing topography
                        self.topographyBase = self.CreateBaseTopography()
                        self.topographyTop = value.copy()
                        self.topography = self.topographyBase + self.topographyTop
                        break
                if keyFound == False:
                    # Crate a new topography
                    self.topographyTop = self.CreateTopography(topographyCode=topographyCode)
                    #r = np.random.rand()
                    #if r < 0.5:
                    #    self.topographyTop = np.zeros((self.MODEL_RESOLUTION, self.MODEL_RESOLUTION))
                    #else:
                    #    self.topographyTop = 0.5 + np.zeros((self.MODEL_RESOLUTION, self.MODEL_RESOLUTION))

                    self.topographyDictionary[topographyCode] = self.topographyTop.copy()
                    self.topographyBase = self.CreateBaseTopography()

                    self.topography = self.topographyBase + self.topographyTop

        else:
            self.topographyBase = np.zeros((self.MODEL_RESOLUTION, self.MODEL_RESOLUTION))
            self.topographyTop = np.zeros((self.MODEL_RESOLUTION, self.MODEL_RESOLUTION))
            self.topography = np.zeros((self.MODEL_RESOLUTION, self.MODEL_RESOLUTION))

    def CreateBaseTopography(self):
        tileSlopeWidth = (1 - self.pandaProgram.settings.TILE_CENTER_WIDTH) / 2
        if self.row > 0 and self.row < self.N_ROWS - 1:
            tileElevation = self.pandaProgram.world.elevation[self.row, self.colon]

            adjacentCross = np.zeros((8, 2), dtype=int)
            adjacentCross[:, 0] = int(self.row) + self.pandaProgram.settings.ADJACENT_TILES_TEMPLATE[:, 0]
            adjacentCross[:, 1] = np.mod(int(self.colon) + self.pandaProgram.settings.ADJACENT_TILES_TEMPLATE[:, 1], self.N_COLONS)
            adjacentZValues = self.pandaProgram.world.elevation[adjacentCross[:, 0], adjacentCross[:, 1]]

            adjacentZValues -= tileElevation

            # Indices of the vertices and triangles
            # 12 --- 15 ------ 8 --- 11
            #  :\  12 : 11  /  : 9  / :
            #  :  \   :   /    :  /   :
            #  : 13 \ : /  10  :/  8  :
            # 13 -- 14,19 --- 9,18 --- 10
            #  :\  14 :  16 /  :\  7  :
            #  :  \   :   /    :  \   :
            #  : 15 \ : /  17  : 6  \ :
            #  0 --- 3,16 --- 4,17 ---- 7
            #  : 0  / :  2  /  : \ 5  :
            #  :   /  :   /    :   \  :
            #  : /  1 : /   3  : 4  \ :
            #  1 ---- 2 ------ 5 ---- 6
            #

            p0 = np.array([self.colon, self.row + tileSlopeWidth, tileElevation + adjacentZValues[0] / 2])
            p1 = np.array([self.colon, self.row,
                           tileElevation + (adjacentZValues[0] + adjacentZValues[1] + adjacentZValues[2]) / 4])
            p2 = np.array([self.colon + tileSlopeWidth, self.row, tileElevation + adjacentZValues[2] / 2])
            p3 = np.array([self.colon + tileSlopeWidth, self.row + tileSlopeWidth, tileElevation])

            p4 = np.array([self.colon + self.pandaProgram.settings.TILE_CENTER_WIDTH + tileSlopeWidth, self.row + tileSlopeWidth, tileElevation])
            p5 = np.array(
                [self.colon + self.pandaProgram.settings.TILE_CENTER_WIDTH + tileSlopeWidth, self.row, tileElevation + adjacentZValues[2] / 2])
            p6 = np.array([self.colon + 1, self.row,
                           tileElevation + (adjacentZValues[2] + adjacentZValues[3] + adjacentZValues[4]) / 4])
            p7 = np.array([self.colon + 1, self.row + tileSlopeWidth, tileElevation + adjacentZValues[4] / 2])

            p8 = np.array(
                [self.colon + tileSlopeWidth + self.pandaProgram.settings.TILE_CENTER_WIDTH, self.row + 1,
                 tileElevation + adjacentZValues[6] / 2])
            p9 = np.array(
                [self.colon + tileSlopeWidth + self.pandaProgram.settings.TILE_CENTER_WIDTH, self.row + tileSlopeWidth + self.pandaProgram.settings.TILE_CENTER_WIDTH,
                 tileElevation])
            p10 = np.array(
                [self.colon + 1, self.row + tileSlopeWidth + self.pandaProgram.settings.TILE_CENTER_WIDTH,
                 tileElevation + adjacentZValues[4] / 2])
            p11 = np.array([self.colon + 1, self.row + 1,
                            tileElevation + (adjacentZValues[4] + adjacentZValues[5] + adjacentZValues[6]) / 4])

            p12 = np.array([self.colon, self.row + 1,
                            tileElevation + (adjacentZValues[6] + adjacentZValues[7] + adjacentZValues[0]) / 4])
            p13 = np.array(
                [self.colon, self.row + tileSlopeWidth + self.pandaProgram.settings.TILE_CENTER_WIDTH, tileElevation + adjacentZValues[0] / 2])
            p14 = np.array([self.colon + tileSlopeWidth, self.row + tileSlopeWidth + self.pandaProgram.settings.TILE_CENTER_WIDTH, tileElevation])
            p15 = np.array([self.colon + tileSlopeWidth, self.row + 1, tileElevation + adjacentZValues[6] / 2])


            # Indices of the vertices and triangles

            #  7 ----- 6 ----- 5
            #  :       :       :
            #  :       :       :
            #  :       :       :
            #  0 -----   ----- 4
            #  :       :       :
            #  :       :       :
            #  :       :       :
            #  1 ----- 2 ----- 3
            #

            P0 = np.array([0, 0.5, tileElevation + adjacentZValues[0] / 2])
            P1 = np.array([0, 0,tileElevation + (adjacentZValues[0] + adjacentZValues[1] + adjacentZValues[2]) / 4])
            P2 = np.array([0.5, 0, tileElevation + adjacentZValues[2] / 2])
            P3 = np.array([1, 0,tileElevation + (adjacentZValues[2] + adjacentZValues[3] + adjacentZValues[4]) / 4])
            P4 = np.array([1, 0.5,tileElevation + adjacentZValues[4] / 2])
            P5 = np.array([1, 1,tileElevation + (adjacentZValues[4] + adjacentZValues[5] + adjacentZValues[6]) / 4])
            P6 = np.array([0.5, 1,tileElevation + adjacentZValues[6] / 2])
            P7 = np.array([0, 1,tileElevation + (adjacentZValues[6] + adjacentZValues[7] + adjacentZValues[0]) / 4])

            tileSideWith = (1 - self.pandaProgram.settings.TILE_CENTER_WIDTH) / 2


            baseTopography =  np.zeros((self.pandaProgram.settings.MODEL_RESOLUTION, self.pandaProgram.settings.MODEL_RESOLUTION))

            def InterpolationScaling(value, mode = 'sin', minRange = None, maxRange = None, x = None, y = None):
                if mode == 'sin':
                    return np.sin(value * np.pi / 2)
                elif mode == 'cos':
                    return 1-np.cos(value * np.pi / 2)
                elif mode == 'special':
                    # The value parameter should probably be: value = 1-value
                    if value < self.pandaProgram.settings.TILE_CENTER_WIDTH:
                        return 1
                    else:
                        return np.cos((value-self.pandaProgram.settings.TILE_CENTER_WIDTH)/(1-self.pandaProgram.settings.TILE_CENTER_WIDTH)*np.pi/2)
                elif mode == 'special_circular':


                    range = maxRange - minRange
                    value = minRange + range * value

                    #np.cos((minRange - self.pandaProgram.TILE_CENTER_WIDTH) / (
                    #            maxRange - self.pandaProgram.TILE_CENTER_WIDTH) * np.pi / 2)

                    if value < self.pandaProgram.settings.TILE_CENTER_WIDTH:
                        return 1
                    else:

                        #value -= self.pandaProgram.TILE_CENTER_WIDTH
                        #maxRange -= self.pandaProgram.TILE_CENTER_WIDTH
                        #d = 5
                        #return (1+d*maxRange)/(maxRange**2)*value**2 + (d-2*(1+d*maxRange)/maxRange)*value+1
                        if minRange == maxRange:
                            return 0
                        else:
                            return np.cos((value-self.pandaProgram.settings.TILE_CENTER_WIDTH)/(maxRange-self.pandaProgram.settings.TILE_CENTER_WIDTH)*np.pi/2)

                elif mode == 'squircle':
                    if value < self.pandaProgram.settings.TILE_CENTER_WIDTH:
                        return 1
                    else:
                        if value == 0:
                            return 1
                        else:
                            print(value)
                            value = value-self.pandaProgram.TILE_CENTER_WIDTH

                            squircleRadius =  + np.max([x, y])

                            #squircleRadius = self.pandaProgram.TILE_CENTER_WIDTH + (1-self.pandaProgram.TILE_CENTER_WIDTH)*np.sin(value/(np.sqrt(2)-self.pandaProgram.TILE_CENTER_WIDTH)*np.pi/2)
                            squircleRadius = self.pandaProgram.TILE_CENTER_WIDTH + (1 - self.pandaProgram.TILE_CENTER_WIDTH) \
                                             * value/(np.sqrt(2)-self.pandaProgram.TILE_CENTER_WIDTH)
                            print('r = ', squircleRadius)
                            print('x = ', x)
                            print('y = ', y)

                            #print('x**2 + y**2 - value**2 = ', np.max([x**2 + y**2 - value**2, 0]))
                            return 1-squircleRadius/(0.00001+x*y)*np.sqrt(np.max([x**2 + y**2 - squircleRadius**2, 0]))

            # normal
            # special
            # special_circular
            # special_circular_2
            # special_circular_3
            #interpolationMode = 'special_circular_3'
            interpolationMode = 'special'

            # Creates the vertices.
            for y in np.linspace(0, 1, self.pandaProgram.settings.MODEL_RESOLUTION):
                for x in np.linspace(0, 1, self.pandaProgram.settings.MODEL_RESOLUTION):

                    if interpolationMode == 'special':
                        if x <= 0.5 and y <= 0.5:
                            # Bottom left
                            xLocal = (0.5-x)/0.5
                            yLocal = (0.5-y)/0.5

                            topPart = (InterpolationScaling(xLocal, 'special') * self.elevation + (1 - InterpolationScaling(xLocal, 'special')) * P0[2])
                            bottomPart = (InterpolationScaling(xLocal, 'special') * P2[2] + (1 - InterpolationScaling(xLocal,'special')) * P1[2])
                            z = InterpolationScaling(yLocal, 'special') * topPart + (1-InterpolationScaling(yLocal, 'special')) * bottomPart
                            # 0  self
                            # 1   2
                        elif x > 0.5 and y <= 0.5:
                            # Bottom right
                            xLocal = (x-0.5)/0.5
                            yLocal = (0.5-y)/0.5

                            topPart = (InterpolationScaling(xLocal, 'special') * self.elevation + (1 - InterpolationScaling(xLocal, 'special')) * P4[2])
                            bottomPart = (InterpolationScaling(xLocal, 'special') * P2[2] + (1 - InterpolationScaling(xLocal,'special')) * P3[2])
                            z = InterpolationScaling(yLocal, 'special') * topPart + (1-InterpolationScaling(yLocal, 'special')) * bottomPart
                            # self   4
                            #  2     3
                        elif x <= 0.5 and y > 0.5:
                            # Top left
                            xLocal = (0.5-x)/0.5
                            yLocal = (y-0.5)/0.5

                            bottomPart = (InterpolationScaling(xLocal, 'special') * self.elevation + (1 - InterpolationScaling(xLocal, 'special')) * P0[2])
                            topPart = (InterpolationScaling(xLocal, 'special') * P6[2] + (1 - InterpolationScaling(xLocal,'special')) * P7[2])
                            z = InterpolationScaling(yLocal, 'special') * bottomPart + (1-InterpolationScaling(yLocal, 'special')) * topPart
                            # 7    6
                            # 0   self
                        else:
                            # Top right
                            xLocal = (x - 0.5) / 0.5
                            yLocal = (y - 0.5) / 0.5

                            bottomPart = (InterpolationScaling(xLocal, 'special') * self.elevation + (
                                        1 - InterpolationScaling(xLocal, 'special')) * P4[2])
                            topPart = (InterpolationScaling(xLocal, 'special') * P6[2] + (
                                        1 - InterpolationScaling(xLocal, 'special')) * P5[2])
                            z = InterpolationScaling(yLocal, 'special') * bottomPart + (
                                        1 - InterpolationScaling(yLocal, 'special')) * topPart
                            #  6     5
                            # self   4
                    elif interpolationMode == 'special_circular_2':
                        if x <= 0.5 and y <= 0.5:
                            # Bottom left
                            xLocal = (0.5-x)/0.5
                            yLocal = (0.5-y)/0.5

                            xLarge = xLocal/np.max([xLocal, yLocal])
                            yLarge = yLocal / np.max([xLocal, yLocal])


                            if xLocal > yLocal:
                                #top
                                interpolationValueBorder = InterpolationScaling(yLarge, 'special')
                                borderValue = P0[2]*interpolationValueBorder + P1[2]*(1-interpolationValueBorder)
                            else:
                                #bottom
                                interpolationValueBorder = InterpolationScaling(xLarge, 'special')
                                borderValue = P2[2]*interpolationValueBorder + P1[2]*(1-interpolationValueBorder)

                            '''
                            interpolationValueBorder = InterpolationScaling(yLarge, 'special')
                            borderValueY = P0[2] * interpolationValueBorder + P1[2] * (1 - interpolationValueBorder)
                            interpolationValueBorder = InterpolationScaling(xLarge, 'special')
                            borderValue = P2[2] * interpolationValueBorder + borderValueY * (1 - interpolationValueBorder)
                            '''

                            #diagInterpolation = np.sqrt(InterpolationScaling(yLocal, 'special')**2 + InterpolationScaling(xLocal, 'special')**2)/np.sqrt(2)
                            #diagInterpolation = InterpolationScaling(yLocal, 'special') ** 2 * InterpolationScaling(xLocal,'special') ** 2

                            diagInterpolation = InterpolationScaling(np.sqrt(xLocal ** 2 + yLocal ** 2),
                                                                     'squircle',
                                                                     np.sqrt(xLarge ** 2 + yLarge ** 2),
                                                                     xLocal,
                                                                     yLocal)
                            #diagInterpolation = InterpolationScaling(np.sqrt(xLocal**2+yLocal**2), 'special_circular', np.sqrt(xLarge**2+yLarge**2))
                            #diagInterpolation = InterpolationScaling(np.sqrt(xLocal ** 2 + yLocal ** 2)/np.sqrt(xLarge ** 2 + yLarge ** 2),'special')
                            z = self.elevation * diagInterpolation + (1-diagInterpolation)*borderValue

                            print('diagInterpolation = ', diagInterpolation)
                            print('   ')
                            # 0  self
                            # 1   2
                        elif x > 0.5 and y <= 0.5:
                            # Bottom right
                            xLocal = (x-0.5)/0.5
                            yLocal = (0.5-y)/0.5

                            xLarge = xLocal/np.max([xLocal, yLocal])
                            yLarge = yLocal / np.max([xLocal, yLocal])

                            if xLocal > yLocal:
                                #top
                                interpolationValueBorder = InterpolationScaling(yLarge, 'special')
                                borderValue = P4[2]*interpolationValueBorder + P3[2]*(1-interpolationValueBorder)
                            else:
                                #bottom
                                interpolationValueBorder = InterpolationScaling(xLarge, 'special')
                                borderValue = P2[2]*interpolationValueBorder + P3[2]*(1-interpolationValueBorder)

                            diagInterpolation = InterpolationScaling(np.sqrt(xLocal**2+yLocal**2), 'special_circular', np.sqrt(xLarge**2+yLarge**2))
                            z = self.elevation * diagInterpolation + (1-diagInterpolation)*borderValue

                            # self   4
                            #  2     3
                        elif x <= 0.5 and y > 0.5:
                            # Top left
                            xLocal = (0.5-x)/0.5
                            yLocal = (y-0.5)/0.5

                            xLarge = xLocal/np.max([xLocal, yLocal])
                            yLarge = yLocal / np.max([xLocal, yLocal])

                            if xLocal > yLocal:
                                #top
                                interpolationValueBorder = InterpolationScaling(yLarge, 'special')
                                borderValue = P0[2]*interpolationValueBorder + P7[2]*(1-interpolationValueBorder)
                            else:
                                #bottom
                                interpolationValueBorder = InterpolationScaling(xLarge, 'special')
                                borderValue = P6[2]*interpolationValueBorder + P7[2]*(1-interpolationValueBorder)

                            diagInterpolation = InterpolationScaling(np.sqrt(xLocal**2+yLocal**2), 'special_circular', np.sqrt(xLarge**2+yLarge**2))
                            z = self.elevation * diagInterpolation + (1-diagInterpolation)*borderValue
                            # 7    6
                            # 0   self
                        else:
                            # Top right
                            xLocal = (x - 0.5) / 0.5
                            yLocal = (y - 0.5) / 0.5

                            xLarge = xLocal/np.max([xLocal, yLocal])
                            yLarge = yLocal / np.max([xLocal, yLocal])

                            if xLocal > yLocal:
                                #top
                                interpolationValueBorder = InterpolationScaling(yLarge, 'special')
                                borderValue = P4[2]*interpolationValueBorder + P5[2]*(1-interpolationValueBorder)
                            else:
                                #bottom
                                interpolationValueBorder = InterpolationScaling(xLarge, 'special')
                                borderValue = P6[2]*interpolationValueBorder + P5[2]*(1-interpolationValueBorder)

                            diagInterpolation = InterpolationScaling(np.sqrt(xLocal**2+yLocal**2), 'special_circular', np.sqrt(xLarge**2+yLarge**2))
                            z = self.elevation * diagInterpolation + (1-diagInterpolation)*borderValue
                            #  6     5
                            # self   4
                    elif interpolationMode == 'special_circular':
                        if x <= 0.5 and y <= 0.5:
                            # Bottom left
                            xLocal = (0.5-x)/0.5
                            yLocal = (0.5-y)/0.5

                            corners = [[0.5, 0.5, self.elevation], P0, P2, P1]
                            distances = []
                            weights = []
                            for i, corner in enumerate(corners):
                                distances.append(np.sqrt((corner[0] - x)**2 + (corner[1] - y)**2))
                                weights.append(1/(0.000001+distances[-1]))

                            xLarge = xLocal/np.max([xLocal, yLocal])
                            yLarge = yLocal/np.max([xLocal, yLocal])
                            interpolationValue = InterpolationScaling(2*distances[0], 'special_circular', np.sqrt(xLarge**2 + yLarge**2))



                            weights[0] *= interpolationValue
                            weights[1] *= (1 - interpolationValue)
                            weights[2] *= (1 - interpolationValue)
                            weights[3] *= (1 - interpolationValue)
                            totalWeights = weights[0] + weights[1] + weights[2] + weights[3]

                            z = 0
                            for i in range(4):
                                z += weights[i] * corners[i][2]
                            z /= totalWeights
                            # 0  self
                            # 1   2
                        elif x > 0.5 and y <= 0.5:
                            # Bottom right
                            xLocal = (x-0.5)/0.5
                            yLocal = (0.5-y)/0.5

                            corners = [[0.5, 0.5, self.elevation], P4, P2, P3]
                            distances = []
                            weights = []
                            for i, corner in enumerate(corners):
                                distances.append(np.sqrt((corner[0] - x)**2 + (corner[1] - y)**2))
                                weights.append(1/(0.000001+distances[-1]))

                            xLarge = xLocal/np.max([xLocal, yLocal])
                            yLarge = yLocal/np.max([xLocal, yLocal])
                            interpolationValue = InterpolationScaling(2*distances[0], 'special_circular', np.sqrt(xLarge**2 + yLarge**2))

                            weights[0] *= interpolationValue
                            weights[1] *= (1 - interpolationValue)
                            weights[2] *= (1 - interpolationValue)
                            weights[3] *= (1 - interpolationValue)
                            totalWeights = weights[0] + weights[1] + weights[2] + weights[3]

                            z = 0
                            for i in range(4):
                                z += weights[i] * corners[i][2]
                            z /= totalWeights
                            # self   4
                            #  2     3
                        elif x <= 0.5 and y > 0.5:
                            # Top left
                            xLocal = (0.5-x)/0.5
                            yLocal = (y-0.5)/0.5

                            corners = [[0.5, 0.5, self.elevation], P0, P6, P7]
                            distances = []
                            weights = []
                            for i, corner in enumerate(corners):
                                distances.append(np.sqrt((corner[0] - x)**2 + (corner[1] - y)**2))
                                weights.append(1/(0.000001+distances[-1]))

                            xLarge = xLocal/np.max([xLocal, yLocal])
                            yLarge = yLocal/np.max([xLocal, yLocal])
                            interpolationValue = InterpolationScaling(2*distances[0], 'special_circular', np.sqrt(xLarge**2 + yLarge**2))

                            weights[0] *= interpolationValue
                            weights[1] *= (1 - interpolationValue)
                            weights[2] *= (1 - interpolationValue)
                            weights[3] *= (1 - interpolationValue)
                            totalWeights = weights[0] + weights[1] + weights[2] + weights[3]

                            z = 0
                            for i in range(4):
                                z += weights[i] * corners[i][2]
                            z /= totalWeights
                            # 7    6
                            # 0   self
                        else:
                            # Top right
                            xLocal = (x - 0.5) / 0.5
                            yLocal = (y - 0.5) / 0.5

                            corners = [[0.5, 0.5, self.elevation], P4, P6, P5]
                            distances = []
                            weights = []
                            for i, corner in enumerate(corners):
                                distances.append(np.sqrt((corner[0] - x)**2 + (corner[1] - y)**2))
                                weights.append(1/(0.000001+distances[-1]))

                            xLarge = xLocal/np.max([xLocal, yLocal])
                            yLarge = yLocal/np.max([xLocal, yLocal])
                            interpolationValue = InterpolationScaling(2*distances[0], 'special_circular', np.sqrt(xLarge**2 + yLarge**2))

                            weights[0] *= interpolationValue
                            weights[1] *= (1 - interpolationValue)
                            weights[2] *= (1 - interpolationValue)
                            weights[3] *= (1 - interpolationValue)
                            totalWeights = weights[0] + weights[1] + weights[2] + weights[3]

                            z = 0
                            for i in range(4):
                                z += weights[i] * corners[i][2]
                            z /= totalWeights
                            #  6     5
                            # self   4

                    elif interpolationMode == 'special_circular_3':
                        if x <= 0.5 and y <= 0.5:
                            # Bottom left
                            xLocal = (0.5-x)/0.5
                            yLocal = (0.5-y)/0.5

                            tmpMax = np.max((xLocal, yLocal))
                            XLocal = xLocal / tmpMax
                            YLocal = yLocal / tmpMax
                            diagInterpolationValue = InterpolationScaling(np.sqrt(xLocal ** 2 + yLocal ** 2),
                                                                          'special_circular', minRange=0,
                                                                          maxRange=np.sqrt(
                                                                              XLocal ** 2 + YLocal ** 2))

                            if P2[2] == self.elevation:
                                xInterpolationValueTop = InterpolationScaling(xLocal, 'special_circular', minRange=0,
                                                                           maxRange=1)
                                xInterpolationValueBottom = InterpolationScaling(xLocal, 'special_circular', minRange=0,
                                                                           maxRange=1)
                                xInterpolationValue = InterpolationScaling(xLocal, 'special_circular', minRange=0, maxRange=1)
                            else:
                                xInterpolationValueTop = InterpolationScaling(xLocal, 'special_circular', minRange=0,
                                                                           maxRange=1)
                                #xInterpolationValueBottom = InterpolationScaling(xLocal, 'special_circular', minRange=0,
                                #                                                 maxRange=1)
                                xInterpolationValueBottom = InterpolationScaling(xLocal, 'special_circular', minRange=self.pandaProgram.TILE_CENTER_WIDTH,
                                                                           maxRange=1)

                                #xInterpolationValue = diagInterpolationValue * XLocal / (XLocal + YLocal)
                                if np.sqrt(xLocal**2 + yLocal**2)>self.pandaProgram.TILE_CENTER_WIDTH:
                                    xInterpolationValue = diagInterpolationValue
                                else:
                                    xInterpolationValue = diagInterpolationValue
                                #if yLocal < self.pandaProgram.TILE_CENTER_WIDTH:
                                #    xInterpolationValue = InterpolationScaling(xLocal, 'special_circular', minRange=self.pandaProgram.TILE_CENTER_WIDTH*(1-np.cos(yLocal*np.pi/(2*self.pandaProgram.TILE_CENTER_WIDTH))), maxRange=1)
                                #else:
                                #    xInterpolationValue = InterpolationScaling(xLocal, 'special_circular',minRange=np.min((yLocal,self.pandaProgram.TILE_CENTER_WIDTH)),maxRange=1)


                            if P0[2] == self.elevation:
                                yInterpolationValueRight = InterpolationScaling(yLocal, 'special_circular', minRange=0,
                                                                           maxRange=1)
                                yInterpolationValueLeft = InterpolationScaling(yLocal, 'special_circular', minRange=0,
                                                                           maxRange=1)
                                yInterpolationValue = InterpolationScaling(yLocal, 'special_circular', minRange=0, maxRange=1)
                            else:
                                yInterpolationValueRight = InterpolationScaling(yLocal, 'special_circular', minRange=0,
                                                                           maxRange=1)
                                yInterpolationValueLeft = InterpolationScaling(yLocal, 'special_circular', minRange=self.pandaProgram.TILE_CENTER_WIDTH,
                                                                           maxRange=1)
                                #yInterpolationValue = diagInterpolationValue * YLocal / (XLocal + YLocal)
                                yInterpolationValue = diagInterpolationValue
                                #if xLocal < self.pandaProgram.TILE_CENTER_WIDTH:
                                #    yInterpolationValue = InterpolationScaling(yLocal, 'special_circular', minRange=self.pandaProgram.TILE_CENTER_WIDTH*(1-np.cos(xLocal*np.pi/(2*self.pandaProgram.TILE_CENTER_WIDTH))),maxRange=1)
                                #else:
                                #    yInterpolationValue = InterpolationScaling(yLocal, 'special_circular', minRange=np.min((xLocal, self.pandaProgram.TILE_CENTER_WIDTH)), maxRange=1)

                            topPart = xInterpolationValueTop * self.elevation + (1 - xInterpolationValueTop) * P0[2]
                            bottomPart = xInterpolationValueBottom * P2[2] + (1 - xInterpolationValueBottom) * P1[2]
                            rightPart = yInterpolationValueRight * self.elevation + (1 - yInterpolationValueRight) * P2[2]
                            leftPart = yInterpolationValueLeft * P0[2] + (1 - yInterpolationValueLeft) * P1[2]



                            z1 = yInterpolationValue * topPart + (1 - yInterpolationValue) * bottomPart
                            z2 = xInterpolationValue * rightPart + (1-xInterpolationValue) * leftPart
                            #z = (z1 + z2) / 2
                            z = z1
                            # 0  self
                            # 1   2
                        elif x > 0.5 and y <= 0.5:
                            # Bottom right
                            xLocal = (x-0.5)/0.5
                            yLocal = (0.5-y)/0.5

                            '''
                            if P2[2] == self.elevation:
                                xInterpolationValue = InterpolationScaling(xLocal, 'special_circular', minRange=0, maxRange=1)
                            else:
                                if yLocal < self.pandaProgram.TILE_CENTER_WIDTH:
                                    xInterpolationValue = InterpolationScaling(xLocal, 'special_circular', minRange=self.pandaProgram.TILE_CENTER_WIDTH*(1-np.cos(yLocal*np.pi/(2*self.pandaProgram.TILE_CENTER_WIDTH))), maxRange=1)
                                else:
                                    xInterpolationValue = InterpolationScaling(xLocal, 'special_circular', minRange=np.min((yLocal, self.pandaProgram.TILE_CENTER_WIDTH)), maxRange=1)

                            if P4[2] == self.elevation:
                                yInterpolationValue = InterpolationScaling(yLocal, 'special_circular', minRange=0, maxRange=1)
                            else:
                                if yLocal < self.pandaProgram.TILE_CENTER_WIDTH:
                                    yInterpolationValue = InterpolationScaling(yLocal, 'special_circular', minRange=self.pandaProgram.TILE_CENTER_WIDTH*(1-np.cos(xLocal*np.pi/(2*self.pandaProgram.TILE_CENTER_WIDTH))), maxRange=1)
                                else:
                                    yInterpolationValue = InterpolationScaling(yLocal, 'special_circular', minRange=np.min((xLocal, self.pandaProgram.TILE_CENTER_WIDTH)), maxRange=1)

                            topPart = xInterpolationValue * self.elevation + (1 - xInterpolationValue) * P4[2]
                            bottomPart = xInterpolationValue * P2[2] + (1 - xInterpolationValue) * P3[2]
                            z =  yInterpolationValue * topPart + (1-yInterpolationValue) * bottomPart
                            '''

                            topPart = (InterpolationScaling(xLocal, 'special') * self.elevation + (1 - InterpolationScaling(xLocal, 'special')) * P4[2])
                            bottomPart = (InterpolationScaling(xLocal, 'special') * P2[2] + (1 - InterpolationScaling(xLocal,'special')) * P3[2])
                            yInterpolationValue = InterpolationScaling(yLocal, 'special_circular', minRange=0, maxRange=1)
                            z = yInterpolationValue * topPart + (1-yInterpolationValue) * bottomPart
                            # self   4
                            #  2     3
                        elif x <= 0.5 and y > 0.5:
                            # Top left
                            xLocal = (0.5-x)/0.5
                            yLocal = (y-0.5)/0.5

                            bottomPart = (InterpolationScaling(xLocal, 'special') * self.elevation + (1 - InterpolationScaling(xLocal, 'special')) * P0[2])
                            topPart = (InterpolationScaling(xLocal, 'special') * P6[2] + (1 - InterpolationScaling(xLocal,'special')) * P7[2])
                            yInterpolationValue = InterpolationScaling(yLocal, 'special_circular', minRange=0, maxRange=1)
                            z = yInterpolationValue * bottomPart + (1-yInterpolationValue) * topPart
                            # 7    6
                            # 0   self
                        else:
                            # Top right
                            xLocal = (x - 0.5) / 0.5
                            yLocal = (y - 0.5) / 0.5

                            bottomPart = (InterpolationScaling(xLocal, 'special') * self.elevation + (
                                        1 - InterpolationScaling(xLocal, 'special')) * P4[2])
                            topPart = (InterpolationScaling(xLocal, 'special') * P6[2] + (
                                        1 - InterpolationScaling(xLocal, 'special')) * P5[2])
                            yInterpolationValue = InterpolationScaling(yLocal, 'special_circular', minRange=0, maxRange=1)
                            z = yInterpolationValue * bottomPart + (1 - yInterpolationValue) * topPart
                            #  6     5
                            # self   4


                    elif interpolationMode == 'normal':
                        if x <= tileSideWith and y <= tileSideWith:
                            # Bottom left corner
                            xLocal = x / tileSideWith
                            yLocal = y / tileSideWith
                            z = (1 - InterpolationScaling(xLocal)) * (InterpolationScaling(yLocal) * p0[2] + (1 - InterpolationScaling(yLocal)) * p1[2]) + InterpolationScaling(xLocal) * (
                                        InterpolationScaling(yLocal) * p3[2] + (1 - InterpolationScaling(yLocal)) * p2[2])
                        elif x >= self.TILE_CENTER_WIDTH + tileSideWith and y <= tileSideWith:
                            # Bottom right corner
                            xLocal = (x - self.TILE_CENTER_WIDTH - tileSideWith) / tileSideWith
                            yLocal = y / tileSideWith
                            z = (1 - InterpolationScaling(xLocal, 'cos')) * (InterpolationScaling(yLocal) * p4[2] + (1 - InterpolationScaling(yLocal)) * p5[2]) + InterpolationScaling(xLocal, 'cos') * (
                                        InterpolationScaling(yLocal) * p7[2] + (1 - InterpolationScaling(yLocal)) * p6[2])
                        elif x >= self.TILE_CENTER_WIDTH + tileSideWith and y >= self.TILE_CENTER_WIDTH + tileSideWith:
                            # Top right corner
                            xLocal = (x - self.TILE_CENTER_WIDTH - tileSideWith) / tileSideWith
                            yLocal = (y - self.TILE_CENTER_WIDTH - tileSideWith) / tileSideWith
                            z = (1 - InterpolationScaling(xLocal, 'cos')) * (InterpolationScaling(yLocal, 'cos') * p8[2] + (1 - InterpolationScaling(yLocal, 'cos')) * p9[2]) + InterpolationScaling(xLocal, 'cos') * (
                                        InterpolationScaling(yLocal, 'cos') * p11[2] + (1 - InterpolationScaling(yLocal, 'cos')) * p10[2])
                        elif x <= tileSideWith and y >= self.TILE_CENTER_WIDTH + tileSideWith:
                            # Top left corner
                            xLocal = x / tileSideWith
                            yLocal = (y - self.TILE_CENTER_WIDTH - tileSideWith) / tileSideWith
                            z = (1 - InterpolationScaling(xLocal)) * (InterpolationScaling(yLocal, 'cos') * p12[2] + (1 - InterpolationScaling(yLocal, 'cos')) * p13[2]) + InterpolationScaling(xLocal) * (
                                        InterpolationScaling(yLocal, 'cos') * p15[2] + (1 - InterpolationScaling(yLocal, 'cos')) * p14[2])
                        elif x <= tileSideWith and y >= tileSideWith and y <= self.TILE_CENTER_WIDTH + tileSideWith:
                            # Left side
                            xLocal = x / tileSideWith
                            yLocal = (y - tileSideWith) / tileSideWith
                            z = (1 - InterpolationScaling(xLocal)) * (yLocal * p0[2] + (1 - yLocal) * p13[2]) + InterpolationScaling(xLocal) * (
                                        yLocal * p14[2] + (1 - yLocal) * p3[2])
                        elif x >= tileSideWith and x <= self.TILE_CENTER_WIDTH + tileSideWith and y <= tileSideWith:
                            # Bottom side
                            xLocal = (x - tileSideWith) / tileSideWith
                            yLocal = y / tileSideWith
                            z = (1 - xLocal) * (InterpolationScaling(yLocal) * p3[2] + (1 - InterpolationScaling(yLocal)) * p2[2]) + xLocal * (
                                        InterpolationScaling(yLocal) * p4[2] + (1 - InterpolationScaling(yLocal)) * p5[2])
                        elif x >= self.TILE_CENTER_WIDTH + tileSideWith and y >= tileSideWith and y <= self.TILE_CENTER_WIDTH + tileSideWith:
                            # Right side
                            xLocal = (x - tileSideWith - self.TILE_CENTER_WIDTH) / tileSideWith
                            yLocal = (y - tileSideWith) / tileSideWith
                            z = (1 - InterpolationScaling(xLocal, mode = 'cos')) * (yLocal * p4[2] + (1 - yLocal) * p9[2]) + InterpolationScaling(xLocal, mode = 'cos') * (
                                        yLocal * p10[2] + (1 - yLocal) * p7[2])
                        elif x >= tileSideWith and x <= self.TILE_CENTER_WIDTH + tileSideWith and y >= self.TILE_CENTER_WIDTH + tileSideWith:
                            # Top side
                            xLocal = (x - tileSideWith) / tileSideWith
                            yLocal = (y - self.TILE_CENTER_WIDTH - tileSideWith) / tileSideWith
                            z = (1 - xLocal) * (InterpolationScaling(yLocal, 'cos') * p15[2] + (1 - InterpolationScaling(yLocal, 'cos')) * p14[2]) + xLocal * (
                                        InterpolationScaling(yLocal, 'cos') * p8[2] + (1 - InterpolationScaling(yLocal, 'cos')) * p9[2])
                        else:
                            # center
                            z = self.elevation

                    #a = self.topography[int(np.round((1 - y) * (self.MODEL_RESOLUTION - 1))),
                    #                    int(np.round(x * (self.MODEL_RESOLUTION - 1)))]
                    #baseTopography[int(np.round((1 - y) * (self.MODEL_RESOLUTION - 1))), int(np.round(x * (self.MODEL_RESOLUTION - 1)))] = z
                    baseTopography[int(np.round((1-y) * (self.pandaProgram.settings.MODEL_RESOLUTION - 1))),
                                   int(np.round((x) * (self.pandaProgram.settings.MODEL_RESOLUTION - 1)))] = z

        else:
            baseTopography = np.zeros((self.pandaProgram.settings.MODEL_RESOLUTION, self.pandaProgram.settings.MODEL_RESOLUTION))
        return baseTopography

    def CreateTopography(self, topographyCode):

        tilePartsImage = []
        splitCode = topographyCode.split('-')
        for terrain in splitCode:
            tilePartsImage.append(self.terrainTopography[terrain])

        tileTopography = np.multiply(tilePartsImage[0]/255, self.topographyFilters['center']/255) + \
                         np.multiply(tilePartsImage[1]/255, self.topographyFilters['left']/255) + \
                         np.multiply(tilePartsImage[2]/255, self.topographyFilters['bottom']/255) + \
                         np.multiply(tilePartsImage[3]/255, self.topographyFilters['right']/255) + \
                         np.multiply(tilePartsImage[4]/255, self.topographyFilters['top']/255) + \
                         np.multiply(tilePartsImage[5]/255, self.topographyFilters['bottom_left']/255) + \
                         np.multiply(tilePartsImage[6]/255, self.topographyFilters['bottom_right']/255) + \
                         np.multiply(tilePartsImage[7]/255, self.topographyFilters['top_left']/255) + \
                         np.multiply(tilePartsImage[8]/255, self.topographyFilters['top_right']/255) + \
                         np.multiply(tilePartsImage[9]/255, self.topographyFilters['left_left']/255) + \
                         np.multiply(tilePartsImage[10]/255, self.topographyFilters['bottom_bottom']/255) + \
                         np.multiply(tilePartsImage[11]/255, self.topographyFilters['right_right']/255) + \
                         np.multiply(tilePartsImage[12]/255, self.topographyFilters['top_top']/255) + \
                         np.multiply(tilePartsImage[13]/255, self.topographyFilters['bottom_left_left']/255) + \
                         np.multiply(tilePartsImage[14]/255, self.topographyFilters['bottom_left_bottom']/255) + \
                         np.multiply(tilePartsImage[15]/255, self.topographyFilters['bottom_right_bottom']/255) + \
                         np.multiply(tilePartsImage[16]/255, self.topographyFilters['bottom_right_right']/255) + \
                         np.multiply(tilePartsImage[17]/255, self.topographyFilters['top_right_right']/255) + \
                         np.multiply(tilePartsImage[18]/255, self.topographyFilters['top_right_top']/255) +\
                         np.multiply(tilePartsImage[19]/255, self.topographyFilters['top_left_top']/255) + \
                         np.multiply(tilePartsImage[20]/255, self.topographyFilters['top_left_left']/255)
        return tileTopography

    def TopographyCleanUp(self):
        '''
        Loops over the topography maps. In each loop a corner with 4 surrounding tiles is choosen. The topography on the border of these tiles are made even.
        :return:
        '''

        for row in range(self.N_ROWS-1):
            for colon in range(self.N_COLONS):
                break
                bottomLefti = colon + row * self.N_COLONS
                bottomRighti = np.mod(colon+1, self.N_COLONS) + row * self.N_COLONS
                topLefti = colon + (row+1) * self.N_COLONS
                topRighti = np.mod(colon+1, self.N_COLONS) + (row+1) * self.N_COLONS

                bottomLeftTopography = self.tileList[bottomLefti].topographyTop
                bottomRightTopography = self.tileList[bottomRighti].topographyTop
                topLeftTopography = self.tileList[topLefti].topographyTop
                topRightTopography = self.tileList[topRighti].topographyTop

                blendSize = 6
                # Horizontal evening
                rightEdgeValues = bottomRightTopography[:, 0].copy()
                leftEdgeValues = bottomLeftTopography[:, -1].copy()
                bottomEdgeValues = bottomLeftTopography[0, :].copy()
                topEdgeValues = topLeftTopography[-1, :].copy()

                for x in np.linspace(0, blendSize-1, blendSize, dtype=int):
                    xTransitionValue = self.SinusTransition(x / (blendSize - 1))
                    bottomRightTopography[:, x] = bottomRightTopography[:, x] * (1 + xTransitionValue) / 2 + leftEdgeValues * (1 - xTransitionValue) / 2
                    bottomLeftTopography[:, -x-1] = rightEdgeValues * (1 - xTransitionValue) / 2 + bottomLeftTopography[:,-x-1] * (1 + xTransitionValue) / 2
                for y in np.linspace(0, blendSize - 1, blendSize, dtype=int):
                    yTransitionValue = self.SinusTransition(y / (blendSize - 1))
                    bottomLeftTopography[y, :] = bottomLeftTopography[y, :] * (1 + yTransitionValue) / 2 + topEdgeValues * (1 - yTransitionValue) / 2
                    topLeftTopography[-y - 1, :] = bottomEdgeValues * (1 - yTransitionValue) / 2 + topLeftTopography[-y - 1, :] * (1 + yTransitionValue) / 2

                self.tileList[bottomLefti].topographyTop = bottomLeftTopography
                self.tileList[bottomRighti].topographyTop = bottomRightTopography
                self.tileList[topLefti].topographyTop = topLeftTopography
                self.tileList[topRighti].topographyTop = topRightTopography

                self.tileList[bottomLefti].topography = self.tileList[bottomLefti].topographyBase + self.tileList[bottomLefti].topographyTop
                self.tileList[bottomRighti].topography = self.tileList[bottomRighti].topographyBase + self.tileList[bottomRighti].topographyTop
                self.tileList[topLefti].topography = self.tileList[topLefti].topographyBase + self.tileList[topLefti].topographyTop
                self.tileList[topRighti].topography = self.tileList[topRighti].topographyBase + self.tileList[topRighti].topographyTop


        for row in range(self.N_ROWS - 1):
            for colon in range(self.N_COLONS):
                bottomLefti = colon + row * self.N_COLONS
                bottomRighti = np.mod(colon+1, self.N_COLONS) + row * self.N_COLONS
                topLefti = colon + (row+1) * self.N_COLONS
                topRighti = np.mod(colon+1, self.N_COLONS) + (row+1) * self.N_COLONS

                bottomLeftTopography = self.tileList[bottomLefti].topography
                bottomRightTopography = self.tileList[bottomRighti].topography
                topLeftTopography = self.tileList[topLefti].topography
                topRightTopography = self.tileList[topRighti].topography

                # Horizontal evening
                bottomMean = (bottomLeftTopography[:, -1] + bottomRightTopography[:, 0]) / 2
                bottomLeftTopography[:, -1] = bottomMean
                bottomRightTopography[:, 0] = bottomMean

                # Vertical evening
                leftMean = (bottomLeftTopography[0, :] + topLeftTopography[-1, :]) / 2
                bottomLeftTopography[0, :] = leftMean
                topLeftTopography[-1, :] = leftMean

                # Evening of corner
                cornerMean = (bottomLeftTopography[0, -1] + bottomRightTopography[0, 0] + topLeftTopography[-1, -1] + topRightTopography[-1, 0]) / 4
                bottomLeftTopography[0, -1] = cornerMean
                bottomRightTopography[0, 0] = cornerMean
                topLeftTopography[-1, -1] = cornerMean
                topRightTopography[-1, 0] = cornerMean

                self.tileList[bottomLefti].topography = bottomLeftTopography
                self.tileList[bottomRighti].topography = bottomRightTopography
                self.tileList[topLefti].topography = topLeftTopography
                self.tileList[topRighti].topography = topRightTopography

    def CreateNormals(self):
        '''
        The normal is calculated at each vertex of the tile, except for the border vertices. The border normals will
        need to be calculated using the topogaphy of the adjacent tiles.
        :return:
        '''

        self.normals = np.zeros((self.pandaProgram.settings.MODEL_RESOLUTION, self.pandaProgram.settings.MODEL_RESOLUTION, 3))

        for y in range(self.pandaProgram.settings.MODEL_RESOLUTION):
            for x in range(self.pandaProgram.settings.MODEL_RESOLUTION):
                if x !=0 and x != self.pandaProgram.settings.MODEL_RESOLUTION-1 and y != 0 and y != self.pandaProgram.settings.MODEL_RESOLUTION-1:
                    diffx = np.array((2/(self.pandaProgram.settings.MODEL_RESOLUTION-1), 0, self.topography[self.pandaProgram.settings.MODEL_RESOLUTION-y, x+1]-self.topography[self.pandaProgram.settings.MODEL_RESOLUTION-y, x-1]))
                    diffy = np.array((0, 2 / (self.pandaProgram.settings.MODEL_RESOLUTION - 1),
                                      self.topography[self.pandaProgram.settings.MODEL_RESOLUTION - y - 2, x] - self.topography[
                                          self.pandaProgram.settings.MODEL_RESOLUTION - y, x]))
                else:
                    #print(x)
                    #print(y)
                    #print(' ')
                    if x == 0:
                        diffx = np.array((1 / (self.pandaProgram.settings.MODEL_RESOLUTION - 1), 0,
                                          self.topography[self.pandaProgram.settings.MODEL_RESOLUTION - y-1, x + 1] -
                                          self.topography[self.pandaProgram.settings.MODEL_RESOLUTION - y-1, x]))
                    else:
                        diffx = np.array((1 / (self.pandaProgram.settings.MODEL_RESOLUTION - 1), 0,
                                          self.topography[self.pandaProgram.settings.MODEL_RESOLUTION - y-1, x] -
                                          self.topography[self.pandaProgram.settings.MODEL_RESOLUTION - y-1, x - 1]))
                    if y == 0:
                        diffy = np.array((0, 1 / (self.pandaProgram.settings.MODEL_RESOLUTION - 1),
                                          self.topography[self.pandaProgram.settings.MODEL_RESOLUTION - y - 2, x] -
                                          self.topography[self.pandaProgram.settings.MODEL_RESOLUTION - y - 1, x]))
                    else:
                        diffy = np.array((0, 1 / (self.pandaProgram.settings.MODEL_RESOLUTION - 1),
                                          self.topography[self.pandaProgram.settings.MODEL_RESOLUTION - y - 1, x] -
                                          self.topography[self.pandaProgram.settings.MODEL_RESOLUTION - y, x]))

                normal = [diffx[1] * diffy[2] - diffx[2] * diffy[1],
                          diffx[2] * diffy[0] - diffx[0] * diffy[2],
                          diffx[0] * diffy[1] - diffx[1] * diffy[0]]
                self.normals[y, x] = normal

    def NormalizeNormals(self):
        for y in range(self.pandaProgram.settings.MODEL_RESOLUTION):
            for x in range(self.pandaProgram.settings.MODEL_RESOLUTION):
                normal = self.normals[y, x]
                self.normals[y, x] = normal / np.sqrt(normal[0]**2 + normal[1]**2 + normal[2]**2)

    def NormalsCleanup(self):
        '''
        Calculates the normals for the border of every tile. The topography of adjacent tiles is uses for perfect normals.
        :return:
        '''
        for row in range(self.N_ROWS-1):
            for colon in range(self.N_COLONS):
                bottomLefti = colon + row * self.N_COLONS
                bottomRighti = np.mod(colon+1, self.N_COLONS) + row * self.N_COLONS
                topLefti = colon + (row+1) * self.N_COLONS
                topRighti = np.mod(colon+1, self.N_COLONS) + (row+1) * self.N_COLONS

                bottomLeftNormals = self.tileList[bottomLefti].normals
                bottomRightNormals = self.tileList[bottomRighti].normals
                topLeftNormals = self.tileList[topLefti].normals
                topRightNormals = self.tileList[topRighti].normals

                bottomLeftTopography = self.tileList[bottomLefti].topography
                bottomRightTopography = self.tileList[bottomRighti].topography
                topLeftTopography = self.tileList[topLefti].topography


                # Horizontal normals
                for x in np.linspace(1, self.pandaProgram.settings.MODEL_RESOLUTION-2, self.pandaProgram.settings.MODEL_RESOLUTION-2, dtype=int):
                    diffx = np.array((2/(self.pandaProgram.settings.MODEL_RESOLUTION-1), 0, bottomLeftTopography[0, x+1]-bottomLeftTopography[0, x-1]))
                    diffy = np.array((0, 2 / (self.pandaProgram.settings.MODEL_RESOLUTION - 1),topLeftTopography[-2, x] - bottomLeftTopography[1, x]))
                    normal = [diffx[1] * diffy[2] - diffx[2] * diffy[1],
                              diffx[2] * diffy[0] - diffx[0] * diffy[2],
                              diffx[0] * diffy[1] - diffx[1] * diffy[0]]
                    bottomLeftNormals[-1, x] = normal
                    topLeftNormals[0, x] = normal

                # Vertical normals
                for y in np.linspace(1, self.pandaProgram.settings.MODEL_RESOLUTION-2, self.pandaProgram.settings.MODEL_RESOLUTION-2, dtype=int):
                    diffx = np.array((2/(self.pandaProgram.settings.MODEL_RESOLUTION-1), 0, bottomRightTopography[self.pandaProgram.settings.MODEL_RESOLUTION - y - 1, 1]-bottomLeftTopography[self.pandaProgram.settings.MODEL_RESOLUTION - y - 1, -2]))
                    diffy = np.array((0, 2 / (self.pandaProgram.settings.MODEL_RESOLUTION - 1),bottomLeftTopography[self.pandaProgram.settings.MODEL_RESOLUTION-y-2, -1] - bottomLeftTopography[self.pandaProgram.settings.MODEL_RESOLUTION - y, -1]))
                    normal = [diffx[1] * diffy[2] - diffx[2] * diffy[1],
                              diffx[2] * diffy[0] - diffx[0] * diffy[2],
                              diffx[0] * diffy[1] - diffx[1] * diffy[0]]
                    bottomLeftNormals[y, -1] = normal
                    bottomRightNormals[y, 0] = normal

                # Corner normals
                diffx = np.array((2 / (self.pandaProgram.settings.MODEL_RESOLUTION - 1), 0,bottomRightTopography[0, 1] - bottomLeftTopography[0, -2]))
                diffy = np.array((0, 2 / (self.pandaProgram.settings.MODEL_RESOLUTION - 1),topLeftTopography[-2, -1] - bottomLeftTopography[1, -1]))
                normal = [diffx[1] * diffy[2] - diffx[2] * diffy[1],
                          diffx[2] * diffy[0] - diffx[0] * diffy[2],
                          diffx[0] * diffy[1] - diffx[1] * diffy[0]]
                bottomLeftNormals[-1, -1] = normal
                bottomRightNormals[-1, 0] = normal
                topLeftNormals[0, -1] = normal
                topRightNormals[0, 0] = normal

    def DetermineTileFeatures(self):
        grassProbability = self.grassProbabilityMap[self.row, self.colon]
        desertProbability = self.desertProbabilityMap[self.row, self.colon]
        tundraProbability = self.tundraProbabilityMap[self.row, self.colon]

        summedProbability = grassProbability + desertProbability + tundraProbability
        grassProbability /= summedProbability
        desertProbability /= summedProbability
        tundraProbability /= summedProbability

        r = np.random.rand()
        if r <= grassProbability:
            self.terrain = 'grass'
        elif r <= grassProbability + desertProbability:
            self.terrain = 'desert'
        elif r <= grassProbability + desertProbability + tundraProbability:
            self.terrain = 'tundra'

    def TextureTile(self):

        '''
        myImageGrass = p3d.PNMImage()
        myImageGrass.read("panda3d-master/samples/chessboard/models/grass_4.jpg")
        #myImageGrass.read("panda3d-master/samples/chessboard/models/desert_1.jpg")
        # myImageGrass.read("panda3d-master/samples/chessboard/models/tundra_1.jpg")

        myImageRock = p3d.PNMImage()
        # myImageRock.read("panda3d-master/samples/chessboard/models/rock_1.jpg")
        myImageRock.read("panda3d-master/samples/chessboard/models/grass_cliff_3.jpg")
        #myImageRock.read("panda3d-master/samples/chessboard/models/desert_rock_2.jpg")
        # myImageRock.read("panda3d-master/samples/chessboard/models/tundra_cliff_1.jpg")

        filterCenter = p3d.PNMImage()
        filterCenter.read("panda3d-master/samples/chessboard/models/tile_filter_center.jpg")

        filterSideLeft = p3d.PNMImage()
        filterSideBottom = p3d.PNMImage()
        filterSideRight = p3d.PNMImage()
        filterSideTop = p3d.PNMImage()

        filterSideLeft.read("panda3d-master/samples/chessboard/models/tile_filter_side_Left.jpg")
        filterSideBottom.read("panda3d-master/samples/chessboard/models/tile_filter_side_Bottom.jpg")
        filterSideRight.read("panda3d-master/samples/chessboard/models/tile_filter_side_Right.jpg")
        filterSideTop.read("panda3d-master/samples/chessboard/models/tile_filter_side_Top.jpg")

        filterCornerBottomLeft = p3d.PNMImage()
        filterCornerBottomRight = p3d.PNMImage()
        filterCornerTopLeft = p3d.PNMImage()
        filterCornerTopRight = p3d.PNMImage()

        filterCornerBottomLeft.read("panda3d-master/samples/chessboard/models/tile_filter_corner_Bottom_Left.jpg")
        filterCornerBottomRight.read("panda3d-master/samples/chessboard/models/tile_filter_corner_Bottom_Right.jpg")
        filterCornerTopLeft.read("panda3d-master/samples/chessboard/models/tile_filter_corner_Top_Left.jpg")
        filterCornerTopRight.read("panda3d-master/samples/chessboard/models/tile_filter_corner_Top_Right.jpg")
        '''

        if self.row > 0 and self.row < self.N_ROWS - 1:

                adjacentCross = np.zeros((8, 2), dtype=int)
                adjacentCross[:, 0] = int(self.row) + self.ADJACENT_TILES_TEMPLATE[:, 0]
                adjacentCross[:, 1] = np.mod(int(self.colon) + self.ADJACENT_TILES_TEMPLATE[:, 1], self.N_COLONS)
                adjacentZValues = self.elevationMap[adjacentCross[:, 0], adjacentCross[:, 1]]

                adjacentZValues -= self.elevation

                textureCode = self.CreateTextureCode()
                keyFound = False
                for key, value in self.textureDictionary.items():
                    if key == textureCode:
                        keyFound = True
                        # Load an existing texture
                        tileTexture = value
                        break
                if keyFound == False:
                    # Crate a new texture
                    tileTexture = self.CreateTexture(textureCode=textureCode)
                    self.textureDictionary[textureCode] = tileTexture

        else:
            '''
            tilePartsImage = [myImageGrass,
                              myImageGrass,
                              myImageGrass,
                              myImageGrass,
                              myImageGrass,
                              myImageGrass,
                              myImageGrass,
                              myImageGrass,
                              myImageGrass]

            myEmptyImage = tilePartsImage[0] * filterCenter + \
                           tilePartsImage[1] * filterSideLeft + \
                           tilePartsImage[2] * filterSideBottom + \
                           tilePartsImage[3] * filterSideRight + \
                           tilePartsImage[4] * filterSideTop + \
                           tilePartsImage[5] * filterCornerBottomLeft + \
                           tilePartsImage[6] * filterCornerBottomRight + \
                           tilePartsImage[7] * filterCornerTopLeft + \
                           tilePartsImage[8] * filterCornerTopRight

            # Assume we already have myImage which is our modified PNMImage
            tileTexture = p3d.Texture("texture name")
            # This texture now contains the data from myImage
            tileTexture.load(myEmptyImage)
            '''
            textureArray = np.zeros((self.TEXTUER_RESOLUTION, self.TEXTUER_RESOLUTION, 3), dtype=np.uint8)
            tileTexture = p3d.Texture()
            tileTexture.setup2dTexture(self.TEXTUER_RESOLUTION, self.TEXTUER_RESOLUTION, p3d.Texture.T_unsigned_byte,
                               p3d.Texture.F_rgb)

            buf = textureArray[:, :, :].tostring()
            tileTexture.setRamImage(buf)  # np.array -> texture


        self.node.setTexture(tileTexture)
        #return tileTexture

    def ApplyTexture(self):
        textureArray = np.zeros((self.pandaProgram.settings.TILE_TEXTURE_RESOLUTION,
                                 self.pandaProgram.settings.TILE_TEXTURE_RESOLUTION, 3), dtype=np.uint8)
        textureArray[:, :, 0] = np.uint8(255 * self.textureArray[:, :, 2])
        textureArray[:, :, 1] = np.uint8(255 * self.textureArray[:, :, 1])
        textureArray[:, :, 2] = np.uint8(255 * self.textureArray[:, :, 0])

        tex = p3d.Texture()
        tex.setup2dTexture(self.pandaProgram.settings.TILE_TEXTURE_RESOLUTION,
                           self.pandaProgram.settings.TILE_TEXTURE_RESOLUTION,
                           p3d.Texture.T_unsigned_byte, p3d.Texture.F_rgb)


        buf = textureArray[:, :, :].tostring()
        tex.setRamImage(buf) # np.array -> texture

        # Use texture pixels without interpolation.
        tex.setMagfilter(p3d.Texture.FT_nearest)
        tex.setMinfilter(p3d.Texture.FT_nearest)

        self.node.setTexture(tex)
        self.textureArray = None

    def CreateWater(self, isOcean = False):
        self.isWater = True
        self.isOcean = isOcean
        iTile = self.CoordinateToIndex(self.row, self.colon)
        adjacentTiles = self.pandaProgram.mapGraph.GetConnections(iTile)
        for adjacentTile in adjacentTiles:
            adjacentTile = self.tileList[adjacentTile]
            if adjacentTile.isWater == False:
                adjacentTile.isShore = True
                if isOcean:
                    adjacentTile.isOcean = True



    def ApplyWaterTexture(self):
        waterTextureArray = self.terrainTextures['water']
        textureArray = np.zeros((64, 64, 4), dtype=np.uint8)
        textureArray[:, :, 0] = np.uint8(255 * waterTextureArray[:, :, 2])
        textureArray[:, :, 1] = np.uint8(255 * waterTextureArray[:, :, 1])
        textureArray[:, :, 2] = np.uint8(255 * waterTextureArray[:, :, 0])
        textureArray[:, :, 3] = np.uint8(255 * waterTextureArray[:, :, 3])

        tex = p3d.Texture()
        tex.setup2dTexture(64, 64, p3d.Texture.T_unsigned_byte, p3d.Texture.F_rgba)

        buf = textureArray[:, :, :].tostring()
        tex.setRamImage(buf) # np.array -> texture

        # Use texture pixels without interpolation.
        tex.setMagfilter(p3d.Texture.FT_nearest)
        tex.setMinfilter(p3d.Texture.FT_nearest)

        self.waterNode.setTexture(tex)

    def CreateTextureCodeSimple(self):
        #
        # Returns a string containing a code which specifies the texture.
        #
        adjacentCross = np.zeros((8, 2), dtype=int)

        adjacentCross[:, 0] = np.mod(int(self.row) + self.ADJACENT_TILES_TEMPLATE[:, 0], self.N_ROWS)
        adjacentCross[:, 1] = np.mod(int(self.colon) + self.ADJACENT_TILES_TEMPLATE[:, 1], self.N_COLONS)
        adjacentZValues = self.elevationMap[adjacentCross[:, 0], adjacentCross[:, 1]]

        adjacentZValues -= self.elevation

        textureCode = ''
        # Makes the sides rock if the slope is too big.
        textureCode += self.terrain
        textureCode += '-'
        textureCode += self.terrain
        if abs(adjacentZValues[0]) > 1:
            # left
            textureCode += 'cliff'
        textureCode += '-'
        textureCode += self.terrain
        if abs(adjacentZValues[2]) > 1:
            # bottom
            textureCode += 'cliff'
        textureCode += '-'
        textureCode += self.terrain
        if abs(adjacentZValues[4]) > 1:
            # right
            textureCode += 'cliff'
        textureCode += '-'
        textureCode += self.terrain
        if abs(adjacentZValues[6]) > 1:
            # top
            textureCode += 'cliff'
        textureCode += '-'
        textureCode += self.terrain
        if abs(adjacentZValues[0] - adjacentZValues[2]) > 1 or abs(adjacentZValues[1]) > 1:
            # bottom left
            textureCode += 'cliff'
        textureCode += '-'
        textureCode += self.terrain
        if abs(adjacentZValues[2] - adjacentZValues[4]) > 1 or abs(adjacentZValues[3]) > 1:
            # bottom right
            textureCode += 'cliff'
        textureCode += '-'
        textureCode += self.terrain
        if abs(adjacentZValues[0] - adjacentZValues[6]) > 1 or abs(adjacentZValues[7]) > 1:
            # top left
            textureCode += 'cliff'
        textureCode += '-'
        textureCode += self.terrain
        if abs(adjacentZValues[4] - adjacentZValues[6]) > 1 or abs(adjacentZValues[5]) > 1:
            # top right
            textureCode += 'cliff'

        return textureCode

    def CreateTextureCode(self):
        #
        # Returns a string containing a code which specifies the texture.
        #
        adjacentCross = np.zeros((8, 2), dtype=int)
        adjacentCross[:, 0] = int(self.row) + self.ADJACENT_TILES_TEMPLATE[:, 0]
        adjacentCross[:, 1] = np.mod(int(self.colon) + self.ADJACENT_TILES_TEMPLATE[:, 1], self.N_COLONS)
        adjacentZValues = self.elevationMap[adjacentCross[:, 0], adjacentCross[:, 1]]

        adjacentZValues -= self.elevation

        textureCode = ''
        # Makes the sides rock if the slope is too big.
        textureCode += self.terrain # center
        textureCode += '-'
        textureCode += self.terrain
        if abs(adjacentZValues[0]) > 1:
            # left
            textureCode += 'cliff'
        textureCode += '-'
        textureCode += self.terrain
        if abs(adjacentZValues[2]) > 1:
            # bottom
            textureCode += 'cliff'
        textureCode += '-'
        textureCode += self.terrain
        if abs(adjacentZValues[4]) > 1:
            # right
            textureCode += 'cliff'
        textureCode += '-'
        textureCode += self.terrain
        if abs(adjacentZValues[6]) > 1:
            # top
            textureCode += 'cliff'
        textureCode += '-'
        textureCode += self.terrain
        if abs(adjacentZValues[0] - adjacentZValues[2]) > 1 or abs(adjacentZValues[1]) > 1:
            # bottom left
            textureCode += 'cliff'
        textureCode += '-'
        textureCode += self.terrain
        if abs(adjacentZValues[2] - adjacentZValues[4]) > 1 or abs(adjacentZValues[3]) > 1:
            # bottom right
            textureCode += 'cliff'
        textureCode += '-'
        textureCode += self.terrain
        if abs(adjacentZValues[0] - adjacentZValues[6]) > 1 or abs(adjacentZValues[7]) > 1:
            # top left
            textureCode += 'cliff'
        textureCode += '-'
        textureCode += self.terrain
        if abs(adjacentZValues[4] - adjacentZValues[6]) > 1 or abs(adjacentZValues[5]) > 1:
            # top right
            textureCode += 'cliff'

        # Left tile
        iTileLeft = self.colon-1 + self.row * self.N_COLONS
        leftCode = self.tileList[iTileLeft].textureCodeSimple
        leftTerrain = []
        splitCode = leftCode.split('-')
        for terrain in splitCode:
            leftTerrain.append(terrain)

        # Bottom tile
        iTileBottom = self.colon + (self.row-1) * self.N_COLONS
        bottomCode = self.tileList[iTileBottom].textureCodeSimple
        bottomTerrain = []
        splitCode = bottomCode.split('-')
        for terrain in splitCode:
            bottomTerrain.append(terrain)

        # Right tile
        iTileRight = self.colon+1 + self.row * self.N_COLONS
        rightCode = self.tileList[iTileRight].textureCodeSimple
        rightTerrain = []
        splitCode = rightCode.split('-')
        for terrain in splitCode:
            rightTerrain.append(terrain)

        # Top tile
        iTileTop = self.colon + (self.row+1) * self.N_COLONS
        topCode = self.tileList[iTileTop].textureCodeSimple
        topTerrain = []
        splitCode = topCode.split('-')
        for terrain in splitCode:
            topTerrain.append(terrain)

        # left side border
        textureCode += '-'
        textureCode += leftTerrain[3]

        # bottom side border
        textureCode += '-'
        textureCode += bottomTerrain[4]

        # right side border
        textureCode += '-'
        textureCode += rightTerrain[1]

        # top side border
        textureCode += '-'
        textureCode += topTerrain[2]

        # bottom left left border
        textureCode += '-'
        textureCode += leftTerrain[6]

        # bottom left bottom border
        textureCode += '-'
        textureCode += bottomTerrain[7]

        # bottom right bottom border
        textureCode += '-'
        textureCode += bottomTerrain[8]

        # bottom right right border
        textureCode += '-'
        textureCode += rightTerrain[5]

        # top right right border
        textureCode += '-'
        textureCode += rightTerrain[7]

        # top right top border
        textureCode += '-'
        textureCode += topTerrain[6]

        # top left top border
        textureCode += '-'
        textureCode += topTerrain[5]

        # top left left border
        textureCode += '-'
        textureCode += leftTerrain[8]

        return textureCode

    def CreateTextureArray(self):
        if self.isWater == False:
            soilFertility = self.pandaProgram.world.soilFertility[self.row, self.colon]
            self.textureArray = self.terrainTextures['soil_fertility_' + str(soilFertility)].copy()
        else:
            if self.elevation == 0:
                self.textureArray = self.terrainTextures['deep_water_terrain'].copy()
            else:
                self.textureArray = self.terrainTextures['shallow_water_terrain'].copy()

    def AddSlopeTexture(self, detail = 'low'):
        if self.elevation > 0:
            rockTexture = self.terrainTextures['rock']
            if detail == 'low':
                for xModel in np.linspace(0, self.pandaProgram.settings.MODEL_RESOLUTION-1, self.pandaProgram.settings.MODEL_RESOLUTION):
                    for yModel in np.linspace(0, self.pandaProgram.settings.MODEL_RESOLUTION-1, self.pandaProgram.settings.MODEL_RESOLUTION):
                        if self.normals[int(xModel), int(yModel), 2] < self.pandaProgram.settings.ROCK_TEXTURE_SLOPE_THRESHOLD:

                            xTexture = int(round(self.pandaProgram.settings.TILE_TEXTURE_RESOLUTION*xModel/self.pandaProgram.settings.MODEL_RESOLUTION))
                            yTexture = int(round(self.pandaProgram.settings.TILE_TEXTURE_RESOLUTION*yModel/self.pandaProgram.settings.MODEL_RESOLUTION))

                            rockCircle = self.pandaProgram.settings.ROCK_TEXTURE_CIRCLE.copy()
                            rockCircle[:, 0] += xTexture
                            rockCircle[:, 1] += yTexture
                            for point in rockCircle:
                                if point[0] >= 0 and \
                                   point[0] < self.pandaProgram.settings.TILE_TEXTURE_RESOLUTION and \
                                   point[1] >= 0 and \
                                   point[1] < self.pandaProgram.settings.TILE_TEXTURE_RESOLUTION:
                                    #self.textureArray[int(point[0]), int(point[1])] = [0, 0, 0, 1]
                                    self.textureArray[int(point[0]), int(point[1])] = rockTexture[int(point[0]), int(point[1]), :]
        elif detail == 'high':
            import scipy
            interp = scipy.interpolate.RectBivariateSpline(
                np.linspace(0, 1, self.pandaProgram.settings.MODEL_RESOLUTION),
                np.linspace(0, 1, self.pandaProgram.settings.MODEL_RESOLUTION), self.normals[:, :, 2])

            for x in np.linspace(0, 1, self.pandaProgram.settings.TILE_TEXTURE_RESOLUTION):
                for y in np.linspace(0, 1, self.pandaProgram.settings.TILE_TEXTURE_RESOLUTION):
                    zNormal = interp(x, y)
                    if zNormal < self.pandaProgram.settings.ROCK_TEXTURE_SLOPE_THRESHOLD:
                        xTexture = int(round((self.pandaProgram.settings.TILE_TEXTURE_RESOLUTION-1) * x))
                        yTexture = int(round((self.pandaProgram.settings.TILE_TEXTURE_RESOLUTION-1) * y))

                        self.textureArray[xTexture, yTexture] = rockTexture[xTexture, yTexture, :]

    def CreateTexture(self, textureCode):
        '''

        :param textureCode:
        :return:
        '''

        adjacentCross = np.zeros((8, 2), dtype=int)
        adjacentCross[:, 0] = int(self.row) + self.ADJACENT_TILES_TEMPLATE[:, 0]
        adjacentCross[:, 1] = np.mod(int(self.colon) + self.ADJACENT_TILES_TEMPLATE[:, 1], self.N_COLONS)
        adjacentZValues = self.elevationMap[adjacentCross[:, 0], adjacentCross[:, 1]]

        adjacentZValues -= self.elevation

        '''
        myImageGrass = p3d.PNMImage()
        myImageGrass.read("panda3d-master/samples/chessboard/models/grass_4.jpg")
        #myImageGrass.read("panda3d-master/samples/chessboard/models/desert_1.jpg")
        # myImageGrass.read("panda3d-master/samples/chessboard/models/tundra_1.jpg")

        myImageRock = p3d.PNMImage()
        # myImageRock.read("panda3d-master/samples/chessboard/models/rock_1.jpg")
        myImageRock.read("panda3d-master/samples/chessboard/models/grass_cliff_3.jpg")
        #myImageRock.read("panda3d-master/samples/chessboard/models/desert_rock_2.jpg")
        # myImageRock.read("panda3d-master/samples/chessboard/models/tundra_cliff_1.jpg")

        filterCenter = p3d.PNMImage()
        filterCenter.read("panda3d-master/samples/chessboard/models/tile_filter_center.jpg")

        filterSideLeft = p3d.PNMImage()
        filterSideBottom = p3d.PNMImage()
        filterSideRight = p3d.PNMImage()
        filterSideTop = p3d.PNMImage()

        filterSideLeft.read("panda3d-master/samples/chessboard/models/tile_filter_side_Left.jpg")
        filterSideBottom.read("panda3d-master/samples/chessboard/models/tile_filter_side_Bottom.jpg")
        filterSideRight.read("panda3d-master/samples/chessboard/models/tile_filter_side_Right.jpg")
        filterSideTop.read("panda3d-master/samples/chessboard/models/tile_filter_side_Top.jpg")

        filterCornerBottomLeft = p3d.PNMImage()
        filterCornerBottomRight = p3d.PNMImage()
        filterCornerTopLeft = p3d.PNMImage()
        filterCornerTopRight = p3d.PNMImage()

        filterCornerBottomLeft.read("panda3d-master/samples/chessboard/models/tile_filter_corner_Bottom_Left.jpg")
        filterCornerBottomRight.read("panda3d-master/samples/chessboard/models/tile_filter_corner_Bottom_Right.jpg")
        filterCornerTopLeft.read("panda3d-master/samples/chessboard/models/tile_filter_corner_Top_Left.jpg")
        filterCornerTopRight.read("panda3d-master/samples/chessboard/models/tile_filter_corner_Top_Right.jpg")

        filterBorderSideLeft = p3d.PNMImage()
        filterBorderSideBottom = p3d.PNMImage()
        filterBorderSideRight = p3d.PNMImage()
        filterBorderSideTop = p3d.PNMImage()

        filterBorderSideLeft.read("panda3d-master/samples/chessboard/models/tile_filter_adjacent_side_Left.jpg")
        filterBorderSideBottom.read("panda3d-master/samples/chessboard/models/tile_filter_adjacent_side_Bottom.jpg")
        filterBorderSideRight.read("panda3d-master/samples/chessboard/models/tile_filter_adjacent_side_Right.jpg")
        filterBorderSideTop.read("panda3d-master/samples/chessboard/models/tile_filter_adjacent_side_Top.jpg")

        filterBorderCornerBottomLeftLeft = p3d.PNMImage()
        filterBorderCornerBottomLeftBottom = p3d.PNMImage()
        filterBorderCornerBottomRightBottom = p3d.PNMImage()
        filterBorderCornerBottomRightRight = p3d.PNMImage()
        filterBorderCornerTopRightRight = p3d.PNMImage()
        filterBorderCornerTopoRightTop = p3d.PNMImage()
        filterBorderCornerTopLeftTop = p3d.PNMImage()
        filterBorderCornerTopLeftLeft = p3d.PNMImage()

        filterBorderCornerBottomLeftLeft.read("panda3d-master/samples/chessboard/models/tile_filter_adjacent_corner_Bottom_Left_Left.jpg")
        filterBorderCornerBottomLeftBottom.read("panda3d-master/samples/chessboard/models/tile_filter_adjacent_corner_Bottom_Left_Bottom.jpg")
        filterBorderCornerBottomRightBottom.read("panda3d-master/samples/chessboard/models/tile_filter_adjacent_corner_Bottom_Right_Bottom.jpg")
        filterBorderCornerBottomRightRight.read("panda3d-master/samples/chessboard/models/tile_filter_adjacent_corner_Bottom_Right_Right.jpg")
        filterBorderCornerTopRightRight.read("panda3d-master/samples/chessboard/models/tile_filter_adjacent_corner_Top_Right_Right.jpg")
        filterBorderCornerTopoRightTop.read("panda3d-master/samples/chessboard/models/tile_filter_adjacent_corner_Top_Right_Top.jpg")
        filterBorderCornerTopLeftTop.read("panda3d-master/samples/chessboard/models/tile_filter_adjacent_corner_Top_Left_Top.jpg")
        filterBorderCornerTopLeftLeft.read("panda3d-master/samples/chessboard/models/tile_filter_adjacent_corner_Top_Left_Left.jpg")
        '''

        tilePartsImage = []
        splitCode = textureCode.split('-')
        for terrain in splitCode:
            tilePartsImage.append(self.terrainTextures[terrain])

        '''
        textureImage = tilePartsImage[0] * filterCenter + \
                       tilePartsImage[1] * filterSideLeft + \
                       tilePartsImage[2] * filterSideBottom + \
                       tilePartsImage[3] * filterSideRight + \
                       tilePartsImage[4] * filterSideTop + \
                       tilePartsImage[5] * filterCornerBottomLeft + \
                       tilePartsImage[6] * filterCornerBottomRight + \
                       tilePartsImage[7] * filterCornerTopLeft + \
                       tilePartsImage[8] * filterCornerTopRight + \
                       tilePartsImage[9] * filterBorderSideLeft + \
                       tilePartsImage[10] * filterBorderSideBottom + \
                       tilePartsImage[11] * filterBorderSideRight + \
                       tilePartsImage[12] * filterBorderSideTop + \
                       tilePartsImage[13] * filterBorderCornerBottomLeftLeft + \
                       tilePartsImage[14] * filterBorderCornerBottomLeftBottom + \
                       tilePartsImage[15] * filterBorderCornerBottomRightBottom + \
                       tilePartsImage[16] * filterBorderCornerBottomRightRight + \
                       tilePartsImage[17] * filterBorderCornerTopRightRight + \
                       tilePartsImage[18] * filterBorderCornerTopoRightTop +\
                       tilePartsImage[19] * filterBorderCornerTopLeftTop + \
                       tilePartsImage[20] * filterBorderCornerTopLeftLeft
        '''

        redTexture = np.multiply(tilePartsImage[0][:, :, 0] / 255, self.textureFilters['center'] / 255) + \
                     np.multiply(tilePartsImage[1][:, :, 0] / 255, self.textureFilters['left'] / 255) + \
                     np.multiply(tilePartsImage[2][:, :, 0] / 255, self.textureFilters['bottom'] / 255) + \
                     np.multiply(tilePartsImage[3][:, :, 0] / 255, self.textureFilters['right'] / 255) + \
                     np.multiply(tilePartsImage[4][:, :, 0] / 255, self.textureFilters['top'] / 255) + \
                     np.multiply(tilePartsImage[5][:, :, 0] / 255, self.textureFilters['bottom_left'] / 255) + \
                     np.multiply(tilePartsImage[6][:, :, 0] / 255, self.textureFilters['bottom_right'] / 255) + \
                     np.multiply(tilePartsImage[7][:, :, 0] / 255, self.textureFilters['top_left'] / 255) + \
                     np.multiply(tilePartsImage[8][:, :, 0] / 255, self.textureFilters['top_right'] / 255) + \
                     np.multiply(np.flip(tilePartsImage[9][:, :, 0], 1) / 255, self.textureFilters['left_left'] / 255) + \
                     np.multiply(np.flip(tilePartsImage[10][:, :, 0], 0) / 255, self.textureFilters['bottom_bottom'] / 255) + \
                     np.multiply(np.flip(tilePartsImage[11][:, :, 0], 1) / 255, self.textureFilters['right_right'] / 255) + \
                     np.multiply(np.flip(tilePartsImage[12][:, :, 0], 0) / 255, self.textureFilters['top_top'] / 255) + \
                     np.multiply(tilePartsImage[13][:, :, 0] / 255, self.textureFilters['bottom_left_left'] / 255) + \
                     np.multiply(tilePartsImage[14][:, :, 0] / 255, self.textureFilters['bottom_left_bottom'] / 255) + \
                     np.multiply(tilePartsImage[15][:, :, 0] / 255, self.textureFilters['bottom_right_bottom'] / 255) + \
                     np.multiply(tilePartsImage[16][:, :, 0] / 255, self.textureFilters['bottom_right_right'] / 255) + \
                     np.multiply(tilePartsImage[17][:, :, 0] / 255, self.textureFilters['top_right_right'] / 255) + \
                     np.multiply(tilePartsImage[18][:, :, 0] / 255, self.textureFilters['top_right_top'] / 255) + \
                     np.multiply(tilePartsImage[19][:, :, 0] / 255, self.textureFilters['top_left_top'] / 255) + \
                     np.multiply(tilePartsImage[20][:, :, 0] / 255, self.textureFilters['top_left_left'] / 255)

        greenTexture = np.multiply(tilePartsImage[0][:, :, 1] / 255, self.textureFilters['center'] / 255) + \
                     np.multiply(tilePartsImage[1][:, :, 1] / 255, self.textureFilters['left'] / 255) + \
                     np.multiply(tilePartsImage[2][:, :, 1] / 255, self.textureFilters['bottom'] / 255) + \
                     np.multiply(tilePartsImage[3][:, :, 1] / 255, self.textureFilters['right'] / 255) + \
                     np.multiply(tilePartsImage[4][:, :, 1] / 255, self.textureFilters['top'] / 255) + \
                     np.multiply(tilePartsImage[5][:, :, 1] / 255, self.textureFilters['bottom_left'] / 255) + \
                     np.multiply(tilePartsImage[6][:, :, 1] / 255, self.textureFilters['bottom_right'] / 255) + \
                     np.multiply(tilePartsImage[7][:, :, 1] / 255, self.textureFilters['top_left'] / 255) + \
                     np.multiply(tilePartsImage[8][:, :, 1] / 255, self.textureFilters['top_right'] / 255) + \
                     np.multiply(np.flip(tilePartsImage[9][:, :, 1], 1) / 255, self.textureFilters['left_left'] / 255) + \
                     np.multiply(np.flip(tilePartsImage[10][:, :, 1], 0) / 255, self.textureFilters['bottom_bottom'] / 255) + \
                     np.multiply(np.flip(tilePartsImage[11][:, :, 1], 1) / 255, self.textureFilters['right_right'] / 255) + \
                     np.multiply(np.flip(tilePartsImage[12][:, :, 1], 0) / 255, self.textureFilters['top_top'] / 255) + \
                     np.multiply(tilePartsImage[13][:, :, 1] / 255, self.textureFilters['bottom_left_left'] / 255) + \
                     np.multiply(tilePartsImage[14][:, :, 1] / 255, self.textureFilters['bottom_left_bottom'] / 255) + \
                     np.multiply(tilePartsImage[15][:, :, 1] / 255, self.textureFilters['bottom_right_bottom'] / 255) + \
                     np.multiply(tilePartsImage[16][:, :, 1] / 255, self.textureFilters['bottom_right_right'] / 255) + \
                     np.multiply(tilePartsImage[17][:, :, 1] / 255, self.textureFilters['top_right_right'] / 255) + \
                     np.multiply(tilePartsImage[18][:, :, 1] / 255, self.textureFilters['top_right_top'] / 255) + \
                     np.multiply(tilePartsImage[19][:, :, 1] / 255, self.textureFilters['top_left_top'] / 255) + \
                     np.multiply(tilePartsImage[20][:, :, 1] / 255, self.textureFilters['top_left_left'] / 255)

        blueTexture = np.multiply(tilePartsImage[0][:, :, 2] / 255, self.textureFilters['center'] / 255) + \
                     np.multiply(tilePartsImage[1][:, :, 2] / 255, self.textureFilters['left'] / 255) + \
                     np.multiply(tilePartsImage[2][:, :, 2] / 255, self.textureFilters['bottom'] / 255) + \
                     np.multiply(tilePartsImage[3][:, :, 2] / 255, self.textureFilters['right'] / 255) + \
                     np.multiply(tilePartsImage[4][:, :, 2] / 255, self.textureFilters['top'] / 255) + \
                     np.multiply(tilePartsImage[5][:, :, 2] / 255, self.textureFilters['bottom_left'] / 255) + \
                     np.multiply(tilePartsImage[6][:, :, 2] / 255, self.textureFilters['bottom_right'] / 255) + \
                     np.multiply(tilePartsImage[7][:, :, 2] / 255, self.textureFilters['top_left'] / 255) + \
                     np.multiply(tilePartsImage[8][:, :, 2] / 255, self.textureFilters['top_right'] / 255) + \
                     np.multiply(np.flip(tilePartsImage[9][:, :, 2], 1) / 255, self.textureFilters['left_left'] / 255) + \
                     np.multiply(np.flip(tilePartsImage[10][:, :, 2], 0) / 255, self.textureFilters['bottom_bottom'] / 255) + \
                     np.multiply(np.flip(tilePartsImage[11][:, :, 2], 1) / 255, self.textureFilters['right_right'] / 255) + \
                     np.multiply(np.flip(tilePartsImage[12][:, :, 2], 0) / 255, self.textureFilters['top_top'] / 255) + \
                     np.multiply(tilePartsImage[13][:, :, 2] / 255, self.textureFilters['bottom_left_left'] / 255) + \
                     np.multiply(tilePartsImage[14][:, :, 2] / 255, self.textureFilters['bottom_left_bottom'] / 255) + \
                     np.multiply(tilePartsImage[15][:, :, 2] / 255, self.textureFilters['bottom_right_bottom'] / 255) + \
                     np.multiply(tilePartsImage[16][:, :, 2] / 255, self.textureFilters['bottom_right_right'] / 255) + \
                     np.multiply(tilePartsImage[17][:, :, 2] / 255, self.textureFilters['top_right_right'] / 255) + \
                     np.multiply(tilePartsImage[18][:, :, 2] / 255, self.textureFilters['top_right_top'] / 255) + \
                     np.multiply(tilePartsImage[19][:, :, 2] / 255, self.textureFilters['top_left_top'] / 255) + \
                     np.multiply(tilePartsImage[20][:, :, 2] / 255, self.textureFilters['top_left_left'] / 255)

        '''
        redTexture = np.multiply(tilePartsImage[0][:, :, 0] / 255, self.textureFilters['center'] / 255) + \
                     np.multiply(tilePartsImage[1][:, :, 0] / 255, self.textureFilters['left'] / 255) + \
                     np.multiply(tilePartsImage[2][:, :, 0] / 255, self.textureFilters['bottom'] / 255) + \
                     np.multiply(tilePartsImage[3][:, :, 0] / 255, self.textureFilters['right'] / 255) + \
                     np.multiply(tilePartsImage[4][:, :, 0] / 255, self.textureFilters['top'] / 255) + \
                     np.multiply(tilePartsImage[5][:, :, 0] / 255, self.textureFilters['bottom_left'] / 255) + \
                     np.multiply(tilePartsImage[6][:, :, 0] / 255, self.textureFilters['bottom_right'] / 255) + \
                     np.multiply(tilePartsImage[7][:, :, 0] / 255, self.textureFilters['top_left'] / 255) + \
                     np.multiply(tilePartsImage[8][:, :, 0] / 255, self.textureFilters['top_right'] / 255) + \
                     np.multiply(np.flip(tilePartsImage[9][:, :, 0], 1) / 255, self.textureFilters['left_left'] / 255) + \
                     np.multiply(np.flip(tilePartsImage[10][:, :, 0], 0) / 255, self.textureFilters['bottom_bottom'] / 255) + \
                     np.multiply(np.flip(tilePartsImage[11][:, :, 0], 1) / 255, self.textureFilters['right_right'] / 255) + \
                     np.multiply(np.flip(tilePartsImage[12][:, :, 0], 0) / 255, self.textureFilters['top_top'] / 255) + \
                     np.multiply(tilePartsImage[13][:, :, 0] / 255, self.textureFilters['bottom_left_left'] / 255) + \
                     np.multiply(tilePartsImage[14][:, :, 0] / 255, self.textureFilters['bottom_left_bottom'] / 255) + \
                     np.multiply(tilePartsImage[15][:, :, 0] / 255, self.textureFilters['bottom_right_bottom'] / 255) + \
                     np.multiply(tilePartsImage[16][:, :, 0] / 255, self.textureFilters['bottom_right_right'] / 255) + \
                     np.multiply(tilePartsImage[17][:, :, 0] / 255, self.textureFilters['top_right_right'] / 255) + \
                     np.multiply(tilePartsImage[18][:, :, 0] / 255, self.textureFilters['top_right_top'] / 255) + \
                     np.multiply(tilePartsImage[19][:, :, 0] / 255, self.textureFilters['top_left_top'] / 255) + \
                     np.multiply(tilePartsImage[20][:, :, 0] / 255, self.textureFilters['top_left_left'] / 255)

        greenTexture = np.multiply(tilePartsImage[0][:, :, 1] / 255, self.textureFilters['center'] / 255) + \
                     np.multiply(tilePartsImage[1][:, :, 1] / 255, self.textureFilters['left'] / 255) + \
                     np.multiply(tilePartsImage[2][:, :, 1] / 255, self.textureFilters['bottom'] / 255) + \
                     np.multiply(tilePartsImage[3][:, :, 1] / 255, self.textureFilters['right'] / 255) + \
                     np.multiply(tilePartsImage[4][:, :, 1] / 255, self.textureFilters['top'] / 255) + \
                     np.multiply(tilePartsImage[5][:, :, 1] / 255, self.textureFilters['bottom_left'] / 255) + \
                     np.multiply(tilePartsImage[6][:, :, 1] / 255, self.textureFilters['bottom_right'] / 255) + \
                     np.multiply(tilePartsImage[7][:, :, 1] / 255, self.textureFilters['top_left'] / 255) + \
                     np.multiply(tilePartsImage[8][:, :, 1] / 255, self.textureFilters['top_right'] / 255) + \
                     np.multiply(np.flip(tilePartsImage[9][:, :, 1], 1) / 255, self.textureFilters['left_left'] / 255) + \
                     np.multiply(np.flip(tilePartsImage[10][:, :, 1], 0) / 255, self.textureFilters['bottom_bottom'] / 255) + \
                     np.multiply(np.flip(tilePartsImage[11][:, :, 1], 1) / 255, self.textureFilters['right_right'] / 255) + \
                     np.multiply(np.flip(tilePartsImage[12][:, :, 1], 0) / 255, self.textureFilters['top_top'] / 255) + \
                     np.multiply(tilePartsImage[13][:, :, 1] / 255, self.textureFilters['bottom_left_left'] / 255) + \
                     np.multiply(tilePartsImage[14][:, :, 1] / 255, self.textureFilters['bottom_left_bottom'] / 255) + \
                     np.multiply(tilePartsImage[15][:, :, 1] / 255, self.textureFilters['bottom_right_bottom'] / 255) + \
                     np.multiply(tilePartsImage[16][:, :, 1] / 255, self.textureFilters['bottom_right_right'] / 255) + \
                     np.multiply(tilePartsImage[17][:, :, 1] / 255, self.textureFilters['top_right_right'] / 255) + \
                     np.multiply(tilePartsImage[18][:, :, 1] / 255, self.textureFilters['top_right_top'] / 255) + \
                     np.multiply(tilePartsImage[19][:, :, 1] / 255, self.textureFilters['top_left_top'] / 255) + \
                     np.multiply(tilePartsImage[20][:, :, 1] / 255, self.textureFilters['top_left_left'] / 255)

        blueTexture = np.multiply(tilePartsImage[0][:, :, 2] / 255, self.textureFilters['center'] / 255) + \
                     np.multiply(tilePartsImage[1][:, :, 2] / 255, self.textureFilters['left'] / 255) + \
                     np.multiply(tilePartsImage[2][:, :, 2] / 255, self.textureFilters['bottom'] / 255) + \
                     np.multiply(tilePartsImage[3][:, :, 2] / 255, self.textureFilters['right'] / 255) + \
                     np.multiply(tilePartsImage[4][:, :, 2] / 255, self.textureFilters['top'] / 255) + \
                     np.multiply(tilePartsImage[5][:, :, 2] / 255, self.textureFilters['bottom_left'] / 255) + \
                     np.multiply(tilePartsImage[6][:, :, 2] / 255, self.textureFilters['bottom_right'] / 255) + \
                     np.multiply(tilePartsImage[7][:, :, 2] / 255, self.textureFilters['top_left'] / 255) + \
                     np.multiply(tilePartsImage[8][:, :, 2] / 255, self.textureFilters['top_right'] / 255) + \
                     np.multiply(np.flip(tilePartsImage[9][:, :, 2], 1) / 255, self.textureFilters['left_left'] / 255) + \
                     np.multiply(np.flip(tilePartsImage[10][:, :, 2], 0) / 255, self.textureFilters['bottom_bottom'] / 255) + \
                     np.multiply(np.flip(tilePartsImage[11][:, :, 2], 1) / 255, self.textureFilters['right_right'] / 255) + \
                     np.multiply(np.flip(tilePartsImage[12][:, :, 2], 0) / 255, self.textureFilters['top_top'] / 255) + \
                     np.multiply(tilePartsImage[13][:, :, 2] / 255, self.textureFilters['bottom_left_left'] / 255) + \
                     np.multiply(tilePartsImage[14][:, :, 2] / 255, self.textureFilters['bottom_left_bottom'] / 255) + \
                     np.multiply(tilePartsImage[15][:, :, 2] / 255, self.textureFilters['bottom_right_bottom'] / 255) + \
                     np.multiply(tilePartsImage[16][:, :, 2] / 255, self.textureFilters['bottom_right_right'] / 255) + \
                     np.multiply(tilePartsImage[17][:, :, 2] / 255, self.textureFilters['top_right_right'] / 255) + \
                     np.multiply(tilePartsImage[18][:, :, 2] / 255, self.textureFilters['top_right_top'] / 255) + \
                     np.multiply(tilePartsImage[19][:, :, 2] / 255, self.textureFilters['top_left_top'] / 255) + \
                     np.multiply(tilePartsImage[20][:, :, 2] / 255, self.textureFilters['top_left_left'] / 255)
        '''

        textureArray = np.zeros((self.TEXTUER_RESOLUTION, self.TEXTUER_RESOLUTION, 3), dtype = np.uint8)
        textureArray[:, :, 2] = np.uint8(255*np.flip(redTexture, 0))
        textureArray[:, :, 1] = np.uint8(255*np.flip(greenTexture, 0))
        textureArray[:, :, 0] = np.uint8(255*np.flip(blueTexture, 0))


        tex = p3d.Texture()
        tex.setup2dTexture(self.TEXTUER_RESOLUTION, self.TEXTUER_RESOLUTION, p3d.Texture.T_unsigned_byte, p3d.Texture.F_rgb)

        #textureArray[-1, :, :] = 0
        #textureArray[:, -1, :] = 0

        buf = textureArray[:, :, :].tostring()
        tex.setRamImage(buf) # np.array -> texture

        # Use texture pixels without interpolation.
        tex.setMagfilter(p3d.Texture.FT_nearest)
        tex.setMinfilter(p3d.Texture.FT_nearest)

        return tex

    def SinusTransition(self, value):
        return np.sin(np.pi*value/2)
        #return value

    def Wrap(self, direction):
        self.wrapperNode = self.pandaProgram.tileRoot.attachNewNode('wrapperNode')
        self.node.copyTo(self.wrapperNode)
        if self.waterNode is not None:
            self.wrapperNodeWater = self.pandaProgram.tileRoot.attachNewNode('wrapperNodeWater')
            self.waterNode.copyTo(self.wrapperNodeWater)

        if direction == 'left':
            self.wrapperNode.setPos(self.wrapperNode, (-self.N_COLONS, 0, 0))
            if self.waterNode is not None:
                self.wrapperNodeWater.setPos(self.wrapperNodeWater, (-self.N_COLONS, 0, 0))
        if direction == 'right':
            self.wrapperNode.setPos(self.wrapperNode, (self.N_COLONS, 0, 0))
            if self.waterNode is not None:
                self.wrapperNodeWater.setPos(self.wrapperNodeWater, (self.N_COLONS, 0, 0))

    @classmethod
    def Initialize(cls, N_ROWS, N_COLONS, tileList, pandaProgram):
        #
        # The texture dictionary is used to store textures which has been used on a tile. If the same texture is needed
        # for another tile it can simply be retrieved from the dictionary.
        #

        cls.pandaProgram = pandaProgram

        cls.N_ROWS = N_ROWS
        cls.N_COLONS = N_COLONS

        cls.tileList = tileList

        #cls.elevationMap = elevationMap
        #cls.ADJACENT_TILES_TEMPLATE = ADJACENT_TILES_TEMPLATE
        #cls.TILE_CENTER_WIDTH = TILE_CENTER_WIDTH

        #cls.MODEL_RESOLUTION = modelResolution
        #cls.TEXTUER_RESOLUTION = textureResolution

        try:
            topographyFile = open('topography_dictionary.pkl', 'rb')
            cls.topographyDictionary = pickle.load(topographyFile)
            topographyFile.close()
        except:
            cls.topographyDictionary = {}
        try:
            textureFile = open('texture_dictionary.pkl', 'rb')
            cls.textureDictionary = pickle.load(textureFile)
            textureFile.close()
        except:
            cls.textureDictionary = {}

        #cls.grassProbabilityMap = grassProbabilityMap
        #cls.desertProbabilityMap = desertProbabilityMap
        #cls.tundraProbabilityMap = tundraProbabilityMap

        #terrainCodes = {'grass': 'g', 'desert': 'd', 'tundra': 't', 'cliff': 'c'}

        #cls.terrainTopography ={'grass':image.imread("panda3d-master/samples/chessboard/models/topography_grass_symmetrical.jpg")[:, :, 0],
        #                        'desert':image.imread("panda3d-master/samples/chessboard/models/topography_desert_symmetrical.jpg")[:, :, 0],
        #                        'tundra':image.imread("panda3d-master/samples/chessboard/models/topography_tundra_symmetrical.jpg")[:, :, 0],
        #                        'grasscliff':image.imread("panda3d-master/samples/chessboard/models/topography_grass_cliff_symmetrical.jpg")[:, :, 0],
        #                        'desertcliff':image.imread("panda3d-master/samples/chessboard/models/topography_grass_cliff_symmetrical.jpg")[:, :, 0],
        #                        'tundracliff':image.imread("panda3d-master/samples/chessboard/models/topography_grass_cliff_symmetrical.jpg")[:, :, 0]}
        cls.terrainTopography ={'grass':image.imread(Root_Directory.Path() + "/Data/Tile_Data/topography_desert_symmetrical.jpg")[:, :, 0],
                                'desert':image.imread(Root_Directory.Path() + "/Data/Tile_Data/topography_desert_symmetrical.jpg")[:, :, 0],
                                'tundra':image.imread(Root_Directory.Path() + "/Data/Tile_Data/topography_desert_symmetrical.jpg")[:, :, 0],
                                'grasscliff':image.imread(Root_Directory.Path() + "/Data/Tile_Data/topography_desert_symmetrical.jpg")[:, :, 0],
                                'desertcliff':image.imread(Root_Directory.Path() + "/Data/Tile_Data/topography_desert_symmetrical.jpg")[:, :, 0],
                                'tundracliff':image.imread(Root_Directory.Path() + "/Data/Tile_Data/topography_desert_symmetrical.jpg")[:, :, 0],
                                'topography_roughness_0':image.imread(Root_Directory.Path() + "/Data/Tile_Data/topography_roughness_0.png")[:, :, 0],
                                'topography_roughness_1':image.imread(Root_Directory.Path() + "/Data/Tile_Data/topography_roughness_1.png")[:, :, 0],
                                'topography_roughness_2':image.imread(Root_Directory.Path() + "/Data/Tile_Data/topography_roughness_2.png")[:, :, 0]}

        cls.topographyFilters = {'center':image.imread(Root_Directory.Path() + "/Data/Tile_Data/topography_filter_center.jpg")[:, :, 0],
                                 'left':image.imread(Root_Directory.Path() + "/Data/Tile_Data/topography_filter_side_Left.jpg")[:, :, 0],
                                 'bottom':image.imread(Root_Directory.Path() + "/Data/Tile_Data/topography_filter_side_Bottom.jpg")[:, :, 0],
                                 'right':image.imread(Root_Directory.Path() + "/Data/Tile_Data/topography_filter_side_Right.jpg")[:, :, 0],
                                 'top':image.imread(Root_Directory.Path() + "/Data/Tile_Data/topography_filter_side_Top.jpg")[:, :, 0],
                                 'bottom_left':image.imread(Root_Directory.Path() + "/Data/Tile_Data/topography_filter_corner_Bottom_Left.jpg")[:, :, 0],
                                 'bottom_right':image.imread(Root_Directory.Path() + "/Data/Tile_Data/topography_filter_corner_Bottom_Right.jpg")[:, :, 0],
                                 'top_right':image.imread(Root_Directory.Path() + "/Data/Tile_Data/topography_filter_corner_Top_Right.jpg")[:, :, 0],
                                 'top_left':image.imread(Root_Directory.Path() + "/Data/Tile_Data/topography_filter_corner_Top_Left.jpg")[:, :, 0],
                                 'left_left':image.imread(Root_Directory.Path() + "/Data/Tile_Data/topography_filter_adjacent_side_Left.jpg")[:, :, 0],
                                 'bottom_bottom':image.imread(Root_Directory.Path() + "/Data/Tile_Data/topography_filter_adjacent_side_Bottom.jpg")[:, :, 0],
                                 'right_right':image.imread(Root_Directory.Path() + "/Data/Tile_Data/topography_filter_adjacent_side_Right.jpg")[:, :, 0],
                                 'top_top':image.imread(Root_Directory.Path() + "/Data/Tile_Data/topography_filter_adjacent_side_Top.jpg")[:, :, 0],
                                 'bottom_left_left':image.imread(Root_Directory.Path() + "/Data/Tile_Data/topography_filter_adjacent_corner_Bottom_Left_Left.jpg")[:, :, 0],
                                 'bottom_left_bottom':image.imread(Root_Directory.Path() + "/Data/Tile_Data/topography_filter_adjacent_corner_Bottom_Left_Bottom.jpg")[:, :, 0],
                                 'bottom_right_bottom':image.imread(Root_Directory.Path() + "/Data/Tile_Data/topography_filter_adjacent_corner_Bottom_Right_Bottom.jpg")[:, :, 0],
                                 'bottom_right_right':image.imread(Root_Directory.Path() + "/Data/Tile_Data/topography_filter_adjacent_corner_Bottom_Right_Right.jpg")[:, :, 0],
                                 'top_right_right':image.imread(Root_Directory.Path() + "/Data/Tile_Data/topography_filter_adjacent_corner_Top_Right_Right.jpg")[:, :, 0],
                                 'top_right_top':image.imread(Root_Directory.Path() + "/Data/Tile_Data/topography_filter_adjacent_corner_Top_Right_Top.jpg")[:, :, 0],
                                 'top_left_top':image.imread(Root_Directory.Path() + "/Data/Tile_Data/topography_filter_adjacent_corner_Top_Left_Top.jpg")[:, :, 0],
                                 'top_left_left':image.imread(Root_Directory.Path() + "/Data/Tile_Data/topography_filter_adjacent_corner_Top_Left_Left.jpg")[:, :, 0]}

        cls.textureFilters = {'center':image.imread(Root_Directory.Path() + "/Data/Tile_Data/tile_filter_center.jpg")[:, :, 0],
                                 'left':image.imread(Root_Directory.Path() + "/Data/Tile_Data/tile_filter_side_Left.jpg")[:, :, 0],
                                 'bottom':image.imread(Root_Directory.Path() + "/Data/Tile_Data/tile_filter_side_Bottom.jpg")[:, :, 0],
                                 'right':image.imread(Root_Directory.Path() + "/Data/Tile_Data/tile_filter_side_Right.jpg")[:, :, 0],
                                 'top':image.imread(Root_Directory.Path() + "/Data/Tile_Data/tile_filter_side_Top.jpg")[:, :, 0],
                                 'bottom_left':image.imread(Root_Directory.Path() + "/Data/Tile_Data/tile_filter_corner_Bottom_Left.jpg")[:, :, 0],
                                 'bottom_right':image.imread(Root_Directory.Path() + "/Data/Tile_Data/tile_filter_corner_Bottom_Right.jpg")[:, :, 0],
                                 'top_right':image.imread(Root_Directory.Path() + "/Data/Tile_Data/tile_filter_corner_Top_Right.jpg")[:, :, 0],
                                 'top_left':image.imread(Root_Directory.Path() + "/Data/Tile_Data/tile_filter_corner_Top_Left.jpg")[:, :, 0],
                                 'left_left':image.imread(Root_Directory.Path() + "/Data/Tile_Data/tile_filter_adjacent_side_Left.jpg")[:, :, 0],
                                 'bottom_bottom':image.imread(Root_Directory.Path() + "/Data/Tile_Data/tile_filter_adjacent_side_Bottom.jpg")[:, :, 0],
                                 'right_right':image.imread(Root_Directory.Path() + "/Data/Tile_Data/tile_filter_adjacent_side_Right.jpg")[:, :, 0],
                                 'top_top':image.imread(Root_Directory.Path() + "/Data/Tile_Data/tile_filter_adjacent_side_Top.jpg")[:, :, 0],
                                 'bottom_left_left':image.imread(Root_Directory.Path() + "/Data/Tile_Data/tile_filter_adjacent_corner_Bottom_Left_Left.jpg")[:, :, 0],
                                 'bottom_left_bottom':image.imread(Root_Directory.Path() + "/Data/Tile_Data/tile_filter_adjacent_corner_Bottom_Left_Bottom.jpg")[:, :, 0],
                                 'bottom_right_bottom':image.imread(Root_Directory.Path() + "/Data/Tile_Data/tile_filter_adjacent_corner_Bottom_Right_Bottom.jpg")[:, :, 0],
                                 'bottom_right_right':image.imread(Root_Directory.Path() + "/Data/Tile_Data/tile_filter_adjacent_corner_Bottom_Right_Right.jpg")[:, :, 0],
                                 'top_right_right':image.imread(Root_Directory.Path() + "/Data/Tile_Data/tile_filter_adjacent_corner_Top_Right_Right.jpg")[:, :, 0],
                                 'top_right_top':image.imread(Root_Directory.Path() + "/Data/Tile_Data/tile_filter_adjacent_corner_Top_Right_Top.jpg")[:, :, 0],
                                 'top_left_top':image.imread(Root_Directory.Path() + "/Data/Tile_Data/tile_filter_adjacent_corner_Top_Left_Top.jpg")[:, :, 0],
                                 'top_left_left':image.imread(Root_Directory.Path() + "/Data/Tile_Data/tile_filter_adjacent_corner_Top_Left_Left.jpg")[:, :, 0]}

        #cls.terrainTextures = {'grass':imageGrass,
        #                       'desert':imageDesert,
        #                       'tundra':imageTundra,
        #                       'grasscliff':imageGrassCliff,
        #                       'desertcliff':imageDesertCliff,
        #                       'tundracliff':imageTundraCliff}
        #"panda3d-master/samples/chessboard/models/grass_4_symmetrical.jpg"

        #cls.terrainTextures = {'grass':image.imread("panda3d-master/samples/chessboard/models/white.jpg"),
        #                       'desert':image.imread("panda3d-master/samples/chessboard/models/white.jpg"),
        #                       'tundra':image.imread("panda3d-master/samples/chessboard/models/white.jpg"),
        #                       'grasscliff':image.imread("panda3d-master/samples/chessboard/models/white.jpg"),
        #                       'desertcliff':image.imread("panda3d-master/samples/chessboard/models/white.jpg"),
        #                       'tundracliff':image.imread("panda3d-master/samples/chessboard/models/white.jpg")}
        cls.terrainTextures = {'grass':image.imread(Root_Directory.Path() + "/Data/Tile_Data/grass_5.jpg"),
                               'desert':image.imread(Root_Directory.Path() + "/Data/Tile_Data/desert_1.jpg"),
                               'tundra':image.imread(Root_Directory.Path() + "/Data/Tile_Data/tundra_1.jpg"),
                               'grasscliff':image.imread(Root_Directory.Path() + "/Data/Tile_Data/grass_cliff_5.jpg"),
                               'desertcliff':image.imread(Root_Directory.Path() + "/Data/Tile_Data/desert_rock_2.jpg"),
                               'tundracliff':image.imread(Root_Directory.Path() + "/Data/Tile_Data/tundra_cliff_2.jpg"),
                               'soil_fertility_0':image.imread(Root_Directory.Path() + "/Data/Tile_Data/soil_fertility_0.png"),
                               'soil_fertility_1':image.imread(Root_Directory.Path() + "/Data/Tile_Data/soil_fertility_1.png"),
                               'soil_fertility_2':image.imread(Root_Directory.Path() + "/Data/Tile_Data/soil_fertility_2.png"),
                               'soil_fertility_3':image.imread(Root_Directory.Path() + "/Data/Tile_Data/soil_fertility_3.png"),
                               'rock':image.imread(Root_Directory.Path() + "/Data/Tile_Data/rock_terrain.png"),
                               'water':image.imread(Root_Directory.Path() + "/Data/Tile_Data/water.png"),
                               'deep_water_terrain':image.imread(Root_Directory.Path() + "/Data/Tile_Data/deep_water_terrain.png"),
                               'shallow_water_terrain':image.imread(Root_Directory.Path() + "/Data/Tile_Data/shallow_water_terrain.png")}

        #cls.terrainTextures = {'grass':image.imread("panda3d-master/samples/chessboard/models/grass_4_symmetrical.jpg"),
        #                       'desert':image.imread("panda3d-master/samples/chessboard/models/desert_1_symmetrical.jpg"),
        #                       'tundra':image.imread("panda3d-master/samples/chessboard/models/tundra_1_symmetrical.jpg"),
        #                       'grasscliff':image.imread("panda3d-master/samples/chessboard/models/grass_cliff_5_symmetrical.jpg"),
        #                       'desertcliff':image.imread("panda3d-master/samples/chessboard/models/desert_rock_2_symmetrical.jpg"),
        #                       'tundracliff':image.imread("panda3d-master/samples/chessboard/models/tundra_cliff_1_symmetrical.jpg")}

    @classmethod
    def CoordinateToIndex(cls, row, colon):
        return int(colon) + int(row) * cls.N_COLONS

    @classmethod
    def IndexToCoordinate(cls, index):
        colon = int(index%cls.N_COLONS)
        row = int((index-colon)/cls.N_COLONS)
        return row, colon

    @classmethod
    def SaveDictionariesToFile(cls):
        pickle.dump(cls.topographyDictionary, open('topography_dictionary.pkl', 'wb'), pickle.HIGHEST_PROTOCOL)
        pickle.dump(cls.textureDictionary, open('texture_dictionary.pkl', 'wb'), pickle.HIGHEST_PROTOCOL)

class FeatureClass(Entity):
    #
    # Features are that which exist on top of tiles.
    #
    def __init__(self,
                 parentTile,
                 type,
                 hprValue = None,
                 numberOfcomponents = 1,
                 distributionType = 'random',
                 distributionValue = 2,
                 gridAlignedHPR = False):
        '''

        :param parentTile:
        :param type:
        :param hprValue:
        :param numberOfcomponents: The number of visual objects, for example the number of trees in a forest.
        :param distributionType: 'random', 'spread' or 'grid'.
                                  'Spread' will spread out the objects, the distance between objects is
                                  used as weights. The distributionValue determines how heavily this weight should be
                                  considered. For a value of 1 the objects should be evenly placed, for a value of 0
                                  they should be randomly placed.
                                  'grid' will place the objects on a grid. The grid is aligned along a random vector,
                                  this vector is unique for each tile. The distributionValue will determine the
                                  dimensions of the grid.
        :param distributionValue: A value used for placing the node, has different uses depending on the
                                  distributionType value.
        :param gridAlignedHPR: Wether or not the nodes should be aligned in the grid.
        '''
        super().__init__(parentTile.row, parentTile.colon, parentTile.elevation)
        self.tile = parentTile
        self.type = type
        self.hprValue = hprValue
        self.numberOfComponents = numberOfcomponents
        self.distributionType = distributionType
        self.distributionValue = distributionValue
        self.gridAlignedHPR = gridAlignedHPR

        self.template = self.featureTemplates[self.type]

        self.positionValues = None
        self.hprValues = None
        self.scaleValues = []
        self.templateIndices = []


        self.CreateComponentData()
        self.CreateNodes()

    def CreateComponentData(self):
        '''
        Creates all the data needed to place the nodes; position, scale, model types.
        :return:
        '''
        if self.distributionType == 'spread':
            positioningWeights = np.ones([self.pandaProgram.MODEL_RESOLUTION, self.pandaProgram.MODEL_RESOLUTION])
            self.positionValues = np.zeros((self.numberOfComponents, 2), dtype=int)
            for iComponent in range(self.numberOfComponents):
                totalWeight = 0
                for row in range(self.pandaProgram.MODEL_RESOLUTION):
                    for colon in range(self.pandaProgram.MODEL_RESOLUTION):
                        totalWeight += positioningWeights[row, colon]
                r = np.random.rand()
                a = 0
                accumulativeWeights = 0
                for row in range(self.pandaProgram.MODEL_RESOLUTION):
                    for colon in range(self.pandaProgram.MODEL_RESOLUTION):
                        accumulativeWeights += positioningWeights[row, colon] / totalWeight
                        if r < accumulativeWeights:

                            if a == 0:
                                self.positionValues[iComponent, :] = [colon, row]
                                a = 1
                            # break

                for row in range(self.pandaProgram.settings.MODEL_RESOLUTION):
                    for colon in range(self.pandaProgram.settings.MODEL_RESOLUTION):
                        positioningWeights[row, colon] += np.sqrt(
                            (self.positionValues[iComponent, 0] - colon) ** 2 + (
                                        self.positionValues[iComponent, 1] - row) ** 2) ** self.distributionValue

        elif self.distributionType == 'random':
            self.positionValues = np.random.randint(0, self.pandaProgram.settings.MODEL_RESOLUTION, [self.numberOfComponents, 2])
        elif self.distributionType == 'grid':
            gridVectors = None
            self.positionValues = np.zeros((self.numberOfComponents, 2), dtype=int)
            if gridVectors == None:
                angle = 2 * np.pi * np.random.rand()
                # angle = np.pi/2
                if self.gridAlignedHPR: self.hprValue = [-angle * 180 / np.pi, 90, 0]
                gridVectors = [[np.cos(angle), np.sin(angle)], [-np.sin(angle), np.cos(angle)]]

                v1 = gridVectors[0] / np.sqrt(2)
                v2 = gridVectors[1] / np.sqrt(2)

            t1Range = np.linspace(-1, 1, self.distributionValue)
            t2Range = np.linspace(-1, 1, self.distributionValue)

            gridPoints = []
            for t1 in t1Range:
                for t2 in t2Range:
                    px = int(np.floor(self.pandaProgram.settings.MODEL_RESOLUTION * (0.5 + v1[0] * t1 + v2[0] * t2)))
                    py = int(np.floor(self.pandaProgram.settings.MODEL_RESOLUTION * (0.5 + v1[1] * t1 + v2[1] * t2)))

                    if 0 <= px and px < self.pandaProgram.settings.MODEL_RESOLUTION and \
                            0 <= py and py < self.pandaProgram.settings.MODEL_RESOLUTION:
                        gridPoints.append([px, py])

            if len(gridPoints) > self.numberOfComponents:
                choosenPoints = np.random.choice(len(gridPoints), self.numberOfComponents, replace=False)
                for i in range(self.numberOfComponents):
                    self.positionValues[i, 0] = gridPoints[choosenPoints[i]][0]
                    self.positionValues[i, 1] = gridPoints[choosenPoints[i]][1]
            else:
                self.numberOfComponents = len(gridPoints)
                for i in range(self.numberOfComponents):
                    self.positionValues[i, 0] = gridPoints[i][0]
                    self.positionValues[i, 1] = gridPoints[i][1]

        # Access template data
        for i in range(self.numberOfComponents):
            r0 = np.random.rand()
            r1 = np.random.rand()
            weigthsSummed = 0
            for iModel, weight in enumerate(self.template.weights):
                weigthsSummed += weight
                if r0 < weigthsSummed:
                    self.templateIndices.append(iModel)
                    scaleRange = self.template.scaleRange[iModel]
                    self.scaleValues.append(scaleRange[0] + r1*(scaleRange[1]-scaleRange[0]))
                    break

    def CreateNodes(self):
        '''
        Creates the nodes of the feature. The nodes are flattened using flattenStrong() to improve performance.
        :return:
        '''
        self.node = self.pandaProgram.featureRoot.attachNewNode('featureNode')
        nodes = [self.node.attachNewNode('single_feature') for i in range(self.numberOfComponents)]
        for iNode, node in enumerate(nodes):

            self.template.models[self.templateIndices[iNode]].copyTo(node)

            node.setPos(p3d.LPoint3(self.colon + self.positionValues[iNode, 0] / self.pandaProgram.settings.MODEL_RESOLUTION,
                                    self.row + 1 - self.positionValues[iNode, 1] / self.pandaProgram.settings.MODEL_RESOLUTION,
                                    self.pandaProgram.settings.ELEVATION_SCALE * self.tile.topography[
                                        self.positionValues[iNode, 1], self.positionValues[iNode, 0]]))

            if self.hprValue is None:
                node.set_hpr(360*np.random.rand(), 90, 0)
            else:
                node.set_hpr(self.hprValue[0] + 90*np.random.randint(0, 4), self.hprValue[1], self.hprValue[2])

            node.setScale(self.scaleValues[iNode], self.scaleValues[iNode], self.scaleValues[iNode])

            node.setTransparency(p3d.TransparencyAttrib.MAlpha)
            node.clearModelNodes()
        self.node.flattenStrong()

        if self.colon < self.pandaProgram.settings.HORIZONTAL_WRAP_BUFFER:
            self.Wrap('right')
        if self.colon > (self.pandaProgram.settings.N_COLONS - self.pandaProgram.settings.HORIZONTAL_WRAP_BUFFER):
            self.Wrap('left')

    def Wrap(self, direction):
        self.wrapperNode = self.pandaProgram.featureRoot.attachNewNode('wrapperNode')
        self.node.copyTo(self.wrapperNode)

        if direction == 'left':
            self.wrapperNode.setPos(self.wrapperNode, (-self.pandaProgram.settings.N_COLONS, 0, 0))
        if direction == 'right':
            self.wrapperNode.setPos(self.wrapperNode, (self.pandaProgram.settings.N_COLONS, 0, 0))

    @classmethod
    def Initialize(cls, featureTemplates, pandaProgram):
        cls.featureTemplates = featureTemplates
        cls.pandaProgram = pandaProgram

    @classmethod
    def ConstructionMenuFunction(cls, value):
        print('construct builing')
        print(value)
        print()
        tileID = cls.pandaProgram.selected_tile_ID
        tile = cls.pandaProgram.tileList[tileID]
        if value == 0:
            tile.features.append(FeatureClass(parentTile=tile,
                                                                        type='farm',
                                                                        numberOfcomponents=1,
                                                                        distributionType='random'))
        elif value == 1:
            tile.features.append(FeatureClass(parentTile=tile,
                                                                        type='town',
                                                                        numberOfcomponents=20,
                                                                        distributionType='grid',
                                                                        distributionValue=7,
                                                                        gridAlignedHPR=True
                                                                        ))
        elif value == 2:
            tile.features.append(FeatureClass(parentTile=tile,
                                                                        type='jungle',
                                                                        numberOfcomponents=20))
        elif value == 3:
            tile.features.append(FeatureClass(parentTile=tile,
                                                                        type='conifer_forest',
                                                                        numberOfcomponents=20))
        else:
            tile.features.append(FeatureClass(parentTile=tile,
                                                                        type='temperate_forest',
                                                                        numberOfcomponents=20))

    @classmethod
    def RemoveFeatureFunction(cls):
        tile = cls.pandaProgram.tileList[cls.pandaProgram.selected_tile_ID]
        for feature in tile.features:
            feature.node.detachNode()

class NaturalFeature(FeatureClass):
    #
    # Natural features include forest, shrubland and resources
    #
    def __init__(self, row, colon, elevation):
        super().__init__(row, colon, elevation)

class ConstructedFeature(FeatureClass):
    #
    # Buildings, improvements and cities.
    #
    def __init__(self, row, colon, elevation):
        super().__init__(row, colon, elevation)


class ForestFeature(NaturalFeature):
    def __init__(self):
        super().__init__()
        pass

from direct.task.Task import Task
class UnitClass(Entity):
    IDCounter = 0
    def __init__(self, row, colon, elevation, type, ID):
        super().__init__(row, colon, elevation)

        self.ID = ID
        self.CreateNode(type)

        self.movementAnimationIndex = None
        self.movementAnimationLength = None
        self.movementAnimationPath = None

        self.isSelected = False
        self.isMoving = False

    def CreateNode(self, type):
        if type == 'unit_test':
            self.node = loader.loadModel(Root_Directory.Path(style = 'unix') + "/Data/Models/unit_test_textured_8.dae")
            self.node.set_hpr(0, 90, 0)
            self.node.setScale(0.3, 0.25, 0.3)
        self.node.setPos(p3d.LPoint3(self.colon + 0.5, self.row + 0.5, self.ELEVATION_SCALE * self.elevation))
        self.node.reparentTo(self.unitRoot)
        self.node.setTag('type', 'unit')
        self.node.setTag('ID', str(self.ID))

    def Destroy(self):
        '''
        Destroys the unit and all references to it.
        :return:
        '''

        self.tileList[TileClass.CoordinateToIndex(self.row, self.colon)].unit = None
        self.node.removeNode()
        del self.unitDictionary[self.ID]

        self.ChessBoardDemo.selected_tile_ID = None
        self.ChessBoardDemo.selected_unit_ID = None
        self.ChessBoardDemo.unitMarker.detachNode()

        self.ChessBoardDemo.GUIObject.unitFrame.frame.hide()

        self.ChessBoardDemo.LeftMouseButtonFunction = self.StandardClicker

    def SimpleMove(self, row, colon, elevation):
        '''
        This is a simple move functions which only works for movements between tiles. Arbitraru row/colon values are not supported.
        :param row:
        :param colon:
        :param elevation:
        :return:
        '''

        self.tileList[TileClass.CoordinateToIndex(self.row, self.colon)].unit = None

        self.row = row
        self.colon = colon
        self.elevation = elevation

        self.ChessBoardDemo.unitMarker.setPos(self.colon + 0.5, self.row + 0.5,self.ELEVATION_SCALE * (self.elevation + 0.1))
        self.node.setPos(self.colon + 0.5, self.row + 0.5,self.ELEVATION_SCALE * (self.elevation + 0.1))

        self.tileList[TileClass.CoordinateToIndex(self.row, self.colon)].unit = self
        print('Unit should move')

    @classmethod
    def MoveUnitButtonFunction(cls, value):
        if value == 1:
            cls.ChessBoardDemo.LeftMouseButtonFunction = cls.MoveUnitClicker

        else:
            cls.ChessBoardDemo.LeftMouseButtonFunction = cls.StandardClicker

    @classmethod
    def MoveUnitClicker(cls):
        tileID, unitID = cls.ChessBoardDemo.StandardPicker()
        if tileID:
            tileToMoveTo = cls.tileList[tileID]
            unit = cls.unitDictionary[cls.ChessBoardDemo.selected_unit_ID]
            if tileToMoveTo.unit == None and unit.isMoving == False:
                path = Pathfinding.AStar(TileClass.CoordinateToIndex(unit.row, unit.colon), tileID, cls.ChessBoardDemo.movementGraph)
                #path = Pathfinding.SimplePathfinding(TileClass.CoordinateToIndex(unit.row, unit.colon), tileID,cls.ChessBoardDemo.movementGraph)

                coordinatePath = []
                pathLength = []
                print(path)
                print('--------')
                for i, iTile in enumerate(path):
                    tile = cls.tileList[iTile]
                    coordinatePath.append([tile.row, tile.colon, tile.elevation])
                    if i>0:
                        pathLength.append(30) #                        THIS IS HARDCODED, SHOULD BE DEFINED AS A MACRO

                cls.tileList[TileClass.CoordinateToIndex(unit.row, unit.colon)].unit = None
                tileToMoveTo.unit = unit
                unit.isMoving = True

                Animation.UnitAnimationClass(unit, coordinatePath, pathLength)
            else:
                if tileToMoveTo.unit != None:
                    print('A unit already occupy this tile')
                elif unit.isMoving == True:
                    print('Unit is already moving')

    @classmethod
    def PlaceUnitClicker(cls):
        '''

        :param task:
        :return:
        '''
        tileID, unitID = cls.ChessBoardDemo.StandardPicker()
        if tileID:
            tile = cls.tileList[tileID]
            if tile.unit == None:
                print('A unit was added.')
                cls.CreateUnit(row=tile.row, colon=tile.colon, elevation=tile.elevation, type='unit_test')
            else:
                print('A unit already exist here.')

    @classmethod
    def Initialize(cls, unitRoot, ELEVATION_SCALE, unitDictionary, tileList, standardClicker, ChessboardDemo):
        cls.unitRoot = unitRoot
        cls.ELEVATION_SCALE = ELEVATION_SCALE
        cls.unitDictionary = unitDictionary
        cls.tileList = tileList

        cls.StandardClicker = standardClicker

        cls.ChessBoardDemo = ChessboardDemo

    @classmethod
    def CreateUnit(cls, row, colon, elevation, type):
        ID = cls.IDCounter
        cls.IDCounter += 1
        cls.unitDictionary[ID] = UnitClass(row, colon, elevation, type, ID)
        iTile = TileClass.CoordinateToIndex(row, colon)
        cls.tileList[iTile].unit = cls.unitDictionary[ID]

    @classmethod
    def AddUnitButtonFunction(cls, value):
        '''
        The method changes which method should be used for picking. The cls.PlaceUnitPicker method puts a unit on the
        clicked tile.
        :param value:
        :return:
        '''
        print(value)
        if value == 1:
            cls.ChessBoardDemo.LeftMouseButtonFunction = cls.PlaceUnitClicker
        else:
            cls.ChessBoardDemo.LeftMouseButtonFunction = cls.StandardClicker



