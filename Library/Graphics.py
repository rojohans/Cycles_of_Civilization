import panda3d.core as p3d
import numpy as np


class WorldMesh():
    def __init__(self, mainProgram, vertices, faces, faceNormals):
        self.mainProgram = mainProgram
        self.vertices = vertices
        self.faces = faces
        self.faceNormals = faceNormals

        # Wether the object's textures are up-to-date.
        self.textureUpdatedStatus = False

        # getV3n3c4t2() : vertices3, normals3, colours4, textureCoordinates2
        # v3n3t2 : vertices3, normals3, textureCoordinates2
        #vertex_format = p3d.GeomVertexFormat.get_v3n3t2()
        vertex_format = p3d.GeomVertexFormat.getV3n3c4t2()

        # vertex_format = p3d.GeomVertexFormat.get_v3t2()
        self.vertexData = p3d.GeomVertexData("triangle_data", vertex_format, p3d.Geom.UH_static)

        pos_writer = p3d.GeomVertexWriter(self.vertexData, "vertex")
        normal_writer = p3d.GeomVertexWriter(self.vertexData, "normal")
        colour_writer = p3d.GeomVertexWriter(self.vertexData, 'color')
        tex_writer = p3d.GeomVertexWriter(self.vertexData, 'texcoord')

        for iFace in range(np.size(self.faces, 0)):
            vertices = self.vertices[self.faces[iFace, 1:]]
            pos_writer.add_data3(vertices[0, 0], vertices[0, 1], vertices[0, 2])
            pos_writer.add_data3(vertices[1, 0], vertices[1, 1], vertices[1, 2])
            pos_writer.add_data3(vertices[2, 0], vertices[2, 1], vertices[2, 2])

            colour_writer.add_data4(1, 1, 1, 1)
            colour_writer.add_data4(1, 1, 1, 1)
            colour_writer.add_data4(1, 1, 1, 1)

            #vertices /= np.sqrt(vertices[0]**2 + vertices[1]**2 + vertices[2]**2)
            normal = self.faceNormals[iFace, :]
            normal /= np.sqrt(normal[0]**2 + normal[1]**2 + normal[2]**2)


            vertices = np.sum(vertices, axis=0) / 3
            vertices /= np.sqrt(vertices[0] ** 2 + vertices[1] ** 2 + vertices[2] ** 2)

            textureKey = self.DetermineTextureKey(iFace)

            rIndices = self.mainProgram.closeTexture.textureIndices[textureKey]
            tex_writer.addData2f(rIndices[0], 0)
            tex_writer.addData2f(rIndices[1], 0)
            tex_writer.addData2f((rIndices[0] + rIndices[1])/2, np.sqrt(3)/2)

        tri = p3d.GeomTriangles(p3d.Geom.UH_static)

        # Creates the triangles.
        n = 0
        for iFace in range(np.size(self.faces, 0)):
            tri.add_vertices(n, n+1, n+2)
            n += 3

        # Assigns a normal to each vertex.
        for iFace in range(np.size(self.faces, 0)):

            normal = self.faceNormals[iFace, :]
            normal_writer.add_data3(p3d.Vec3(normal[0], normal[1], normal[2]))
            normal_writer.add_data3(p3d.Vec3(normal[0], normal[1], normal[2]))
            normal_writer.add_data3(p3d.Vec3(normal[0], normal[1], normal[2]))

        geom = p3d.Geom(self.vertexData)
        geom.add_primitive(tri)

        node = p3d.GeomNode("Planet")
        node.add_geom(geom)
        self.node = p3d.NodePath(node)

        self.node.reparentTo(render)
        self.node.setTexture(self.mainProgram.closeTexture.stitchedTexture)
        self.node.setTransparency(p3d.TransparencyAttrib.MAlpha)

    def DetermineTextureKey(self, i):
        if len(self.mainProgram.featureList[i]) > 0:
            textureKey = self.mainProgram.featureList[i][0].template.textureKey
        else:
            textureKey = None

        if textureKey == None:
            if self.mainProgram.worldProperties.slope[i] > 30:
                if self.mainProgram.worldProperties.temperature[i, 0] < 0.1:
                    textureKey = 'snow'
                else:
                    textureKey = 'rock'
            else:
                if self.mainProgram.worldProperties.temperature[i, 0] < 0.3:
                    textureKey = 'snow'
                elif self.mainProgram.worldProperties.temperature[i, 0] < 0.4:
                    textureKey = 'tundra'
                else:
                    textureKey = 'grass'
        return textureKey

class LineSegments():
    def __init__(self, coordinates, lineIndices):
        pass

    @staticmethod
    def LineSegments(coordinates, lineIndices, coordinateMultiplier = 1.0):
        vertex_format = p3d.GeomVertexFormat.getV3c4()
        vertexData = p3d.GeomVertexData("line_data", vertex_format, p3d.Geom.UH_static)
        pos_writer = p3d.GeomVertexWriter(vertexData, "vertex")
        colour_writer = p3d.GeomVertexWriter(vertexData, 'color')

        for coordinate in coordinates:
            pos_writer.add_data3(coordinateMultiplier*coordinate[0],
                                 coordinateMultiplier*coordinate[1],
                                 coordinateMultiplier*coordinate[2])
            colour_writer.add_data4(1, 0, 0, 1)

        ln = p3d.GeomLines(p3d.Geom.UH_static)

        for line in lineIndices:
            ln.add_vertices(line[0], line[1])


        geom = p3d.Geom(vertexData)
        geom.add_primitive(ln)

        tmpNode = p3d.GeomNode("link")
        tmpNode.add_geom(geom)
        node = p3d.NodePath(tmpNode)

        node.setRenderModeThickness(10)
        node.reparentTo(render)
        return node

    @staticmethod
    def IndicesToCoordinates(indices, mainProgram):
        coordinates = []
        for index in indices:
            coordinates.append(mainProgram.world.faceCoordinates[index, :])
        return coordinates

