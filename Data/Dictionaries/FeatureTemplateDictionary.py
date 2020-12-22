
from pandac import *
from direct import *
from panda3d.core import *
from direct.showbase.Loader import *
import Root_Directory

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
        [loader.loadModel(Root_Directory.Path(style = 'unix') + "/Data/Models/spruce_1.bam")],
        [1],
        [[0.8, 1.1]])
    featureTemplateDictionary['birch_forest'] = FeatureProperties(
        [loader.loadModel(Root_Directory.Path(style = 'unix') + "/Data/Models/birch_1.bam")],
        [1],
        [[0.5, 1.1]])
    featureTemplateDictionary['pine_forest'] = FeatureProperties(
        [loader.loadModel(Root_Directory.Path(style = 'unix') + "/Data/Models/pine_1.bam")],
        [1],
        [[0.7, 1.1]])
    featureTemplateDictionary['gold_ore'] = FeatureProperties(
        [loader.loadModel(Root_Directory.Path(style = 'unix') + "/Data/Models/gold_model_1.bam")],
        [1],
        [[1, 1]])
    featureTemplateDictionary['town'] = FeatureProperties(
        [loader.loadModel(Root_Directory.Path(style = 'unix') + "/Data/Models/house_1.bam")],
        [1],
        [[1.0, 1.0]])
    #featureTemplateDictionary['wheat_field'] = FeatureProperties(
    #    [loader.loadModel(Root_Directory.Path(style = 'unix') + "/Data/Models/models/wheat_1.bam")],
    #    [1],
    #    [[1.9, 2.1]])
    featureTemplateDictionary['oak_forest'] = FeatureProperties(
        [loader.loadModel(Root_Directory.Path(style = 'unix') + "/Data/Models/oak_1.bam")],
        [1],
        [[0.5, 1.1]])
    featureTemplateDictionary['palm_forest'] = FeatureProperties(
        [loader.loadModel(Root_Directory.Path(style = 'unix') + "/Data/Models/palm_1.bam")],
        [1],
        [[0.5, 1]])
    #featureTemplateDictionary['jungle_trees'] = FeatureProperties(
    #    [loader.loadModel(Root_Directory.Path(style = 'unix') + "/Data/Models/kapok_1.bam")],
    #    [1],
    #    [[0.8, 1.2]])
    featureTemplateDictionary['jungle'] = FeatureProperties(
        [loader.loadModel(Root_Directory.Path(style = 'unix') + "/Data/Models/kapok_2.bam"),
         loader.loadModel(Root_Directory.Path(style = 'unix') + "/Data/Models/palm_1.bam"),
         loader.loadModel(Root_Directory.Path(style = 'unix') + "/Data/Models/palm_2.bam"),
         loader.loadModel(Root_Directory.Path(style = 'unix') + "/Data/Models/fern_1.bam")],
        weights = [1, 1.5, 5, 7],
        scaleRange = [[0.8, 1.2], [1.1, 1.4], [1.6, 1.9], [0.9, 1.2]])
    featureTemplateDictionary['temperate_forest'] = FeatureProperties(
        [loader.loadModel(Root_Directory.Path(style = 'unix') + "/Data/Models/oak_1.bam"),
         loader.loadModel(Root_Directory.Path(style = 'unix') + "/Data/Models/birch_1.bam")],
        [1, 3],
        [[0.7, 1.1], [0.7, 1]])
    featureTemplateDictionary['conifer_forest'] = FeatureProperties(
        [loader.loadModel(Root_Directory.Path(style = 'unix') + "/Data/Models/pine_1.bam"),
         loader.loadModel(Root_Directory.Path(style = 'unix') + "/Data/Models/spruce_1.bam")],
        weights = [1, 2],
        scaleRange = [[0.8, 1.2], [0.8, 1.1]])

    featureTemplateDictionary['boar_herd'] = FeatureProperties(
        [loader.loadModel(Root_Directory.Path(style = 'unix') + "/Data/Models/boar_1.bam")],
        weights = [1],
        scaleRange = [[0.8, 1.2]])


    featureTemplateDictionary['8_bit_test'] = FeatureProperties(
        [loader.loadModel(Root_Directory.Path(style = 'unix') + "/Data/Models/8_bit_test.bam")],
        weights = [1],
        scaleRange = [[2.2, 2.2]])


    featureTemplateDictionary['farm'] = FeatureProperties(
        [loader.loadModel(Root_Directory.Path(style = 'unix') + "/Data/Models/farm_1.bam")],
        [1],
        [[1.2, 1.2]])

    return featureTemplateDictionary

class GlobeFeatureProperties():
    def __init__(self, models, weights, scaleRange, triangleDivisions, nObjects, orientationMode, GUILabel, textureKey, buildingTemplate = None, movementCost = None):
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
        self.triangleDivisions = triangleDivisions
        self.nObjects = nObjects # Determines how many models will be placed on the tile.
        self.orientationMode = orientationMode
        self.GUILabel = GUILabel
        self.textureKey = textureKey

        self.buildingTemplate  = buildingTemplate
        self.movementCost = movementCost


        self.numberOfComponents = len(models)
    def NormalizeWeights(self, weights):
        weightsSummed = 0
        for weight in weights:
            weightsSummed += weight
        for i, weight in enumerate(weights):
            weights[i] = weight/weightsSummed

def GetFeatureTemplateDictionaryGlobe(mainProgram):
    '''
    This dictionary should contain an item for every feature in the game. Each dictionary entry should contain the
    properties of that features; for example: 3d models to use, movement cost and resource occurance. When a feature is
    to be places on the map all feature specific information should be contained within this dictionary.
    :return:
    '''
    featureTemplateDictionary = {}

    import Data.Templates.Building_Templates as Building_Templates
    import Library.Industry as Industry

    featureTemplateDictionary['town'] = GlobeFeatureProperties(
        models = [loader.loadModel(Root_Directory.Path(style = 'unix') + "/Data/Models/house_1.bam")],
        weights  = [1],
        scaleRange = [[1.3, 1.3]],
        triangleDivisions=4,
        nObjects=15,
        orientationMode='uniform',
        GUILabel = 'TOWN',
        textureKey = None,
        buildingTemplate = Building_Templates.Household)
    featureTemplateDictionary['farm'] = GlobeFeatureProperties(
        models = [loader.loadModel(Root_Directory.Path(style = 'unix') + "/Data/Models/farm_1.bam")],
        weights  = [1],
        scaleRange = [[1.6, 1.6]],
        triangleDivisions=0,
        nObjects=1,
        orientationMode = 'random',
        GUILabel = 'FARM',
        textureKey = 'farm_field',
        buildingTemplate = Building_Templates.GrainFarm)
    featureTemplateDictionary['tuber_farm'] = GlobeFeatureProperties(
        models = [loader.loadModel(Root_Directory.Path(style = 'unix') + "/Data/Models/farm_1.bam")],
        weights  = [1],
        scaleRange = [[1.6, 1.6]],
        triangleDivisions=0,
        nObjects=1,
        orientationMode = 'random',
        GUILabel = 'TUBER FARM',
        textureKey = 'tuber_farm_field',
        buildingTemplate = Building_Templates.TuberFarm)
    featureTemplateDictionary['road'] = GlobeFeatureProperties(
        models = [],
        weights  = [1],
        scaleRange = [[1.6, 1.6]],
        triangleDivisions=0,
        nObjects=1,
    orientationMode = 'random',
        GUILabel = 'ROAD',
    textureKey = 'road',
    movementCost=4)
    featureTemplateDictionary['stone_road'] = GlobeFeatureProperties(
        models = [],
        weights  = [1],
        scaleRange = [[1.6, 1.6]],
        triangleDivisions=0,
        nObjects=1,
    orientationMode = 'random',
        GUILabel = 'STONE ROAD',
    textureKey = 'stone_road',
    movementCost=2)
    featureTemplateDictionary['field'] = GlobeFeatureProperties(
        models = [],
        weights  = [1],
        scaleRange = [[1.6, 1.6]],
        triangleDivisions=0,
        nObjects=1,
    orientationMode = 'random',
        GUILabel = 'FIELD',
    textureKey = 'farm_field')
    featureTemplateDictionary['storage_hall'] = GlobeFeatureProperties(
        models = [loader.loadModel(Root_Directory.Path(style = 'unix') + "/Data/Models/storage_hall_1.bam")],
        weights  = [1],
        scaleRange = [[1.2, 1.2]],
        triangleDivisions=0,
        nObjects=1,
    orientationMode = 'random',
        GUILabel = 'STORAGE HALL',
    textureKey = None,
    buildingTemplate = Building_Templates.Stockpile)
    featureTemplateDictionary['lumbermill'] = GlobeFeatureProperties(
        models = [loader.loadModel(Root_Directory.Path(style = 'unix') + "/Data/Models/lumbermill_1.bam")],
        weights  = [1],
        scaleRange = [[0.2, 0.2]],
        triangleDivisions=0,
        nObjects=1,
    orientationMode = 'random',
        GUILabel = 'LUMBER MILL',
    textureKey = None,
    buildingTemplate = Building_Templates.Lumbermill)
    featureTemplateDictionary['windmill'] = GlobeFeatureProperties(
        models = [loader.loadModel(Root_Directory.Path(style = 'unix') + "/Data/Models/windmill_1.bam")],
        weights  = [1],
        scaleRange = [[0.2, 0.2]],
        triangleDivisions=1,
        nObjects=3,
    orientationMode = 'uniform',
        GUILabel = 'WIND MILL',
    textureKey = None,
    buildingTemplate = Building_Templates.Windmill)
    featureTemplateDictionary['bakery'] = GlobeFeatureProperties(
        models = [loader.loadModel(Root_Directory.Path(style = 'unix') + "/Data/Models/bakery_1.bam")],
        weights  = [1],
        scaleRange = [[0.2, 0.2]],
        triangleDivisions=1,
        nObjects=3,
    orientationMode = 'uniform',
        GUILabel = 'BAKERY',
    textureKey = None,
    buildingTemplate = Building_Templates.Bakery)
    featureTemplateDictionary['quarry'] = GlobeFeatureProperties(
        models = [loader.loadModel(Root_Directory.Path(style = 'unix') + "/Data/Models/quarry_1.bam")],
        weights  = [1],
        scaleRange = [[0.14, 0.14]],
        triangleDivisions=0,
        nObjects=1,
        orientationMode = 'random',
        GUILabel = 'QUARRY',
    textureKey = None,
    buildingTemplate = Building_Templates.Quarry)
    featureTemplateDictionary['iron mine'] = GlobeFeatureProperties(
        models = [loader.loadModel(Root_Directory.Path(style = 'unix') + "/Data/Models/mine_1.bam")],
        weights  = [1],
        scaleRange = [[0.13, 0.13]],
        triangleDivisions=0,
        nObjects=1,
        orientationMode = 'random',
        GUILabel = 'IRON MINE',
    textureKey = None,
    buildingTemplate = Building_Templates.IronMine)
    featureTemplateDictionary['coal mine'] = GlobeFeatureProperties(
        models = [loader.loadModel(Root_Directory.Path(style = 'unix') + "/Data/Models/mine_1.bam")],
        weights  = [1],
        scaleRange = [[0.13, 0.13]],
        triangleDivisions=0,
        nObjects=1,
        orientationMode = 'random',
        GUILabel = 'COAL MINE',
    textureKey = None,
    buildingTemplate = Building_Templates.CoalMine)
    featureTemplateDictionary['foundry'] = GlobeFeatureProperties(
        models = [loader.loadModel(Root_Directory.Path(style = 'unix') + "/Data/Models/foundry_1.bam")],
        weights  = [1],
        scaleRange = [[0.13, 0.13]],
        triangleDivisions=0,
        nObjects=1,
        orientationMode = 'random',
        GUILabel = 'FOUNDRY',
    textureKey = None,
    buildingTemplate = Building_Templates.Foundry)
    featureTemplateDictionary['blacksmith'] = GlobeFeatureProperties(
        models = [loader.loadModel(Root_Directory.Path(style = 'unix') + "/Data/Models/blacksmith_1.bam")],
        weights  = [1],
        scaleRange = [[0.13, 0.13]],
        triangleDivisions=0,
        nObjects=1,
        orientationMode = 'random',
        GUILabel = 'BLACKSMITH',
    textureKey = None,
    buildingTemplate = Building_Templates.Blacksmith)
    featureTemplateDictionary['granary'] = GlobeFeatureProperties(
        models = [loader.loadModel(Root_Directory.Path(style = 'unix') + "/Data/Models/granary_1.bam")],
        weights  = [1],
        scaleRange = [[0.21, 0.21]],
        triangleDivisions=0,
        nObjects=1,
        orientationMode = 'random',
        GUILabel = 'GRANARY',
    textureKey = None,
    buildingTemplate = Building_Templates.Granary)

    featureTemplateDictionary['pine_forest'] = GlobeFeatureProperties(
        models = [loader.loadModel(Root_Directory.Path(style = 'unix') + "/Data/Models/pine_1.bam")],
        weights  = [1],
        scaleRange = [[3.4, 3.6]],
        triangleDivisions=2,
        nObjects=5,
    orientationMode = 'random',
        GUILabel = 'PINE FOREST',
    textureKey = 'forest',
    movementCost=15)
    featureTemplateDictionary['conifer_forest'] = GlobeFeatureProperties(
        models = [loader.loadModel(Root_Directory.Path(style = 'unix') + "/Data/Models/pine_1.bam"),
         loader.loadModel(Root_Directory.Path(style = 'unix') + "/Data/Models/spruce_1.bam")],
        weights = [2, 1],
        scaleRange = [[3.4, 3.6], [3.4, 3.6]],
        triangleDivisions=2,
        nObjects=5,
    orientationMode = 'random',
        GUILabel = 'CONIFER FOREST',
    textureKey = 'forest',
    movementCost=15)
    featureTemplateDictionary['temperate_forest'] = GlobeFeatureProperties(
        models = [loader.loadModel(Root_Directory.Path(style = 'unix') + "/Data/Models/kapok_2.bam")],
        weights  = [1],
        scaleRange = [[1.4, 1.6]],
        triangleDivisions=2,
        nObjects=5,
    orientationMode = 'random',
        GUILabel = 'TEMPERATE FOREST',
    textureKey = 'forest',
    movementCost=15)
    featureTemplateDictionary['jungle'] = GlobeFeatureProperties(
        models = [loader.loadModel(Root_Directory.Path(style = 'unix') + "/Data/Models/palm_2.bam")],
        weights  = [1],
        scaleRange = [[4.3, 4.7]],
        triangleDivisions=2,
        nObjects=5,
    orientationMode = 'random',
        GUILabel = 'JUNGLE',
    textureKey = 'forest')

    return featureTemplateDictionary

#loader.loadModel(Root_Directory.Path(style = 'unix') + "/Data/Models/palm_2.bam")
#loader.loadModel(Root_Directory.Path(style = 'unix') + "/Data/Models/kapok_2.bam")