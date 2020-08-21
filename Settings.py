

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



        '''
        self.N_ROWS = 128
        self.N_COLONS = 128
        self.MODEL_RESOLUTION = 30
        self.ELEVATION_SCALE = 0.3

        self.FEATURE_RENDER_RADIUS = 12
        self.FEATURE_RENDER_CAPACITY = 2000
        self.FEATURE_RENDER_MAX_SPEED = 2 # The maximum #features to add each frame.