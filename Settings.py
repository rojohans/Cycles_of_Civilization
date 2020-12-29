import numpy as np

class SettingsClass():
    def __init__(self):
        '''
        N_ROWS : The number of rows in the tile grid.
        N_COLONS : The number of colons in the tile grid.
        MODEL_RESOLUTION : The dimension of the tile vertex structure. A tile with model resolution X will consist of
                           X*X vertices. This value might need to correlate with certain file dimensions, topography
                           files for example.
        ELEVATION_SCALE : The z-scale used for tiles. A value of 1 will make the tiles 1 unit high and 1 unit wide. A
                          value of 0 will make all tiles flat. A good value might be 0.3.
        FEATUER_RENDER_RADIUS :
        FEATURE_RENDER_CAPACITY :
        FEATURE_RENDER_MAX_SPEED :
        '''
        self.N_ROWS = 32
        self.N_COLONS = 64
        self.HORIZONTAL_WRAP_BUFFER = 20

        self.MODEL_RESOLUTION = 10
        self.TILE_CENTER_WIDTH = 0.5
        self.TILE_TEXTURE_RESOLUTION = 128
        self.ADJACENT_TILES_TEMPLATE_CROSS = np.array([[0, -1], [-1, 0], [0, 1], [1, 0]], dtype=int)
        self.ADJACENT_TILES_TEMPLATE = np.array([[0, -1], [-1, -1], [-1, 0], [-1, 1], [0, 1], [1, 1], [1, 0], [1, -1]],
                                           dtype=int)
        self.ADJACENT_TILES_TEMPLATE_BIG = np.array([[-1, 1], [0, 1], [1, 1], [-1, 0], [0, 0], [1, 0], [-1, -1], [0, -1], [1, -1]],
                                           dtype=int)

        self.ROCK_TEXTURE_SLOPE_THRESHOLD = 0.3
        self.ROCK_TEXTURE_RADIUS = round(self.TILE_TEXTURE_RESOLUTION / (self.MODEL_RESOLUTION*1.2))
        self.ROCK_TEXTURE_CIRCLE = []
        for row in np.linspace(-self.ROCK_TEXTURE_RADIUS, self.ROCK_TEXTURE_RADIUS, self.ROCK_TEXTURE_RADIUS * 2 + 1):
            for colon in np.linspace(-self.ROCK_TEXTURE_RADIUS, self.ROCK_TEXTURE_RADIUS, self.ROCK_TEXTURE_RADIUS * 2 + 1):
                if np.sqrt(row**2 + colon**2) <= self.ROCK_TEXTURE_RADIUS:
                    self.ROCK_TEXTURE_CIRCLE.append([colon, row])
        self.ROCK_TEXTURE_CIRCLE = np.array(self.ROCK_TEXTURE_CIRCLE)


        self.FEATURE_RENDER_RADIUS = 12
        self.FEATURE_RENDER_CAPACITY = 2000 # the maximum # tiles which will be kept in RAM.
        self.FEATURE_RENDER_MAX_SPEED = 2 # The maximum #features to add each frame.


        # ================ WORLD GENERATION ============================================================================
        self.WATER_HEIGHT = 0.5 # The water level above the underlying tile.
        self.OCEAN_HEIGHT = 1.5
        self.ELEVATION_SCALE = 0.6
        self.ELEVATION_LEVELS = 9
        self.DISCRETE_ELEVATION = False
        #self.ELEVATION_DISTRIBUTION = [0.325, 0.125, 0.18, 0.155, 0.11, 0.06, 0.03, 0.01, 0.005]
        self.ELEVATION_DISTRIBUTION = np.array([(0, 0),
                                                (1, 0.325),
                                                (2, 0.125),
                                                (3, 0.18),
                                                (4, 0.155),
                                                (5, 0.11),
                                                (6, 0.065),
                                                (7, 0.03),
                                                (8, 0.01)])
        self.ELEVATION_MINIMAP_COLOURS = np.array([(0.1, 0.1, 0.3),
                                                   (0.1, 0.3, 0.7),
                                                   (0.15, 0.5, 0.05),
                                                   (0.4, 0.7, 0.1),
                                                   (0.8, 0.8, 0.1),
                                                   (0.8, 0.4, 0.3),
                                                   (0.5, 0.3, 0.25),
                                                   (0.2, 0.2, 0.25),
                                                   (1.0, 1.0, 1.0)])
        self.ELEVATION_MINIMAP_COLOURS_BOUNDS = np.array([(0.0, 0.0, 0.0),
                                                          (1.0, 1.0, 1.0)])

        self.SOIL_FERTILITY_LEVELS = 4
        self.DISCRETE_SOIL_FERTILITY_LEVELS = False
        self.SOIL_FERTILITY_DISTRIBUTION = [0.15, 0.3, 0.45, 0.1]
        # type  : barren  poor  normal  lush
        # yield :   0     0.5     1     1.25
        self.SOIL_FERTILITY_MINIMAP_COLOURS = np.array([(0.3, 0.3, 0.3),
                                                        (0.55, 0.55, 0.4),
                                                        (0.6, 0.9, 0.3),
                                                        (0.15, 0.6, 0.05)])
        self.SOIL_FERTILITY_MINIMAP_COLOURS_BOUNDS = np.array([(0.0, 0.0, 0.0),
                                                               (0.15, 0.6, 0.05)])

        self.TOPOGRAPHY_ROUGHNESS_LEVELS = 3
        self.DISCRETE_TOPOGRAPHY_ROUGHNESS_LEVELS = False
        self.TOPOGRAPHY_ROUGHNESS_DISTRIBUTION = [0.3, 0.5, 0.2]
        #type  :  flat    hilly    mountanious
        #yield :
        self.TOPOGRAPHY_ROUGHNESS_MINIMAP_COLOURS = np.array([(1.0, 1.0, 1.0),       # white
                                                              (0.6, 0.6, 0.3),       # yellow/light brown
                                                              (0.25, 0.2, 0.1)])    # dark brown
        self.TOPOGRAPHY_ROUGHNESS_MINIMAP_COLOURS_BOUNDS = np.array([(0.0, 0.0, 0.0),
                                                                     (0.25, 0.2, 0.1)])

        self.TEMPERATURE_MIN_VALUE = -20
        self.TEMPERATURE_MAX_VALUE = 30
        self.TEMPERATURE_PERLIN_WEIGHT = 0.5
        self.TEMPERATURE_ELEVATION_WEIGHT = 1.7
        self.TEMPERATURE_LATITUDE_WEIGHT = 3
        self.TEMPERATURE_MINIMAP_COLOURS = np.array([(1.0, 1.0, 1.0),  #-40
                                                     (0.8, 0.1, 0.8),  #-30
                                                     (0.1, 0.0, 0.4),  #-20
                                                     (0.1, 0.2, 0.6),  #-10
                                                     (0.1, 0.8, 1.0),  #2
                                                     (1.0, 1.0, 0.1),  #13
                                                     (0.7, 0.5, 0.0),  #20
                                                     (0.3, 0.0, 0.0)]) #30
        self.TEMPERATURE_MINIMAP_COLOURS_BOUNDS = np.array([(0, 0, 0),
                                                            (0.3, 0.0, 0.0)])

        # The range in which ocean increases moisture
        self.MOISTURE_OCEAN_RANGE = self.N_COLONS/7
        self.MOISTURE_PERLIN_WEIGHT = 1.7
        self.MOISTURE_OCEAN_WEIGHT = 0.8
        self.MOISTURE_ELEVATION_WEIGHT = 0.1
        self.MOISTURE_LATITUDE_WEIGHT = 1.5#2
        self.MOISTURE_MINIMAP_COLOURS = np.array([(0.4, 0.3, 0.1),
                                                  (0.7, 0.7, 0.3),
                                                  (0.2, 0.5, 0.7),
                                                  (0.1, 0.1, 0.4)])
        self.MOISTURE_MINIMAP_COLOURS_BOUNDS = np.array([(0, 0, 0),
                                                         (0.1, 0.1, 0.4)])

        # ================= ECOSYSTEM ============================================================================
        self.VEGETATION_INTERPOLATION_RESOLUTION = 50
        self.VEGETATION_OUTCOMPETE_PARAMETER = 10
        self.ANIMAL_OUTCOMPETE_PARAMETER = 2

        # ==================== GUI ================================================================================
        self.BUTTON_SCALE = 0.08
        self.RELATIVE_SELECTION_FRAME_WIDTH = 0.5

        self.MINIMAP_SELECTION_BUTTON_SCALE = 0.8 # A percentage of the frame width
        self.MINIMAP_RESOLUTION = [256, 256]

class GlobeSettings:
    def __init__(self):

        self.forestPerlinThreshold = 0.1


        self.transportLinkUpdateInterval = 10


        self.defaultMovementRange = 60 # The movement range of a building by default.
        self.defaultMovementCost =  10 # The movement cost of normal terrain without features.


        # =============================================================================================================
        # ==================================================== GUI ====================================================
        # =============================================================================================================
        self.buttonSize = 0.05

        self.quitButtonPosition = (0.95, 0, 0.95)

        self.tileInformationFramePosition = (-0.85, 0, -0.7)
        self.tileInformationFrameSize = (-0.15, 0.15, -0.3, 0.3)
        self.tileInformationMargin = 0.03

        self.tileActionFramePosition = (-0.55, 0, -0.85)
        self.tileActionFrameSize = (-0.15, 0.15, -0.15, 0.15)


        self.featureInformationFramePosition = (0, 0, 0)
        self.featureInformationFrameSize = (-1, -0.6, -0.4, 0.7)
        self.featureInformationMargin = [0.03, 0.1]


        self.addFeatureFramePosition = (0, 0, 0)
        self.addFeatureFrameSize = (-1, -0.6, -0.4, 0.7)
        self.addFeatureFrameCanvasSize = (0, 0.4, -3.6, 0)
        self.addFeatureFrameChildrenGap = 0.1

        self.statisticsGraphPosition = (-0.2, 0.0, -0.2)
        self.statisticsGraphSize = (-0.7, 0.7, -0.6, 0.6)


