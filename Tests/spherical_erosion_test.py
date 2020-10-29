import pyvista as pv
import numpy as np

'''
Y = np.arange(0, shape[0], 1)
X = np.arange(0, shape[1], 1)
X, Y = np.meshgrid(X, Y)

def CoordinatesToIndex(x, y):
    return x + y * shape[1]

NPoints = shape[0 ] *shape[1]
terrainPoints = np.zeros((NPoints, 3))
terrainPoints[:, 0] = np.reshape(X, (NPoints, 1))[:, 0]
terrainPoints[:, 1] = np.reshape(Y, (NPoints, 1))[:, 0]
terrainPoints[:, 2] = np.reshape(self.heightMap[:, :, 0], (NPoints, 1))[:, 0]

faces = []
for x in range(shape[1] - 1):
    for y in range(shape[0] - 1):
        faces.append([4, CoordinatesToIndex(x, y), CoordinatesToIndex(x + 1, y), CoordinatesToIndex(x + 1, y + 1),
                      CoordinatesToIndex(x, y + 1)])
faces = np.hstack(faces)

terrainMesh = pv.PolyData(terrainPoints, faces)

plotter = pv.Plotter()
plotter.add_mesh(terrainMesh, color=[0.3, 0.3, 0.35], smooth_shading=True)

plotter.enable_eye_dome_lighting()
plotter.show(auto_close=False)
'''

N = 100

def NormalizeVertex(x, y, z):
    '''
    Returns the vertex coordinates after being scaled to a unit sphere.
    '''

    radius = np.sqrt(x ** 2 + y ** 2 + z ** 2)
    return [i / radius for i in (x, y, z)]

import Library.World as World
world = World.SphericalWorld()
baseVertices = world.icosahedronVertices
baseFaces = world.icosahedronFaces


xCorner = baseVertices[baseFaces[0, :]]
v0 = xCorner[1, :] - xCorner[0, :]
v1 = xCorner[2, :] - xCorner[0, :]
xBase = xCorner[0, :]

# Calculate the total number of vertices
nVertices = 0
for i0, l0 in enumerate(np.linspace(0, 1, N)):
    for l1 in np.linspace(0, 1-l0, N-i0):
        nVertices += 1

print('Number of vertices = ', nVertices)
print('Number of vertices (globe) = ', 20*nVertices)

# Calculates the vertices
vertices = np.empty((nVertices, 3))
nVertice = 0
for i0, l0 in enumerate(np.linspace(0, 1, N)):
    for l1 in np.linspace(0, 1-l0, N-i0):
        vertices[nVertice, :] = xBase + l0*v0 + l1*v1
        nVertice += 1

# Calculate the total number of faces
m = 0
nFaces = 0
for i0 in np.linspace(0, N-2, N-1, dtype=int):
    for i1 in np.linspace(0, N-i0-2, N-i0-1):
        nFaces += 1
        if i1 > 0:
            nFaces += 1
    m += N - i0

print('number of faces = ', nFaces)
print('number of faces (globe) = ', 20*nFaces)

faces = []
m = 0
nFace = 0
for i0 in np.linspace(0, N-2, N-1, dtype=int):
    for i1 in np.linspace(0, N-i0-2, N-i0-1, dtype=int):
        faces.append([3, m+i1+1, m+i1, m+N-i0+i1])
        nFace += 1
        if i1 > 0:
            faces.append([3, m+i1, m+N-i0+i1-1, m+N-i0+i1])
            nFace += 1
    m += N - i0
faces = np.hstack(faces)







'''
import perlin_numpy
#shape = (512, 512, 512)
shape = (32, 32, 32)
rMap = perlin_numpy.generate_fractal_noise_3d(shape, (1, 1, 1), octaves=5, lacunarity=2, persistence=0.7,
                                                      tileable=(False, False, False))
print(np.shape(rMap))
#print(rMap)

from matplotlib import pyplot as plt
plotter = plt.imshow(rMap[:, :, 0])
for i in range(shape[2]):
    plotter.set_data(rMap[:, :, i])
    plt.pause(0.1)
plt.show()
'''

#scalarsFaces = np.random.rand(nFaces, 1)
scalarsFaces = np.random.rand(np.size(world.f, 0), 1)
scalarsVertices = 1+0.01*np.random.rand(nVertices, 1)

for i, vertice in enumerate(vertices):
    vertices[i, :] = scalarsVertices[i] * NormalizeVertex(vertice[0], vertice[1], vertice[2])

print(np.shape(world.v))
print(np.shape(world.f))


#faces = np.hstack(faces)
terrainMesh = pv.PolyData(world.v, np.hstack(world.f))
#terrainMesh = pv.PolyData(vertices, faces)


plotter = pv.Plotter()
plotter.add_mesh(terrainMesh, scalars=scalarsFaces, smooth_shading=True)

plotter.enable_eye_dome_lighting()
plotter.show(auto_close=False)
