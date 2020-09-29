import numpy as np
from matplotlib import pyplot as plt
import time

import Settings
import Library.World as World



class Main():
    def __init__(self):
        self.settings = Settings.SettingsClass()

        tic = time.time()
        World.WorldClass.Initialize(mainProgram = self)
        self.world = World.WorldClass()
        toc = time.time()
        print('World creation time: ', toc-tic)

        tic = time.time()
        self.worldTopography = self.world.elevationInterpolator(np.linspace(-0.5, self.settings.N_COLONS-0.5, self.settings.N_COLONS*self.settings.MODEL_RESOLUTION),
                                         np.linspace(-0.5, self.settings.N_ROWS-0.5, self.settings.N_ROWS*self.settings.MODEL_RESOLUTION))
        toc = time.time()
        print('Topography interpolation', toc-tic)

        self.world.VisualizeMaps([self.world.elevation, self.worldTopography])




Main()
print('Erosion test finished')