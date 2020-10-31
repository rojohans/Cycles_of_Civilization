import pyvista as pv
import numpy as np

import Library.World as World
world = World.SphericalWorld()

terrainMesh = pv.PolyData(world.v, np.hstack(world.f))

plotter = pv.Plotter()
plotter.add_mesh(terrainMesh, scalars=world.faceRadius, smooth_shading=True)

#plotter.enable_eye_dome_lighting()
plotter.show(auto_close=False)





