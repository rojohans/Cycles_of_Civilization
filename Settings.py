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
        self.N_ROWS = 16
        self.N_COLONS = 16
        self.HORIZONTAL_WRAP_BUFFER = 20

        self.MODEL_RESOLUTION = 30
        self.TILE_CENTER_WIDTH = 0.5
        self.TILE_TEXTURE_RESOLUTION = 128
        self.ADJACENT_TILES_TEMPLATE = np.array([[0, -1], [-1, -1], [-1, 0], [-1, 1], [0, 1], [1, 1], [1, 0], [1, -1]],
                                           dtype=int)

        self.ROCK_TEXTURE_SLOPE_THRESHOLD = 0.2
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

        self.ELEVATION_SCALE = 0.3
        self.DISCRETE_ELEVATION = True
        self.MAXIMUM_ELEVATION = 5

        self.SOIL_FERTILITY_LEVELS = 4
        self.DISCRETE_SOIL_FERTILITY_LEVELS = False
        self.SOIL_FERTILITY_DISTRIBUTION = [0.15, 0.3, 0.45, 0.1]
        #type  : barren  poor  normal  lush
        #yield :   0     0.5     1     1.25

        self.TOPOGRAPHY_ROUGHNESS_LEVELS = 3
        self.DISCRETE_TOPOGRAPHY_ROUGHNESS_LEVELS = False
        self.TOPOGRAPHY_ROUGHNESS_DISTRIBUTION = [0.6, 0.3, 0.1]
        #type  :  flat    hilly    mountanious
        #yield :

        # ==================== GUI ================================================================================
        self.BUTTON_SCALE = 0.08
        self.RELATIVE_SELECTION_FRAME_WIDTH = 0.6