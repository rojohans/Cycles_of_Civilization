
import numpy as np
from panda3d import core as p3d

RESOLUTION = 128
MAXVAL = 255
CENTERWIDTH = 0.6
SIDEWIDTH = (1-CENTERWIDTH)/2
TRANSITIONWIDTH = 0.2


import Noise
noiseCenter = Noise.SimpleNoise(RESOLUTION, numberOfInitialIterationsToSkip=0, amplitudeReduction=1.2)
noiseCenter -= 0.5
noiseVertical = Noise.SimpleNoise(RESOLUTION, numberOfInitialIterationsToSkip=0, amplitudeReduction=1.2)
noiseVertical -= 0.5
noiseHorisontal = Noise.SimpleNoise(RESOLUTION, numberOfInitialIterationsToSkip=0, amplitudeReduction=1.2)
noiseHorisontal -= 0.5
print(np.min(noiseCenter))
print(np.max(noiseCenter))

#
#   The indices of the filters
#  :---------------------------:
#  : \   9   :   8   : 7     / :
#  :   \-------------------/   :
#  : 10 : 19 :   18  : 17 : 6  :
#  :---------------------------:
#  :    :    :       :    :    :
#  : 11 : 12 :   20  : 16 : 5  :
#  :    :    :       :    :    :
#  :---------------------------:
#  : 0  : 13 :   14  : 15 : 4  :
#  :   /-------------------\   :
#  : /    1  :   2   : 3     \ :
#  :---------------------------:
#

filterCenter = p3d.PNMImage(RESOLUTION, RESOLUTION)

filterSideLeft = p3d.PNMImage(RESOLUTION, RESOLUTION)
filterSideBottom = p3d.PNMImage(RESOLUTION, RESOLUTION)
filterSideRight = p3d.PNMImage(RESOLUTION, RESOLUTION)
filterSideTop = p3d.PNMImage(RESOLUTION, RESOLUTION)

filterCornerBottomLeft = p3d.PNMImage(RESOLUTION, RESOLUTION)
filterCornerBottomRight = p3d.PNMImage(RESOLUTION, RESOLUTION)
filterCornerTopLeft = p3d.PNMImage(RESOLUTION, RESOLUTION)
filterCornerTopRight = p3d.PNMImage(RESOLUTION, RESOLUTION)

filterAdjacentSideLeft = p3d.PNMImage(RESOLUTION, RESOLUTION)
filterAdjacentSideBottom = p3d.PNMImage(RESOLUTION, RESOLUTION)
filterAdjacentSideRight = p3d.PNMImage(RESOLUTION, RESOLUTION)
filterAdjacentSideTop = p3d.PNMImage(RESOLUTION, RESOLUTION)

filterAdjacentCornerBottomLeftLeft = p3d.PNMImage(RESOLUTION, RESOLUTION)
filterAdjacentCornerBottomLeftBottom = p3d.PNMImage(RESOLUTION, RESOLUTION)
filterAdjacentCornerBottomRightBottom = p3d.PNMImage(RESOLUTION, RESOLUTION)
filterAdjacentCornerBottomRightRight = p3d.PNMImage(RESOLUTION, RESOLUTION)
filterAdjacentCornerTopRightRight = p3d.PNMImage(RESOLUTION, RESOLUTION)
filterAdjacentCornerTopRightTop = p3d.PNMImage(RESOLUTION, RESOLUTION)
filterAdjacentCornerTopLeftTop = p3d.PNMImage(RESOLUTION, RESOLUTION)
filterAdjacentCornerTopLeftLeft = p3d.PNMImage(RESOLUTION, RESOLUTION)


centerProbability = np.zeros((RESOLUTION, RESOLUTION))

sideLeftProbability = np.zeros((RESOLUTION, RESOLUTION))
sideBottomProbability = np.zeros((RESOLUTION, RESOLUTION))
sideRightProbability = np.zeros((RESOLUTION, RESOLUTION))
sideTopProbability = np.zeros((RESOLUTION, RESOLUTION))

cornerBottomLeftProbability = np.zeros((RESOLUTION, RESOLUTION))
cornerBottomRightProbability = np.zeros((RESOLUTION, RESOLUTION))
cornerTopRightProbability = np.zeros((RESOLUTION, RESOLUTION))
cornerTopLeftProbability = np.zeros((RESOLUTION, RESOLUTION))

borderSideLeftProbability = np.zeros((RESOLUTION, RESOLUTION))
borderSideBottomProbability = np.zeros((RESOLUTION, RESOLUTION))
borderSideRightProbability = np.zeros((RESOLUTION, RESOLUTION))
borderSideTopProbability = np.zeros((RESOLUTION, RESOLUTION))

borderCornerBottomLeftLeftProbability = np.zeros((RESOLUTION, RESOLUTION))
borderCornerBottomLeftBottomProbability = np.zeros((RESOLUTION, RESOLUTION))
borderCornerBottomRightBottomProbability = np.zeros((RESOLUTION, RESOLUTION))
borderCornerBottomRightRightProbability = np.zeros((RESOLUTION, RESOLUTION))
borderCornerTopRightRightProbability = np.zeros((RESOLUTION, RESOLUTION))
borderCornerTopRightTopProbability = np.zeros((RESOLUTION, RESOLUTION))
borderCornerTopLeftTopProbability = np.zeros((RESOLUTION, RESOLUTION))
borderCornerTopLeftLeftProbability = np.zeros((RESOLUTION, RESOLUTION))
if False:
    for y in range(RESOLUTION):
        for x in range(RESOLUTION):

            if x >= RESOLUTION * (SIDEWIDTH + TRANSITIONWIDTH/2) and \
                    x <= RESOLUTION * (SIDEWIDTH + CENTERWIDTH - TRANSITIONWIDTH/2) and \
                    y >= RESOLUTION * (SIDEWIDTH + TRANSITIONWIDTH/2) and \
                    y <= RESOLUTION * (SIDEWIDTH + CENTERWIDTH - TRANSITIONWIDTH/2):
                # Center
                centerProbability[x, y] = 1
            elif x >= RESOLUTION * (SIDEWIDTH - TRANSITIONWIDTH/2) and \
                    x <= RESOLUTION * (SIDEWIDTH + TRANSITIONWIDTH/2) and \
                    y >= RESOLUTION * (SIDEWIDTH + TRANSITIONWIDTH/2) and \
                    y <= RESOLUTION * (SIDEWIDTH + CENTERWIDTH - TRANSITIONWIDTH/2):
                # Left transition
                xContribution = np.sin((np.pi / 2) * (x - RESOLUTION * (SIDEWIDTH - TRANSITIONWIDTH / 2)) / (
                        RESOLUTION * TRANSITIONWIDTH)) ** 2
                centerProbability[x, y] = xContribution
                sideLeftProbability[x, y] = 1-xContribution
            elif x >= RESOLUTION * (SIDEWIDTH + CENTERWIDTH - TRANSITIONWIDTH/2) and \
                    x <= RESOLUTION * (SIDEWIDTH + CENTERWIDTH + TRANSITIONWIDTH/2) and \
                    y >= RESOLUTION * (SIDEWIDTH + TRANSITIONWIDTH/2) and \
                    y <= RESOLUTION * (SIDEWIDTH + CENTERWIDTH - TRANSITIONWIDTH/2):
                # Right transition
                xContribution = np.sin((np.pi/2) + (np.pi / 2) * (x - RESOLUTION * (SIDEWIDTH + CENTERWIDTH - TRANSITIONWIDTH / 2)) / (
                        RESOLUTION * TRANSITIONWIDTH)) ** 2
                centerProbability[x, y] = xContribution
                sideRightProbability[x, y] = 1-xContribution
            elif x >= RESOLUTION * (SIDEWIDTH + TRANSITIONWIDTH/2) and \
                    x <= RESOLUTION * (SIDEWIDTH + CENTERWIDTH - TRANSITIONWIDTH/2) and \
                    y >= RESOLUTION * (SIDEWIDTH - TRANSITIONWIDTH/2) and \
                    y <= RESOLUTION * (SIDEWIDTH + TRANSITIONWIDTH/2):
                # Top transition
                yContribution = np.sin((np.pi / 2) * (y - RESOLUTION * (SIDEWIDTH - TRANSITIONWIDTH / 2)) / (RESOLUTION * TRANSITIONWIDTH)) ** 2
                centerProbability[x, y] = yContribution
                sideTopProbability[x, y] = 1-yContribution
            elif x >= RESOLUTION * (SIDEWIDTH + TRANSITIONWIDTH/2) and \
                    x <= RESOLUTION * (SIDEWIDTH + CENTERWIDTH - TRANSITIONWIDTH/2) and \
                    y >= RESOLUTION * (SIDEWIDTH + CENTERWIDTH - TRANSITIONWIDTH/2) and \
                    y <= RESOLUTION * (SIDEWIDTH + CENTERWIDTH + TRANSITIONWIDTH/2):
                # Bottom transition
                yContribution = np.cos((np.pi / 2) * (y - RESOLUTION * (SIDEWIDTH + CENTERWIDTH - TRANSITIONWIDTH / 2)) / (RESOLUTION * TRANSITIONWIDTH)) ** 2
                centerProbability[x, y] = yContribution
                sideBottomProbability[x, y] = 1-yContribution
            elif x >= RESOLUTION * (SIDEWIDTH - TRANSITIONWIDTH/2) and \
                    x <= RESOLUTION * (SIDEWIDTH + TRANSITIONWIDTH/2) and \
                    y >= RESOLUTION * (SIDEWIDTH + CENTERWIDTH - TRANSITIONWIDTH/2) and \
                    y <= RESOLUTION * (SIDEWIDTH + CENTERWIDTH + TRANSITIONWIDTH/2):
                # Bottom Left transition
                xContribution = np.sin((np.pi / 2) * (x - RESOLUTION * (SIDEWIDTH - TRANSITIONWIDTH / 2)) / (
                            RESOLUTION * TRANSITIONWIDTH)) ** 2
                yContribution = np.cos((np.pi / 2) * (y - RESOLUTION * (SIDEWIDTH + CENTERWIDTH - TRANSITIONWIDTH / 2)) / (
                            RESOLUTION * TRANSITIONWIDTH)) ** 2
                centerProbability[x, y] = xContribution * yContribution
                sideLeftProbability[x, y] = (1-xContribution) * yContribution
                sideBottomProbability[x, y] = xContribution * (1-yContribution)
                cornerBottomLeftProbability[x, y] = (1-xContribution) * (1-yContribution)
            elif x >= RESOLUTION * (SIDEWIDTH + CENTERWIDTH - TRANSITIONWIDTH / 2) and \
                 x <= RESOLUTION * (SIDEWIDTH + CENTERWIDTH + TRANSITIONWIDTH / 2) and \
                 y >= RESOLUTION * (SIDEWIDTH + CENTERWIDTH - TRANSITIONWIDTH / 2) and \
                 y <= RESOLUTION * (SIDEWIDTH + CENTERWIDTH + TRANSITIONWIDTH / 2):
                # Bottom Right transition
                xContribution = np.cos((np.pi / 2) * (x - RESOLUTION * (SIDEWIDTH + CENTERWIDTH - TRANSITIONWIDTH / 2)) / (
                        RESOLUTION * TRANSITIONWIDTH)) ** 2
                yContribution = np.cos((np.pi / 2) * (y - RESOLUTION * (SIDEWIDTH + CENTERWIDTH - TRANSITIONWIDTH / 2)) / (
                        RESOLUTION * TRANSITIONWIDTH)) ** 2
                centerProbability[x, y] = xContribution * yContribution
                sideBottomProbability[x, y] = xContribution * (1-yContribution)
                sideRightProbability[x, y] = (1-xContribution) * yContribution
                cornerBottomRightProbability[x, y] = (1-xContribution) * (1-yContribution)
            elif x >= RESOLUTION * (SIDEWIDTH + CENTERWIDTH - TRANSITIONWIDTH / 2) and \
                 x <= RESOLUTION * (SIDEWIDTH + CENTERWIDTH + TRANSITIONWIDTH / 2) and \
                 y >= RESOLUTION * (SIDEWIDTH - TRANSITIONWIDTH / 2) and \
                 y <= RESOLUTION * (SIDEWIDTH + TRANSITIONWIDTH / 2):
                # Top Right transition
                xContribution = np.cos((np.pi / 2) * (x - RESOLUTION * (SIDEWIDTH + CENTERWIDTH - TRANSITIONWIDTH / 2)) / (
                        RESOLUTION * TRANSITIONWIDTH)) ** 2
                yContribution = np.sin((np.pi / 2) * (y - RESOLUTION * (SIDEWIDTH - TRANSITIONWIDTH / 2)) / (
                        RESOLUTION * TRANSITIONWIDTH)) ** 2
                centerProbability[x, y] = xContribution * yContribution
                sideRightProbability[x, y] = (1-xContribution) * yContribution
                sideTopProbability[x, y] = xContribution * (1-yContribution)
                cornerTopRightProbability[x, y] = (1-xContribution) * (1-yContribution)
            elif x >= RESOLUTION * (SIDEWIDTH - TRANSITIONWIDTH/2) and \
                    x <= RESOLUTION * (SIDEWIDTH + TRANSITIONWIDTH/2) and \
                    y >= RESOLUTION * (SIDEWIDTH - TRANSITIONWIDTH/2) and \
                    y <= RESOLUTION * (SIDEWIDTH + TRANSITIONWIDTH/2):
                # Top Left transition
                xContribution = np.sin((np.pi / 2) * (x - RESOLUTION * (SIDEWIDTH - TRANSITIONWIDTH / 2)) / (
                            RESOLUTION * TRANSITIONWIDTH)) ** 2
                yContribution = np.sin((np.pi / 2) * (y - RESOLUTION * (SIDEWIDTH - TRANSITIONWIDTH / 2)) / (
                            RESOLUTION * TRANSITIONWIDTH)) ** 2
                centerProbability[x, y] = xContribution * yContribution
                sideLeftProbability[x, y] = (1-xContribution) * yContribution
                sideTopProbability[x, y] = xContribution * (1-yContribution)
                cornerTopLeftProbability[x, y] = (1-xContribution) * (1-yContribution)
            elif x >= RESOLUTION * (TRANSITIONWIDTH/2) and \
                    x <= RESOLUTION * (SIDEWIDTH - TRANSITIONWIDTH/2) and \
                    y >= RESOLUTION * (SIDEWIDTH + TRANSITIONWIDTH/2) and \
                    y <= RESOLUTION * (SIDEWIDTH + CENTERWIDTH - TRANSITIONWIDTH/2):
                # Left center
                sideLeftProbability[x, y] = 1
            elif x >= RESOLUTION * (SIDEWIDTH + CENTERWIDTH - TRANSITIONWIDTH / 2) and \
                 x <= RESOLUTION * (1 - TRANSITIONWIDTH / 2) and \
                 y >= RESOLUTION * (SIDEWIDTH + TRANSITIONWIDTH / 2) and \
                 y <= RESOLUTION * (SIDEWIDTH + CENTERWIDTH - TRANSITIONWIDTH / 2):
                # Right center
                sideRightProbability[x, y] = 1
            elif x >= RESOLUTION * (SIDEWIDTH + TRANSITIONWIDTH / 2) and \
                 x <= RESOLUTION * (SIDEWIDTH + CENTERWIDTH - TRANSITIONWIDTH / 2) and \
                 y >= RESOLUTION * (SIDEWIDTH + CENTERWIDTH - TRANSITIONWIDTH / 2) and \
                 y <= RESOLUTION * (1 - TRANSITIONWIDTH / 2):
                # Bottom center
                sideBottomProbability[x, y] = 1
            elif x >= RESOLUTION * (SIDEWIDTH + TRANSITIONWIDTH / 2) and \
                 x <= RESOLUTION * (SIDEWIDTH + CENTERWIDTH - TRANSITIONWIDTH / 2) and \
                 y >= RESOLUTION * (TRANSITIONWIDTH / 2) and \
                 y <= RESOLUTION * (SIDEWIDTH - TRANSITIONWIDTH / 2):
                # Top center
                sideTopProbability[x, y] = 1
            elif x >= RESOLUTION * (TRANSITIONWIDTH / 2) and \
                 x <= RESOLUTION * (SIDEWIDTH - TRANSITIONWIDTH / 2) and \
                 y >= RESOLUTION * (SIDEWIDTH + CENTERWIDTH + TRANSITIONWIDTH / 2) and \
                 y <= RESOLUTION * (1 - TRANSITIONWIDTH / 2):
                # Bottom Left Center
                cornerBottomLeftProbability[x, y] = 1
            elif x >= RESOLUTION * (SIDEWIDTH + CENTERWIDTH + TRANSITIONWIDTH / 2) and \
                 x <= RESOLUTION * (1 - TRANSITIONWIDTH / 2) and \
                 y >= RESOLUTION * (SIDEWIDTH + CENTERWIDTH + TRANSITIONWIDTH / 2) and \
                 y <= RESOLUTION * (1 - TRANSITIONWIDTH / 2):
                # Bottom Right Center
                cornerBottomRightProbability[x, y] = 1
            elif x >= RESOLUTION * (SIDEWIDTH + CENTERWIDTH + TRANSITIONWIDTH / 2) and \
                 x <= RESOLUTION * (1 - TRANSITIONWIDTH / 2) and \
                 y >= RESOLUTION * (TRANSITIONWIDTH / 2) and \
                 y <= RESOLUTION * (SIDEWIDTH - TRANSITIONWIDTH / 2):
                # Top Right Center
                cornerTopRightProbability[x, y] = 1
            elif x >= RESOLUTION * (TRANSITIONWIDTH / 2) and \
                 x <= RESOLUTION * (SIDEWIDTH - TRANSITIONWIDTH / 2) and \
                 y >= RESOLUTION * (TRANSITIONWIDTH / 2) and \
                 y <= RESOLUTION * (SIDEWIDTH - TRANSITIONWIDTH / 2):
                # Top Left Center
                cornerTopLeftProbability[x, y] = 1

            elif x >= RESOLUTION * (SIDEWIDTH - TRANSITIONWIDTH / 2) and \
                 x <= RESOLUTION * (SIDEWIDTH + TRANSITIONWIDTH / 2) and \
                 y >= RESOLUTION * (SIDEWIDTH + CENTERWIDTH + TRANSITIONWIDTH / 2) and \
                 y <= RESOLUTION * (1 - TRANSITIONWIDTH / 2):
                xContribution = np.sin((np.pi / 2) * (x - RESOLUTION * (SIDEWIDTH - TRANSITIONWIDTH / 2)) / (
                            RESOLUTION * TRANSITIONWIDTH)) ** 2
                cornerBottomLeftProbability[x, y] = 1-xContribution
                sideBottomProbability[x, y] = xContribution
            elif x >= RESOLUTION * (SIDEWIDTH + CENTERWIDTH - TRANSITIONWIDTH / 2) and \
                 x <= RESOLUTION * (SIDEWIDTH + CENTERWIDTH + TRANSITIONWIDTH / 2) and \
                 y >= RESOLUTION * (SIDEWIDTH + CENTERWIDTH + TRANSITIONWIDTH / 2) and \
                 y <= RESOLUTION * (1 - TRANSITIONWIDTH / 2):
                xContribution = np.cos((np.pi / 2) * (x - RESOLUTION * (SIDEWIDTH + CENTERWIDTH - TRANSITIONWIDTH / 2)) / (
                        RESOLUTION * TRANSITIONWIDTH)) ** 2
                cornerBottomRightProbability[x, y] = 1-xContribution
                sideBottomProbability[x, y] = xContribution
            elif x >= RESOLUTION * (SIDEWIDTH + CENTERWIDTH - TRANSITIONWIDTH / 2) and \
                 x <= RESOLUTION * (SIDEWIDTH + CENTERWIDTH + TRANSITIONWIDTH / 2) and \
                 y >= RESOLUTION * (TRANSITIONWIDTH / 2) and \
                 y <= RESOLUTION * (SIDEWIDTH - TRANSITIONWIDTH / 2):
                xContribution = np.cos((np.pi / 2) * (x - RESOLUTION * (SIDEWIDTH + CENTERWIDTH - TRANSITIONWIDTH / 2)) / (
                        RESOLUTION * TRANSITIONWIDTH)) ** 2
                cornerTopRightProbability[x, y] = 1-xContribution
                sideTopProbability[x, y] = xContribution
            elif x >= RESOLUTION * (SIDEWIDTH - TRANSITIONWIDTH / 2) and \
                 x <= RESOLUTION * (SIDEWIDTH + TRANSITIONWIDTH / 2) and \
                 y >= RESOLUTION * (TRANSITIONWIDTH / 2) and \
                 y <= RESOLUTION * (SIDEWIDTH - TRANSITIONWIDTH / 2):
                xContribution = np.sin((np.pi / 2) * (x - RESOLUTION * (SIDEWIDTH - TRANSITIONWIDTH / 2)) / (
                        RESOLUTION * TRANSITIONWIDTH)) ** 2
                cornerTopLeftProbability[x, y] = 1-xContribution
                sideTopProbability[x, y] = xContribution

            elif x >= RESOLUTION * (TRANSITIONWIDTH / 2) and \
                 x <= RESOLUTION * (SIDEWIDTH - TRANSITIONWIDTH / 2) and \
                 y >= RESOLUTION * (SIDEWIDTH - TRANSITIONWIDTH / 2) and \
                 y <= RESOLUTION * (SIDEWIDTH + TRANSITIONWIDTH / 2):
                yContribution = np.sin((np.pi / 2) * (y - RESOLUTION * (SIDEWIDTH - TRANSITIONWIDTH / 2)) / (
                        RESOLUTION * TRANSITIONWIDTH)) ** 2
                cornerTopLeftProbability[x, y] = 1-yContribution
                sideLeftProbability[x, y] = yContribution
            elif x >= RESOLUTION * (TRANSITIONWIDTH / 2) and \
                 x <= RESOLUTION * (SIDEWIDTH - TRANSITIONWIDTH / 2) and \
                 y >= RESOLUTION * (SIDEWIDTH + CENTERWIDTH - TRANSITIONWIDTH / 2) and \
                 y <= RESOLUTION * (SIDEWIDTH + CENTERWIDTH + TRANSITIONWIDTH / 2):
                yContribution = np.cos((np.pi / 2) * (y - RESOLUTION * (SIDEWIDTH + CENTERWIDTH - TRANSITIONWIDTH / 2)) / (
                        RESOLUTION * TRANSITIONWIDTH)) ** 2
                cornerBottomLeftProbability[x, y] = 1-yContribution
                sideLeftProbability[x, y] = yContribution
            elif x >= RESOLUTION * (SIDEWIDTH + CENTERWIDTH + TRANSITIONWIDTH / 2) and \
                 x <= RESOLUTION * (1 - TRANSITIONWIDTH / 2) and \
                 y >= RESOLUTION * (SIDEWIDTH + CENTERWIDTH - TRANSITIONWIDTH / 2) and \
                 y <= RESOLUTION * (SIDEWIDTH + CENTERWIDTH + TRANSITIONWIDTH / 2):
                yContribution = np.cos((np.pi / 2) * (y - RESOLUTION * (SIDEWIDTH + CENTERWIDTH - TRANSITIONWIDTH / 2)) / (
                        RESOLUTION * TRANSITIONWIDTH)) ** 2
                cornerBottomRightProbability[x, y] = 1-yContribution
                sideRightProbability[x, y] = yContribution
            elif x >= RESOLUTION * (SIDEWIDTH + CENTERWIDTH + TRANSITIONWIDTH / 2) and \
                 x <= RESOLUTION * (1 - TRANSITIONWIDTH / 2) and \
                 y >= RESOLUTION * (SIDEWIDTH - TRANSITIONWIDTH / 2) and \
                 y <= RESOLUTION * (SIDEWIDTH + TRANSITIONWIDTH / 2):
                yContribution = np.sin((np.pi / 2) * (y - RESOLUTION * (SIDEWIDTH - TRANSITIONWIDTH / 2)) / (
                        RESOLUTION * TRANSITIONWIDTH)) ** 2
                cornerTopRightProbability[x, y] = 1-yContribution
                sideRightProbability[x, y] = yContribution

            elif x >= RESOLUTION * (0) and \
                 x <= RESOLUTION * (TRANSITIONWIDTH/2) and \
                 y >= RESOLUTION * (SIDEWIDTH + TRANSITIONWIDTH / 2) and \
                 y <= RESOLUTION * (SIDEWIDTH + CENTERWIDTH - TRANSITIONWIDTH / 2):
                # Left Border
                xContribution = np.sin((np.pi / 2) * (x) / (RESOLUTION * TRANSITIONWIDTH/2)) ** 1
                borderSideLeftProbability[x, y] = 0.5 - 0.5*xContribution
                sideLeftProbability[x, y] = 0.5+0.5*xContribution
            elif x >= RESOLUTION * (1-TRANSITIONWIDTH/2) and \
                 x <= RESOLUTION * (1) and \
                 y >= RESOLUTION * (SIDEWIDTH + TRANSITIONWIDTH / 2) and \
                 y <= RESOLUTION * (SIDEWIDTH + CENTERWIDTH - TRANSITIONWIDTH / 2):
                # Right Border
                xContribution = np.cos((np.pi / 2) * (x - RESOLUTION * (1-TRANSITIONWIDTH/2)) / (RESOLUTION * TRANSITIONWIDTH/2)) ** 1
                borderSideRightProbability[x, y] = 0.5 - 0.5*xContribution
                sideRightProbability[x, y] = 0.5+0.5*xContribution
            elif x >= RESOLUTION * (SIDEWIDTH + TRANSITIONWIDTH/2) and \
                 x <= RESOLUTION * (SIDEWIDTH + CENTERWIDTH - TRANSITIONWIDTH/2) and \
                 y >= RESOLUTION * (1-TRANSITIONWIDTH / 2) and \
                 y <= RESOLUTION * (1):
                # Bottom Border
                yContribution = np.cos((np.pi / 2) * (y - RESOLUTION * (1 - TRANSITIONWIDTH / 2)) / (RESOLUTION * TRANSITIONWIDTH/2)) ** 1
                borderSideBottomProbability[x, y] = 0.5 - 0.5*yContribution
                sideBottomProbability[x, y] = 0.5+0.5*yContribution
            elif x >= RESOLUTION * (SIDEWIDTH + TRANSITIONWIDTH/2) and \
                 x <= RESOLUTION * (SIDEWIDTH + CENTERWIDTH - TRANSITIONWIDTH/2) and \
                 y >= RESOLUTION * (0) and \
                 y <= RESOLUTION * (TRANSITIONWIDTH/2):
                # top Border
                yContribution = np.sin((np.pi / 2) * (y) / (RESOLUTION * TRANSITIONWIDTH/2)) ** 1
                borderSideTopProbability[x, y] = 0.5 - 0.5*yContribution
                sideTopProbability[x, y] = 0.5+0.5*yContribution

            elif x >= RESOLUTION * (0) and \
                 x <= RESOLUTION * (TRANSITIONWIDTH/2) and \
                 y >= RESOLUTION * (SIDEWIDTH + CENTERWIDTH + TRANSITIONWIDTH/2) and \
                 y <= RESOLUTION * (1 - TRANSITIONWIDTH/2):
                # Bottom left border
                xContribution = np.sin((np.pi / 2) * (x) / (RESOLUTION * TRANSITIONWIDTH / 2)) ** 1
                borderCornerBottomLeftLeftProbability[x, y] = 0.5 - 0.5*xContribution
                cornerBottomLeftProbability[x, y] = 0.5+0.5*xContribution
            elif x >= RESOLUTION * (TRANSITIONWIDTH/2) and \
                 x <= RESOLUTION * (SIDEWIDTH - TRANSITIONWIDTH/2) and \
                 y >= RESOLUTION * (1 - TRANSITIONWIDTH/2) and \
                 y <= RESOLUTION * (1):
                # Bottom left border
                yContribution = np.cos((np.pi / 2) * (y - RESOLUTION * (1-TRANSITIONWIDTH/2)) / (RESOLUTION * TRANSITIONWIDTH / 2)) ** 1
                borderCornerBottomLeftBottomProbability[x, y] = 0.5 - 0.5*yContribution
                cornerBottomLeftProbability[x, y] = 0.5+0.5*yContribution
            elif x >= RESOLUTION * (0) and \
                 x <= RESOLUTION * (TRANSITIONWIDTH/2) and \
                 y >= RESOLUTION * (1 - TRANSITIONWIDTH/2) and \
                 y <= RESOLUTION * (1):
                # Bottom left border
                xContribution = np.sin((np.pi / 2) * (x) / (RESOLUTION * TRANSITIONWIDTH / 2)) ** 1
                yContribution = np.cos((np.pi / 2) * (y - RESOLUTION * (1-TRANSITIONWIDTH/2)) / (RESOLUTION * TRANSITIONWIDTH / 2)) ** 1
                borderCornerBottomLeftLeftProbability[x, y] = (0.5 + 0.5 * yContribution) * (0.5 - 0.5 * xContribution)
                borderCornerBottomLeftBottomProbability[x, y] = (0.5 - 0.5*yContribution) * (0.5+0.5*xContribution)
                cornerBottomLeftProbability[x, y] = (0.5+0.5*yContribution) * (0.5+0.5*xContribution)
            elif x >= RESOLUTION * (0) and \
                 x <= RESOLUTION * (TRANSITIONWIDTH/2) and \
                 y >= RESOLUTION * (SIDEWIDTH + CENTERWIDTH - TRANSITIONWIDTH/2) and \
                 y <= RESOLUTION * (SIDEWIDTH + CENTERWIDTH + TRANSITIONWIDTH/2):
                # Bottom left border
                xContribution = np.sin((np.pi / 2) * (x) / (RESOLUTION * TRANSITIONWIDTH / 2)) ** 1
                yContribution = np.sin((np.pi / 2) * (y - RESOLUTION * (SIDEWIDTH + CENTERWIDTH - TRANSITIONWIDTH / 2)) / (
                        RESOLUTION * TRANSITIONWIDTH)) ** 2
                borderSideLeftProbability[x, y] = (1-yContribution) * (0.5-0.5*xContribution)
                borderCornerBottomLeftLeftProbability[x, y] = yContribution * (0.5-0.5*xContribution)
                cornerBottomLeftProbability[x, y] = yContribution * (0.5+0.5*xContribution)
                sideLeftProbability[x, y] = (1-yContribution) * (0.5+0.5*xContribution)
            elif x >= RESOLUTION * (SIDEWIDTH - TRANSITIONWIDTH/2) and \
                 x <= RESOLUTION * (SIDEWIDTH + TRANSITIONWIDTH/2) and \
                 y >= RESOLUTION * (1-TRANSITIONWIDTH/2) and \
                 y <= RESOLUTION * (1):
                # Bottom left border
                xContribution = np.cos((np.pi / 2) * (x - RESOLUTION * (SIDEWIDTH - TRANSITIONWIDTH / 2)) / (
                        RESOLUTION * TRANSITIONWIDTH)) ** 2
                yContribution = np.cos((np.pi / 2) * (y - RESOLUTION * (1-TRANSITIONWIDTH/2)) / (RESOLUTION * TRANSITIONWIDTH / 2)) ** 1

                borderSideBottomProbability[x, y] = (1-xContribution) * (0.5-0.5*yContribution)
                borderCornerBottomLeftBottomProbability[x, y] = xContribution * (0.5-0.5*yContribution)
                cornerBottomLeftProbability[x, y] = xContribution * (0.5+0.5*yContribution)
                sideBottomProbability[x, y] = (1-xContribution) * (0.5+0.5*yContribution)



            elif x >= RESOLUTION * (1-TRANSITIONWIDTH/2) and \
                 x <= RESOLUTION * (1) and \
                 y >= RESOLUTION * (SIDEWIDTH + CENTERWIDTH + TRANSITIONWIDTH/2) and \
                 y <= RESOLUTION * (1 - TRANSITIONWIDTH/2):
                # Bottom Right border
                xContribution = np.cos(
                    (np.pi / 2) * (x - RESOLUTION * (1-TRANSITIONWIDTH/2)) / (RESOLUTION * TRANSITIONWIDTH / 2)) ** 1
                borderCornerBottomRightRightProbability[x, y] = 0.5 - 0.5*xContribution
                cornerBottomRightProbability[x, y] = 0.5+0.5*xContribution
            elif x >= RESOLUTION * (SIDEWIDTH + CENTERWIDTH + TRANSITIONWIDTH/2) and \
                 x <= RESOLUTION * (1-TRANSITIONWIDTH/2) and \
                 y >= RESOLUTION * (1- TRANSITIONWIDTH/2) and \
                 y <= RESOLUTION * (1):
                # Bottom Right border
                yContribution = np.cos((np.pi / 2) * (y - RESOLUTION * (1-TRANSITIONWIDTH/2)) / (RESOLUTION * TRANSITIONWIDTH / 2)) ** 1
                borderCornerBottomRightBottomProbability[x, y] = 0.5 - 0.5*yContribution
                cornerBottomRightProbability[x, y] = 0.5+0.5*yContribution
            elif x >= RESOLUTION * (1 - TRANSITIONWIDTH/2) and \
                 x <= RESOLUTION * (1) and \
                 y >= RESOLUTION * (1- TRANSITIONWIDTH/2) and \
                 y <= RESOLUTION * (1):
                # Bottom Right border
                xContribution = np.cos((np.pi / 2) * (x - RESOLUTION * (1 - TRANSITIONWIDTH / 2)) / (RESOLUTION * TRANSITIONWIDTH / 2)) ** 1
                yContribution = np.cos((np.pi / 2) * (y - RESOLUTION * (1 - TRANSITIONWIDTH / 2)) / (RESOLUTION * TRANSITIONWIDTH / 2)) ** 1
                borderCornerBottomRightBottomProbability[x, y] = (0.5+0.5*xContribution)*(0.5-0.5*yContribution)
                borderCornerBottomRightRightProbability[x, y] = (0.5-0.5*xContribution)*(0.5+0.5*yContribution)
                cornerBottomRightProbability[x, y] = (0.5+0.5*xContribution)*(0.5+0.5*yContribution)
            elif x >= RESOLUTION * (SIDEWIDTH + CENTERWIDTH - TRANSITIONWIDTH/2) and \
                 x <= RESOLUTION * (SIDEWIDTH + CENTERWIDTH + TRANSITIONWIDTH/2) and \
                 y >= RESOLUTION * (1- TRANSITIONWIDTH/2) and \
                 y <= RESOLUTION * (1):
                # Bottom Right border
                xContribution = np.sin((np.pi / 2) * (x - RESOLUTION * (SIDEWIDTH + CENTERWIDTH - TRANSITIONWIDTH / 2)) / (RESOLUTION * TRANSITIONWIDTH)) ** 2
                yContribution = np.cos((np.pi / 2) * (y - RESOLUTION * (1 - TRANSITIONWIDTH / 2)) / (RESOLUTION * TRANSITIONWIDTH / 2)) ** 1
                cornerBottomRightProbability[x, y] = xContribution*(0.5+0.5*yContribution)
                sideBottomProbability[x, y] = (1-xContribution)*(0.5+0.5*yContribution)
                borderCornerBottomRightBottomProbability[x, y] = xContribution*(0.5-0.5*yContribution)
                borderSideBottomProbability[x, y] = (1-xContribution)*(0.5-0.5*yContribution)
            elif x >= RESOLUTION * (1 - TRANSITIONWIDTH/2) and \
                 x <= RESOLUTION * (1) and \
                 y >= RESOLUTION * (SIDEWIDTH + CENTERWIDTH - TRANSITIONWIDTH/2) and \
                 y <= RESOLUTION * (SIDEWIDTH + CENTERWIDTH + TRANSITIONWIDTH/2):
                # Bottom Right border
                xContribution = np.cos((np.pi / 2) * (x - RESOLUTION * (1 - TRANSITIONWIDTH / 2)) / (RESOLUTION * TRANSITIONWIDTH/2)) ** 1
                yContribution = np.sin((np.pi / 2) * (y - RESOLUTION * (SIDEWIDTH + CENTERWIDTH - TRANSITIONWIDTH / 2)) / (RESOLUTION * TRANSITIONWIDTH)) ** 2
                cornerBottomRightProbability[x, y] = yContribution*(0.5+0.5*xContribution)
                sideRightProbability[x, y] = (1-yContribution)*(0.5+0.5*xContribution)
                borderCornerBottomRightRightProbability[x, y] = yContribution*(0.5-0.5*xContribution)
                borderSideRightProbability[x, y] = (1-yContribution)*(0.5-0.5*xContribution)

            elif x >= RESOLUTION * (1-TRANSITIONWIDTH/2) and \
                 x <= RESOLUTION * (1) and \
                 y >= RESOLUTION * (TRANSITIONWIDTH/2) and \
                 y <= RESOLUTION * (SIDEWIDTH - TRANSITIONWIDTH/2):
                # Top Right border
                xContribution = np.cos(
                    (np.pi / 2) * (x - RESOLUTION * (1-TRANSITIONWIDTH/2)) / (RESOLUTION * TRANSITIONWIDTH / 2)) ** 1
                borderCornerTopRightRightProbability[x, y] = 0.5 - 0.5*xContribution
                cornerTopRightProbability[x, y] = 0.5+0.5*xContribution
            elif x >= RESOLUTION * (SIDEWIDTH + CENTERWIDTH + TRANSITIONWIDTH/2) and \
                 x <= RESOLUTION * (1-TRANSITIONWIDTH/2) and \
                 y >= RESOLUTION * (0) and \
                 y <= RESOLUTION * (TRANSITIONWIDTH/2):
                # Top Right border
                yContribution = np.sin(
                    (np.pi / 2) * (y) / (RESOLUTION * TRANSITIONWIDTH / 2)) ** 1
                borderCornerTopRightTopProbability[x, y] = 0.5 - 0.5*yContribution
                cornerTopRightProbability[x, y] = 0.5+0.5*yContribution
            elif x >= RESOLUTION * (1 - TRANSITIONWIDTH/2) and \
                 x <= RESOLUTION * (1) and \
                 y >= RESOLUTION * (0) and \
                 y <= RESOLUTION * (TRANSITIONWIDTH/2):
                # Top Right border
                xContribution = np.cos((np.pi / 2) * (x - RESOLUTION * (1 - TRANSITIONWIDTH / 2)) / (RESOLUTION * TRANSITIONWIDTH / 2)) ** 1
                yContribution = np.sin((np.pi / 2) * (y) / (RESOLUTION * TRANSITIONWIDTH / 2)) ** 1
                borderCornerTopRightTopProbability[x, y] = (0.5+0.5*xContribution) * (0.5-0.5*yContribution)
                borderCornerTopRightRightProbability[x, y] = (0.5-0.5*xContribution) * (0.5+0.5*yContribution)
                cornerTopRightProbability[x, y] = (0.5+0.5*xContribution) * (0.5+0.5*yContribution)
            elif x >= RESOLUTION * (1 - TRANSITIONWIDTH/2) and \
                 x <= RESOLUTION * (1) and \
                 y >= RESOLUTION * (SIDEWIDTH - TRANSITIONWIDTH/2) and \
                 y <= RESOLUTION * (SIDEWIDTH + TRANSITIONWIDTH/2):
                # Top Right border
                xContribution = np.cos((np.pi / 2) * (x - RESOLUTION * (1 - TRANSITIONWIDTH / 2)) / (RESOLUTION * TRANSITIONWIDTH / 2)) ** 1
                yContribution = np.cos((np.pi / 2) * (y - RESOLUTION * (SIDEWIDTH - TRANSITIONWIDTH/2)) / (RESOLUTION * TRANSITIONWIDTH)) ** 2
                cornerTopRightProbability[x, y] = (0.5+0.5*xContribution) * yContribution
                sideRightProbability[x, y] = (0.5 + 0.5 * xContribution) * (1-yContribution)
                borderCornerTopRightRightProbability[x, y] = (0.5 - 0.5 * xContribution) * yContribution
                borderSideRightProbability[x, y] = (0.5 - 0.5 * xContribution) * (1-yContribution)
            elif x >= RESOLUTION * (SIDEWIDTH + CENTERWIDTH - TRANSITIONWIDTH/2) and \
                 x <= RESOLUTION * (SIDEWIDTH + CENTERWIDTH + TRANSITIONWIDTH/2) and \
                 y >= RESOLUTION * (0) and \
                 y <= RESOLUTION * (TRANSITIONWIDTH/2):
                # Top Right border
                xContribution = np.sin((np.pi / 2) * (x - RESOLUTION * (SIDEWIDTH + CENTERWIDTH - TRANSITIONWIDTH / 2)) / (RESOLUTION * TRANSITIONWIDTH)) ** 2
                yContribution = np.sin((np.pi / 2) * (y) / (RESOLUTION * TRANSITIONWIDTH/2)) ** 1
                cornerTopRightProbability[x, y] = (0.5+0.5*yContribution) * xContribution
                sideTopProbability[x, y] = (0.5 + 0.5 * yContribution) * (1-xContribution)
                borderSideTopProbability[x, y] = (0.5 - 0.5 * yContribution) * (1-xContribution)
                borderCornerTopRightTopProbability[x, y] = (0.5 - 0.5 * yContribution) * xContribution

            elif x >= RESOLUTION * (0) and \
                 x <= RESOLUTION * (TRANSITIONWIDTH/2) and \
                 y >= RESOLUTION * (TRANSITIONWIDTH/2) and \
                 y <= RESOLUTION * (SIDEWIDTH - TRANSITIONWIDTH/2):
                # Top left border
                xContribution = np.sin((np.pi / 2) * (x) / (RESOLUTION * TRANSITIONWIDTH / 2)) ** 1
                borderCornerTopLeftLeftProbability[x, y] = 0.5 - 0.5*xContribution
                cornerTopLeftProbability[x, y] = 0.5+0.5*xContribution
            elif x >= RESOLUTION * (TRANSITIONWIDTH/2) and \
                 x <= RESOLUTION * (SIDEWIDTH - TRANSITIONWIDTH/2) and \
                 y >= RESOLUTION * (0) and \
                 y <= RESOLUTION * (TRANSITIONWIDTH/2):
                # Top left border
                yContribution = np.sin((np.pi / 2) * (y) / (RESOLUTION * TRANSITIONWIDTH / 2)) ** 1
                borderCornerTopLeftTopProbability[x, y] = 0.5 - 0.5*yContribution
                cornerTopLeftProbability[x, y] = 0.5+0.5*yContribution
            elif x >= RESOLUTION * (0) and \
                 x <= RESOLUTION * (TRANSITIONWIDTH/2) and \
                 y >= RESOLUTION * (0) and \
                 y <= RESOLUTION * (TRANSITIONWIDTH/2):
                # Top left border
                xContribution = np.sin((np.pi / 2) * (x) / (RESOLUTION * TRANSITIONWIDTH / 2)) ** 1
                yContribution = np.sin((np.pi / 2) * (y) / (RESOLUTION * TRANSITIONWIDTH / 2)) ** 1
                borderCornerTopLeftTopProbability[x, y] = (0.5+0.5*xContribution) * (0.5-0.5*yContribution)
                borderCornerTopLeftLeftProbability[x, y] = (0.5-0.5*xContribution) * (0.5+0.5*yContribution)
                cornerTopLeftProbability[x, y] = (0.5+0.5*xContribution) * (0.5+0.5*yContribution)
            elif x >= RESOLUTION * (SIDEWIDTH - TRANSITIONWIDTH/2) and \
                 x <= RESOLUTION * (SIDEWIDTH + TRANSITIONWIDTH/2) and \
                 y >= RESOLUTION * (0) and \
                 y <= RESOLUTION * (TRANSITIONWIDTH/2):
                # Top Left border
                xContribution = np.cos((np.pi / 2) * (x - RESOLUTION * (SIDEWIDTH - TRANSITIONWIDTH / 2)) / (RESOLUTION * TRANSITIONWIDTH)) ** 2
                yContribution = np.sin((np.pi / 2) * (y) / (RESOLUTION * TRANSITIONWIDTH/2)) ** 1
                cornerTopLeftProbability[x, y] = (0.5+0.5*yContribution) * xContribution
                sideTopProbability[x, y] = (0.5 + 0.5 * yContribution) * (1-xContribution)
                borderSideTopProbability[x, y] = (0.5 - 0.5 * yContribution) * (1-xContribution)
                borderCornerTopLeftTopProbability[x, y] = (0.5 - 0.5 * yContribution) * xContribution
            elif x >= RESOLUTION * (0) and \
                 x <= RESOLUTION * (TRANSITIONWIDTH/2) and \
                 y >= RESOLUTION * (SIDEWIDTH - TRANSITIONWIDTH/2) and \
                 y <= RESOLUTION * (SIDEWIDTH + TRANSITIONWIDTH/2):
                # Top Left border
                xContribution = np.sin((np.pi / 2) * (x) / (RESOLUTION * TRANSITIONWIDTH/2)) ** 1
                yContribution = np.cos((np.pi / 2) * (y - RESOLUTION * (SIDEWIDTH - TRANSITIONWIDTH/2)) / (RESOLUTION * TRANSITIONWIDTH)) ** 2
                cornerTopLeftProbability[x, y] = (0.5+0.5*xContribution) * yContribution
                sideLeftProbability[x, y] = (0.5 + 0.5 * xContribution) * (1-yContribution)
                borderSideLeftProbability[x, y] = (0.5 - 0.5 * xContribution) * (1-yContribution)
                borderCornerTopLeftLeftProbability[x, y] = (0.5 - 0.5 * xContribution) * yContribution
    for y in range(RESOLUTION):
        for x in range(RESOLUTION):

            centerValue = 0

            leftSideValue = 0
            bottomSideValue = 0
            rightSideValue = 0
            topSideValue = 0

            bottomLeftCornerValue = 0
            bottomRightCornerValue = 0
            topRightCornerValue = 0
            topLeftCornerValue = 0

            adjacentLeftSideValue = 0
            adjacentBottomSideValue = 0
            adjacentRightSideValue = 0
            adjacentTopSideValue = 0

            adjacentCornerBottomLeftLeftValue = 0
            adjacentCornerBottomLeftBottomValue = 0
            adjacentCornerBottomRightBottomValue = 0
            adjacentCornerBottomRightRightValue = 0
            adjacentCornerTopRightRightValue = 0
            adjacentCornerTopRightTopValue = 0
            adjacentCornerTopLeftTopValue = 0
            adjacentCornerTopLeftLeftValue = 0

            probabilities = np.array([centerProbability[x, y], \
                                      sideLeftProbability[x, y], \
                                      sideBottomProbability[x, y], \
                                      sideRightProbability[x, y], \
                                      sideTopProbability[x, y], \
                                      cornerBottomLeftProbability[x, y], \
                                      cornerBottomRightProbability[x, y], \
                                      cornerTopRightProbability[x, y], \
                                      cornerTopLeftProbability[x, y], \
                                      borderSideLeftProbability[x, y], \
                                      borderSideBottomProbability[x, y], \
                                      borderSideRightProbability[x, y], \
                                      borderSideTopProbability[x, y], \
                                      borderCornerBottomLeftLeftProbability[x, y], \
                                      borderCornerBottomLeftBottomProbability[x, y], \
                                      borderCornerBottomRightBottomProbability[x, y], \
                                      borderCornerBottomRightRightProbability[x, y], \
                                      borderCornerTopRightRightProbability[x, y], \
                                      borderCornerTopRightTopProbability[x, y], \
                                      borderCornerTopLeftTopProbability[x, y], \
                                      borderCornerTopLeftLeftProbability[x, y]])

            totalPropability = np.sum(probabilities)
            r = np.random.rand()
            for i in range(21):
                if r <= np.sum(probabilities[0:i + 1]) / totalPropability:
                    if i == 0:
                        centerValue = 1
                    elif i == 1:
                        leftSideValue = 1
                    elif i == 2:
                        bottomSideValue = 1
                    elif i == 3:
                        rightSideValue = 1
                    elif i == 4:
                        topSideValue = 1
                    elif i == 5:
                        bottomLeftCornerValue = 1
                    elif i == 6:
                        bottomRightCornerValue = 1
                    elif i == 7:
                        topRightCornerValue = 1
                    elif i == 8:
                        topLeftCornerValue = 1
                    elif i == 9:
                        adjacentLeftSideValue = 1
                    elif i == 10:
                        adjacentBottomSideValue = 1
                    elif i == 11:
                        adjacentRightSideValue = 1
                    elif i == 12:
                        adjacentTopSideValue = 1
                    elif i == 13:
                        adjacentCornerBottomLeftLeftValue = 1
                    elif i == 14:
                        adjacentCornerBottomLeftBottomValue = 1
                    elif i == 15:
                        adjacentCornerBottomRightBottomValue = 1
                    elif i == 16:
                        adjacentCornerBottomRightRightValue = 1
                    elif i == 17:
                        adjacentCornerTopRightRightValue = 1
                    elif i == 18:
                        adjacentCornerTopRightTopValue = 1
                    elif i == 19:
                        adjacentCornerTopLeftTopValue = 1
                    elif i == 20:
                        adjacentCornerTopLeftLeftValue = 1
                    break

            centerValue = int(np.floor(MAXVAL * (1 - centerValue)))

            leftSideValue = int(np.floor(MAXVAL * (1 - leftSideValue)))
            bottomSideValue = int(np.floor(MAXVAL * (1 - bottomSideValue)))
            rightSideValue = int(np.floor(MAXVAL * (1 - rightSideValue)))
            topSideValue = int(np.floor(MAXVAL * (1 - topSideValue)))

            bottomLeftCornerValue = int(np.floor(MAXVAL * (1 - bottomLeftCornerValue)))
            bottomRightCornerValue = int(np.floor(MAXVAL * (1 - bottomRightCornerValue)))
            topLeftCornerValue = int(np.floor(MAXVAL * (1 - topLeftCornerValue)))
            topRightCornerValue = int(np.floor(MAXVAL * (1 - topRightCornerValue)))

            adjacentLeftSideValue = int(np.floor(MAXVAL * (1 - adjacentLeftSideValue)))
            adjacentBottomSideValue = int(np.floor(MAXVAL * (1 - adjacentBottomSideValue)))
            adjacentRightSideValue = int(np.floor(MAXVAL * (1 - adjacentRightSideValue)))
            adjacentTopSideValue = int(np.floor(MAXVAL * (1 - adjacentTopSideValue)))

            adjacentCornerBottomLeftLeftValue = int(np.floor(MAXVAL * (1 - adjacentCornerBottomLeftLeftValue)))
            adjacentCornerBottomLeftBottomValue = int(np.floor(MAXVAL * (1 - adjacentCornerBottomLeftBottomValue)))
            adjacentCornerBottomRightBottomValue = int(np.floor(MAXVAL * (1 - adjacentCornerBottomRightBottomValue)))
            adjacentCornerBottomRightRightValue = int(np.floor(MAXVAL * (1 - adjacentCornerBottomRightRightValue)))
            adjacentCornerTopRightRightValue = int(np.floor(MAXVAL * (1 - adjacentCornerTopRightRightValue)))
            adjacentCornerTopRightTopValue = int(np.floor(MAXVAL * (1 - adjacentCornerTopRightTopValue)))
            adjacentCornerTopLeftTopValue = int(np.floor(MAXVAL * (1 - adjacentCornerTopLeftTopValue)))
            adjacentCornerTopLeftLeftValue = int(np.floor(MAXVAL * (1 - adjacentCornerTopLeftLeftValue)))

            filterCenter.setPixel(x, y, (centerValue, centerValue, centerValue))

            filterSideLeft.setPixel(x, y, (leftSideValue, leftSideValue, leftSideValue))
            filterSideBottom.setPixel(x, y, (bottomSideValue, bottomSideValue, bottomSideValue))
            filterSideRight.setPixel(x, y, (rightSideValue, rightSideValue, rightSideValue))
            filterSideTop.setPixel(x, y, (topSideValue, topSideValue, topSideValue))

            filterCornerBottomLeft.setPixel(x, y, (bottomLeftCornerValue, bottomLeftCornerValue, bottomLeftCornerValue))
            filterCornerBottomRight.setPixel(x, y,
                                             (bottomRightCornerValue, bottomRightCornerValue, bottomRightCornerValue))
            filterCornerTopLeft.setPixel(x, y, (topLeftCornerValue, topLeftCornerValue, topLeftCornerValue))
            filterCornerTopRight.setPixel(x, y, (topRightCornerValue, topRightCornerValue, topRightCornerValue))

            filterAdjacentSideLeft.setPixel(x, y, (adjacentLeftSideValue, adjacentLeftSideValue, adjacentLeftSideValue))
            filterAdjacentSideBottom.setPixel(x, y, (
            adjacentBottomSideValue, adjacentBottomSideValue, adjacentBottomSideValue))
            filterAdjacentSideRight.setPixel(x, y,
                                             (adjacentRightSideValue, adjacentRightSideValue, adjacentRightSideValue))
            filterAdjacentSideTop.setPixel(x, y, (adjacentTopSideValue, adjacentTopSideValue, adjacentTopSideValue))

            filterAdjacentCornerBottomLeftLeft.setPixel(x, y, (
            adjacentCornerBottomLeftLeftValue, adjacentCornerBottomLeftLeftValue, adjacentCornerBottomLeftLeftValue))
            filterAdjacentCornerBottomLeftBottom.setPixel(x, y, (
            adjacentCornerBottomLeftBottomValue, adjacentCornerBottomLeftBottomValue,
            adjacentCornerBottomLeftBottomValue))
            filterAdjacentCornerBottomRightBottom.setPixel(x, y, (
            adjacentCornerBottomRightBottomValue, adjacentCornerBottomRightBottomValue,
            adjacentCornerBottomRightBottomValue))
            filterAdjacentCornerBottomRightRight.setPixel(x, y, (
            adjacentCornerBottomRightRightValue, adjacentCornerBottomRightRightValue,
            adjacentCornerBottomRightRightValue))
            filterAdjacentCornerTopRightRight.setPixel(x, y, (
            adjacentCornerTopRightRightValue, adjacentCornerTopRightRightValue, adjacentCornerTopRightRightValue))
            filterAdjacentCornerTopRightTop.setPixel(x, y, (
            adjacentCornerTopRightTopValue, adjacentCornerTopRightTopValue, adjacentCornerTopRightTopValue))
            filterAdjacentCornerTopLeftTop.setPixel(x, y, (
            adjacentCornerTopLeftTopValue, adjacentCornerTopLeftTopValue, adjacentCornerTopLeftTopValue))
            filterAdjacentCornerTopLeftLeft.setPixel(x, y, (
            adjacentCornerTopLeftLeftValue, adjacentCornerTopLeftLeftValue, adjacentCornerTopLeftLeftValue))
else:
    for y in range(RESOLUTION):
        for x in range(RESOLUTION):

            if x >= RESOLUTION * (SIDEWIDTH + TRANSITIONWIDTH / 2) and \
                    x <= RESOLUTION * (SIDEWIDTH + CENTERWIDTH - TRANSITIONWIDTH / 2) and \
                    y >= RESOLUTION * (SIDEWIDTH + TRANSITIONWIDTH / 2) and \
                    y <= RESOLUTION * (SIDEWIDTH + CENTERWIDTH - TRANSITIONWIDTH / 2):
                # Center
                centerProbability[x, y] = 1
            elif x >= RESOLUTION * (SIDEWIDTH - TRANSITIONWIDTH / 2) and \
                    x <= RESOLUTION * (SIDEWIDTH + TRANSITIONWIDTH / 2) and \
                    y >= RESOLUTION * (SIDEWIDTH + TRANSITIONWIDTH / 2) and \
                    y <= RESOLUTION * (SIDEWIDTH + CENTERWIDTH - TRANSITIONWIDTH / 2):
                # Left transition
                xContribution = np.sin((np.pi / 2) * (x - RESOLUTION * (SIDEWIDTH - TRANSITIONWIDTH / 2)) / (
                        RESOLUTION * TRANSITIONWIDTH)) ** 2
                centerProbability[x, y] = xContribution
                sideLeftProbability[x, y] = 1 - xContribution
            elif x >= RESOLUTION * (SIDEWIDTH + CENTERWIDTH - TRANSITIONWIDTH / 2) and \
                    x <= RESOLUTION * (SIDEWIDTH + CENTERWIDTH + TRANSITIONWIDTH / 2) and \
                    y >= RESOLUTION * (SIDEWIDTH + TRANSITIONWIDTH / 2) and \
                    y <= RESOLUTION * (SIDEWIDTH + CENTERWIDTH - TRANSITIONWIDTH / 2):
                # Right transition
                xContribution = np.sin(
                    (np.pi / 2) + (np.pi / 2) * (x - RESOLUTION * (SIDEWIDTH + CENTERWIDTH - TRANSITIONWIDTH / 2)) / (
                            RESOLUTION * TRANSITIONWIDTH)) ** 2
                centerProbability[x, y] = xContribution
                sideRightProbability[x, y] = 1 - xContribution
            elif x >= RESOLUTION * (SIDEWIDTH + TRANSITIONWIDTH / 2) and \
                    x <= RESOLUTION * (SIDEWIDTH + CENTERWIDTH - TRANSITIONWIDTH / 2) and \
                    y >= RESOLUTION * (SIDEWIDTH - TRANSITIONWIDTH / 2) and \
                    y <= RESOLUTION * (SIDEWIDTH + TRANSITIONWIDTH / 2):
                # Top transition
                yContribution = np.sin((np.pi / 2) * (y - RESOLUTION * (SIDEWIDTH - TRANSITIONWIDTH / 2)) / (
                            RESOLUTION * TRANSITIONWIDTH)) ** 2
                centerProbability[x, y] = yContribution
                sideTopProbability[x, y] = 1 - yContribution
            elif x >= RESOLUTION * (SIDEWIDTH + TRANSITIONWIDTH / 2) and \
                    x <= RESOLUTION * (SIDEWIDTH + CENTERWIDTH - TRANSITIONWIDTH / 2) and \
                    y >= RESOLUTION * (SIDEWIDTH + CENTERWIDTH - TRANSITIONWIDTH / 2) and \
                    y <= RESOLUTION * (SIDEWIDTH + CENTERWIDTH + TRANSITIONWIDTH / 2):
                # Bottom transition
                yContribution = np.cos(
                    (np.pi / 2) * (y - RESOLUTION * (SIDEWIDTH + CENTERWIDTH - TRANSITIONWIDTH / 2)) / (
                                RESOLUTION * TRANSITIONWIDTH)) ** 2
                centerProbability[x, y] = yContribution
                sideBottomProbability[x, y] = 1 - yContribution
            elif x >= RESOLUTION * (SIDEWIDTH - TRANSITIONWIDTH / 2) and \
                    x <= RESOLUTION * (SIDEWIDTH + TRANSITIONWIDTH / 2) and \
                    y >= RESOLUTION * (SIDEWIDTH + CENTERWIDTH - TRANSITIONWIDTH / 2) and \
                    y <= RESOLUTION * (SIDEWIDTH + CENTERWIDTH + TRANSITIONWIDTH / 2):
                # Bottom Left transition
                xContribution = np.sin((np.pi / 2) * (x - RESOLUTION * (SIDEWIDTH - TRANSITIONWIDTH / 2)) / (
                        RESOLUTION * TRANSITIONWIDTH)) ** 2
                yContribution = np.cos(
                    (np.pi / 2) * (y - RESOLUTION * (SIDEWIDTH + CENTERWIDTH - TRANSITIONWIDTH / 2)) / (
                            RESOLUTION * TRANSITIONWIDTH)) ** 2
                centerProbability[x, y] = xContribution * yContribution
                sideLeftProbability[x, y] = (1 - xContribution) * yContribution
                sideBottomProbability[x, y] = xContribution * (1 - yContribution)
                cornerBottomLeftProbability[x, y] = (1 - xContribution) * (1 - yContribution)
            elif x >= RESOLUTION * (SIDEWIDTH + CENTERWIDTH - TRANSITIONWIDTH / 2) and \
                    x <= RESOLUTION * (SIDEWIDTH + CENTERWIDTH + TRANSITIONWIDTH / 2) and \
                    y >= RESOLUTION * (SIDEWIDTH + CENTERWIDTH - TRANSITIONWIDTH / 2) and \
                    y <= RESOLUTION * (SIDEWIDTH + CENTERWIDTH + TRANSITIONWIDTH / 2):
                # Bottom Right transition
                xContribution = np.cos(
                    (np.pi / 2) * (x - RESOLUTION * (SIDEWIDTH + CENTERWIDTH - TRANSITIONWIDTH / 2)) / (
                            RESOLUTION * TRANSITIONWIDTH)) ** 2
                yContribution = np.cos(
                    (np.pi / 2) * (y - RESOLUTION * (SIDEWIDTH + CENTERWIDTH - TRANSITIONWIDTH / 2)) / (
                            RESOLUTION * TRANSITIONWIDTH)) ** 2
                centerProbability[x, y] = xContribution * yContribution
                sideBottomProbability[x, y] = xContribution * (1 - yContribution)
                sideRightProbability[x, y] = (1 - xContribution) * yContribution
                cornerBottomRightProbability[x, y] = (1 - xContribution) * (1 - yContribution)
            elif x >= RESOLUTION * (SIDEWIDTH + CENTERWIDTH - TRANSITIONWIDTH / 2) and \
                    x <= RESOLUTION * (SIDEWIDTH + CENTERWIDTH + TRANSITIONWIDTH / 2) and \
                    y >= RESOLUTION * (SIDEWIDTH - TRANSITIONWIDTH / 2) and \
                    y <= RESOLUTION * (SIDEWIDTH + TRANSITIONWIDTH / 2):
                # Top Right transition
                xContribution = np.cos(
                    (np.pi / 2) * (x - RESOLUTION * (SIDEWIDTH + CENTERWIDTH - TRANSITIONWIDTH / 2)) / (
                            RESOLUTION * TRANSITIONWIDTH)) ** 2
                yContribution = np.sin((np.pi / 2) * (y - RESOLUTION * (SIDEWIDTH - TRANSITIONWIDTH / 2)) / (
                        RESOLUTION * TRANSITIONWIDTH)) ** 2
                centerProbability[x, y] = xContribution * yContribution
                sideRightProbability[x, y] = (1 - xContribution) * yContribution
                sideTopProbability[x, y] = xContribution * (1 - yContribution)
                cornerTopRightProbability[x, y] = (1 - xContribution) * (1 - yContribution)
            elif x >= RESOLUTION * (SIDEWIDTH - TRANSITIONWIDTH / 2) and \
                    x <= RESOLUTION * (SIDEWIDTH + TRANSITIONWIDTH / 2) and \
                    y >= RESOLUTION * (SIDEWIDTH - TRANSITIONWIDTH / 2) and \
                    y <= RESOLUTION * (SIDEWIDTH + TRANSITIONWIDTH / 2):
                # Top Left transition
                xContribution = np.sin((np.pi / 2) * (x - RESOLUTION * (SIDEWIDTH - TRANSITIONWIDTH / 2)) / (
                        RESOLUTION * TRANSITIONWIDTH)) ** 2
                yContribution = np.sin((np.pi / 2) * (y - RESOLUTION * (SIDEWIDTH - TRANSITIONWIDTH / 2)) / (
                        RESOLUTION * TRANSITIONWIDTH)) ** 2
                centerProbability[x, y] = xContribution * yContribution
                sideLeftProbability[x, y] = (1 - xContribution) * yContribution
                sideTopProbability[x, y] = xContribution * (1 - yContribution)
                cornerTopLeftProbability[x, y] = (1 - xContribution) * (1 - yContribution)
            elif x >= RESOLUTION * (TRANSITIONWIDTH / 2) and \
                    x <= RESOLUTION * (SIDEWIDTH - TRANSITIONWIDTH / 2) and \
                    y >= RESOLUTION * (SIDEWIDTH + TRANSITIONWIDTH / 2) and \
                    y <= RESOLUTION * (SIDEWIDTH + CENTERWIDTH - TRANSITIONWIDTH / 2):
                # Left center
                sideLeftProbability[x, y] = 1
            elif x >= RESOLUTION * (SIDEWIDTH + CENTERWIDTH - TRANSITIONWIDTH / 2) and \
                    x <= RESOLUTION * (1 - TRANSITIONWIDTH / 2) and \
                    y >= RESOLUTION * (SIDEWIDTH + TRANSITIONWIDTH / 2) and \
                    y <= RESOLUTION * (SIDEWIDTH + CENTERWIDTH - TRANSITIONWIDTH / 2):
                # Right center
                sideRightProbability[x, y] = 1
            elif x >= RESOLUTION * (SIDEWIDTH + TRANSITIONWIDTH / 2) and \
                    x <= RESOLUTION * (SIDEWIDTH + CENTERWIDTH - TRANSITIONWIDTH / 2) and \
                    y >= RESOLUTION * (SIDEWIDTH + CENTERWIDTH - TRANSITIONWIDTH / 2) and \
                    y <= RESOLUTION * (1 - TRANSITIONWIDTH / 2):
                # Bottom center
                sideBottomProbability[x, y] = 1
            elif x >= RESOLUTION * (SIDEWIDTH + TRANSITIONWIDTH / 2) and \
                    x <= RESOLUTION * (SIDEWIDTH + CENTERWIDTH - TRANSITIONWIDTH / 2) and \
                    y >= RESOLUTION * (TRANSITIONWIDTH / 2) and \
                    y <= RESOLUTION * (SIDEWIDTH - TRANSITIONWIDTH / 2):
                # Top center
                sideTopProbability[x, y] = 1
            elif x >= RESOLUTION * (TRANSITIONWIDTH / 2) and \
                    x <= RESOLUTION * (SIDEWIDTH - TRANSITIONWIDTH / 2) and \
                    y >= RESOLUTION * (SIDEWIDTH + CENTERWIDTH + TRANSITIONWIDTH / 2) and \
                    y <= RESOLUTION * (1 - TRANSITIONWIDTH / 2):
                # Bottom Left Center
                cornerBottomLeftProbability[x, y] = 1
            elif x >= RESOLUTION * (SIDEWIDTH + CENTERWIDTH + TRANSITIONWIDTH / 2) and \
                    x <= RESOLUTION * (1 - TRANSITIONWIDTH / 2) and \
                    y >= RESOLUTION * (SIDEWIDTH + CENTERWIDTH + TRANSITIONWIDTH / 2) and \
                    y <= RESOLUTION * (1 - TRANSITIONWIDTH / 2):
                # Bottom Right Center
                cornerBottomRightProbability[x, y] = 1
            elif x >= RESOLUTION * (SIDEWIDTH + CENTERWIDTH + TRANSITIONWIDTH / 2) and \
                    x <= RESOLUTION * (1 - TRANSITIONWIDTH / 2) and \
                    y >= RESOLUTION * (TRANSITIONWIDTH / 2) and \
                    y <= RESOLUTION * (SIDEWIDTH - TRANSITIONWIDTH / 2):
                # Top Right Center
                cornerTopRightProbability[x, y] = 1
            elif x >= RESOLUTION * (TRANSITIONWIDTH / 2) and \
                    x <= RESOLUTION * (SIDEWIDTH - TRANSITIONWIDTH / 2) and \
                    y >= RESOLUTION * (TRANSITIONWIDTH / 2) and \
                    y <= RESOLUTION * (SIDEWIDTH - TRANSITIONWIDTH / 2):
                # Top Left Center
                cornerTopLeftProbability[x, y] = 1

            elif x >= RESOLUTION * (SIDEWIDTH - TRANSITIONWIDTH / 2) and \
                    x <= RESOLUTION * (SIDEWIDTH + TRANSITIONWIDTH / 2) and \
                    y >= RESOLUTION * (SIDEWIDTH + CENTERWIDTH + TRANSITIONWIDTH / 2) and \
                    y <= RESOLUTION * (1 - TRANSITIONWIDTH / 2):
                xContribution = np.sin((np.pi / 2) * (x - RESOLUTION * (SIDEWIDTH - TRANSITIONWIDTH / 2)) / (
                        RESOLUTION * TRANSITIONWIDTH)) ** 2
                cornerBottomLeftProbability[x, y] = 1 - xContribution
                sideBottomProbability[x, y] = xContribution
            elif x >= RESOLUTION * (SIDEWIDTH + CENTERWIDTH - TRANSITIONWIDTH / 2) and \
                    x <= RESOLUTION * (SIDEWIDTH + CENTERWIDTH + TRANSITIONWIDTH / 2) and \
                    y >= RESOLUTION * (SIDEWIDTH + CENTERWIDTH + TRANSITIONWIDTH / 2) and \
                    y <= RESOLUTION * (1 - TRANSITIONWIDTH / 2):
                xContribution = np.cos(
                    (np.pi / 2) * (x - RESOLUTION * (SIDEWIDTH + CENTERWIDTH - TRANSITIONWIDTH / 2)) / (
                            RESOLUTION * TRANSITIONWIDTH)) ** 2
                cornerBottomRightProbability[x, y] = 1 - xContribution
                sideBottomProbability[x, y] = xContribution
            elif x >= RESOLUTION * (SIDEWIDTH + CENTERWIDTH - TRANSITIONWIDTH / 2) and \
                    x <= RESOLUTION * (SIDEWIDTH + CENTERWIDTH + TRANSITIONWIDTH / 2) and \
                    y >= RESOLUTION * (TRANSITIONWIDTH / 2) and \
                    y <= RESOLUTION * (SIDEWIDTH - TRANSITIONWIDTH / 2):
                xContribution = np.cos(
                    (np.pi / 2) * (x - RESOLUTION * (SIDEWIDTH + CENTERWIDTH - TRANSITIONWIDTH / 2)) / (
                            RESOLUTION * TRANSITIONWIDTH)) ** 2
                cornerTopRightProbability[x, y] = 1 - xContribution
                sideTopProbability[x, y] = xContribution
            elif x >= RESOLUTION * (SIDEWIDTH - TRANSITIONWIDTH / 2) and \
                    x <= RESOLUTION * (SIDEWIDTH + TRANSITIONWIDTH / 2) and \
                    y >= RESOLUTION * (TRANSITIONWIDTH / 2) and \
                    y <= RESOLUTION * (SIDEWIDTH - TRANSITIONWIDTH / 2):
                xContribution = np.sin((np.pi / 2) * (x - RESOLUTION * (SIDEWIDTH - TRANSITIONWIDTH / 2)) / (
                        RESOLUTION * TRANSITIONWIDTH)) ** 2
                cornerTopLeftProbability[x, y] = 1 - xContribution
                sideTopProbability[x, y] = xContribution

            elif x >= RESOLUTION * (TRANSITIONWIDTH / 2) and \
                    x <= RESOLUTION * (SIDEWIDTH - TRANSITIONWIDTH / 2) and \
                    y >= RESOLUTION * (SIDEWIDTH - TRANSITIONWIDTH / 2) and \
                    y <= RESOLUTION * (SIDEWIDTH + TRANSITIONWIDTH / 2):
                yContribution = np.sin((np.pi / 2) * (y - RESOLUTION * (SIDEWIDTH - TRANSITIONWIDTH / 2)) / (
                        RESOLUTION * TRANSITIONWIDTH)) ** 2
                cornerTopLeftProbability[x, y] = 1 - yContribution
                sideLeftProbability[x, y] = yContribution
            elif x >= RESOLUTION * (TRANSITIONWIDTH / 2) and \
                    x <= RESOLUTION * (SIDEWIDTH - TRANSITIONWIDTH / 2) and \
                    y >= RESOLUTION * (SIDEWIDTH + CENTERWIDTH - TRANSITIONWIDTH / 2) and \
                    y <= RESOLUTION * (SIDEWIDTH + CENTERWIDTH + TRANSITIONWIDTH / 2):
                yContribution = np.cos(
                    (np.pi / 2) * (y - RESOLUTION * (SIDEWIDTH + CENTERWIDTH - TRANSITIONWIDTH / 2)) / (
                            RESOLUTION * TRANSITIONWIDTH)) ** 2
                cornerBottomLeftProbability[x, y] = 1 - yContribution
                sideLeftProbability[x, y] = yContribution
            elif x >= RESOLUTION * (SIDEWIDTH + CENTERWIDTH + TRANSITIONWIDTH / 2) and \
                    x <= RESOLUTION * (1 - TRANSITIONWIDTH / 2) and \
                    y >= RESOLUTION * (SIDEWIDTH + CENTERWIDTH - TRANSITIONWIDTH / 2) and \
                    y <= RESOLUTION * (SIDEWIDTH + CENTERWIDTH + TRANSITIONWIDTH / 2):
                yContribution = np.cos(
                    (np.pi / 2) * (y - RESOLUTION * (SIDEWIDTH + CENTERWIDTH - TRANSITIONWIDTH / 2)) / (
                            RESOLUTION * TRANSITIONWIDTH)) ** 2
                cornerBottomRightProbability[x, y] = 1 - yContribution
                sideRightProbability[x, y] = yContribution
            elif x >= RESOLUTION * (SIDEWIDTH + CENTERWIDTH + TRANSITIONWIDTH / 2) and \
                    x <= RESOLUTION * (1 - TRANSITIONWIDTH / 2) and \
                    y >= RESOLUTION * (SIDEWIDTH - TRANSITIONWIDTH / 2) and \
                    y <= RESOLUTION * (SIDEWIDTH + TRANSITIONWIDTH / 2):
                yContribution = np.sin((np.pi / 2) * (y - RESOLUTION * (SIDEWIDTH - TRANSITIONWIDTH / 2)) / (
                        RESOLUTION * TRANSITIONWIDTH)) ** 2
                cornerTopRightProbability[x, y] = 1 - yContribution
                sideRightProbability[x, y] = yContribution

            elif x >= RESOLUTION * (0) and \
                    x <= RESOLUTION * (TRANSITIONWIDTH / 2) and \
                    y >= RESOLUTION * (SIDEWIDTH + TRANSITIONWIDTH / 2) and \
                    y <= RESOLUTION * (SIDEWIDTH + CENTERWIDTH - TRANSITIONWIDTH / 2):
                # Left Border
                xContribution = np.sin((np.pi / 2) * (x) / (RESOLUTION * TRANSITIONWIDTH / 2)) ** 1
                borderSideLeftProbability[x, y] = 0.5 - 0.5 * xContribution
                sideLeftProbability[x, y] = 0.5 + 0.5 * xContribution
            elif x >= RESOLUTION * (1 - TRANSITIONWIDTH / 2) and \
                    x <= RESOLUTION * (1) and \
                    y >= RESOLUTION * (SIDEWIDTH + TRANSITIONWIDTH / 2) and \
                    y <= RESOLUTION * (SIDEWIDTH + CENTERWIDTH - TRANSITIONWIDTH / 2):
                # Right Border
                xContribution = np.cos((np.pi / 2) * (x - RESOLUTION * (1 - TRANSITIONWIDTH / 2)) / (
                            RESOLUTION * TRANSITIONWIDTH / 2)) ** 1
                borderSideRightProbability[x, y] = 0.5 - 0.5 * xContribution
                sideRightProbability[x, y] = 0.5 + 0.5 * xContribution
            elif x >= RESOLUTION * (SIDEWIDTH + TRANSITIONWIDTH / 2) and \
                    x <= RESOLUTION * (SIDEWIDTH + CENTERWIDTH - TRANSITIONWIDTH / 2) and \
                    y >= RESOLUTION * (1 - TRANSITIONWIDTH / 2) and \
                    y <= RESOLUTION * (1):
                # Bottom Border
                yContribution = np.cos((np.pi / 2) * (y - RESOLUTION * (1 - TRANSITIONWIDTH / 2)) / (
                            RESOLUTION * TRANSITIONWIDTH / 2)) ** 1
                borderSideBottomProbability[x, y] = 0.5 - 0.5 * yContribution
                sideBottomProbability[x, y] = 0.5 + 0.5 * yContribution
            elif x >= RESOLUTION * (SIDEWIDTH + TRANSITIONWIDTH / 2) and \
                    x <= RESOLUTION * (SIDEWIDTH + CENTERWIDTH - TRANSITIONWIDTH / 2) and \
                    y >= RESOLUTION * (0) and \
                    y <= RESOLUTION * (TRANSITIONWIDTH / 2):
                # top Border
                yContribution = np.sin((np.pi / 2) * (y) / (RESOLUTION * TRANSITIONWIDTH / 2)) ** 1
                borderSideTopProbability[x, y] = 0.5 - 0.5 * yContribution
                sideTopProbability[x, y] = 0.5 + 0.5 * yContribution

            elif x >= RESOLUTION * (0) and \
                    x <= RESOLUTION * (TRANSITIONWIDTH / 2) and \
                    y >= RESOLUTION * (SIDEWIDTH + CENTERWIDTH + TRANSITIONWIDTH / 2) and \
                    y <= RESOLUTION * (1 - TRANSITIONWIDTH / 2):
                # Bottom left border
                xContribution = np.sin((np.pi / 2) * (x) / (RESOLUTION * TRANSITIONWIDTH / 2)) ** 1
                borderCornerBottomLeftLeftProbability[x, y] = 0.5 - 0.5 * xContribution
                cornerBottomLeftProbability[x, y] = 0.5 + 0.5 * xContribution
            elif x >= RESOLUTION * (TRANSITIONWIDTH / 2) and \
                    x <= RESOLUTION * (SIDEWIDTH - TRANSITIONWIDTH / 2) and \
                    y >= RESOLUTION * (1 - TRANSITIONWIDTH / 2) and \
                    y <= RESOLUTION * (1):
                # yContribution = np.cos((np.pi / 2) * (y - RESOLUTION * (1-TRANSITIONWIDTH/2)) / (RESOLUTION * TRANSITIONWIDTH / 2)) ** 1
                yContribution = np.sin((np.pi / 2) * (RESOLUTION - y - 1) / (RESOLUTION * TRANSITIONWIDTH / 2)) ** 1
                borderCornerBottomLeftBottomProbability[x, y] = 0.5 - 0.5 * yContribution
                cornerBottomLeftProbability[x, y] = 0.5 + 0.5 * yContribution
                # -----------------------------------------------------------
                # -----------------------------------------------------------
            elif x >= RESOLUTION * (0) and \
                    x <= RESOLUTION * (TRANSITIONWIDTH / 2) and \
                    y >= RESOLUTION * (1 - TRANSITIONWIDTH / 2) and \
                    y <= RESOLUTION * (1):
                # Bottom left border
                xContribution = np.sin((np.pi / 2) * (x) / (RESOLUTION * TRANSITIONWIDTH / 2)) ** 1
                # yContribution = np.cos((np.pi / 2) * (y - RESOLUTION * (1-TRANSITIONWIDTH/2)) / (RESOLUTION * TRANSITIONWIDTH / 2)) ** 1
                yContribution = np.sin((np.pi / 2) * (RESOLUTION - y - 1) / (RESOLUTION * TRANSITIONWIDTH / 2)) ** 1
                borderCornerBottomLeftLeftProbability[x, y] = (0.5 + 0.5 * yContribution) * (0.5 - 0.5 * xContribution)
                borderCornerBottomLeftBottomProbability[x, y] = (0.5 - 0.5 * yContribution) * (
                            0.5 + 0.5 * xContribution)
                cornerBottomLeftProbability[x, y] = (0.5 + 0.5 * yContribution) * (0.5 + 0.5 * xContribution)
                # -----------------------------------------------------------
                # -----------------------------------------------------------
            elif x >= RESOLUTION * (0) and \
                    x <= RESOLUTION * (TRANSITIONWIDTH / 2) and \
                    y >= RESOLUTION * (SIDEWIDTH + CENTERWIDTH - TRANSITIONWIDTH / 2) and \
                    y <= RESOLUTION * (SIDEWIDTH + CENTERWIDTH + TRANSITIONWIDTH / 2):
                # Bottom left border
                xContribution = np.sin((np.pi / 2) * (x) / (RESOLUTION * TRANSITIONWIDTH / 2)) ** 1
                yContribution = np.sin(
                    (np.pi / 2) * (y - RESOLUTION * (SIDEWIDTH + CENTERWIDTH - TRANSITIONWIDTH / 2)) / (
                            RESOLUTION * TRANSITIONWIDTH)) ** 2
                borderSideLeftProbability[x, y] = (1 - yContribution) * (0.5 - 0.5 * xContribution)
                borderCornerBottomLeftLeftProbability[x, y] = yContribution * (0.5 - 0.5 * xContribution)
                cornerBottomLeftProbability[x, y] = yContribution * (0.5 + 0.5 * xContribution)
                sideLeftProbability[x, y] = (1 - yContribution) * (0.5 + 0.5 * xContribution)
            elif x >= RESOLUTION * (SIDEWIDTH - TRANSITIONWIDTH / 2) and \
                    x <= RESOLUTION * (SIDEWIDTH + TRANSITIONWIDTH / 2) and \
                    y >= RESOLUTION * (1 - TRANSITIONWIDTH / 2) and \
                    y <= RESOLUTION * (1):
                # Bottom left border
                xContribution = np.cos((np.pi / 2) * (x - RESOLUTION * (SIDEWIDTH - TRANSITIONWIDTH / 2)) / (
                        RESOLUTION * TRANSITIONWIDTH)) ** 2
                # yContribution = np.cos((np.pi / 2) * (y - RESOLUTION * (1-TRANSITIONWIDTH/2)) / (RESOLUTION * TRANSITIONWIDTH / 2)) ** 1
                yContribution = np.sin((np.pi / 2) * (RESOLUTION - y - 1) / (RESOLUTION * TRANSITIONWIDTH / 2)) ** 1
                borderSideBottomProbability[x, y] = (1 - xContribution) * (0.5 - 0.5 * yContribution)
                borderCornerBottomLeftBottomProbability[x, y] = xContribution * (0.5 - 0.5 * yContribution)
                cornerBottomLeftProbability[x, y] = xContribution * (0.5 + 0.5 * yContribution)
                sideBottomProbability[x, y] = (1 - xContribution) * (0.5 + 0.5 * yContribution)
                # -----------------------------------------------------------
                # -----------------------------------------------------------



            elif x >= RESOLUTION * (1 - TRANSITIONWIDTH / 2) and \
                    x <= RESOLUTION * (1) and \
                    y >= RESOLUTION * (SIDEWIDTH + CENTERWIDTH + TRANSITIONWIDTH / 2) and \
                    y <= RESOLUTION * (1 - TRANSITIONWIDTH / 2):
                # Bottom Right border
                xContribution = np.cos(
                    (np.pi / 2) * (x - RESOLUTION * (1 - TRANSITIONWIDTH / 2)) / (
                                RESOLUTION * TRANSITIONWIDTH / 2)) ** 1
                borderCornerBottomRightRightProbability[x, y] = 0.5 - 0.5 * xContribution
                cornerBottomRightProbability[x, y] = 0.5 + 0.5 * xContribution
            elif x >= RESOLUTION * (SIDEWIDTH + CENTERWIDTH + TRANSITIONWIDTH / 2) and \
                    x <= RESOLUTION * (1 - TRANSITIONWIDTH / 2) and \
                    y >= RESOLUTION * (1 - TRANSITIONWIDTH / 2) and \
                    y <= RESOLUTION * (1):
                # Bottom Right border
                yContribution = np.cos((np.pi / 2) * (y - RESOLUTION * (1 - TRANSITIONWIDTH / 2)) / (
                            RESOLUTION * TRANSITIONWIDTH / 2)) ** 1
                borderCornerBottomRightBottomProbability[x, y] = 0.5 - 0.5 * yContribution
                cornerBottomRightProbability[x, y] = 0.5 + 0.5 * yContribution
            elif x >= RESOLUTION * (1 - TRANSITIONWIDTH / 2) and \
                    x <= RESOLUTION * (1) and \
                    y >= RESOLUTION * (1 - TRANSITIONWIDTH / 2) and \
                    y <= RESOLUTION * (1):
                # Bottom Right border
                xContribution = np.cos((np.pi / 2) * (x - RESOLUTION * (1 - TRANSITIONWIDTH / 2)) / (
                            RESOLUTION * TRANSITIONWIDTH / 2)) ** 1
                yContribution = np.cos((np.pi / 2) * (y - RESOLUTION * (1 - TRANSITIONWIDTH / 2)) / (
                            RESOLUTION * TRANSITIONWIDTH / 2)) ** 1
                borderCornerBottomRightBottomProbability[x, y] = (0.5 + 0.5 * xContribution) * (
                            0.5 - 0.5 * yContribution)
                borderCornerBottomRightRightProbability[x, y] = (0.5 - 0.5 * xContribution) * (
                            0.5 + 0.5 * yContribution)
                cornerBottomRightProbability[x, y] = (0.5 + 0.5 * xContribution) * (0.5 + 0.5 * yContribution)
            elif x >= RESOLUTION * (SIDEWIDTH + CENTERWIDTH - TRANSITIONWIDTH / 2) and \
                    x <= RESOLUTION * (SIDEWIDTH + CENTERWIDTH + TRANSITIONWIDTH / 2) and \
                    y >= RESOLUTION * (1 - TRANSITIONWIDTH / 2) and \
                    y <= RESOLUTION * (1):
                # Bottom Right border
                xContribution = np.sin(
                    (np.pi / 2) * (x - RESOLUTION * (SIDEWIDTH + CENTERWIDTH - TRANSITIONWIDTH / 2)) / (
                                RESOLUTION * TRANSITIONWIDTH)) ** 2
                yContribution = np.cos((np.pi / 2) * (y - RESOLUTION * (1 - TRANSITIONWIDTH / 2)) / (
                            RESOLUTION * TRANSITIONWIDTH / 2)) ** 1
                cornerBottomRightProbability[x, y] = xContribution * (0.5 + 0.5 * yContribution)
                sideBottomProbability[x, y] = (1 - xContribution) * (0.5 + 0.5 * yContribution)
                borderCornerBottomRightBottomProbability[x, y] = xContribution * (0.5 - 0.5 * yContribution)
                borderSideBottomProbability[x, y] = (1 - xContribution) * (0.5 - 0.5 * yContribution)
            elif x >= RESOLUTION * (1 - TRANSITIONWIDTH / 2) and \
                    x <= RESOLUTION * (1) and \
                    y >= RESOLUTION * (SIDEWIDTH + CENTERWIDTH - TRANSITIONWIDTH / 2) and \
                    y <= RESOLUTION * (SIDEWIDTH + CENTERWIDTH + TRANSITIONWIDTH / 2):
                # Bottom Right border
                xContribution = np.cos((np.pi / 2) * (x - RESOLUTION * (1 - TRANSITIONWIDTH / 2)) / (
                            RESOLUTION * TRANSITIONWIDTH / 2)) ** 1
                yContribution = np.sin(
                    (np.pi / 2) * (y - RESOLUTION * (SIDEWIDTH + CENTERWIDTH - TRANSITIONWIDTH / 2)) / (
                                RESOLUTION * TRANSITIONWIDTH)) ** 2
                cornerBottomRightProbability[x, y] = yContribution * (0.5 + 0.5 * xContribution)
                sideRightProbability[x, y] = (1 - yContribution) * (0.5 + 0.5 * xContribution)
                borderCornerBottomRightRightProbability[x, y] = yContribution * (0.5 - 0.5 * xContribution)
                borderSideRightProbability[x, y] = (1 - yContribution) * (0.5 - 0.5 * xContribution)

            elif x >= RESOLUTION * (1 - TRANSITIONWIDTH / 2) and \
                    x <= RESOLUTION * (1) and \
                    y >= RESOLUTION * (TRANSITIONWIDTH / 2) and \
                    y <= RESOLUTION * (SIDEWIDTH - TRANSITIONWIDTH / 2):
                # Top Right border
                xContribution = np.cos(
                    (np.pi / 2) * (x - RESOLUTION * (1 - TRANSITIONWIDTH / 2)) / (
                                RESOLUTION * TRANSITIONWIDTH / 2)) ** 1
                borderCornerTopRightRightProbability[x, y] = 0.5 - 0.5 * xContribution
                cornerTopRightProbability[x, y] = 0.5 + 0.5 * xContribution
            elif x >= RESOLUTION * (SIDEWIDTH + CENTERWIDTH + TRANSITIONWIDTH / 2) and \
                    x <= RESOLUTION * (1 - TRANSITIONWIDTH / 2) and \
                    y >= RESOLUTION * (0) and \
                    y <= RESOLUTION * (TRANSITIONWIDTH / 2):
                # Top Right border
                yContribution = np.sin(
                    (np.pi / 2) * (y) / (RESOLUTION * TRANSITIONWIDTH / 2)) ** 1
                borderCornerTopRightTopProbability[x, y] = 0.5 - 0.5 * yContribution
                cornerTopRightProbability[x, y] = 0.5 + 0.5 * yContribution
            elif x >= RESOLUTION * (1 - TRANSITIONWIDTH / 2) and \
                    x <= RESOLUTION * (1) and \
                    y >= RESOLUTION * (0) and \
                    y <= RESOLUTION * (TRANSITIONWIDTH / 2):
                # Top Right border
                xContribution = np.cos((np.pi / 2) * (x - RESOLUTION * (1 - TRANSITIONWIDTH / 2)) / (
                            RESOLUTION * TRANSITIONWIDTH / 2)) ** 1
                yContribution = np.sin((np.pi / 2) * (y) / (RESOLUTION * TRANSITIONWIDTH / 2)) ** 1
                borderCornerTopRightTopProbability[x, y] = (0.5 + 0.5 * xContribution) * (0.5 - 0.5 * yContribution)
                borderCornerTopRightRightProbability[x, y] = (0.5 - 0.5 * xContribution) * (0.5 + 0.5 * yContribution)
                cornerTopRightProbability[x, y] = (0.5 + 0.5 * xContribution) * (0.5 + 0.5 * yContribution)
            elif x >= RESOLUTION * (1 - TRANSITIONWIDTH / 2) and \
                    x <= RESOLUTION * (1) and \
                    y >= RESOLUTION * (SIDEWIDTH - TRANSITIONWIDTH / 2) and \
                    y <= RESOLUTION * (SIDEWIDTH + TRANSITIONWIDTH / 2):
                # Top Right border
                xContribution = np.cos((np.pi / 2) * (x - RESOLUTION * (1 - TRANSITIONWIDTH / 2)) / (
                            RESOLUTION * TRANSITIONWIDTH / 2)) ** 1
                yContribution = np.cos((np.pi / 2) * (y - RESOLUTION * (SIDEWIDTH - TRANSITIONWIDTH / 2)) / (
                            RESOLUTION * TRANSITIONWIDTH)) ** 2
                cornerTopRightProbability[x, y] = (0.5 + 0.5 * xContribution) * yContribution
                sideRightProbability[x, y] = (0.5 + 0.5 * xContribution) * (1 - yContribution)
                borderCornerTopRightRightProbability[x, y] = (0.5 - 0.5 * xContribution) * yContribution
                borderSideRightProbability[x, y] = (0.5 - 0.5 * xContribution) * (1 - yContribution)
            elif x >= RESOLUTION * (SIDEWIDTH + CENTERWIDTH - TRANSITIONWIDTH / 2) and \
                    x <= RESOLUTION * (SIDEWIDTH + CENTERWIDTH + TRANSITIONWIDTH / 2) and \
                    y >= RESOLUTION * (0) and \
                    y <= RESOLUTION * (TRANSITIONWIDTH / 2):
                # Top Right border
                xContribution = np.sin(
                    (np.pi / 2) * (x - RESOLUTION * (SIDEWIDTH + CENTERWIDTH - TRANSITIONWIDTH / 2)) / (
                                RESOLUTION * TRANSITIONWIDTH)) ** 2
                yContribution = np.sin((np.pi / 2) * (y) / (RESOLUTION * TRANSITIONWIDTH / 2)) ** 1
                cornerTopRightProbability[x, y] = (0.5 + 0.5 * yContribution) * xContribution
                sideTopProbability[x, y] = (0.5 + 0.5 * yContribution) * (1 - xContribution)
                borderSideTopProbability[x, y] = (0.5 - 0.5 * yContribution) * (1 - xContribution)
                borderCornerTopRightTopProbability[x, y] = (0.5 - 0.5 * yContribution) * xContribution

            elif x >= RESOLUTION * (0) and \
                    x <= RESOLUTION * (TRANSITIONWIDTH / 2) and \
                    y >= RESOLUTION * (TRANSITIONWIDTH / 2) and \
                    y <= RESOLUTION * (SIDEWIDTH - TRANSITIONWIDTH / 2):
                # Top left border
                xContribution = np.sin((np.pi / 2) * (x) / (RESOLUTION * TRANSITIONWIDTH / 2)) ** 1
                borderCornerTopLeftLeftProbability[x, y] = 0.5 - 0.5 * xContribution
                cornerTopLeftProbability[x, y] = 0.5 + 0.5 * xContribution
            elif x >= RESOLUTION * (TRANSITIONWIDTH / 2) and \
                    x <= RESOLUTION * (SIDEWIDTH - TRANSITIONWIDTH / 2) and \
                    y >= RESOLUTION * (0) and \
                    y <= RESOLUTION * (TRANSITIONWIDTH / 2):
                # Top left border
                yContribution = np.sin((np.pi / 2) * (y) / (RESOLUTION * TRANSITIONWIDTH / 2)) ** 1
                borderCornerTopLeftTopProbability[x, y] = 0.5 - 0.5 * yContribution
                cornerTopLeftProbability[x, y] = 0.5 + 0.5 * yContribution
            elif x >= RESOLUTION * (0) and \
                    x <= RESOLUTION * (TRANSITIONWIDTH / 2) and \
                    y >= RESOLUTION * (0) and \
                    y <= RESOLUTION * (TRANSITIONWIDTH / 2):
                # Top left border
                xContribution = np.sin((np.pi / 2) * (x) / (RESOLUTION * TRANSITIONWIDTH / 2)) ** 1
                yContribution = np.sin((np.pi / 2) * (y) / (RESOLUTION * TRANSITIONWIDTH / 2)) ** 1
                borderCornerTopLeftTopProbability[x, y] = (0.5 + 0.5 * xContribution) * (0.5 - 0.5 * yContribution)
                borderCornerTopLeftLeftProbability[x, y] = (0.5 - 0.5 * xContribution) * (0.5 + 0.5 * yContribution)
                cornerTopLeftProbability[x, y] = (0.5 + 0.5 * xContribution) * (0.5 + 0.5 * yContribution)
            elif x >= RESOLUTION * (SIDEWIDTH - TRANSITIONWIDTH / 2) and \
                    x <= RESOLUTION * (SIDEWIDTH + TRANSITIONWIDTH / 2) and \
                    y >= RESOLUTION * (0) and \
                    y <= RESOLUTION * (TRANSITIONWIDTH / 2):
                # Top Left border
                xContribution = np.cos((np.pi / 2) * (x - RESOLUTION * (SIDEWIDTH - TRANSITIONWIDTH / 2)) / (
                            RESOLUTION * TRANSITIONWIDTH)) ** 2
                yContribution = np.sin((np.pi / 2) * (y) / (RESOLUTION * TRANSITIONWIDTH / 2)) ** 1
                cornerTopLeftProbability[x, y] = (0.5 + 0.5 * yContribution) * xContribution
                sideTopProbability[x, y] = (0.5 + 0.5 * yContribution) * (1 - xContribution)
                borderSideTopProbability[x, y] = (0.5 - 0.5 * yContribution) * (1 - xContribution)
                borderCornerTopLeftTopProbability[x, y] = (0.5 - 0.5 * yContribution) * xContribution
            elif x >= RESOLUTION * (0) and \
                    x <= RESOLUTION * (TRANSITIONWIDTH / 2) and \
                    y >= RESOLUTION * (SIDEWIDTH - TRANSITIONWIDTH / 2) and \
                    y <= RESOLUTION * (SIDEWIDTH + TRANSITIONWIDTH / 2):
                # Top Left border
                xContribution = np.sin((np.pi / 2) * (x) / (RESOLUTION * TRANSITIONWIDTH / 2)) ** 1
                yContribution = np.cos((np.pi / 2) * (y - RESOLUTION * (SIDEWIDTH - TRANSITIONWIDTH / 2)) / (
                            RESOLUTION * TRANSITIONWIDTH)) ** 2
                cornerTopLeftProbability[x, y] = (0.5 + 0.5 * xContribution) * yContribution
                sideLeftProbability[x, y] = (0.5 + 0.5 * xContribution) * (1 - yContribution)
                borderSideLeftProbability[x, y] = (0.5 - 0.5 * xContribution) * (1 - yContribution)
                borderCornerTopLeftLeftProbability[x, y] = (0.5 - 0.5 * xContribution) * yContribution
    sideRightProbability = np.flip(sideLeftProbability, 0)
    sideTopProbability = np.transpose(sideLeftProbability)
    sideBottomProbability = np.flip(sideTopProbability, 1)

    borderSideRightProbability = np.flip(borderSideLeftProbability, 0)
    borderSideTopProbability = np.transpose(borderSideLeftProbability)
    borderSideBottomProbability = np.flip(borderSideTopProbability, 1)

    tmp = np.flip(cornerBottomLeftProbability, 1)
    tmpTranspose = np.transpose(tmp)
    tmp = (tmp + tmpTranspose) / 2
    cornerBottomLeftProbability = np.flip(tmp, 1)

    cornerBottomRightProbability = np.flip(cornerBottomLeftProbability, 0)
    cornerTopLeftProbability = np.flip(cornerBottomLeftProbability, 1)
    cornerTopRightProbability = np.flip(cornerBottomRightProbability, 1)

    borderCornerBottomRightRightProbability = np.flip(borderCornerBottomLeftLeftProbability, 0)
    borderCornerTopLeftLeftProbability = np.flip(borderCornerBottomLeftLeftProbability, 1)
    borderCornerTopRightRightProbability = np.flip(borderCornerBottomRightRightProbability, 1)

    borderCornerTopRightTopProbability = np.transpose(borderCornerBottomLeftLeftProbability)
    borderCornerTopLeftTopProbability = np.flip(borderCornerTopRightTopProbability, 0)
    borderCornerBottomRightBottomProbability = np.flip(borderCornerTopRightTopProbability, 1)
    borderCornerBottomLeftBottomProbability = np.flip(borderCornerTopLeftTopProbability, 1)

    # borderCornerBottomRightBottomProbability = np.flip(borderCornerBottomLeftBottomProbability, 0)
    # borderCornerTopLeftTopProbability = np.flip(borderCornerBottomLeftBottomProbability, 1)
    # borderCornerTopRightTopProbability = np.flip(borderCornerBottomRightBottomProbability, 1)

    centerProbability[centerProbability < 0.01] = 0

    sideLeftProbability[sideLeftProbability < 0.01] = 0
    sideBottomProbability[sideBottomProbability < 0.01] = 0
    sideRightProbability[sideRightProbability < 0.01] = 0
    sideTopProbability[sideTopProbability < 0.01] = 0

    cornerBottomLeftProbability[cornerBottomLeftProbability < 0.01] = 0
    cornerBottomRightProbability[cornerBottomRightProbability < 0.01] = 0
    cornerTopLeftProbability[cornerTopLeftProbability < 0.01] = 0
    cornerTopRightProbability[cornerTopRightProbability < 0.01] = 0

    borderSideLeftProbability[borderSideLeftProbability < 0.01] = 0
    borderSideBottomProbability[borderSideBottomProbability < 0.01] = 0
    borderSideRightProbability[borderSideRightProbability < 0.01] = 0
    borderSideTopProbability[borderSideTopProbability < 0.01] = 0

    borderCornerBottomLeftLeftProbability[borderCornerBottomLeftLeftProbability < 0.01] = 0
    borderCornerBottomLeftBottomProbability[borderCornerBottomLeftBottomProbability < 0.01] = 0
    borderCornerBottomRightBottomProbability[borderCornerBottomRightBottomProbability < 0.01] = 0
    borderCornerBottomRightRightProbability[borderCornerBottomRightRightProbability < 0.01] = 0
    borderCornerTopRightRightProbability[borderCornerTopRightRightProbability < 0.01] = 0
    borderCornerTopRightTopProbability[borderCornerTopRightTopProbability < 0.01] = 0
    borderCornerTopLeftTopProbability[borderCornerTopLeftTopProbability < 0.01] = 0
    borderCornerTopLeftLeftProbability[borderCornerTopLeftLeftProbability < 0.01] = 0

    for y in range(RESOLUTION):
        for x in range(RESOLUTION):
            probabilities = np.array([centerProbability[x, y], \
                                      sideLeftProbability[x, y], \
                                      sideBottomProbability[x, y], \
                                      sideRightProbability[x, y], \
                                      sideTopProbability[x, y], \
                                      cornerBottomLeftProbability[x, y], \
                                      cornerBottomRightProbability[x, y], \
                                      cornerTopRightProbability[x, y], \
                                      cornerTopLeftProbability[x, y], \
                                      borderSideLeftProbability[x, y], \
                                      borderSideBottomProbability[x, y], \
                                      borderSideRightProbability[x, y], \
                                      borderSideTopProbability[x, y], \
                                      borderCornerBottomLeftLeftProbability[x, y], \
                                      borderCornerBottomLeftBottomProbability[x, y], \
                                      borderCornerBottomRightBottomProbability[x, y], \
                                      borderCornerBottomRightRightProbability[x, y], \
                                      borderCornerTopRightRightProbability[x, y], \
                                      borderCornerTopRightTopProbability[x, y], \
                                      borderCornerTopLeftTopProbability[x, y], \
                                      borderCornerTopLeftLeftProbability[x, y]])
            totalPropability = np.sum(probabilities)

            centerValue = centerProbability[x, y] / totalPropability

            leftSideValue = sideLeftProbability[x, y] / totalPropability
            bottomSideValue = sideBottomProbability[x, y] / totalPropability
            rightSideValue = sideRightProbability[x, y] / totalPropability
            topSideValue = sideTopProbability[x, y] / totalPropability

            bottomLeftCornerValue = cornerBottomLeftProbability[x, y] / totalPropability
            bottomRightCornerValue = cornerBottomRightProbability[x, y] / totalPropability
            topLeftCornerValue = cornerTopLeftProbability[x, y] / totalPropability
            topRightCornerValue = cornerTopRightProbability[x, y] / totalPropability

            adjacentLeftSideValue = borderSideLeftProbability[x, y] / totalPropability
            adjacentBottomSideValue = borderSideBottomProbability[x, y] / totalPropability
            adjacentRightSideValue = borderSideRightProbability[x, y] / totalPropability
            adjacentTopSideValue = borderSideTopProbability[x, y] / totalPropability

            adjacentCornerBottomLeftLeftValue = borderCornerBottomLeftLeftProbability[x, y] / totalPropability
            adjacentCornerBottomLeftBottomValue = borderCornerBottomLeftBottomProbability[x, y] / totalPropability
            adjacentCornerBottomRightBottomValue = borderCornerBottomRightBottomProbability[x, y] / totalPropability
            adjacentCornerBottomRightRightValue = borderCornerBottomRightRightProbability[x, y] / totalPropability
            adjacentCornerTopRightRightValue = borderCornerTopRightRightProbability[x, y] / totalPropability
            adjacentCornerTopRightTopValue = borderCornerTopRightTopProbability[x, y] / totalPropability
            adjacentCornerTopLeftTopValue = borderCornerTopLeftTopProbability[x, y] / totalPropability
            adjacentCornerTopLeftLeftValue = borderCornerTopLeftLeftProbability[x, y] / totalPropability

            centerValue = int(np.floor(MAXVAL * centerValue))

            leftSideValue = int(np.floor(MAXVAL * leftSideValue))
            bottomSideValue = int(np.floor(MAXVAL * bottomSideValue))
            rightSideValue = int(np.floor(MAXVAL * rightSideValue))
            topSideValue = int(np.floor(MAXVAL * topSideValue))

            bottomLeftCornerValue = int(np.floor(MAXVAL * bottomLeftCornerValue))
            bottomRightCornerValue = int(np.floor(MAXVAL * bottomRightCornerValue))
            topLeftCornerValue = int(np.floor(MAXVAL * topLeftCornerValue))
            topRightCornerValue = int(np.floor(MAXVAL * topRightCornerValue))

            adjacentLeftSideValue = int(np.floor(MAXVAL * adjacentLeftSideValue))
            adjacentBottomSideValue = int(np.floor(MAXVAL * adjacentBottomSideValue))
            adjacentRightSideValue = int(np.floor(MAXVAL * adjacentRightSideValue))
            adjacentTopSideValue = int(np.floor(MAXVAL * adjacentTopSideValue))

            adjacentCornerBottomLeftLeftValue = int(np.floor(MAXVAL * adjacentCornerBottomLeftLeftValue))
            adjacentCornerBottomLeftBottomValue = int(np.floor(MAXVAL * adjacentCornerBottomLeftBottomValue))
            adjacentCornerBottomRightBottomValue = int(np.floor(MAXVAL * adjacentCornerBottomRightBottomValue))
            adjacentCornerBottomRightRightValue = int(np.floor(MAXVAL * adjacentCornerBottomRightRightValue))
            adjacentCornerTopRightRightValue = int(np.floor(MAXVAL * adjacentCornerTopRightRightValue))
            adjacentCornerTopRightTopValue = int(np.floor(MAXVAL * adjacentCornerTopRightTopValue))
            adjacentCornerTopLeftTopValue = int(np.floor(MAXVAL * adjacentCornerTopLeftTopValue))
            adjacentCornerTopLeftLeftValue = int(np.floor(MAXVAL * adjacentCornerTopLeftLeftValue))

            # print(centerValue)
            filterCenter.setPixel(x, y, (centerValue, centerValue, centerValue))

            filterSideLeft.setPixel(x, y, (leftSideValue, leftSideValue, leftSideValue))
            filterSideBottom.setPixel(x, y, (bottomSideValue, bottomSideValue, bottomSideValue))
            filterSideRight.setPixel(x, y, (rightSideValue, rightSideValue, rightSideValue))
            filterSideTop.setPixel(x, y, (topSideValue, topSideValue, topSideValue))

            filterCornerBottomLeft.setPixel(x, y, (bottomLeftCornerValue, bottomLeftCornerValue, bottomLeftCornerValue))
            filterCornerBottomRight.setPixel(x, y,
                                             (bottomRightCornerValue, bottomRightCornerValue, bottomRightCornerValue))
            filterCornerTopLeft.setPixel(x, y, (topLeftCornerValue, topLeftCornerValue, topLeftCornerValue))
            filterCornerTopRight.setPixel(x, y, (topRightCornerValue, topRightCornerValue, topRightCornerValue))

            filterAdjacentSideLeft.setPixel(x, y, (adjacentLeftSideValue, adjacentLeftSideValue, adjacentLeftSideValue))
            filterAdjacentSideBottom.setPixel(x, y, (
            adjacentBottomSideValue, adjacentBottomSideValue, adjacentBottomSideValue))
            filterAdjacentSideRight.setPixel(x, y,
                                             (adjacentRightSideValue, adjacentRightSideValue, adjacentRightSideValue))
            filterAdjacentSideTop.setPixel(x, y, (adjacentTopSideValue, adjacentTopSideValue, adjacentTopSideValue))

            filterAdjacentCornerBottomLeftLeft.setPixel(x, y, (
            adjacentCornerBottomLeftLeftValue, adjacentCornerBottomLeftLeftValue, adjacentCornerBottomLeftLeftValue))
            filterAdjacentCornerBottomLeftBottom.setPixel(x, y, (
            adjacentCornerBottomLeftBottomValue, adjacentCornerBottomLeftBottomValue,
            adjacentCornerBottomLeftBottomValue))
            filterAdjacentCornerBottomRightBottom.setPixel(x, y, (
            adjacentCornerBottomRightBottomValue, adjacentCornerBottomRightBottomValue,
            adjacentCornerBottomRightBottomValue))
            filterAdjacentCornerBottomRightRight.setPixel(x, y, (
            adjacentCornerBottomRightRightValue, adjacentCornerBottomRightRightValue,
            adjacentCornerBottomRightRightValue))
            filterAdjacentCornerTopRightRight.setPixel(x, y, (
            adjacentCornerTopRightRightValue, adjacentCornerTopRightRightValue, adjacentCornerTopRightRightValue))
            filterAdjacentCornerTopRightTop.setPixel(x, y, (
            adjacentCornerTopRightTopValue, adjacentCornerTopRightTopValue, adjacentCornerTopRightTopValue))
            filterAdjacentCornerTopLeftTop.setPixel(x, y, (
            adjacentCornerTopLeftTopValue, adjacentCornerTopLeftTopValue, adjacentCornerTopLeftTopValue))
            filterAdjacentCornerTopLeftLeft.setPixel(x, y, (
            adjacentCornerTopLeftLeftValue, adjacentCornerTopLeftLeftValue, adjacentCornerTopLeftLeftValue))




filterCenter.write("models/tile_filter_center.jpg")

filterSideLeft.write("models/tile_filter_side_Left.jpg")
filterSideBottom.write("models/tile_filter_side_Bottom.jpg")
filterSideRight.write("models/tile_filter_side_Right.jpg")
filterSideTop.write("models/tile_filter_side_Top.jpg")

filterCornerBottomLeft.write("models/tile_filter_corner_Bottom_Left.jpg")
filterCornerBottomRight.write("models/tile_filter_corner_Bottom_Right.jpg")
filterCornerTopLeft.write("models/tile_filter_corner_Top_Left.jpg")
filterCornerTopRight.write("models/tile_filter_corner_Top_Right.jpg")

filterAdjacentSideLeft.write("models/tile_filter_adjacent_side_Left.jpg")
filterAdjacentSideBottom.write("models/tile_filter_adjacent_side_Bottom.jpg")
filterAdjacentSideRight.write("models/tile_filter_adjacent_side_Right.jpg")
filterAdjacentSideTop.write("models/tile_filter_adjacent_side_Top.jpg")

filterAdjacentCornerBottomLeftLeft.write("models/tile_filter_adjacent_corner_Bottom_Left_Left.jpg")
filterAdjacentCornerBottomLeftBottom.write("models/tile_filter_adjacent_corner_Bottom_Left_Bottom.jpg")
filterAdjacentCornerBottomRightBottom.write("models/tile_filter_adjacent_corner_Bottom_Right_Bottom.jpg")
filterAdjacentCornerBottomRightRight.write("models/tile_filter_adjacent_corner_Bottom_Right_Right.jpg")
filterAdjacentCornerTopRightRight.write("models/tile_filter_adjacent_corner_Top_Right_Right.jpg")
filterAdjacentCornerTopRightTop.write("models/tile_filter_adjacent_corner_Top_Right_Top.jpg")
filterAdjacentCornerTopLeftTop.write("models/tile_filter_adjacent_corner_Top_Left_Top.jpg")
filterAdjacentCornerTopLeftLeft.write("models/tile_filter_adjacent_corner_Top_Left_Left.jpg")


filterSummed = p3d.PNMImage(RESOLUTION, RESOLUTION)
filterSummed = (filterCenter + filterSideBottom + filterCornerBottomRight)
filterSummed.write("models/tile_filter_summed_sharp.jpg")

myImageGrass = p3d.PNMImage()
#myImageGrass.read("models/grass_3.jpg")
myImageGrass.read("models/green.jpg")

#filterTest = p3d.PNMImage(RESOLUTION, RESOLUTION)
#print(filterTest)
#print(filterCenter)
#print(myImageGrass)
#filterTest = myImageGrass * filterCenter + myImageGrass * filterSideBottom + myImageGrass * filterCornerBottomRight
#filterTest.write("models/tile_filter_Test_sharp.jpg")




