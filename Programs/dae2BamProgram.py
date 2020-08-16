import panda3d.core as p3d
#from direct.showbase.Loader import Loader
from direct.task.Task import Task
from direct.showbase.DirectObject import DirectObject

from direct.showbase.ShowBase import ShowBase

class MyGame(ShowBase):
    def __init__(self):
        super().__init__()

        self.dae2Bam('pine_tree_3_13', 'pine_1')
        self.dae2Bam('pine_tree_2_15', 'spruce_1')
        self.dae2Bam('birch_tree_2_17', 'birch_1')
        self.dae2Bam('oak_tree_1_29', 'oak_1')
        self.dae2Bam('palm_tree_1_6', 'palm_1')
        self.dae2Bam('jungle_tree_1_8', 'kapok_1')
        self.dae2Bam('jungle_undergrowth_1_2', 'fern_1')

        self.dae2Bam('wheat_2_2', 'wheat_1')

        self.dae2Bam('gold_model_1')
        self.dae2Bam('tower_model_2')
        self.dae2Bam('house_1_4', 'house_1')
        self.dae2Bam('8_bit_test', '8_bit_test')

        quit()

    def dae2Bam(self, modelName, bamName = None):
        model = loader.loadModel(modelPath = modelName + '.dae')

        vertex_format = p3d.GeomVertexFormat.getV3n3t2()

        geomNodeCollection = model.findAllMatches('**/+GeomNode')
        for nodePath in geomNodeCollection:
            geomNode = nodePath.node()

            for i in range(geomNode.getNumGeoms()):
                geomNode.modifyGeom(i).modifyVertexData().setFormat(vertex_format)

        if bamName == None:
            model.writeBamFile(modelName + '.bam')
        else:
            model.writeBamFile(bamName + '.bam')


game = MyGame()
game.run()
