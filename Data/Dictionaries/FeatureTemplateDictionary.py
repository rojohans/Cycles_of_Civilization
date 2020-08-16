
from pandac import *
from direct import *
from panda3d.core import *
from direct.showbase.Loader import *

class FeatureProperties():
    def __init__(self, models, weights, scaleRange):
        '''
        N : Number of models
        :param models: nodes containing 3d models. [N long list of nodes]
        :param weights: Determines in what proportion the different models are used. [N long list of floats]
        :param scaleRange: Used when randomly scaling teh models. [N long list of [float ,float]]

        Attributes to add:
                            movement cost
                            resources
        '''
        self.models = models
        self.weights = weights
        self.NormalizeWeights(self.weights)
        self.scaleRange = scaleRange

        self.numberOfComponents = len(models)
    def NormalizeWeights(self, weights):
        weightsSummed = 0
        for weight in weights:
            weightsSummed += weight
        for i, weight in enumerate(weights):
            weights[i] = weight/weightsSummed

def GetFeatureTemplateDictionary():
    '''
    This dictionary should contain an item for every feature in the game. Each dictionary entry should contain the
    properties of that features; for example: 3d models to use, movement cost and resource occurance. When a feature is
    to be places on the map all feature specific information should be contained within this dictionary.
    :return:
    '''

    featureTemplateDictionary = {}
    featureTemplateDictionary['spruce_forest'] = FeatureProperties(
        [loader.loadModel("panda3d-master/samples/chessboard/models/spruce_1.bam")],
        [1],
        [[0.8, 1.1]])
    featureTemplateDictionary['birch_forest'] = FeatureProperties(
        [loader.loadModel("panda3d-master/samples/chessboard/models/birch_1.bam")],
        [1],
        [[0.5, 1.1]])
    featureTemplateDictionary['pine_forest'] = FeatureProperties(
        [loader.loadModel("panda3d-master/samples/chessboard/models/pine_1.bam")],
        [1],
        [[0.7, 1.1]])
    featureTemplateDictionary['gold_ore'] = FeatureProperties(
        [loader.loadModel("panda3d-master/samples/chessboard/models/gold_model_1.bam")],
        [1],
        [[1, 1]])
    featureTemplateDictionary['town'] = FeatureProperties(
        [loader.loadModel("panda3d-master/samples/chessboard/models/house_1.bam")],
        [1],
        [[1.0, 1.0]])
    featureTemplateDictionary['wheat_field'] = FeatureProperties(
        [loader.loadModel("panda3d-master/samples/chessboard/models/wheat_1.bam")],
        [1],
        [[1.9, 2.1]])
    featureTemplateDictionary['oak_forest'] = FeatureProperties(
        [loader.loadModel("panda3d-master/samples/chessboard/models/oak_1.bam")],
        [1],
        [[0.5, 1.1]])
    featureTemplateDictionary['palm_forest'] = FeatureProperties(
        [loader.loadModel("panda3d-master/samples/chessboard/models/palm_1.bam")],
        [1],
        [[0.5, 1]])
    featureTemplateDictionary['jungle_trees'] = FeatureProperties(
        [loader.loadModel("panda3d-master/samples/chessboard/models/kapok_1.bam")],
        [1],
        [[0.8, 1.2]])
    featureTemplateDictionary['jungle'] = FeatureProperties(
        [loader.loadModel("panda3d-master/samples/chessboard/models/kapok_1.bam"),
         loader.loadModel("panda3d-master/samples/chessboard/models/palm_1.bam"),
         loader.loadModel("panda3d-master/samples/chessboard/models/fern_1.bam")],
        weights = [1, 4, 8],
        scaleRange = [[0.8, 1.2], [0.6, 0.9], [0.9, 1.2]])
    featureTemplateDictionary['temperate_forest'] = FeatureProperties(
        [loader.loadModel("panda3d-master/samples/chessboard/models/oak_1.bam"),
         loader.loadModel("panda3d-master/samples/chessboard/models/birch_1.bam")],
        [1, 3],
        [[0.7, 1.1], [0.7, 1]])
    featureTemplateDictionary['conifer_forest'] = FeatureProperties(
        [loader.loadModel("panda3d-master/samples/chessboard/models/pine_1.bam"),
         loader.loadModel("panda3d-master/samples/chessboard/models/spruce_1.bam")],
        weights = [1, 2],
        scaleRange = [[0.8, 1.2], [0.8, 1.1]])

    featureTemplateDictionary['8_bit_test'] = FeatureProperties(
        [loader.loadModel("panda3d-master/samples/chessboard/models/8_bit_test.bam")],
        weights = [1],
        scaleRange = [[0.8, 1.2]])
    return featureTemplateDictionary



