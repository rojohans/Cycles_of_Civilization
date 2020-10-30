from direct.showbase.ShowBase import ShowBase
import panda3d.core as p3d
import numpy as np
import time

import Library.TileClass as TileClass
import Library.Light as Light
import Library.Camera as Camera
import Library.World as World
import Library.Pathfinding as Pathfinding
import Library.Animation as Animation
import Library.Ecosystem as Ecosystem
import Library.Texture as Texture

import Data.Dictionaries.FeatureTemplateDictionary as FeatureTemplateDictionary
import Data.Templates.Vegetation_Templates as Vegetation_Templates
import Data.Templates.Animal_Templates as Animal_Templates

import Settings
import Root_Directory

class Game(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        p3d.PStatClient.connect()

        base.setFrameRateMeter(True)

        texture = Texture.Texture()
        self.lightObject = Light.LightClass(shadowsEnabled=False)
        world = World.SphericalWorld()

        # v3n3t2 : vertices3, normals3, textureCoordinates2
        vertex_format = p3d.GeomVertexFormat.get_v3n3t2()
        # vertex_format = p3d.GeomVertexFormat.get_v3t2()
        vertex_data = p3d.GeomVertexData("triangle_data", vertex_format, p3d.Geom.UH_static)

        pos_writer = p3d.GeomVertexWriter(vertex_data, "vertex")
        normal_writer = p3d.GeomVertexWriter(vertex_data, "normal")
        tex_writer = p3d.GeomVertexWriter(vertex_data, 'texcoord')

        for iFace in range(np.size(world.f, 0)):
            vertices = world.v[world.f[iFace, 1:]]
            pos_writer.add_data3(vertices[0, 0], vertices[0, 1], vertices[0, 2])
            pos_writer.add_data3(vertices[1, 0], vertices[1, 1], vertices[1, 2])
            pos_writer.add_data3(vertices[2, 0], vertices[2, 1], vertices[2, 2])

            r = np.random.choice(['water', 'grass', 'rock', 'snow'])
            rIndices = texture.textureIndices[r]
            tex_writer.addData2f(rIndices[0], 0)
            tex_writer.addData2f(rIndices[1], 0)
            tex_writer.addData2f((rIndices[0] + rIndices[1])/2, np.sqrt(3)/2)

        tri = p3d.GeomTriangles(p3d.Geom.UH_static)

        # Creates the triangles.
        n = 0
        for iFace in range(np.size(world.f, 0)):
            #tri.add_vertices(world.f[iFace, 0], world.f[iFace, 1], world.f[iFace, 2])
            tri.add_vertices(n, n+1, n+2)
            n += 3

        # Assigns a normal to each vertex.
        for iFace in range(np.size(world.f, 0)):
            #normal_writer.add_data3(p3d.Vec3(self.normals[y, x, 0], self.normals[y, x, 1], self.normals[y, x, 2]))

            vertices = world.v[world.f[iFace, 1:]]
            v0 = vertices[1, :] - vertices[0, :]
            v1 = vertices[2, :] - vertices[0, :]
            normal = [v0[1]*v1[2] - v1[1]*v0[2], v0[0]*v1[2] - v1[0]*v0[2], v0[0]*v1[1] - v1[0]*v0[1]]

            #normal_writer.add_data3(p3d.Vec3(0, 0, 1))
            #normal_writer.add_data3(p3d.Vec3(0, 0, 1))
            #normal_writer.add_data3(p3d.Vec3(0, 0, 1))
            normal_writer.add_data3(p3d.Vec3(normal[0], normal[1], normal[2]))
            normal_writer.add_data3(p3d.Vec3(normal[0], normal[1], normal[2]))
            normal_writer.add_data3(p3d.Vec3(normal[0], normal[1], normal[2]))

        geom = p3d.Geom(vertex_data)
        geom.add_primitive(tri)

        node = p3d.GeomNode("Tile")
        node.add_geom(geom)
        tile = p3d.NodePath(node)

        tile.reparentTo(render)

        base.setBackgroundColor(1, 1, 1)
        tile.setTexture(texture.stitchedTexture)


game = Game()
game.run()

