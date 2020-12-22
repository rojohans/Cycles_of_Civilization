import panda3d.core as p3d
#from direct.showbase.Loader import Loader
from direct.task.Task import Task
from direct.showbase.DirectObject import DirectObject

from direct.showbase.ShowBase import ShowBase
import Root_Directory

class MyGame(ShowBase):
    def __init__(self):
        super().__init__()

        self.dae2Bam(Root_Directory.Path(style = 'unix') + '/Data/Models/', 'pine_tree_3_13', 'pine_1')
        self.dae2Bam(Root_Directory.Path(style = 'unix') + '/Data/Models/', 'pine_tree_2_15', 'spruce_1')
        self.dae2Bam(Root_Directory.Path(style = 'unix') + '/Data/Models/', 'birch_tree_2_17', 'birch_1')
        self.dae2Bam(Root_Directory.Path(style = 'unix') + '/Data/Models/', 'oak_tree_1_30', 'oak_1')
        self.dae2Bam(Root_Directory.Path(style = 'unix') + '/Data/Models/', 'palm_tree_3_3', 'palm_1')
        self.dae2Bam(Root_Directory.Path(style = 'unix') + '/Data/Models/', 'palm_tree_2_8', 'palm_2')
        self.dae2Bam(Root_Directory.Path(style = 'unix') + '/Data/Models/', 'kapok_tree_4_1', 'kapok_2')
        self.dae2Bam(Root_Directory.Path(style = 'unix') + '/Data/Models/', 'jungle_undergrowth_1_4', 'fern_1')

        #self.dae2Bam('wheat_2_2', 'wheat_1')

        self.dae2Bam(Root_Directory.Path(style = 'unix') + '/Data/Models/', 'gold_model_1')
        #self.dae2Bam('tower_model_2')
        self.dae2Bam(Root_Directory.Path(style='unix') + '/Data/Models/', 'farm_1_5', 'farm_1')
        self.dae2Bam(Root_Directory.Path(style = 'unix') + '/Data/Models/', 'house_1_4', 'house_1')
        self.dae2Bam(Root_Directory.Path(style = 'unix') + '/Data/Models/', '8_bit_test', '8_bit_test')
        self.dae2Bam(Root_Directory.Path(style='unix') + '/Data/Models/', 'storage_hall_1_1', 'storage_hall_1')
        self.dae2Bam(Root_Directory.Path(style='unix') + '/Data/Models/', 'lumbermill_1_1', 'lumbermill_1')
        self.dae2Bam(Root_Directory.Path(style='unix') + '/Data/Models/', 'windmill_1_3', 'windmill_1')
        self.dae2Bam(Root_Directory.Path(style='unix') + '/Data/Models/', 'bakery_1_1', 'bakery_1')
        self.dae2Bam(Root_Directory.Path(style='unix') + '/Data/Models/', 'quarry_1_1', 'quarry_1')
        self.dae2Bam(Root_Directory.Path(style='unix') + '/Data/Models/', 'mine_1_1', 'mine_1')
        self.dae2Bam(Root_Directory.Path(style='unix') + '/Data/Models/', 'foundry_1_1', 'foundry_1')
        self.dae2Bam(Root_Directory.Path(style='unix') + '/Data/Models/', 'blacksmith_1_1', 'blacksmith_1')
        self.dae2Bam(Root_Directory.Path(style='unix') + '/Data/Models/', 'granary_1_1', 'granary_1')

        self.dae2Bam(Root_Directory.Path(style='unix') + '/Data/Models/', 'boar_1_2', 'boar_1')

        quit()

    def dae2Bam(self, directoryPath, inputName, outputName = None):
        inputName = directoryPath + inputName
        if outputName == None:
            outputName = inputName
        else:
            outputName = directoryPath + outputName

        model = loader.loadModel(modelPath = inputName + '.dae')

        vertex_format = p3d.GeomVertexFormat.getV3n3t2()

        geomNodeCollection = model.findAllMatches('**/+GeomNode')
        for nodePath in geomNodeCollection:
            geomNode = nodePath.node()

            for i in range(geomNode.getNumGeoms()):
                geomNode.modifyGeom(i).modifyVertexData().setFormat(vertex_format)

        if outputName == None:
            model.writeBamFile(inputName + '.bam')
        else:
            model.writeBamFile(outputName + '.bam')


game = MyGame()
game.run()
