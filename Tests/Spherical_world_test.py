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
        base.setBackgroundColor(1, 1, 1)

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
            r = 'rock'
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

        node = p3d.GeomNode("Planet")
        node.add_geom(geom)
        self.planet = p3d.NodePath(node)

        self.planet.reparentTo(render)
        self.planet.setTexture(texture.stitchedTexture)
        #self.planet.setTag('iFace', 'THE PLANET')

        # Since we are using collision detection to do picking, we set it up like
        # any other collision detection system with a traverser and a handler
        self.picker = p3d.CollisionTraverser()  # Make a traverser
        self.pq = p3d.CollisionHandlerQueue()  # Make a handler
        # Make a collision node for our picker ray
        self.pickerNode = p3d.CollisionNode('mouseRay')
        # Attach that node to the camera since the ray will need to be positioned
        # relative to it
        self.pickerNP = camera.attachNewNode(self.pickerNode)
        # Everything to be picked will use bit 1. This way if we were doing other
        # collision we could separate it
        self.pickerNode.setFromCollideMask(p3d.GeomNode.getDefaultCollideMask())
        self.pickerRay = p3d.CollisionRay()  # Make our ray
        # Add it to the collision node
        self.pickerNode.addSolid(self.pickerRay)
        # Register the ray as something that can cause collisions
        self.picker.addCollider(self.pickerNP, self.pq)



        base.cTrav = p3d.CollisionTraverser()
        collisionHandler = p3d.CollisionHandlerQueue()

        # ** This is where we define the heart collider that will trig the collision event against the smiley ball, therefore it is who'll stir up the event, named FROM object. The major difference from this object and the other, called INTO object. is that we'll going to put it in the main traverser list, making it automatically figure as a FROM object just because of this. Any other object in the scene instead, is automatically considered as INTO by the system - the FROM either.

        #smileyCollider = self.planet.attachNewNode(p3d.CollisionNode('smileycnode'))
        #smileyCollider.node().addSolid(p3d.CollisionSphere(0, 0, 0, 70))
        #self.planet.reparentTo(render)
        #smileyCollider.show()

        self.collidableRoot = render.attachNewNode('collidableRoot')
        collisionNodes = []
        for iFace in range(np.size(world.f, 0)):
            vertices = world.v[world.f[iFace, 1:]]

            collisionNodes.append(self.collidableRoot.attachNewNode(p3d.CollisionNode('cnode')))
            #collisionNodes.append(self.planet.attachNewNode(p3d.CollisionNode('cnode')))
            collisionNodes[-1].node().addSolid(p3d.CollisionPolygon(p3d.Point3(vertices[0, 0], vertices[0, 1], vertices[0, 2]),
                                                                    p3d.Point3(vertices[1, 0], vertices[1, 1], vertices[1, 2]),
                                                                    p3d.Point3(vertices[2, 0], vertices[2, 1], vertices[2, 2])))
            collisionNodes[-1].node().setIntoCollideMask(p3d.GeomNode.getDefaultCollideMask())
            collisionNodes[-1].node().setTag('iFace', str(iFace))
            #collisionNodes[-1].node().setTag('iFace', 'test_text_here')
            #collisionNodes[-1].show()

        # ** This is the frowney model that will intereact with the smiley - it is shaped and settled exactly as smiley so there isn't much to say here, other than this time we won't add this object to the main traverser. This makes him an INTO object.
        # first we load the model as usual...
        self.pickerNode = p3d.CollisionNode('mouseRay')
        # Attach that node to the camera since the ray will need to be positioned
        # relative to it
        self.pickerNP = camera.attachNewNode(self.pickerNode)
        # Everything to be picked will use bit 1. This way if we were doing other
        # collision we could separate it
        self.pickerNode.setFromCollideMask(p3d.GeomNode.getDefaultCollideMask())
        self.pickerRay = p3d.CollisionRay()  # Make our ray
        # Add it to the collision node
        self.pickerNode.addSolid(self.pickerRay)
        # Register the ray as something that can cause collisions
        base.cTrav.addCollider(self.pickerNP, collisionHandler)




        # ** This is the loop periodically checked to find out if the have been collisions - it is fired by the taskMgr.add function set below.
        def traverseTask(task=None):
            # as soon as a collison is detected, the collision queue handler will contain all the objects taking part in the collison, but we must sort that list first, so to have the first INTO object collided then the second and so on. Of course here it is pretty useless 'cos there is just one INTO object to collide with in the scene but this is the way to go when there are many other.
            collisionHandler.sortEntries()
            for i in range(collisionHandler.getNumEntries()):
                # we get here the n-th object collided (we know it is frowney for sure) - it is a CollisionEntry object (look into the manual to see its methods)
                entry = collisionHandler.getEntry(i)
                # we'll turn on the lights, to visually show this happy event
                #print('HIT DETECTION')
                a = entry.getIntoNodePath()

                if a.node().hasTags():
                    print(a.getNetTag('iFace'))
                    # and we skip out cos we ain't other things to do here.
                    if task: return task.cont

            # If there are no collisions the collision queue will be empty so the program flow arrives here and we'll shut down the lights and clear the text message

            if task: return task.cont

        # ** let start the collision check loop
        taskMgr.add(traverseTask, "tsk_traverse")




        self.add_task(self.PickTask, 'picking')

    def PickTask(self, Task):
        #print('picking')
        if self.mouseWatcherNode.hasMouse():
            # get the mouse position
            mpos = self.mouseWatcherNode.getMouse()

            # Set the position of the ray based on the mouse position
            self.pickerRay.setFromLens(self.camNode, mpos.getX(), mpos.getY())

            #self.picker.traverse(self.collidableRoot)
            self.picker.traverse(render)
            #print(self.pq.getNumEntries())
            if self.pq.getNumEntries() > 0:
                # if we have hit something, sort the hits so that the closest
                # is first, and highlight that node
                self.pq.sortEntries()
                pickedObj = self.pq.getEntry(0).getIntoNodePath()

                #print('hit')

                for entry in self.pq.get_entries():
                    print(entry.getIntoNodePath())
                    #print(entry.getIntoNodePath().getNetTag('iFace'))

                    print(entry.getIntoNodePath().getTag('iFace'))
                    print(entry.getIntoNodePath().node().hasTags())

                #print('   ')

                #if int(pickedObj.getNetTag('iFace')) == 'tile':
                #    tileID = int(pickedObj.getNetTag('square'))
        return Task.cont

game = Game()
game.run()

