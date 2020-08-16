
import numpy as np
from panda3d import core as p3d


filterCenter = p3d.PNMImage()
filterCenter.read("models/tile_filter_center.jpg")
#filterSide = p3d.PNMImage()
#filterSide.read("models/tile_filter_side.jpg")
#filterCorner = p3d.PNMImage()
#filterCorner.read("models/tile_filter_corner.jpg")


filterSideLeft = p3d.PNMImage()
filterSideBottom = p3d.PNMImage()
filterSideRight = p3d.PNMImage()
filterSideTop = p3d.PNMImage()

filterSideLeft.read("models/tile_filter_side.jpg")
filterSideBottom.read("models/tile_filter_side.jpg")
filterSideRight.read("models/tile_filter_side.jpg")
filterSideTop.read("models/tile_filter_side.jpg")

filterSideLeft.flip(flip_x=False, flip_y=False, transpose=True)
filterSideLeft.flip(flip_x=True, flip_y=False, transpose=False)
filterSideRight.flip(flip_x=False, flip_y=False, transpose=True)
filterSideTop.flip(flip_x=False, flip_y=True, transpose=False)



filterCornerBottomLeft = p3d.PNMImage()
filterCornerBottomRight = p3d.PNMImage()
filterCornerTopLeft = p3d.PNMImage()
filterCornerTopRight = p3d.PNMImage()

filterCornerBottomLeft.read("models/tile_filter_corner.jpg")
filterCornerBottomRight.read("models/tile_filter_corner.jpg")
filterCornerTopLeft.read("models/tile_filter_corner.jpg")
filterCornerTopRight.read("models/tile_filter_corner.jpg")

filterCornerBottomLeft.flip(flip_x=True, flip_y=False, transpose=False)
filterCornerTopLeft.flip(flip_x=True, flip_y=True, transpose=False)
filterCornerTopRight.flip(flip_x=False, flip_y=True, transpose=False)




for X in range(128):
    for Y in range(128):
        pixelCenter = filterCenter.getPixel(x=X, y=Y)

        pixelSideLeft = filterSideLeft.getPixel(x=X, y=Y)
        pixelSideBottom = filterSideBottom.getPixel(x=X, y=Y)
        pixelSideRight = filterSideRight.getPixel(x=X, y=Y)
        pixelSideTop = filterSideTop.getPixel(x=X, y=Y)

        pixelCornerBottomLeft = filterCornerBottomLeft.getPixel(X, Y)
        pixelCornerBottomRight = filterCornerBottomRight.getPixel(X, Y)
        pixelCornerTopLeft = filterCornerTopLeft.getPixel(X, Y)
        pixelCornerTopRight = filterCornerTopRight.getPixel(X, Y)

        totalPixelValue = 255-pixelCenter[0] + 255-pixelSideLeft[0] + 255-pixelSideBottom[0] + 255-pixelSideRight[0] + 255-pixelSideTop[0] + 255-pixelCornerBottomLeft[0] + 255-pixelCornerBottomRight[0] + 255-pixelCornerTopLeft[0] + 255-pixelCornerTopRight[0]
        #totalPixelValue = pixelCenter[0] + pixelSideLeft[0] + pixelSideBottom[0] + pixelSideRight[0] + pixelSideTop[0] + pixelCornerBottomLeft[0] + pixelCornerBottomRight[0] + pixelCornerTopLeft[0] + pixelCornerTopRight[0]
        totalPixelValue = max(totalPixelValue, 1)
        #print(pixelCenter[0])
        #print(sidePixel[0])
        #print(cornerPixel[0])

        #a = int(np.floor(pixelCenter[0] / (totalPixelValue/255)))
        #b = int(np.floor(pixelSideBottom[0] / (totalPixelValue / 255)))
        #c = int(np.floor(pixelCornerBottomRight[0] / (totalPixelValue / 255)))

        a = int(255 - np.floor(255 * (255 - pixelCenter[0]) / (totalPixelValue / 1)))
        b = int(255 - np.floor(255 * (255 - pixelSideBottom[0]) / (totalPixelValue / 1)))
        c = int(255 - np.floor(255 * (255 - pixelCornerBottomRight[0]) / (totalPixelValue / 1)))
        d = int(255 - np.floor(255 * (255 - pixelSideLeft[0]) / (totalPixelValue / 1)))
        e = int(255 - np.floor(255 * (255 - pixelSideRight[0]) / (totalPixelValue / 1)))
        f = int(255 - np.floor(255 * (255 - pixelSideTop[0]) / (totalPixelValue / 1)))
        g = int(255 - np.floor(255 * (255 - pixelCornerBottomLeft[0]) / (totalPixelValue / 1)))
        h = int(255 - np.floor(255 * (255 - pixelCornerTopLeft[0]) / (totalPixelValue / 1)))
        i = int(255 - np.floor(255 * (255 - pixelCornerTopRight[0]) / (totalPixelValue / 1)))

        #a = 255 - a
        #b = 255 - b
        #c = 255 - c

        #print(totalPixelValue)
        #print(pixelCenter[0])
        #print(a)
        #print(b)
        #print(c)
        print(pixelCenter[0])
        print(pixelSideBottom[0])
        print(pixelCornerBottomRight[0])
        print(a + b + c)
        print('-----')
        #filterCenter.setPixel(X, Y, (255*centerPixel[0]/totalPixelValue, 255*centerPixel[0]/totalPixelValue, 255*centerPixel[0]/totalPixelValue), 0)
        #filterCenter.setPixel(X, Y, (10, 70, 10))
        #filterCenter.setPixel(X, Y, (int(np.floor(255 * pixelCenter[0] / totalPixelValue)), int(np.floor(255 * pixelCenter[0] / totalPixelValue)), int(np.floor(255 * pixelCenter[0] / totalPixelValue))))

        filterCenter.setPixel(X, Y, (a, a, a))
        filterSideBottom.setPixel(X, Y, (b, b, b))
        filterSideLeft.setPixel(X, Y, (d, d, d))
        filterSideRight.setPixel(X, Y, (e, e, e))
        filterSideTop.setPixel(X, Y, (f, f, f))
        filterCornerBottomRight.setPixel(X, Y, (c, c, c))
        filterCornerBottomLeft.setPixel(X, Y, (g, g, g))
        filterCornerTopLeft.setPixel(X, Y, (h, h, h))
        filterCornerTopRight.setPixel(X, Y, (i, i, i))
#setXelVal(x: int, y: int, gray: xelval)


filterCenter.write("models/tile_filter_center_normalized.jpg")
filterSideBottom.write("models/tile_filter_side_normalized.jpg")
filterCornerBottomRight.write("models/tile_filter_corner_normalized.jpg")

summedImage = filterCenter + filterSideBottom + filterSideLeft + filterSideRight + filterSideTop + filterCornerBottomLeft + filterCornerBottomRight + filterCornerTopLeft + filterCornerTopRight
summedImage.write("models/tile_filter_normalized_sum.jpg")

