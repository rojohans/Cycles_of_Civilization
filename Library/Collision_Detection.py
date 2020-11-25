from direct.showbase.ShowBase import ShowBase
import panda3d.core as p3d
import numpy as np

class TilePicker():
    def __init__(self, mainProgram):
        self.mainProgram = mainProgram

        self.collidableRoot = render.attachNewNode('collidableRoot')
        collisionNodes = []
        for iFace in range(np.size(self.mainProgram.world.f, 0)):
            if self.mainProgram.world.faceRadius[iFace] > self.mainProgram.waterWorld.faceRadius[iFace]:
                vertices = self.mainProgram.world.v[self.mainProgram.world.f[iFace, 1:]]
            else:
                vertices = self.mainProgram.waterWorld.v[self.mainProgram.waterWorld.f[iFace, 1:]]

            collisionNodes.append(p3d.CollisionNode('cnode'))
            # collisionNodes.append(self.planet.attachNewNode(p3d.CollisionNode('cnode')))
            collisionNodes[-1].addSolid(
                p3d.CollisionPolygon(p3d.Point3(vertices[0, 0], vertices[0, 1], vertices[0, 2]),
                                     p3d.Point3(vertices[1, 0], vertices[1, 1], vertices[1, 2]),
                                     p3d.Point3(vertices[2, 0], vertices[2, 1], vertices[2, 2])))
            collisionNodes[-1].setIntoCollideMask(p3d.GeomNode.getDefaultCollideMask())
            collisionNodes[-1].setTag('iFace', str(iFace))
            self.collidableRoot.attachNewNode(collisionNodes[-1])



        self.queue = p3d.CollisionHandlerQueue()
        self.traverser = p3d.CollisionTraverser('traverser name')

        pickerNode = p3d.CollisionNode('mouseRay')
        pickerNP = camera.attachNewNode(pickerNode)
        pickerNode.setFromCollideMask(p3d.GeomNode.getDefaultCollideMask())
        self.pickerRay = p3d.CollisionRay()
        pickerNode.addSolid(self.pickerRay)
        self.traverser.addCollider(pickerNP, self.queue)


    def Pick(self):
        mpos = base.mouseWatcherNode.getMouse()
        self.pickerRay.setFromLens(base.camNode, mpos.getX(), mpos.getY())

        self.traverser.traverse(self.collidableRoot)

        if self.queue.getNumEntries() > 0:
            # This is so we get the closest object.
            self.queue.sortEntries()
            for entry in self.queue.get_entries():
                return int(entry.getIntoNodePath().getTag('iFace'))

    def __call__(self, *args, **kwargs):
        return self.Pick()
