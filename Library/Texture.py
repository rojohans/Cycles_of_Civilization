import panda3d.core as p3d

from matplotlib import image
import numpy as np

import Root_Directory

class Texture():
    def __init__(self, textures):
        self.textures = textures

        self.textureIndices = {}
        indices = np.linspace(0, 1, len(self.textures) + 1)

        for i, textureKey in enumerate(self.textures):
            if i == 0:
                stitchedTextureArray = self.textures[textureKey]
            else:
                stitchedTextureArray = np.concatenate((stitchedTextureArray, self.textures[textureKey]), axis=1)
            self.textureIndices[textureKey] = [indices[i], indices[i + 1]]

        shape = np.shape(stitchedTextureArray)

        textureArray = np.zeros((shape[0], shape[1], 3), dtype=np.uint8)
        textureArray[:, :, 0] = np.uint8(255 * stitchedTextureArray[:, :, 2])
        textureArray[:, :, 1] = np.uint8(255 * stitchedTextureArray[:, :, 1])
        textureArray[:, :, 2] = np.uint8(255 * stitchedTextureArray[:, :, 0])

        tex = p3d.Texture()
        tex.setup2dTexture(shape[1], shape[0], p3d.Texture.T_unsigned_byte, p3d.Texture.F_rgb)

        buf = textureArray[:, :, :].tostring()
        tex.setRamImage(buf) # np.array -> texture

        # Use texture pixels without interpolation.
        #tex.setMagfilter(p3d.Texture.FT_nearest)
        #tex.setMinfilter(p3d.Texture.FT_nearest)

        self.stitchedTexture = tex

        # Creates a white texture useful for debugging.
        whiteTextureArray = image.imread(Root_Directory.Path() + "/Data/Tile_Data/white_terrain.png")
        textureArray = np.zeros((shape[0], shape[0], 3), dtype=np.uint8)
        textureArray[:, :, 0] = np.uint8(255 * whiteTextureArray[:, :, 2])
        textureArray[:, :, 1] = np.uint8(255 * whiteTextureArray[:, :, 1])
        textureArray[:, :, 2] = np.uint8(255 * whiteTextureArray[:, :, 0])

        tex = p3d.Texture()
        tex.setup2dTexture(shape[0], shape[0], p3d.Texture.T_unsigned_byte, p3d.Texture.F_rgb)
        buf = textureArray[:, :, :].tostring()
        tex.setRamImage(buf) # np.array -> texture
        self.whiteTexture = tex


