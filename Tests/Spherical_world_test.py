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
import pickle

import Settings
import Root_Directory

class Game(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        p3d.PStatClient.connect()
        base.setFrameRateMeter(True)
        base.setBackgroundColor(0.1, 0.1, 0.15)

        texture = Texture.Texture()
        self.lightObject = Light.LightClass(shadowsEnabled=False)
        if False:
            world = World.SphericalWorld()
        else:
            world = pickle.load(open(Root_Directory.Path() + '/Data/tmp_Data/worldRock.pkl', "rb"))
            '''
            world.v[:, 0] /= world.vertexRadius
            world.v[:, 1] /= world.vertexRadius
            world.v[:, 2] /= world.vertexRadius
            world.vertexRadius = world.Smooth(world.v, world.f, world.vertexRadius, world.faceRadius)
            world.v[:, 0] *= world.vertexRadius
            world.v[:, 1] *= world.vertexRadius
            world.v[:, 2] *= world.vertexRadius
            '''
            world.minRadius = np.min(world.faceRadius)
        self.camera = Camera.GlobeCamera(mainProgram=self, zoomRange = [1.1*world.minRadius, 5*world.minRadius], minRadius = world.minRadius, rotationSpeedRange=[np.pi/500, np.pi/80])
        print(self.camera.focalPoint.getPos())
        print(self.camera.camera.getPos())

        print('# faces : ', np.size(world.f, 0))

        world.faceNormals = world.CalculateFaceNormals(world.v, world.f)
        world.faceTemperature = world.CalculateFaceTemperature(world.v, world.f, world.faceRadius)


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

            #vertices /= np.sqrt(vertices[0]**2 + vertices[1]**2 + vertices[2]**2)
            normal = world.faceNormals[iFace, :]
            normal /= np.sqrt(normal[0]**2 + normal[1]**2 + normal[2]**2)



            vertices = np.sum(vertices, axis=0) / 3
            vertices /= np.sqrt(vertices[0] ** 2 + vertices[1] ** 2 + vertices[2] ** 2)

            #print(normal)
            #print(vertices)

            #print(np.sqrt(vertices[0]**2 + vertices[1]**2 + vertices[2]**2))
            #print(np.sqrt(normal[0]**2 + normal[1]**2 + normal[2]**2))
            #print('  ')

            angle = 180/np.pi*np.arccos( (vertices[0]*normal[0] + vertices[1]*normal[1] + vertices[2]*normal[2]))
            #print(angle)
            temperature = world.faceTemperature[iFace, 0]

            if angle >30:
                if temperature < 0.1:
                    r = 'snow'
                else:
                    r = 'rock'
            else:
                if temperature < 0.3:
                    r = 'snow'
                elif temperature < 0.4:
                    r = 'tundra'
                else:
                    r = 'grass'
            #print('  ')

            #r = np.random.choice(['water', 'grass', 'rock', 'snow'])
            #r = 'grass'
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

            #vertices = world.v[world.f[iFace, 1:]]
            #v0 = vertices[1, :] - vertices[0, :]
            #v1 = vertices[2, :] - vertices[0, :]
            #normal = [v0[1]*v1[2] - v1[1]*v0[2], v0[0]*v1[2] - v1[0]*v0[2], v0[0]*v1[1] - v1[0]*v0[1]]

            normal = world.faceNormals[iFace, :]

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

        #-------------------------------------------------------------

        if False:
            worldWater = World.SphericalWorld()
        else:
            worldWater = pickle.load(open(Root_Directory.Path() + '/Data/tmp_Data/worldWater.pkl', "rb"))
        #worldWater.v *= 0.994 #0.9955
        #worldWater.faceRadius *= 0.994 #0.9955

        # v3n3t2 : vertices3, normals3, textureCoordinates2
        vertex_format = p3d.GeomVertexFormat.get_v3n3t2()
        # vertex_format = p3d.GeomVertexFormat.get_v3t2()
        vertex_data = p3d.GeomVertexData("triangle_data", vertex_format, p3d.Geom.UH_static)

        pos_writer = p3d.GeomVertexWriter(vertex_data, "vertex")
        normal_writer = p3d.GeomVertexWriter(vertex_data, "normal")
        tex_writer = p3d.GeomVertexWriter(vertex_data, 'texcoord')

        for iFace in range(np.size(worldWater.f, 0)):
            vertices = worldWater.v[worldWater.f[iFace, 1:]]
            pos_writer.add_data3(vertices[0, 0], vertices[0, 1], vertices[0, 2])
            pos_writer.add_data3(vertices[1, 0], vertices[1, 1], vertices[1, 2])
            pos_writer.add_data3(vertices[2, 0], vertices[2, 1], vertices[2, 2])

            r = np.random.choice(['water', 'grass', 'rock', 'snow'])
            #r = 'water'
            waterHeight = worldWater.faceRadius[iFace] - world.faceRadius[iFace]
            if waterHeight < 0.5:
                r = 'shallow_water'
            else:
                r = 'water'
            rIndices = texture.textureIndices[r]
            tex_writer.addData2f(rIndices[0], 0)
            tex_writer.addData2f(rIndices[1], 0)
            tex_writer.addData2f((rIndices[0] + rIndices[1])/2, np.sqrt(3)/2)

        tri = p3d.GeomTriangles(p3d.Geom.UH_static)

        # Creates the triangles.
        n = 0
        for iFace in range(np.size(worldWater.f, 0)):
            #tri.add_vertices(world.f[iFace, 0], world.f[iFace, 1], world.f[iFace, 2])
            tri.add_vertices(n, n+1, n+2)
            n += 3

        # Assigns a normal to each vertex.
        for iFace in range(np.size(worldWater.f, 0)):
            #normal_writer.add_data3(p3d.Vec3(self.normals[y, x, 0], self.normals[y, x, 1], self.normals[y, x, 2]))

            vertices = worldWater.v[worldWater.f[iFace, 1:]]
            v0 = vertices[1, :] - vertices[0, :]
            v1 = vertices[2, :] - vertices[0, :]
            normal = [v0[1]*v1[2] - v1[1]*v0[2], -v0[0]*v1[2] + v1[0]*v0[2], v0[0]*v1[1] - v1[0]*v0[1]]

            #normal_writer.add_data3(p3d.Vec3(0, 0, 1))
            #normal_writer.add_data3(p3d.Vec3(0, 0, 1))
            #normal_writer.add_data3(p3d.Vec3(0, 0, 1))
            normal_writer.add_data3(p3d.Vec3(normal[0], normal[1], normal[2]))
            normal_writer.add_data3(p3d.Vec3(normal[0], normal[1], normal[2]))
            normal_writer.add_data3(p3d.Vec3(normal[0], normal[1], normal[2]))

        geom = p3d.Geom(vertex_data)
        geom.add_primitive(tri)

        node = p3d.GeomNode("Water")
        node.add_geom(geom)
        self.water = p3d.NodePath(node)

        # This material adds some shine to the water surface.
        waterMaterial = p3d.Material()
        waterMaterial.setShininess(128.0)
        waterMaterial.setSpecular((0.2, 0.2, 0.2, 1))

        self.water.reparentTo(render)
        #self.water.setMaterial(waterMaterial)
        self.water.setTexture(texture.stitchedTexture)
        self.water.setShaderAuto()

        # ------------------------------------------------------------------
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
        #taskMgr.add(traverseTask, "tsk_traverse")
        #self.add_task(self.PickTask, 'picking')

        self.sunAngle = 0
        self.sunOrbitTime = 30
        self.add_task(self.RotateSun, 'sunRotation')

    def RotateSun(self, Task):
        dt = globalClock.get_dt()
        self.sunAngle = self.sunAngle+dt%self.sunOrbitTime
        sunx = np.cos(-2 * np.pi * self.sunAngle / self.sunOrbitTime)
        suny = np.sin(-2 * np.pi * self.sunAngle / self.sunOrbitTime)
        self.lightObject.sun.node().setDirection(p3d.LVector3(sunx, suny, 0))
        return Task.cont

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

