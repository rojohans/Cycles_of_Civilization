import numpy as np


class AnimationClass():
    def __init__(self):
        #self.node = node
        pass

    def Update(self):
        pass

    def Destroy(self):
        pass

    @classmethod
    def Initialize(cls, ELEVATION_SCALE, mainProgram):
        cls.ELEVATION_SCALE = ELEVATION_SCALE
        cls.mainProgram = mainProgram

        cls.animationList = []

    @classmethod
    def AnimationTaskFunction(cls):
        for animation in cls.animationList:
            animation.Update()



class UnitAnimationClass(AnimationClass):
    def __init__(self, unit, pathNodes, pathLength):
        super().__init__()
        self.unit = unit

        self.index = 0
        self.path = []
        self.indexMax = 0

        for i, length in enumerate(pathLength):
            self.indexMax += length
            currentNode = np.array(pathNodes[i])
            nextNode = np.array(pathNodes[i + 1])
            for j in np.linspace(0, 1, length):
                self.path.append(nextNode*j + currentNode*(1-j))

        self.animationList.append(self)

    def Update(self):
        nextPosition = self.path[self.index]

        self.unit.row = nextPosition[0]
        self.unit.colon = nextPosition[1]
        self.unit.elevation = nextPosition[2]

        self.unit.node.setPos(nextPosition[1] + 0.5, nextPosition[0] + 0.5, self.ELEVATION_SCALE * (nextPosition[2] + 0.1))

        if self.unit.isSelected:
            self.mainProgram.unitMarker.setPos(self.unit.colon + 0.5, self.unit.row + 0.5,
                                               self.ELEVATION_SCALE * (self.unit.elevation + 0.1))

        self.index += 1
        if self.index == self.indexMax:
            self.unit.isMoving = False
            self.Destroy()

    def Destroy(self):
        self.animationList.remove(self)



