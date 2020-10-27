import numpy as np
#from ... import FluidDynamics as FluidDynamics # Be aware that this needs to change if the folder structure were to change,
import matplotlib.pyplot as plt
import scipy.interpolate as interpolate
import System_Information
if System_Information.OPERATING_SYSTEM == 'windows':
    import cupy as cp
from numba import jit
import numba as nb


class HydrolicErosion():
    def __init__(self,
                 terrain,
                 evaporationRate = 0.05,
                 deltaT = 1,
                 flowSpeed = 0.5,
                 sedimentFlowSpeed = 0.5,
                 gridLength = 1,
                 carryCapacityLimit = 1,
                 erosionRate = 0.5,
                 depositionRate = 0.5,
                 maximumErosionDepth = 10,
                 minimumErosionAngle = 0):
        self.NRows = np.size(terrain, 0)
        self.NColons = np.size(terrain, 1)

        self.deltaT = deltaT
        self.evaporationRate = evaporationRate
        self.flowSpeed = flowSpeed
        self.sedimentFlowSpeed = sedimentFlowSpeed
        self.gridLength = gridLength
        self.carryCapacityLimit = carryCapacityLimit
        self.erosionRate = np.array(erosionRate)
        self.depositionRate = depositionRate
        self.maximumErosionDepth = maximumErosionDepth
        self.minimumErosionAngle = np.pi*minimumErosionAngle/180

        self.terrain = terrain
        self.water = np.zeros((self.NRows, self.NColons, 2))

        self.numberOfLayers = np.size(terrain, axis=2)
        self.layerShape = (np.size(terrain, 0), np.size(terrain, 1))

        #self.water[200, 200, 0] = 100
        #self.water[201, 200, 0] = 100
        #self.water[200, 201, 0] = 100
        #self.water[201, 201, 0] = 100

        self.suspendedSediment = np.zeros((self.NRows, self.NColons, 2))

        self.flow = np.zeros((self.NRows, self.NColons, 4)) # Left, Right, Top, Bottom
        self.velocity = np.zeros((self.NRows, self.NColons, 2)) # x, y
        self.slope = np.zeros((self.NRows, self.NColons))
        self.carryCapacity = np.zeros((self.NRows, self.NColons))
        self.sedimentFlow = np.zeros((self.NRows, self.NColons, 4))  # Left, Right, Top, Bottom

        self.inFlowLeft = np.empty((self.NRows, self.NColons))
        self.inFlowRight = np.empty((self.NRows, self.NColons))
        self.inFlowTop = np.empty((self.NRows, self.NColons))
        self.inFlowBottom = np.empty((self.NRows, self.NColons))

        self.terrainplot = None
        self.waterPlot = None
        self.suspendedSedimentPlot = None

    def Rain(self, numberOfDrops = 1, radius = 1, dropSize = 1, application = 'drop'):
        if application == 'drop':
            for iDrop in range(numberOfDrops):
                row = np.random.randint(0, self.NRows)
                colon = np.random.randint(0, self.NColons)

                dropTilesTemplate = self.rainDropTileTemplate[radius]
                dropWeightsFull = self.rainDropWeightTemplate[radius]

                dropTilesFull = np.zeros(np.shape(dropTilesTemplate), dtype=int)
                dropTilesFull[:, 0] = row + dropTilesTemplate[:, 0]
                dropTilesFull[:, 1] = self.Wrap(colon + dropTilesTemplate[:, 1], self.NColons)

                dropTiles = []
                dropWeights = []
                for tile, weight in zip(dropTilesFull, dropWeightsFull):
                    if tile[0] >= 0 and tile[0] < self.NRows:
                        dropTiles.append(tile)
                        dropWeights.append(weight)
                dropTiles = np.array(dropTiles)
                dropWeights = np.array(dropWeights)

                self.water[dropTiles[:, 0], dropTiles[:, 1], 0] += self.deltaT*dropSize*dropWeights
        elif application == 'even':
            self.water[:, :, 0] += numberOfDrops*dropSize

    def UpdateFlow(self):
        deltaHeightLeft = self.CalculateDeltaHeight('left')
        newFlowLeft = self.flow[:, :, 0] + self.deltaT*self.flowSpeed*deltaHeightLeft
        newFlowLeft[newFlowLeft < 0] = 0

        deltaHeightRight = self.CalculateDeltaHeight('right')
        newFlowRight = self.flow[:, :, 1] + self.deltaT*self.flowSpeed*deltaHeightRight
        newFlowRight[newFlowRight < 0] = 0

        deltaHeightTop = self.CalculateDeltaHeight('top')
        newFlowTop = self.flow[:, :, 2] + self.deltaT*self.flowSpeed*deltaHeightTop
        newFlowTop[newFlowTop < 0] = 0

        deltaHeightBottom = self.CalculateDeltaHeight('bottom')
        newFlowBottom = self.flow[:, :, 3] + self.deltaT*self.flowSpeed*deltaHeightBottom
        newFlowBottom[newFlowBottom < 0] = 0

        #newFlowLeft[newFlowLeft < newFlowRight] = 0
        #newFlowRight[newFlowRight < newFlowLeft] = 0
        #newFlowBottom[newFlowBottom < newFlowTop] = 0
        #newFlowTop[newFlowTop < newFlowBottom] = 0

        self.flow[:, :, 0] = newFlowLeft
        self.flow[:, :, 1] = newFlowRight
        self.flow[:, :, 2] = newFlowTop
        self.flow[:, :, 3] = newFlowBottom


        # The 0.9 is to reduce instability in the flow simulation.
        flowScaling = self.water[:, :, 0]/((self.flow[:, :, 0] + self.flow[:, :, 1] + self.flow[:, :, 2] + self.flow[:, :, 3]+0.001)*self.deltaT)
        flowScaling[flowScaling>1] = 1

        #maxFlow = np.max((deltaHeightLeft, deltaHeightRight, deltaHeightTop, deltaHeightBottom))/10
        #flowScaling[flowScaling > maxFlow] = maxFlow
        self.flow[:, :, 0] *= flowScaling
        self.flow[:, :, 1] *= flowScaling
        self.flow[:, :, 2] *= flowScaling
        self.flow[:, :, 3] *= flowScaling


        self.inFlowRight[:, 0:self.NColons-1] = self.flow[:, 1:self.NColons, 0]
        self.inFlowRight[:, self.NColons-1:self.NColons] = self.flow[:, 0:1, 0]

        self.inFlowLeft[:, 0:1] = self.flow[:, self.NColons - 1:self.NColons, 1]
        self.inFlowLeft[:, 1:self.NColons] = self.flow[:, 0:-1, 1]

        self.inFlowBottom[0:1, :] = self.flow[self.NRows - 1:self.NRows, :, 2]
        self.inFlowBottom[1:self.NRows, :] = self.flow[0:-1, :, 2]

        self.inFlowTop[0:self.NRows-1, :] = self.flow[1:self.NRows, :, 3]
        self.inFlowTop[self.NRows-1:self.NRows, :] = self.flow[0:1, :, 3]
        '''

        self.inFlowRight = np.concatenate((self.flow[:, 1:self.NColons, 0],
                                      self.flow[:, 0:1, 0]),
                                     axis=1)
        self.inFlowLeft = np.concatenate((self.flow[:, self.NColons - 1:self.NColons, 1],
                                      self.flow[:, 0:-1, 1]),
                                     axis=1)
        self.inFlowBottom = np.concatenate((self.flow[self.NRows - 1:self.NRows, :, 2],
                                       self.flow[0:-1, :, 2]),
                                      axis=0)
        self.inFlowTop = np.concatenate((self.flow[1:self.NRows, :, 3],
                                    self.flow[0:1, :, 3]),
                                   axis=0)
        '''
    def CalculateDeltaHeight(self, direction = 'left'):
        totalHeight =np.sum(self.terrain, 2) + self.water[:, :, 0]

        if direction == 'left':
            totalHeightWrapped = np.concatenate((totalHeight[:, self.NColons - 1:self.NColons],
                                                 totalHeight[:, 0:-1]),
                                                axis=1)
        elif direction == 'right':
            totalHeightWrapped = np.concatenate((totalHeight[:, 1:self.NColons],
                                                 totalHeight[:, 0:1]),
                                                axis=1)
        elif direction == 'top':
            totalHeightWrapped = np.concatenate((totalHeight[1:self.NRows, :],
                                                 totalHeight[self.NRows-1:self.NRows, :]),
                                                axis=0)
        elif direction == 'bottom':
            totalHeightWrapped = np.concatenate((totalHeight[0:1, :],
                                                 totalHeight[0:self.NRows-1, :]),
                                                axis=0)
        return totalHeight - totalHeightWrapped

    def UpdateWaterHeight(self):
        self.water[:, :, 1] = self.water[:, :, 0] + self.deltaT*(- (
                self.flow[:, :, 0] + self.flow[:, :, 1] + self.flow[:, :, 2] + self.flow[:, :,3]) + \
                              self.inFlowLeft + self.inFlowRight + self.inFlowTop + self.inFlowBottom)
        #self.water[:, :, 1] = self.water[:, :, 0] + self.deltaT*(- (self.flow[:, :, 0] + self.flow[:, :, 1]) + self.inFlowLeft + self.inFlowRight)
        #self.water[:, :, 1] = self.water[:, :, 0] + self.deltaT * (- (self.flow[:, :, 1]) + self.inFlowLeft)
        #self.water[:, :, 1] = self.water[:, :, 0] + self.deltaT * (- (self.flow[:, :, 0]) + self.inFlowRight)
        #self.water[:, :, 1] = self.water[:, :, 0] + self.deltaT*(- (self.flow[:, :, 2] + self.flow[:, :,3]) + self.inFlowTop + self.inFlowBottom)

    def UpdateVelocity(self):
        self.velocity[:, :, 0] = (self.flow[:, :, 1] - self.flow[:, :, 0] + self.inFlowLeft - self.inFlowRight)/2
        self.velocity[:, :, 1] = (self.flow[:, :, 2] - self.flow[:, :, 3] + self.inFlowBottom - self.inFlowTop)/2
        #self.velocity[:, :, 0] = (self.flow[:, :, 1] - self.flow[:, :, 0] + self.inFlowLeft - self.inFlowRight)/\
        #                         (self.water[:, :, 0] + self.water[:, :, 1]+0.001)
        #self.velocity[:, :, 1] = (self.flow[:, :, 2] - self.flow[:, :, 3] + self.inFlowBottom - self.inFlowTop)/\
        #                         (self.water[:, :, 0] + self.water[:, :, 1]+0.001)
    '''
    def UpdateSlope(self):
        self.terrainLeft = np.concatenate((self.terrain[:, self.NColons - 1:self.NColons],
                                      self.terrain[:, 0:-1]),
                                     axis=1)
        self.terrainRight = np.concatenate((self.terrain[:, 1:self.NColons],
                                       self.terrain[:, 0:1]),
                                      axis=1)
        xAngle = np.arctan((self.terrainRight-self.terrainLeft)/ (2*self.gridLength))

        self.terrainTop = np.concatenate((self.terrain[1:self.NRows, :],
                                     self.terrain[self.NRows-1:self.NRows, :]),
                                    axis=0)
        self.terrainBottom = np.concatenate((self.terrain[0:1, :],
                                        self.terrain[0:self.NRows-1, :]),
                                       axis = 0)
        yAngle = np.arctan((self.terrainTop-self.terrainBottom)/(2*self.gridLength))

        self.slope = np.sqrt(xAngle**2 + yAngle**2)/np.sqrt(2)
    '''

    def UpdateSlope(self):
        totalHeight = np.sum(self.terrain, 2)

        self.terrainLeft = np.concatenate((totalHeight[:, self.NColons - 1:self.NColons],
                                      totalHeight[:, 0:-1]),
                                     axis=1)
        self.terrainRight = np.concatenate((totalHeight[:, 1:self.NColons],
                                       totalHeight[:, 0:1]),
                                      axis=1)
        #xAngle = np.arctan((self.terrainRight-self.terrainLeft)/ (2*self.gridLength))

        self.terrainTop = np.concatenate((totalHeight[1:self.NRows, :],
                                     totalHeight[self.NRows-1:self.NRows, :]),
                                    axis=0)
        self.terrainBottom = np.concatenate((totalHeight[0:1, :],
                                        totalHeight[0:self.NRows-1, :]),
                                       axis = 0)
        #yAngle = np.arctan((self.terrainTop-self.terrainBottom)/(2*self.gridLength))


        self.slope = np.arctan(np.gradient(totalHeight))
        r = np.sqrt(self.slope[0] ** 2 + self.slope[1] ** 2)
        self.slope = np.sqrt(self.slope[0] ** 4 + self.slope[1] ** 4)/r
        self.slope[r == 0] = 0

    def UpdateCarryCapacity(self):
        '''
        The carry capacity depends on the water depth. At water > mamimumErosionDepth the capacity is zero.
        :return:
        '''
        #waterDepthMultiplier = self.water[:, :, 1]*2.5
        waterDepthMultiplier = np.ones(np.shape(self.water[:, :, 1]))
        #waterDepthMultiplier = 10*self.water[:, :, 1]*(1-self.water[:, :, 1]/self.maximumErosionDepth)/self.maximumErosionDepth
        waterDepthMultiplier[self.water[:, :, 1] > self.maximumErosionDepth] = 0
        #slopeMultiplier = np.sin(self.slope)
        slopeMultiplier = np.sin((self.slope - self.minimumErosionAngle) /
                                 (np.pi / 2 - self.minimumErosionAngle) * np.pi / 2)
        slopeMultiplier[self.slope < self.minimumErosionAngle] = 0
        #self.carryCapacity =  waterDepthMultiplier * self.carryCapacityLimit * slopeMultiplier * np.sqrt(self.velocity[:, :, 0]**2 + self.velocity[:, :, 1]**2)
        self.carryCapacity = self.carryCapacityLimit * slopeMultiplier * np.sqrt(self.velocity[:, :, 0]**2 + self.velocity[:, :, 1]**2)
        #self.carryCapacity = self.carryCapacityLimit * np.sqrt(self.velocity[:, :, 0] ** 2 + self.velocity[:, :, 1] ** 2)
        self.suspendedSediment[:, :, 1] = self.suspendedSediment[:, :, 0]

    def Erode(self):
        #erosionAlreadyDone = np.ones(self.layerShape)
        erodedSediment = self.deltaT * (self.carryCapacity - self.suspendedSediment[:, :, 0])
        erodedSediment[erodedSediment < 0] = 0
        for iLayer in np.linspace(self.numberOfLayers-1, 0, self.numberOfLayers, dtype=int):
            erodedSediment *= self.erosionRate[iLayer]

            #erodedSediment = self.deltaT*self.erosionRate[iLayer]*(self.carryCapacity - self.suspendedSediment[:, :, 0])
            #erodedSediment[erodedSediment < 0] = 0

            #erosionLimit = self.water[:, :, 1] - 2*self.suspendedSediment[:, :, 0]
            #erodedSediment[erodedSediment > erosionLimit] = erosionLimit[erodedSediment > erosionLimit]


            lowestAdjacentHeight = np.zeros((self.NRows, self.NColons, 4))
            lowestAdjacentHeight[:, :, 0] = self.terrainLeft
            lowestAdjacentHeight[:, :, 1] = self.terrainRight
            lowestAdjacentHeight[:, :, 2] = self.terrainTop
            lowestAdjacentHeight[:, :, 3] = self.terrainBottom
            lowestAdjacentHeight = np.min(lowestAdjacentHeight, axis=2)

            maximumErosion = np.sum(self.terrain, 2) - lowestAdjacentHeight
            erodedSediment[erodedSediment > maximumErosion] = maximumErosion[erodedSediment > maximumErosion]


            self.terrain[:, :, iLayer] -= erodedSediment
            erodedSediment = self.terrain[:, :, iLayer].copy()
            erodedSediment[erodedSediment >= 0] = 0
            erodedSediment *= -1/self.erosionRate[iLayer]

            if iLayer == 0:
                # rock decreases in density as it is eroded.
                self.suspendedSediment[:, :, 1] += 2*erodedSediment
            else:
                self.suspendedSediment[:, :, 1] += erodedSediment
            #self.water[:, :, 1] += erodedSediment

    def Deposit(self):
        depositedSediment = self.deltaT*self.depositionRate * (self.suspendedSediment[:, :, 0] - self.carryCapacity)
        depositedSediment[depositedSediment < 0] = 0
        #minDepos = 0.1 * self.suspendedSediment[:, :, 0]
        #depositedSediment[depositedSediment < minDepos] = minDepos[depositedSediment < minDepos]


        highestAdjacentHeight = np.zeros((self.NRows, self.NColons, 4))
        highestAdjacentHeight[:, :, 0] = self.terrainLeft
        highestAdjacentHeight[:, :, 1] = self.terrainRight
        highestAdjacentHeight[:, :, 2] = self.terrainTop
        highestAdjacentHeight[:, :, 3] = self.terrainBottom
        highestAdjacentHeight = np.max(highestAdjacentHeight, axis=2)

        maximumDeposition = highestAdjacentHeight - np.sum(self.terrain, 2)
        depositedSediment[depositedSediment > maximumDeposition] = maximumDeposition[depositedSediment > maximumDeposition]


        self.terrain[:, :, -1] += depositedSediment
        self.suspendedSediment[:, :, 1] -= depositedSediment
        #self.water[:, :, 1] -= depositedSediment

    def SedimentTransportation(self):
        self.sedimentFlow = self.sedimentFlowSpeed * self.flow.copy()

        flowScaling = self.suspendedSediment[:, :, 1] / ((self.sedimentFlow[:, :, 0] + self.sedimentFlow[:, :, 1] + self.sedimentFlow[:, :,
                                                                                        2] + self.sedimentFlow[:, :,
                                                                                             3] + 0.001) * self.deltaT)
        flowScaling[flowScaling > 1] = 1

        #sedimentFlow = self.flow.copy()

        self.sedimentFlow[:, :, 0] *= flowScaling
        self.sedimentFlow[:, :, 1] *= flowScaling
        self.sedimentFlow[:, :, 2] *= flowScaling
        self.sedimentFlow[:, :, 3] *= flowScaling

        sedimentInFlowRight = np.concatenate((self.sedimentFlow[:, 1:self.NColons, 0],
                                           self.sedimentFlow[:, 0:1, 0]),
                                          axis=1)
        sedimentInFlowLeft = np.concatenate((self.sedimentFlow[:, self.NColons - 1:self.NColons, 1],
                                          self.sedimentFlow[:, 0:-1, 1]),
                                         axis=1)
        sedimentInFlowBottom = np.concatenate((self.sedimentFlow[self.NRows - 1:self.NRows, :, 2],
                                            self.sedimentFlow[0:-1, :, 2]),
                                           axis=0)
        sedimentInFlowTop = np.concatenate((self.sedimentFlow[1:self.NRows, :, 3],
                                         self.sedimentFlow[0:1, :, 3]),
                                        axis=0)

        sedimentOut = self.deltaT * (self.sedimentFlow[:, :, 0] + self.sedimentFlow[:, :, 1] + self.sedimentFlow[:, :, 2] + self.sedimentFlow[:, :, 3])
        sedimentIn = self.deltaT * (sedimentInFlowLeft + sedimentInFlowRight + sedimentInFlowTop + sedimentInFlowBottom)

        self.suspendedSediment[:, :, 0] = self.suspendedSediment[:, :, 1] - sedimentOut + sedimentIn
        #self.water[:, :, 1] -= sedimentOut
        #self.water[:, :, 1] += sedimentIn

    def Evaporation(self):
        self.water[:, :, 0] = self.water[:, :, 1]*(1 - self.evaporationRate*self.deltaT)

    def __call__(self):
        self.UpdateFlow()
        self.UpdateWaterHeight()
        self.UpdateVelocity()

        self.UpdateSlope()

        self.UpdateCarryCapacity()
        self.Erode()
        self.Deposit()
        self.SedimentTransportation()
        self.Evaporation()

    def Visualize(self):
        if self.terrainplot == None:
            if False:
                self.terrainplot = plt.imshow(np.sum(self.terrain, 2))
            else:
                fig, axs = plt.subplots(3, 2)

                self.terrainplot = axs[0][0].imshow(np.sum(self.terrain, 2))
                self.waterPlot = axs[1][0].imshow(self.water[:, :, 0])
                self.totalHeightPlot = axs[2][0].imshow(np.sum(self.terrain, 2) + self.water[:, :, 0])
                self.suspendedSedimentPlot = axs[0][1].imshow(self.suspendedSediment[:, :, 0])
                self.slopeplot = axs[1][1].imshow(180*self.slope/np.pi)
                self.slopeplot.set_clim(vmin=0, vmax=90)
                self.velocityPlot = axs[2, 1].imshow(np.sqrt(self.velocity[:, :, 0]**2 + self.velocity[:, :, 1]**2))

            plt.pause(0.00001)
        else:
            if False:
                self.terrainplot.set_array(np.sum(self.terrain, 2))
                #self.terrainplot.set_clim(vmin=np.min(self.terrain), vmax=np.max(self.terrain))
            else:
                self.terrainplot.set_array(np.sum(self.terrain, 2))
                self.terrainplot.set_clim(vmin=np.min(np.sum(self.terrain, 2)), vmax=np.max(np.sum(self.terrain, 2)))
                self.waterPlot.set_array(self.water[:, :, 0])
                self.totalHeightPlot.set_array(np.sum(self.terrain, 2) + self.water[:, :, 0])
                #self.waterPlot.set_clim(vmin = 0, vmax = np.max(self.water[:, :, 0]))
                self.waterPlot.set_clim(vmin=0, vmax=20)
                self.suspendedSedimentPlot.set_array(self.suspendedSediment[:, :, 0])
                self.suspendedSedimentPlot.set_clim(vmin=0, vmax=2)
                self.slopeplot.set_array(180*self.slope/np.pi)
                self.velocityPlot.set_array(np.sqrt(self.velocity[:, :, 0]**2 + self.velocity[:, :, 1]**2))
                self.velocityPlot.set_clim(vmin=0, vmax=10)

            plt.pause(0.00001)

    @classmethod
    def Wrap(cls, value, wrapValue):
        return np.mod(value, wrapValue)

    @classmethod
    def InitializeRainDropTemplates(cls, maximumRainDropRadius = 1):
        # Initializes lists used as templates when creating rain drops.
        cls.rainDropWeightTemplate = []
        cls.rainDropTileTemplate = []

        for radius in range(0, maximumRainDropRadius+1):
            rows = range(-radius, radius, 1)
            columns = range(-radius, radius, 1)
            rowGrid, columnGrid = np.meshgrid(rows, columns)
            rowList = np.reshape(rowGrid, [rowGrid.size, 1])
            columnList = np.reshape(columnGrid, [columnGrid.size, 1])
            distances = np.sqrt(rowList ** 2 + columnList ** 2)
            rowList = rowList[distances < radius]
            columnList = columnList[distances < radius]

            # The template lists are expanded.
            cls.rainDropWeightTemplate.append(
                (radius - distances[distances < radius]) / np.sum(radius - distances[distances < radius]))

            erosionTiles = np.zeros((cls.rainDropWeightTemplate[radius].shape[0], 2))
            erosionTiles[:, 0] = rowList
            erosionTiles[:, 1] = columnList
            cls.rainDropTileTemplate.append(erosionTiles)

class HydrolicErosion2():
    def __init__(self,
                 terrain,
                 evaporationRate = 0.05,
                 deltaT = 1,
                 flowSpeed = 0.5,
                 sedimentFlowSpeed = 0.5,
                 gridLength = 1,
                 carryCapacityCoefficient = 1,
                 erosionRate = 0.5,
                 disolveRate = 0.1,
                 depositionRate = 0.5,
                 maximumErosionDepth = 10,
                 minimumErosionAngle = 0,
                 erosionWithoutSediment = 1,
                 erosionWithSedimentMax = 5,
                 bedrockHardness = 100000):
        self.NRows = np.size(terrain, 0)
        self.NColons = np.size(terrain, 1)

        self.deltaT = deltaT
        self.evaporationRate = evaporationRate
        self.flowSpeed = flowSpeed
        self.sedimentFlowSpeed = sedimentFlowSpeed
        self.gridLength = gridLength
        self.carryCapacityCoefficient = carryCapacityCoefficient
        self.erosionRate = np.array(erosionRate)
        self.disolveRate = disolveRate
        self.depositionRate = depositionRate
        self.maximumErosionDepth = maximumErosionDepth
        self.minimumErosionAngle = np.pi*minimumErosionAngle/180
        self.bedrockHardness = bedrockHardness

        self.erosionWithSedimentMax = erosionWithSedimentMax
        self.erosionSedimentScalingParameters = [np.arcsin(np.sqrt( erosionWithoutSediment/erosionWithSedimentMax ))]
        self.erosionSedimentScalingParameters.append(np.pi - self.erosionSedimentScalingParameters[0])

        self.terrain = terrain
        self.water = np.zeros((self.NRows, self.NColons, 2))
        self.terrainTotal = np.sum(self.terrain, axis=2)

        self.numberOfLayers = np.size(terrain, axis=2)
        self.layerShape = (np.size(terrain, 0), np.size(terrain, 1))

        #self.water[200, 200, 0] = 100
        #self.water[201, 200, 0] = 100
        #self.water[200, 201, 0] = 100
        #self.water[201, 201, 0] = 100

        self.suspendedSediment = np.zeros((self.NRows, self.NColons, 2))

        self.flow = np.zeros((self.NRows, self.NColons, 4)) # Left, Right, Top, Bottom
        self.velocity = np.zeros((self.NRows, self.NColons, 2)) # x, y
        self.slope = np.zeros((self.NRows, self.NColons))
        self.carryCapacity = np.zeros((self.NRows, self.NColons))
        self.sedimentFlow = np.zeros((self.NRows, self.NColons, 4))  # Left, Right, Top, Bottom

        self.inFlowLeft = np.empty((self.NRows, self.NColons))
        self.inFlowRight = np.empty((self.NRows, self.NColons))
        self.inFlowTop = np.empty((self.NRows, self.NColons))
        self.inFlowBottom = np.empty((self.NRows, self.NColons))

        self.terrainplot = None
        self.waterPlot = None
        self.suspendedSedimentPlot = None

    def Rain(self, numberOfDrops = 1, radius = 1, dropSize = 1, application = 'drop'):
        if application == 'drop':
            for iDrop in range(numberOfDrops):
                row = np.random.randint(0, self.NRows)
                colon = np.random.randint(0, self.NColons)

                dropTilesTemplate = self.rainDropTileTemplate[radius]
                dropWeightsFull = self.rainDropWeightTemplate[radius]

                dropTilesFull = np.zeros(np.shape(dropTilesTemplate), dtype=int)
                dropTilesFull[:, 0] = row + dropTilesTemplate[:, 0]
                dropTilesFull[:, 1] = self.Wrap(colon + dropTilesTemplate[:, 1], self.NColons)

                dropTiles = []
                dropWeights = []
                for tile, weight in zip(dropTilesFull, dropWeightsFull):
                    if tile[0] >= 0 and tile[0] < self.NRows:
                        dropTiles.append(tile)
                        dropWeights.append(weight)
                dropTiles = np.array(dropTiles)
                dropWeights = np.array(dropWeights)

                self.water[dropTiles[:, 0], dropTiles[:, 1], 0] += self.deltaT*dropSize*dropWeights
        elif application == 'even':
            self.water[:, :, 0] += numberOfDrops*dropSize

    def UpdateTotalTerrain(self):
        self.terrainTotal = np.sum(self.terrain, axis=2) + self.water[:, :, 0]

    def UpdateFlow(self):
        deltaHeightLeft = self.CalculateDeltaHeight('left')
        newFlowLeft = self.flow[:, :, 0] + self.deltaT*self.flowSpeed*deltaHeightLeft
        newFlowLeft[newFlowLeft < 0] = 0

        deltaHeightRight = self.CalculateDeltaHeight('right')
        newFlowRight = self.flow[:, :, 1] + self.deltaT*self.flowSpeed*deltaHeightRight
        newFlowRight[newFlowRight < 0] = 0

        deltaHeightTop = self.CalculateDeltaHeight('top')
        newFlowTop = self.flow[:, :, 2] + self.deltaT*self.flowSpeed*deltaHeightTop
        newFlowTop[newFlowTop < 0] = 0

        deltaHeightBottom = self.CalculateDeltaHeight('bottom')
        newFlowBottom = self.flow[:, :, 3] + self.deltaT*self.flowSpeed*deltaHeightBottom
        newFlowBottom[newFlowBottom < 0] = 0

        #newFlowLeft[newFlowLeft < newFlowRight] = 0
        #newFlowRight[newFlowRight < newFlowLeft] = 0
        #newFlowBottom[newFlowBottom < newFlowTop] = 0
        #newFlowTop[newFlowTop < newFlowBottom] = 0

        self.flow[:, :, 0] = newFlowLeft
        self.flow[:, :, 1] = newFlowRight
        self.flow[:, :, 2] = newFlowTop
        self.flow[:, :, 3] = newFlowBottom


        # The 0.9 is to reduce instability in the flow simulation.
        flowScaling = self.water[:, :, 0]/((self.flow[:, :, 0] + self.flow[:, :, 1] + self.flow[:, :, 2] + self.flow[:, :, 3]+0.001)*self.deltaT)
        flowScaling[flowScaling>1] = 1

        #maxFlow = np.max((deltaHeightLeft, deltaHeightRight, deltaHeightTop, deltaHeightBottom))/10
        #flowScaling[flowScaling > maxFlow] = maxFlow
        self.flow[:, :, 0] *= flowScaling
        self.flow[:, :, 1] *= flowScaling
        self.flow[:, :, 2] *= flowScaling
        self.flow[:, :, 3] *= flowScaling


        self.inFlowRight[:, 0:self.NColons-1] = self.flow[:, 1:self.NColons, 0]
        self.inFlowRight[:, self.NColons-1:self.NColons] = self.flow[:, 0:1, 0]

        self.inFlowLeft[:, 0:1] = self.flow[:, self.NColons - 1:self.NColons, 1]
        self.inFlowLeft[:, 1:self.NColons] = self.flow[:, 0:-1, 1]

        self.inFlowBottom[0:1, :] = self.flow[self.NRows - 1:self.NRows, :, 2]
        self.inFlowBottom[1:self.NRows, :] = self.flow[0:-1, :, 2]

        self.inFlowTop[0:self.NRows-1, :] = self.flow[1:self.NRows, :, 3]
        self.inFlowTop[self.NRows-1:self.NRows, :] = self.flow[0:1, :, 3]
        '''

        self.inFlowRight = np.concatenate((self.flow[:, 1:self.NColons, 0],
                                      self.flow[:, 0:1, 0]),
                                     axis=1)
        self.inFlowLeft = np.concatenate((self.flow[:, self.NColons - 1:self.NColons, 1],
                                      self.flow[:, 0:-1, 1]),
                                     axis=1)
        self.inFlowBottom = np.concatenate((self.flow[self.NRows - 1:self.NRows, :, 2],
                                       self.flow[0:-1, :, 2]),
                                      axis=0)
        self.inFlowTop = np.concatenate((self.flow[1:self.NRows, :, 3],
                                    self.flow[0:1, :, 3]),
                                   axis=0)
        '''
    def CalculateDeltaHeight(self, direction = 'left'):
        #totalHeight =np.sum(self.terrain, 2) + self.water[:, :, 0]

        if direction == 'left':
            totalHeightWrapped = np.concatenate((self.terrainTotal[:, self.NColons - 1:self.NColons],
                                                 self.terrainTotal[:, 0:-1]),
                                                axis=1)
        elif direction == 'right':
            totalHeightWrapped = np.concatenate((self.terrainTotal[:, 1:self.NColons],
                                                 self.terrainTotal[:, 0:1]),
                                                axis=1)
        elif direction == 'top':
            totalHeightWrapped = np.concatenate((self.terrainTotal[1:self.NRows, :],
                                                 self.terrainTotal[self.NRows-1:self.NRows, :]),
                                                axis=0)
        elif direction == 'bottom':
            totalHeightWrapped = np.concatenate((self.terrainTotal[0:1, :],
                                                 self.terrainTotal[0:self.NRows-1, :]),
                                                axis=0)
        return self.terrainTotal - totalHeightWrapped

    def UpdateWaterHeight(self):
        self.water[:, :, 1] = self.water[:, :, 0] + self.deltaT*(- (
                self.flow[:, :, 0] + self.flow[:, :, 1] + self.flow[:, :, 2] + self.flow[:, :,3]) + \
                              self.inFlowLeft + self.inFlowRight + self.inFlowTop + self.inFlowBottom)
        #self.water[:, :, 1] = self.water[:, :, 0] + self.deltaT*(- (self.flow[:, :, 0] + self.flow[:, :, 1]) + self.inFlowLeft + self.inFlowRight)
        #self.water[:, :, 1] = self.water[:, :, 0] + self.deltaT * (- (self.flow[:, :, 1]) + self.inFlowLeft)
        #self.water[:, :, 1] = self.water[:, :, 0] + self.deltaT * (- (self.flow[:, :, 0]) + self.inFlowRight)
        #self.water[:, :, 1] = self.water[:, :, 0] + self.deltaT*(- (self.flow[:, :, 2] + self.flow[:, :,3]) + self.inFlowTop + self.inFlowBottom)

    def UpdateVelocity(self):
        self.velocity[:, :, 0] = (self.flow[:, :, 1] - self.flow[:, :, 0] + self.inFlowLeft - self.inFlowRight)/2
        self.velocity[:, :, 1] = (self.flow[:, :, 2] - self.flow[:, :, 3] + self.inFlowBottom - self.inFlowTop)/2
        #self.velocity[:, :, 0] = (self.flow[:, :, 1] - self.flow[:, :, 0] + self.inFlowLeft - self.inFlowRight)/\
        #                         (self.water[:, :, 0] + self.water[:, :, 1]+0.00001)
        #self.velocity[:, :, 1] = (self.flow[:, :, 2] - self.flow[:, :, 3] + self.inFlowBottom - self.inFlowTop)/\
        #                         (self.water[:, :, 0] + self.water[:, :, 1]+0.00001)

    '''
    def UpdateSlope(self):
        self.terrainLeft = np.concatenate((self.terrain[:, self.NColons - 1:self.NColons],
                                      self.terrain[:, 0:-1]),
                                     axis=1)
        self.terrainRight = np.concatenate((self.terrain[:, 1:self.NColons],
                                       self.terrain[:, 0:1]),
                                      axis=1)
        xAngle = np.arctan((self.terrainRight-self.terrainLeft)/ (2*self.gridLength))

        self.terrainTop = np.concatenate((self.terrain[1:self.NRows, :],
                                     self.terrain[self.NRows-1:self.NRows, :]),
                                    axis=0)
        self.terrainBottom = np.concatenate((self.terrain[0:1, :],
                                        self.terrain[0:self.NRows-1, :]),
                                       axis = 0)
        yAngle = np.arctan((self.terrainTop-self.terrainBottom)/(2*self.gridLength))

        self.slope = np.sqrt(xAngle**2 + yAngle**2)/np.sqrt(2)
    '''

    def UpdateSlope(self):
        gradient = np.arctan(np.gradient(self.terrainTotal))
        self.slope = np.sqrt((gradient[0] ** 4 + gradient[1] ** 4) / (gradient[0] ** 2 + gradient[1] ** 2 + 0.0001))

    def UpdateCarryCapacity(self):
        # 10000 ~= 9.82 * 1000 <=> gravity * water density
        self.streamPower = 10000 * np.sin(self.slope) * np.sqrt(self.velocity[:, :, 0]**2 + self.velocity[:, :, 1]**2)
        #self.carryCapacity = self.carryCapacityCoefficient * self.streamPower * self.water[:, :, 1]
        self.carryCapacity = self.carryCapacityCoefficient * self.streamPower

        # The carry capacity cannot be larger than the water level.
        self.carryCapacity[self.carryCapacity > self.water[:, :, 1]] = self.water[self.carryCapacity > self.water[:, :, 1], 1]

    def Erode(self):
        '''
        An article defining an equation for erosion rate.
        https://onlinelibrary.wiley.com/doi/abs/10.1002/esp.4467
        :return:
        '''

        sedimentScaling = self.erosionWithSedimentMax * np.sin( self.erosionSedimentScalingParameters[0] + self.erosionSedimentScalingParameters[1]*self.terrain[:, :, -1]/self.maximumErosionDepth )**2
        #sedimentScaling[sedimentScaling < 0] = 0
        sedimentScaling[self.terrain[:, :, 1] + self.terrain[:, :, 2]>self.maximumErosionDepth] = 0
        erosionStrength = self.streamPower * sedimentScaling

        erosionAmount = self.erosionRate*(erosionStrength/self.bedrockHardness - 1)
        erosionAmount[erosionAmount < 0] = 0

        '''
        terrainTotal = self.terrain[:, :, 0]
        terrainLeft = np.concatenate((terrainTotal[:, self.NColons - 1:self.NColons],
                                      terrainTotal[:, 0:-1]),
                                     axis=1)
        terrainRight = np.concatenate((terrainTotal[:, 1:self.NColons],
                                       terrainTotal[:, 0:1]),
                                      axis=1)
        terrainTop = np.concatenate((terrainTotal[1:self.NRows, :],
                                     terrainTotal[self.NRows-1:self.NRows, :]),
                                    axis=0)
        terrainBottom = np.concatenate((terrainTotal[0:1, :],
                                        terrainTotal[0:self.NRows-1, :]),
                                       axis = 0)

        lowestAdjacentHeight = np.zeros((self.NRows, self.NColons, 4))
        lowestAdjacentHeight[:, :, 0] = terrainLeft
        lowestAdjacentHeight[:, :, 1] = terrainRight
        lowestAdjacentHeight[:, :, 2] = terrainTop
        lowestAdjacentHeight[:, :, 3] = terrainBottom
        lowestAdjacentHeight = np.min(lowestAdjacentHeight, axis=2)
        
        maximumErosion = self.terrain[:, :, 0] - lowestAdjacentHeight
        erosionAmount[erosionAmount > maximumErosion] = maximumErosion[erosionAmount > maximumErosion]
        erosionAmount[maximumErosion<0] = 0
        '''

        self.terrain[:, :, 0] -= erosionAmount
        self.terrain[:, :, 1] += erosionAmount

    def Disolve(self):
        # erosionAlreadyDone = np.ones(self.layerShape)
        erodedSediment = self.deltaT * self.disolveRate * (self.carryCapacity - self.terrain[:, :, 2])
        erodedSediment[erodedSediment < 0] = 0

        '''
        lowestAdjacentHeight = np.zeros((self.NRows, self.NColons, 4))
        lowestAdjacentHeight[:, :, 0] = self.terrainLeft
        lowestAdjacentHeight[:, :, 1] = self.terrainRight
        lowestAdjacentHeight[:, :, 2] = self.terrainTop
        lowestAdjacentHeight[:, :, 3] = self.terrainBottom
        lowestAdjacentHeight = np.min(lowestAdjacentHeight, axis=2)

        maximumErosion = np.sum(self.terrain, 2) - lowestAdjacentHeight
        erodedSediment[erodedSediment > maximumErosion] = maximumErosion[erodedSediment > maximumErosion]
        '''

        self.terrain[:, :, 1] -= erodedSediment
        self.terrain[:, :, 2] += erodedSediment

    def Deposit(self):
        depositedSediment = self.deltaT * self.depositionRate * (self.suspendedSediment[:, :, 0] - self.carryCapacity)
        depositedSediment[depositedSediment < 0] = 0
        #minDepos = 0.3 * self.terrain[:, :, 2]
        #depositedSediment[depositedSediment < minDepos] = minDepos[depositedSediment < minDepos]

        totalHeight = np.sum(self.terrain, 2)
        self.terrainLeft = np.concatenate((totalHeight[:, self.NColons - 1:self.NColons],
                                      totalHeight[:, 0:-1]),
                                     axis=1)
        self.terrainRight = np.concatenate((totalHeight[:, 1:self.NColons],
                                       totalHeight[:, 0:1]),
                                      axis=1)
        self.terrainTop = np.concatenate((totalHeight[1:self.NRows, :],
                                     totalHeight[self.NRows-1:self.NRows, :]),
                                    axis=0)
        self.terrainBottom = np.concatenate((totalHeight[0:1, :],
                                        totalHeight[0:self.NRows-1, :]),
                                       axis = 0)

        highestAdjacentHeight = np.zeros((self.NRows, self.NColons, 4))
        highestAdjacentHeight[:, :, 0] = self.terrainLeft
        highestAdjacentHeight[:, :, 1] = self.terrainRight
        highestAdjacentHeight[:, :, 2] = self.terrainTop
        highestAdjacentHeight[:, :, 3] = self.terrainBottom
        highestAdjacentHeight = np.max(highestAdjacentHeight, axis=2)

        maximumDeposition = highestAdjacentHeight - np.sum(self.terrain, 2)
        depositedSediment[depositedSediment > maximumDeposition] = maximumDeposition[depositedSediment > maximumDeposition]


        self.terrain[:, :, 1] += depositedSediment
        self.terrain[:, :, 2] -= depositedSediment

    def SedimentTransportation(self):
        rows = np.linspace(0, self.NRows-1, self.NRows)
        colons = np.linspace(0, self.NColons-1, self.NColons)
        points = (rows, colons)
        COLONS, ROWS = np.meshgrid(colons, rows)

        nPoints = self.NRows*self.NColons
        samplePoints = np.zeros((nPoints, 2))
        samplePoints[:, 0:1] = np.reshape(ROWS-self.deltaT*self.velocity[:, :, 1], (nPoints, 1))
        samplePoints[:, 1:2] = np.reshape(COLONS-self.deltaT*self.velocity[:, :, 0], (nPoints, 1))

        samplePoints[:, 1] = (samplePoints[:, 1]+self.NColons-1) % (self.NColons-1)
        samplePoints[samplePoints[:, 0] < 0, 0] = 0
        samplePoints[samplePoints[:, 0] > self.NRows-1, 0] = self.NRows-1

        interpolatedValues = interpolate.interpn(points, self.terrain[:, :, -1], samplePoints)
        self.terrain[:, :, -1] = np.reshape(interpolatedValues, (self.NRows, self.NColons))

    def Evaporation(self):
        self.water[:, :, 0] = self.water[:, :, 1]*(1 - self.evaporationRate*self.deltaT)

    def __call__(self):
        self.UpdateTotalTerrain()
        self.UpdateFlow()
        self.UpdateWaterHeight()
        self.UpdateVelocity()

        self.UpdateSlope()

        self.UpdateCarryCapacity()
        self.Erode()
        self.Disolve()
        self.Deposit()
        self.SedimentTransportation()
        self.Evaporation()

    def Visualize(self):
        if self.terrainplot == None:
            if False:
                self.terrainplot = plt.imshow(np.sum(self.terrain, 2))
            else:
                fig, axs = plt.subplots(4, 2)

                self.terrainplot = axs[0][0].imshow(np.sum(self.terrain, 2))
                self.sedimentPlot = axs[1][0].imshow(self.terrain[:, :, 1])
                self.sedimentPlot.set_clim(vmin=0, vmax=5)
                self.waterPlot = axs[2][0].imshow(self.water[:, :, 0])
                self.totalHeightPlot = axs[3][0].imshow(np.sum(self.terrain, 2) + self.water[:, :, 0])
                self.suspendedSedimentPlot = axs[0][1].imshow(self.terrain[:, :, -1])
                self.suspendedSedimentPlot.set_clim(vmin=0, vmax=5)
                self.carryCapacityPlot = axs[1][1].imshow(self.carryCapacity)
                self.carryCapacityPlot.set_clim(vmin=0, vmax=5)
                self.slopeplot = axs[2][1].imshow(180*self.slope/np.pi)
                self.slopeplot.set_clim(vmin=0, vmax=90)
                self.velocityPlot = axs[3, 1].imshow(np.sqrt(self.velocity[:, :, 0]**2 + self.velocity[:, :, 1]**2))

            plt.pause(0.00001)
        else:
            if False:
                self.terrainplot.set_array(np.sum(self.terrain, 2))
                #self.terrainplot.set_clim(vmin=np.min(self.terrain), vmax=np.max(self.terrain))
            else:
                self.terrainplot.set_array(np.sum(self.terrain, 2))
                self.terrainplot.set_clim(vmin=np.min(np.sum(self.terrain, 2)), vmax=np.max(np.sum(self.terrain, 2)))
                self.sedimentPlot.set_array(self.terrain[:, :, 1])
                self.waterPlot.set_array(self.water[:, :, 0])
                self.totalHeightPlot.set_array(np.sum(self.terrain, 2) + self.water[:, :, 0])
                #self.waterPlot.set_clim(vmin = 0, vmax = np.max(self.water[:, :, 0]))
                self.waterPlot.set_clim(vmin=0, vmax=20)
                self.suspendedSedimentPlot.set_array(self.terrain[:, :, -1])
                self.suspendedSedimentPlot.set_clim(vmin=0, vmax=2)
                self.carryCapacityPlot.set_array(self.carryCapacity)
                self.slopeplot.set_array(180*self.slope/np.pi)
                self.velocityPlot.set_array(np.sqrt(self.velocity[:, :, 0]**2 + self.velocity[:, :, 1]**2))
                self.velocityPlot.set_clim(vmin=0, vmax=10)

            plt.pause(0.00001)

    @classmethod
    def Wrap(cls, value, wrapValue):
        return np.mod(value, wrapValue)

    @classmethod
    def InitializeRainDropTemplates(cls, maximumRainDropRadius = 1):
        # Initializes lists used as templates when creating rain drops.
        cls.rainDropWeightTemplate = []
        cls.rainDropTileTemplate = []

        for radius in range(0, maximumRainDropRadius+1):
            rows = range(-radius, radius, 1)
            columns = range(-radius, radius, 1)
            rowGrid, columnGrid = np.meshgrid(rows, columns)
            rowList = np.reshape(rowGrid, [rowGrid.size, 1])
            columnList = np.reshape(columnGrid, [columnGrid.size, 1])
            distances = np.sqrt(rowList ** 2 + columnList ** 2)
            rowList = rowList[distances < radius]
            columnList = columnList[distances < radius]

            # The template lists are expanded.
            cls.rainDropWeightTemplate.append(
                (radius - distances[distances < radius]) / np.sum(radius - distances[distances < radius]))

            erosionTiles = np.zeros((cls.rainDropWeightTemplate[radius].shape[0], 2))
            erosionTiles[:, 0] = rowList
            erosionTiles[:, 1] = columnList
            cls.rainDropTileTemplate.append(erosionTiles)

class HydrolicErosionNumba():
    def __init__(self,
                 terrain,
                 evaporationRate = 0.05,
                 deltaT = 1,
                 flowSpeed = 0.5,
                 sedimentFlowSpeed = 0.5,
                 gridLength = 1,
                 carryCapacityLimit = 1,
                 erosionRate = 0.5,
                 depositionRate = 0.5,
                 maximumErosionDepth = 10,
                 minimumErosionAngle = 0):
        self.NRows = np.size(terrain, 0)
        self.NColons = np.size(terrain, 1)

        self.deltaT = deltaT
        self.evaporationRate = evaporationRate
        self.flowSpeed = flowSpeed
        self.sedimentFlowSpeed = sedimentFlowSpeed
        self.gridLength = gridLength
        self.carryCapacityLimit = carryCapacityLimit
        self.erosionRate = np.array(erosionRate)
        self.depositionRate = depositionRate
        self.maximumErosionDepth = maximumErosionDepth
        self.minimumErosionAngle = np.pi*minimumErosionAngle/180

        self.terrain = terrain
        self.water = np.zeros((self.NRows, self.NColons, 2))

        self.numberOfLayers = np.size(terrain, axis=2)
        self.layerShape = (np.size(terrain, 0), np.size(terrain, 1))

        #self.water[200, 200, 0] = 100
        #self.water[201, 200, 0] = 100
        #self.water[200, 201, 0] = 100
        #self.water[201, 201, 0] = 100

        self.suspendedSediment = np.zeros((self.NRows, self.NColons, 2))

        self.flow = np.zeros((self.NRows, self.NColons, 4)) # Left, Right, Top, Bottom
        self.velocity = np.zeros((self.NRows, self.NColons, 2)) # x, y
        self.slope = np.zeros((self.NRows, self.NColons))
        self.carryCapacity = np.zeros((self.NRows, self.NColons))
        self.sedimentFlow = np.zeros((self.NRows, self.NColons, 4))  # Left, Right, Top, Bottom

        self.terrainplot = None
        self.waterPlot = None
        self.suspendedSedimentPlot = None

    def Rain(self, numberOfDrops = 1, radius = 1, dropSize = 1, application = 'drop'):
        if application == 'drop':
            for iDrop in range(numberOfDrops):
                row = np.random.randint(0, self.NRows)
                colon = np.random.randint(0, self.NColons)

                dropTilesTemplate = self.rainDropTileTemplate[radius]
                dropWeightsFull = self.rainDropWeightTemplate[radius]

                dropTilesFull = np.zeros(np.shape(dropTilesTemplate), dtype=int)
                dropTilesFull[:, 0] = row + dropTilesTemplate[:, 0]
                dropTilesFull[:, 1] = self.Wrap(colon + dropTilesTemplate[:, 1], self.NColons)

                dropTiles = []
                dropWeights = []
                for tile, weight in zip(dropTilesFull, dropWeightsFull):
                    if tile[0] >= 0 and tile[0] < self.NRows:
                        dropTiles.append(tile)
                        dropWeights.append(weight)
                dropTiles = np.array(dropTiles)
                dropWeights = np.array(dropWeights)

                self.water[dropTiles[:, 0], dropTiles[:, 1], 0] += self.deltaT*dropSize*dropWeights
        elif application == 'even':
            self.water[:, :, 0] += numberOfDrops*dropSize

    def UpdateFlow(self):
        deltaHeightLeft = self.CalculateDeltaHeight('left')
        newFlowLeft = self.flow[:, :, 0] + self.deltaT*self.flowSpeed*deltaHeightLeft
        newFlowLeft[newFlowLeft < 0] = 0
        self.flow[:, :, 0] = newFlowLeft

        deltaHeightRight = self.CalculateDeltaHeight('right')
        newFlowRight = self.flow[:, :, 1] + self.deltaT*self.flowSpeed*deltaHeightRight
        newFlowRight[newFlowRight < 0] = 0
        self.flow[:, :, 1] = newFlowRight

        deltaHeightTop = self.CalculateDeltaHeight('top')
        newFlowTop = self.flow[:, :, 2] + self.deltaT*self.flowSpeed*deltaHeightTop
        newFlowTop[newFlowTop < 0] = 0
        self.flow[:, :, 2] = newFlowTop

        deltaHeightBottom = self.CalculateDeltaHeight('bottom')
        newFlowBottom = self.flow[:, :, 3] + self.deltaT*self.flowSpeed*deltaHeightBottom
        newFlowBottom[newFlowBottom < 0] = 0
        self.flow[:, :, 3] = newFlowBottom

        # The 0.9 is to reduce instability in the flow simulation.
        flowScaling = 0.9*self.water[:, :, 0]/((self.flow[:, :, 0] + self.flow[:, :, 1] + self.flow[:, :, 2] + self.flow[:, :, 3]+0.001)*self.deltaT)
        flowScaling[flowScaling>1] = 1

        #maxFlow = np.max((deltaHeightLeft, deltaHeightRight, deltaHeightTop, deltaHeightBottom))/10
        #flowScaling[flowScaling > maxFlow] = maxFlow
        self.flow[:, :, 0] *= flowScaling
        self.flow[:, :, 1] *= flowScaling
        self.flow[:, :, 2] *= flowScaling
        self.flow[:, :, 3] *= flowScaling

        self.inFlowRight = np.concatenate((self.flow[:, 1:self.NColons, 0],
                                      self.flow[:, 0:1, 0]),
                                     axis=1)
        self.inFlowLeft = np.concatenate((self.flow[:, self.NColons - 1:self.NColons, 1],
                                      self.flow[:, 0:-1, 1]),
                                     axis=1)
        self.inFlowBottom = np.concatenate((self.flow[self.NRows - 1:self.NRows, :, 2],
                                       self.flow[0:-1, :, 2]),
                                      axis=0)
        self.inFlowTop = np.concatenate((self.flow[1:self.NRows, :, 3],
                                    self.flow[0:1, :, 3]),
                                   axis=0)

    def CalculateDeltaHeight(self, direction = 'left'):
        totalHeight =np.sum(self.terrain, 2) + self.water[:, :, 0]

        if direction == 'left':
            totalHeightWrapped = np.concatenate((totalHeight[:, self.NColons - 1:self.NColons],
                                                 totalHeight[:, 0:-1]),
                                                axis=1)
        elif direction == 'right':
            totalHeightWrapped = np.concatenate((totalHeight[:, 1:self.NColons],
                                                 totalHeight[:, 0:1]),
                                                axis=1)
        elif direction == 'top':
            totalHeightWrapped = np.concatenate((totalHeight[1:self.NRows, :],
                                                 totalHeight[self.NRows-1:self.NRows, :]),
                                                axis=0)
        elif direction == 'bottom':
            totalHeightWrapped = np.concatenate((totalHeight[0:1, :],
                                                 totalHeight[0:self.NRows-1, :]),
                                                axis=0)
        return totalHeight - totalHeightWrapped

    def UpdateWaterHeight(self):
        self.water[:, :, 1] = self.water[:, :, 0] + self.deltaT*(- (
                self.flow[:, :, 0] + self.flow[:, :, 1] + self.flow[:, :, 2] + self.flow[:, :,3]) + \
                              self.inFlowLeft + self.inFlowRight + self.inFlowTop + self.inFlowBottom)

    def UpdateVelocity(self):
        self.velocity[:, :, 0] = (self.flow[:, :, 1] - self.flow[:, :, 0] + self.inFlowLeft - self.inFlowRight)/2
        self.velocity[:, :, 1] = (self.flow[:, :, 2] - self.flow[:, :, 3] + self.inFlowBottom - self.inFlowTop)/2
        #self.velocity[:, :, 0] = (self.flow[:, :, 1] - self.flow[:, :, 0] + self.inFlowLeft - self.inFlowRight)/\
        #                         (self.water[:, :, 0] + self.water[:, :, 1]+0.001)
        #self.velocity[:, :, 1] = (self.flow[:, :, 2] - self.flow[:, :, 3] + self.inFlowBottom - self.inFlowTop)/\
        #                         (self.water[:, :, 0] + self.water[:, :, 1]+0.001)
    '''
    def UpdateSlope(self):
        self.terrainLeft = np.concatenate((self.terrain[:, self.NColons - 1:self.NColons],
                                      self.terrain[:, 0:-1]),
                                     axis=1)
        self.terrainRight = np.concatenate((self.terrain[:, 1:self.NColons],
                                       self.terrain[:, 0:1]),
                                      axis=1)
        xAngle = np.arctan((self.terrainRight-self.terrainLeft)/ (2*self.gridLength))

        self.terrainTop = np.concatenate((self.terrain[1:self.NRows, :],
                                     self.terrain[self.NRows-1:self.NRows, :]),
                                    axis=0)
        self.terrainBottom = np.concatenate((self.terrain[0:1, :],
                                        self.terrain[0:self.NRows-1, :]),
                                       axis = 0)
        yAngle = np.arctan((self.terrainTop-self.terrainBottom)/(2*self.gridLength))

        self.slope = np.sqrt(xAngle**2 + yAngle**2)/np.sqrt(2)
    '''

    def UpdateSlope(self):
        totalHeight = np.sum(self.terrain, 2)

        self.terrainLeft = np.concatenate((totalHeight[:, self.NColons - 1:self.NColons],
                                      totalHeight[:, 0:-1]),
                                     axis=1)
        self.terrainRight = np.concatenate((totalHeight[:, 1:self.NColons],
                                       totalHeight[:, 0:1]),
                                      axis=1)
        xAngle = np.arctan((self.terrainRight-self.terrainLeft)/ (2*self.gridLength))

        self.terrainTop = np.concatenate((totalHeight[1:self.NRows, :],
                                     totalHeight[self.NRows-1:self.NRows, :]),
                                    axis=0)
        self.terrainBottom = np.concatenate((totalHeight[0:1, :],
                                        totalHeight[0:self.NRows-1, :]),
                                       axis = 0)
        yAngle = np.arctan((self.terrainTop-self.terrainBottom)/(2*self.gridLength))

        #self.slope = np.sqrt(xAngle**2 + yAngle**2)/np.sqrt(2)

        totalHeight = np.sum(self.terrain, 2) + self.water[:, :, 1]
        terrainLeft = np.concatenate((totalHeight[:, self.NColons - 1:self.NColons],
                                      totalHeight[:, 0:-1]),
                                     axis=1)
        terrainRight = np.concatenate((totalHeight[:, 1:self.NColons],
                                       totalHeight[:, 0:1]),
                                      axis=1)
        xAngle = np.arctan((terrainRight-terrainLeft)/ (2*self.gridLength))

        terrainTop = np.concatenate((totalHeight[1:self.NRows, :],
                                     totalHeight[self.NRows-1:self.NRows, :]),
                                    axis=0)
        terrainBottom = np.concatenate((totalHeight[0:1, :],
                                        totalHeight[0:self.NRows-1, :]),
                                       axis = 0)
        yAngle = np.arctan((terrainTop-terrainBottom)/(2*self.gridLength))

        #self.slope = np.sqrt(xAngle**2 + yAngle**2)/np.sqrt(2)


        self.slope = np.arctan(np.gradient(totalHeight))
        r = np.sqrt(self.slope[0] ** 2 + self.slope[1] ** 2)
        #self.slope = self.slope[1]
        self.slope = np.sqrt(self.slope[0] ** 4 + self.slope[1] ** 4)/r
        self.slope[r == 0] = 0
        #self.slope = np.sqrt(self.slope[0] ** 2 + self.slope[1] ** 2)
        #print(np.shape(self.terrain))
        #print(np.shape(self.slope))
        #print(type(self.slope))

        #for slope in self. slope:
        #plt.figure()
        #plt.imshow(slope)
        #plt.show()
        #quit()
        #print('---------------')

    def UpdateCarryCapacity(self):
        '''
        The carry capacity depends on the water depth. At water > mamimumErosionDepth the capacity is zero.
        :return:
        '''
        #waterDepthMultiplier = self.water[:, :, 1]*2.5
        waterDepthMultiplier = np.ones(np.shape(self.water[:, :, 1]))
        #waterDepthMultiplier = 10*self.water[:, :, 1]*(1-self.water[:, :, 1]/self.maximumErosionDepth)/self.maximumErosionDepth
        waterDepthMultiplier[self.water[:, :, 1] > self.maximumErosionDepth] = 0
        #slopeMultiplier = np.sin(self.slope)
        slopeMultiplier = np.sin((self.slope - self.minimumErosionAngle) /
                                 (np.pi / 2 - self.minimumErosionAngle) * np.pi / 2)
        slopeMultiplier[self.slope < self.minimumErosionAngle] = 0
        #self.carryCapacity =  waterDepthMultiplier * self.carryCapacityLimit * slopeMultiplier * np.sqrt(self.velocity[:, :, 0]**2 + self.velocity[:, :, 1]**2)
        self.carryCapacity = self.carryCapacityLimit * slopeMultiplier * np.sqrt(self.velocity[:, :, 0]**2 + self.velocity[:, :, 1]**2)
        #self.carryCapacity = self.carryCapacityLimit * np.sqrt(self.velocity[:, :, 0] ** 2 + self.velocity[:, :, 1] ** 2)
        self.suspendedSediment[:, :, 1] = self.suspendedSediment[:, :, 0]

    def Erode(self):
        #erosionAlreadyDone = np.ones(self.layerShape)
        erodedSediment = self.deltaT * (self.carryCapacity - self.suspendedSediment[:, :, 0])
        erodedSediment[erodedSediment < 0] = 0
        for iLayer in np.linspace(self.numberOfLayers-1, 0, self.numberOfLayers, dtype=int):
            erodedSediment *= self.erosionRate[iLayer]

            #erodedSediment = self.deltaT*self.erosionRate[iLayer]*(self.carryCapacity - self.suspendedSediment[:, :, 0])
            #erodedSediment[erodedSediment < 0] = 0

            #erosionLimit = self.water[:, :, 1] - 2*self.suspendedSediment[:, :, 0]
            #erodedSediment[erodedSediment > erosionLimit] = erosionLimit[erodedSediment > erosionLimit]

            lowestAdjacentHeight = np.zeros((self.NRows, self.NColons, 4))
            lowestAdjacentHeight[:, :, 0] = self.terrainLeft
            lowestAdjacentHeight[:, :, 1] = self.terrainRight
            lowestAdjacentHeight[:, :, 2] = self.terrainTop
            lowestAdjacentHeight[:, :, 3] = self.terrainBottom
            lowestAdjacentHeight = np.min(lowestAdjacentHeight, axis=2)

            maximumErosion = np.sum(self.terrain, 2) - lowestAdjacentHeight
            erodedSediment[erodedSediment > maximumErosion] = maximumErosion[erodedSediment > maximumErosion]

            self.terrain[:, :, iLayer] -= erodedSediment
            erodedSediment = self.terrain[:, :, iLayer].copy()
            erodedSediment[erodedSediment >= 0] = 0
            erodedSediment *= -1/self.erosionRate[iLayer]

            if iLayer == 0:
                # rock decreases in density as it is eroded.
                self.suspendedSediment[:, :, 1] += 2*erodedSediment
            else:
                self.suspendedSediment[:, :, 1] += erodedSediment
            #self.water[:, :, 1] += erodedSediment

    def Deposit(self):
        depositedSediment = self.deltaT*self.depositionRate * (self.suspendedSediment[:, :, 0] - self.carryCapacity)
        depositedSediment[depositedSediment < 0] = 0
        #minDepos = 0.1 * self.suspendedSediment[:, :, 0]
        #depositedSediment[depositedSediment < minDepos] = minDepos[depositedSediment < minDepos]

        highestAdjacentHeight = np.zeros((self.NRows, self.NColons, 4))
        highestAdjacentHeight[:, :, 0] = self.terrainLeft
        highestAdjacentHeight[:, :, 1] = self.terrainRight
        highestAdjacentHeight[:, :, 2] = self.terrainTop
        highestAdjacentHeight[:, :, 3] = self.terrainBottom
        highestAdjacentHeight = np.max(highestAdjacentHeight, axis=2)

        maximumDeposition = highestAdjacentHeight - np.sum(self.terrain, 2)
        depositedSediment[depositedSediment > maximumDeposition] = maximumDeposition[depositedSediment > maximumDeposition]

        self.terrain[:, :, -1] += depositedSediment
        self.suspendedSediment[:, :, 1] -= depositedSediment
        #self.water[:, :, 1] -= depositedSediment

    def SedimentTransportation(self):
        self.sedimentFlow = self.sedimentFlowSpeed * self.flow.copy()

        flowScaling = self.suspendedSediment[:, :, 1] / ((self.sedimentFlow[:, :, 0] + self.sedimentFlow[:, :, 1] + self.sedimentFlow[:, :,
                                                                                        2] + self.sedimentFlow[:, :,
                                                                                             3] + 0.001) * self.deltaT)
        flowScaling[flowScaling > 1] = 1

        #sedimentFlow = self.flow.copy()

        self.sedimentFlow[:, :, 0] *= flowScaling
        self.sedimentFlow[:, :, 1] *= flowScaling
        self.sedimentFlow[:, :, 2] *= flowScaling
        self.sedimentFlow[:, :, 3] *= flowScaling

        sedimentInFlowRight = np.concatenate((self.sedimentFlow[:, 1:self.NColons, 0],
                                           self.sedimentFlow[:, 0:1, 0]),
                                          axis=1)
        sedimentInFlowLeft = np.concatenate((self.sedimentFlow[:, self.NColons - 1:self.NColons, 1],
                                          self.sedimentFlow[:, 0:-1, 1]),
                                         axis=1)
        sedimentInFlowBottom = np.concatenate((self.sedimentFlow[self.NRows - 1:self.NRows, :, 2],
                                            self.sedimentFlow[0:-1, :, 2]),
                                           axis=0)
        sedimentInFlowTop = np.concatenate((self.sedimentFlow[1:self.NRows, :, 3],
                                         self.sedimentFlow[0:1, :, 3]),
                                        axis=0)

        sedimentOut = self.deltaT * (self.sedimentFlow[:, :, 0] + self.sedimentFlow[:, :, 1] + self.sedimentFlow[:, :, 2] + self.sedimentFlow[:, :, 3])
        sedimentIn = self.deltaT * (sedimentInFlowLeft + sedimentInFlowRight + sedimentInFlowTop + sedimentInFlowBottom)

        self.suspendedSediment[:, :, 0] = self.suspendedSediment[:, :, 1] - sedimentOut + sedimentIn
        #self.water[:, :, 1] -= sedimentOut
        #self.water[:, :, 1] += sedimentIn

    def Evaporation(self):
        self.water[:, :, 0] = self.water[:, :, 1]*(1 - self.evaporationRate*self.deltaT)

    def __call__(self):
        self.UpdateFlow()
        self.UpdateWaterHeight()
        self.UpdateVelocity()

        self.UpdateSlope()

        self.UpdateCarryCapacity()
        self.Erode()
        self.Deposit()
        self.SedimentTransportation()
        self.Evaporation()

    def Visualize(self):
        if self.terrainplot == None:
            if False:
                self.terrainplot = plt.imshow(np.sum(self.terrain, 2))
            else:
                fig, axs = plt.subplots(3, 2)

                self.terrainplot = axs[0][0].imshow(np.sum(self.terrain, 2))
                self.waterPlot = axs[1][0].imshow(self.water[:, :, 0])
                self.totalHeightPlot = axs[2][0].imshow(np.sum(self.terrain, 2) + self.water[:, :, 0])
                self.suspendedSedimentPlot = axs[0][1].imshow(self.suspendedSediment[:, :, 0])
                self.slopeplot = axs[1][1].imshow(180*self.slope/np.pi)
                self.slopeplot.set_clim(vmin=0, vmax=90)
                self.velocityPlot = axs[2, 1].imshow(np.sqrt(self.velocity[:, :, 0]**2 + self.velocity[:, :, 1]**2))

            plt.pause(0.00001)
        else:
            if False:
                self.terrainplot.set_array(np.sum(self.terrain, 2))
                #self.terrainplot.set_clim(vmin=np.min(self.terrain), vmax=np.max(self.terrain))
            else:
                self.terrainplot.set_array(np.sum(self.terrain, 2))
                self.terrainplot.set_clim(vmin=np.min(np.sum(self.terrain, 2)), vmax=np.max(np.sum(self.terrain, 2)))
                self.waterPlot.set_array(self.water[:, :, 0])
                self.totalHeightPlot.set_array(np.sum(self.terrain, 2) + self.water[:, :, 0])
                #self.waterPlot.set_clim(vmin = 0, vmax = np.max(self.water[:, :, 0]))
                self.waterPlot.set_clim(vmin=0, vmax=20)
                self.suspendedSedimentPlot.set_array(self.suspendedSediment[:, :, 0])
                self.suspendedSedimentPlot.set_clim(vmin=0, vmax=2)
                self.slopeplot.set_array(180*self.slope/np.pi)
                self.velocityPlot.set_array(np.sqrt(self.velocity[:, :, 0]**2 + self.velocity[:, :, 1]**2))
                self.velocityPlot.set_clim(vmin=0, vmax=10)

            plt.pause(0.00001)

    @classmethod
    def Wrap(cls, value, wrapValue):
        return np.mod(value, wrapValue)

    @classmethod
    def InitializeRainDropTemplates(cls, maximumRainDropRadius = 1):
        # Initializes lists used as templates when creating rain drops.
        cls.rainDropWeightTemplate = []
        cls.rainDropTileTemplate = []

        for radius in range(0, maximumRainDropRadius+1):
            rows = range(-radius, radius, 1)
            columns = range(-radius, radius, 1)
            rowGrid, columnGrid = np.meshgrid(rows, columns)
            rowList = np.reshape(rowGrid, [rowGrid.size, 1])
            columnList = np.reshape(columnGrid, [columnGrid.size, 1])
            distances = np.sqrt(rowList ** 2 + columnList ** 2)
            rowList = rowList[distances < radius]
            columnList = columnList[distances < radius]

            # The template lists are expanded.
            cls.rainDropWeightTemplate.append(
                (radius - distances[distances < radius]) / np.sum(radius - distances[distances < radius]))

            erosionTiles = np.zeros((cls.rainDropWeightTemplate[radius].shape[0], 2))
            erosionTiles[:, 0] = rowList
            erosionTiles[:, 1] = columnList
            cls.rainDropTileTemplate.append(erosionTiles)

class ThermalErosion():
    def __init__(self,
                 terrain,
                 deltaT = 1,
                 flowSpeed = 0.5,
                 maximumSlope = 30,
                 gridLength = 1):
        self.NRows = np.size(terrain, 0)
        self.NColons = np.size(terrain, 1)

        self.deltaT = deltaT
        self.gridLength = gridLength
        self.flowSpeed = flowSpeed
        self.maximumSlopeDegree = np.array(maximumSlope)
        self.maximumSlope = np.pi*self.maximumSlopeDegree.copy()/180
        self.maximumDeltaHeight = gridLength * np.tan(self.maximumSlope)

        self.terrain = terrain
        self.flow = np.zeros((self.NRows, self.NColons, 8))  # Left, Right, Top, Bottom, Top_Left, Bottom_Right, Bottom_Left, Top_Right
        self.deltaHeight = np.zeros((self.NRows, self.NColons, 8))

        self.numberOfLayers = np.size(terrain, 2)

    def UpdateFlow(self, iLayer):
        '''
        self.CalculateDeltaHeight(iLayer)
        self.flow[:, :, 0] = self.flowSpeed*(self.deltaHeight0 - self.maximumDeltaHeight[iLayer])
        self.flow[:, :, 1] = self.flowSpeed*(self.deltaHeight1 - self.maximumDeltaHeight[iLayer])
        self.flow[:, :, 2] = self.flowSpeed*(self.deltaHeight2 - self.maximumDeltaHeight[iLayer])
        self.flow[:, :, 3] = self.flowSpeed*(self.deltaHeight3 - self.maximumDeltaHeight[iLayer])
        self.flow[:, :, 4] = self.flowSpeed*(self.deltaHeight5 - np.sqrt(2)*self.maximumDeltaHeight[iLayer])
        self.flow[:, :, 5] = self.flowSpeed*(self.deltaHeight4 - np.sqrt(2)*self.maximumDeltaHeight[iLayer])
        self.flow[:, :, 6] = self.flowSpeed*(self.deltaHeight7 - np.sqrt(2)*self.maximumDeltaHeight[iLayer])
        self.flow[:, :, 7] = self.flowSpeed*(self.deltaHeight6 - np.sqrt(2)*self.maximumDeltaHeight[iLayer])
        self.flow[self.flow < 0] = 0
        '''

        self.CalculateDeltaHeight(iLayer)
        self.flow0 = self.flowSpeed*(self.deltaHeight0 - self.maximumDeltaHeight[iLayer])
        self.flow1 = self.flowSpeed*(self.deltaHeight1 - self.maximumDeltaHeight[iLayer])
        self.flow2 = self.flowSpeed*(self.deltaHeight2 - self.maximumDeltaHeight[iLayer])
        self.flow3 = self.flowSpeed*(self.deltaHeight3 - self.maximumDeltaHeight[iLayer])
        self.flow4 = self.flowSpeed*(self.deltaHeight5 - np.sqrt(2)*self.maximumDeltaHeight[iLayer])
        self.flow5 = self.flowSpeed*(self.deltaHeight4 - np.sqrt(2)*self.maximumDeltaHeight[iLayer])
        self.flow6 = self.flowSpeed*(self.deltaHeight7 - np.sqrt(2)*self.maximumDeltaHeight[iLayer])
        self.flow7 = self.flowSpeed*(self.deltaHeight6 - np.sqrt(2)*self.maximumDeltaHeight[iLayer])
        self.flow0[self.flow0 < 0] = 0
        self.flow1[self.flow1 < 0] = 0
        self.flow2[self.flow2 < 0] = 0
        self.flow3[self.flow3 < 0] = 0
        self.flow4[self.flow4 < 0] = 0
        self.flow5[self.flow5 < 0] = 0
        self.flow6[self.flow6 < 0] = 0
        self.flow7[self.flow7 < 0] = 0

        self.ScaleFlow(iLayer=iLayer)
        self.UpdateInFlow()

    def ScaleFlow(self, iLayer):
        '''
        flowScaling = self.terrain[:, :, iLayer] / ((np.sum(self.flow, 2) + 0.001) * self.deltaT)
        flowScaling[flowScaling > 1] = 1

        self.flow[:, :, 0] *= flowScaling
        self.flow[:, :, 1] *= flowScaling
        self.flow[:, :, 2] *= flowScaling
        self.flow[:, :, 3] *= flowScaling
        self.flow[:, :, 4] *= flowScaling
        self.flow[:, :, 5] *= flowScaling
        self.flow[:, :, 6] *= flowScaling
        self.flow[:, :, 7] *= flowScaling
        '''
        flowScaling = self.terrain[:, :, iLayer] / ((self.flow0 + self.flow1 + self.flow2 + self.flow3 + self.flow4 + self.flow5 + self.flow6 + self.flow7 + 0.001) * self.deltaT)
        flowScaling[flowScaling > 1] = 1

        self.flow0 *= flowScaling
        self.flow1 *= flowScaling
        self.flow2 *= flowScaling
        self.flow3 *= flowScaling
        self.flow4 *= flowScaling
        self.flow5 *= flowScaling
        self.flow6 *= flowScaling
        self.flow7 *= flowScaling

    def UpdateInFlow(self):
        '''
        self.inFlowRight = np.concatenate((self.flow[:, 1:self.NColons, 0],
                                           self.flow[:, 0:1, 0]),
                                          axis=1)
        self.inFlowLeft = np.concatenate((self.flow[:, self.NColons - 1:self.NColons, 1],
                                          self.flow[:, 0:-1, 1]),
                                         axis=1)
        self.inFlowBottom = np.concatenate((self.flow[self.NRows - 1:self.NRows, :, 2],
                                            self.flow[0:-1, :, 2]),
                                           axis=0)
        self.inFlowTop = np.concatenate((self.flow[1:self.NRows, :, 3],
                                         self.flow[0:1, :, 3]),
                                        axis=0)

        # top left
        self.inFlowTopLeft = np.concatenate((self.flow[:, self.NColons - 1:self.NColons, 4],
                                             self.flow[:, 0:-1, 4]),
                                            axis=1)
        self.inFlowTopLeft = np.concatenate((self.inFlowTopLeft[1:self.NRows, :],
                                             self.inFlowTopLeft[self.NRows - 1:self.NRows, :]),
                                            axis=0)
        # bottom right
        self.inFlowBottomRight = np.concatenate((self.flow[:, 1:self.NColons, 5],
                                             self.flow[:, 0:1, 5]),
                                            axis=1)
        self.inFlowBottomRight = np.concatenate((self.inFlowBottomRight[0:1, :],
                                             self.inFlowBottomRight[0:self.NRows - 1, :]),
                                            axis=0)
        # bottom left
        self.inFlowBottomLeft = np.concatenate((self.flow[:, self.NColons - 1:self.NColons, 6],
                                             self.flow[:, 0:-1, 6]),
                                            axis=1)
        self.inFlowBottomLeft = np.concatenate((self.inFlowBottomLeft[0:1, :],
                                             self.inFlowBottomLeft[0:self.NRows - 1, :]),
                                            axis=0)
        # top right
        self.inFlowTopRight = np.concatenate((self.flow[:, 1:self.NColons, 7],
                                             self.flow[:, 0:1, 7]),
                                            axis=1)
        self.inFlowTopRight = np.concatenate((self.inFlowTopRight[1:self.NRows, :],
                                             self.inFlowTopRight[self.NRows - 1:self.NRows, :]),
                                            axis=0)
        '''
        self.inFlowRight = np.concatenate((self.flow0[:, 1:self.NColons],
                                           self.flow0[:, 0:1]),
                                          axis=1)
        self.inFlowLeft = np.concatenate((self.flow1[:, self.NColons - 1:self.NColons],
                                          self.flow1[:, 0:-1]),
                                         axis=1)
        self.inFlowBottom = np.concatenate((self.flow2[self.NRows - 1:self.NRows, :],
                                            self.flow2[0:-1, :]),
                                           axis=0)
        self.inFlowTop = np.concatenate((self.flow3[1:self.NRows, :],
                                         self.flow3[0:1, :]),
                                        axis=0)

        # top left
        self.inFlowTopLeft = np.concatenate((self.flow4[:, self.NColons - 1:self.NColons],
                                             self.flow4[:, 0:-1]),
                                            axis=1)
        self.inFlowTopLeft = np.concatenate((self.inFlowTopLeft[1:self.NRows, :],
                                             self.inFlowTopLeft[self.NRows - 1:self.NRows, :]),
                                            axis=0)
        # bottom right
        self.inFlowBottomRight = np.concatenate((self.flow5[:, 1:self.NColons],
                                             self.flow5[:, 0:1]),
                                            axis=1)
        self.inFlowBottomRight = np.concatenate((self.inFlowBottomRight[0:1, :],
                                             self.inFlowBottomRight[0:self.NRows - 1, :]),
                                            axis=0)
        # bottom left
        self.inFlowBottomLeft = np.concatenate((self.flow6[:, self.NColons - 1:self.NColons],
                                             self.flow6[:, 0:-1]),
                                            axis=1)
        self.inFlowBottomLeft = np.concatenate((self.inFlowBottomLeft[0:1, :],
                                             self.inFlowBottomLeft[0:self.NRows - 1, :]),
                                            axis=0)
        # top right
        self.inFlowTopRight = np.concatenate((self.flow7[:, 1:self.NColons],
                                             self.flow7[:, 0:1]),
                                            axis=1)
        self.inFlowTopRight = np.concatenate((self.inFlowTopRight[1:self.NRows, :],
                                             self.inFlowTopRight[self.NRows - 1:self.NRows, :]),
                                            axis=0)
    def CalculateDeltaHeight(self, iLayer):
        totalHeight = np.sum(self.terrain[:, :, 0:iLayer+1], axis=2)

        self.deltaHeight0 = -np.concatenate((totalHeight[:, self.NColons - 1:self.NColons],
                                                     totalHeight[:, 0:-1]),
                                                    axis=1)
        self.deltaHeight1 = -np.concatenate((totalHeight[:, 1:self.NColons],
                                                     totalHeight[:, 0:1]),
                                                    axis=1)
        self.deltaHeight2 = -np.concatenate((totalHeight[1:self.NRows, :],
                                                     totalHeight[self.NRows - 1:self.NRows, :]),
                                                    axis=0)
        self.deltaHeight3 = -np.concatenate((totalHeight[0:1, :],
                                                     totalHeight[0:self.NRows - 1, :]),
                                                    axis=0)
        self.deltaHeight4 = -np.concatenate((totalHeight[:, self.NColons - 1:self.NColons],
                                                     totalHeight[:, 0:-1]),
                                                    axis=1)
        self.deltaHeight4 = np.concatenate((self.deltaHeight4[1:self.NRows, :],
                                                    self.deltaHeight4[self.NRows - 1:self.NRows, :]),
                                                   axis=0)
        self.deltaHeight5 = -np.concatenate((totalHeight[:, 1:self.NColons],
                                                     totalHeight[:, 0:1]),
                                                    axis=1)
        self.deltaHeight5 = np.concatenate((self.deltaHeight5[0:1, :],
                                                    self.deltaHeight5[0:self.NRows - 1, :]),
                                                   axis=0)
        self.deltaHeight6 = -np.concatenate((totalHeight[:, self.NColons - 1:self.NColons],
                                                     totalHeight[:, 0:-1]),
                                                    axis=1)
        self.deltaHeight6 = np.concatenate((self.deltaHeight6[0:1, :],
                                                    self.deltaHeight6[0:self.NRows - 1, :]),
                                                   axis=0)
        self.deltaHeight7 = -np.concatenate((totalHeight[:, 1:self.NColons],
                                                     totalHeight[:, 0:1]),
                                                    axis=1)
        self.deltaHeight7 = np.concatenate((self.deltaHeight7[1:self.NRows, :],
                                                    self.deltaHeight7[self.NRows - 1:self.NRows, :]),
                                                   axis=0)

        self.deltaHeight0 += totalHeight
        self.deltaHeight1 += totalHeight
        self.deltaHeight2 += totalHeight
        self.deltaHeight3 += totalHeight
        self.deltaHeight4 += totalHeight
        self.deltaHeight5 += totalHeight
        self.deltaHeight6 += totalHeight
        self.deltaHeight7 += totalHeight

    def UpdateTerrainHeight(self, iLayer):
        #self.terrain[:, :, iLayer] -= self.deltaT*np.sum(self.flow, axis=2)
        self.terrain[:, :, iLayer] -= self.deltaT * (self.flow0 + self.flow1 + self.flow2 + self.flow3 + self.flow4 + self.flow5 + self.flow6 + self.flow7)
        self.terrain[:, :, iLayer] += self.deltaT*(self.inFlowLeft + self.inFlowRight + self.inFlowTop + self.inFlowBottom + self.inFlowTopLeft + self.inFlowBottomRight + self.inFlowBottomLeft + self.inFlowTopRight)

    def __call__(self, *args, **kwargs):
        for iLayer in range(self.numberOfLayers):
            if self.maximumSlopeDegree[iLayer] < 90:
                self.UpdateFlow(iLayer)
                self.UpdateTerrainHeight(iLayer)

from numba import int32, float32    # import the types

spec = [
    ('NRows', int32),               # a simple scalar field
    ('NColons', int32),
    ('deltaT', int32),
    ('gridLength', float32),
    ('flowSpeed', float32),
    ('maximumSlopeDegree', float32[:]),
    ('maximumSlope', float32[:]),
    ('maximumDeltaHeight', float32[:]),
    ('terrain', float32[:]),
    ('flow', float32[:]),
    ('numberOfLayers', int32),
]

@nb.jit(nopython = True)
def _UpdateFlow(self, terrain, flow, NRows, NColons, iLayer):
    # deltaHeightLeft = self.CalculateDeltaHeight(iLayer, 'left')
    deltaHeightLeft = _CalculateDeltaHeight(terrain=terrain, NRows=NRows, NColons=NColons, iLayer=iLayer,
                                            direction='left')
    newFlowLeft = self.flowSpeed * (deltaHeightLeft - self.maximumDeltaHeight[iLayer])
    newFlowLeft[newFlowLeft < 0] = 0
    flow[:, :, 0] = newFlowLeft

    # deltaHeightRight = self.CalculateDeltaHeight(iLayer, 'right')
    deltaHeightRight = _CalculateDeltaHeight(terrain=terrain, NRows=NRows, NColons=NColons,
                                             iLayer=iLayer, direction='right')
    newFlowRight = self.flowSpeed * (deltaHeightRight - self.maximumDeltaHeight[iLayer])
    newFlowRight[newFlowRight < 0] = 0
    flow[:, :, 1] = newFlowRight

    # deltaHeightTop = self.CalculateDeltaHeight(iLayer, 'top')
    deltaHeightTop = _CalculateDeltaHeight(terrain=terrain, NRows=NRows, NColons=NColons,
                                           iLayer=iLayer, direction='top')
    newFlowTop = self.flowSpeed * (deltaHeightTop - self.maximumDeltaHeight[iLayer])
    newFlowTop[newFlowTop < 0] = 0
    flow[:, :, 2] = newFlowTop

    # deltaHeightBottom = self.CalculateDeltaHeight(iLayer, 'bottom')
    deltaHeightBottom = _CalculateDeltaHeight(terrain=terrain, NRows=NRows, NColons=NColons,
                                              iLayer=iLayer, direction='bottom')
    newFlowBottom = self.flowSpeed * (deltaHeightBottom - self.maximumDeltaHeight[iLayer])
    newFlowBottom[newFlowBottom < 0] = 0
    flow[:, :, 3] = newFlowBottom

    # deltaHeightTopLeft = self.CalculateDeltaHeight(iLayer, 'bottom_right')
    deltaHeightTopLeft = _CalculateDeltaHeight(terrain=terrain, NRows=NRows, NColons=NColons,
                                               iLayer=iLayer, direction='bottom_right')
    newFlowTopLeft = self.flowSpeed * (deltaHeightTopLeft - np.sqrt(2) * self.maximumDeltaHeight[iLayer])
    newFlowTopLeft[newFlowTopLeft < 0] = 0
    flow[:, :, 4] = newFlowTopLeft

    # deltaHeightBottomRight = self.CalculateDeltaHeight(iLayer, 'top_left')
    deltaHeightBottomRight = _CalculateDeltaHeight(terrain=terrain, NRows=NRows, NColons=NColons,
                                                   iLayer=iLayer, direction='top_left')
    newFlowBottomRight = self.flowSpeed * (deltaHeightBottomRight - np.sqrt(2) * self.maximumDeltaHeight[iLayer])
    newFlowBottomRight[newFlowBottomRight < 0] = 0
    flow[:, :, 5] = newFlowBottomRight

    # deltaHeightBottomLeft = self.CalculateDeltaHeight(iLayer, 'top_right')
    deltaHeightBottomLeft = _CalculateDeltaHeight(terrain=terrain, NRows=NRows, NColons=NColons,
                                                  iLayer=iLayer, direction='top_right')
    newFlowBottomLeft = self.flowSpeed * (deltaHeightBottomLeft - np.sqrt(2) * self.maximumDeltaHeight[iLayer])
    newFlowBottomLeft[newFlowBottomLeft < 0] = 0
    flow[:, :, 6] = newFlowBottomLeft

    # deltaHeightTopRight = self.CalculateDeltaHeight(iLayer, 'bottom_left')
    deltaHeightTopRight = _CalculateDeltaHeight(terrain=terrain, NRows=NRows, NColons=NColons,
                                                iLayer=iLayer, direction='bottom_left')
    newFlowTopRight = self.flowSpeed * (deltaHeightTopRight - np.sqrt(2) * self.maximumDeltaHeight[iLayer])
    newFlowTopRight[newFlowTopRight < 0] = 0
    flow[:, :, 7] = newFlowTopRight

    # a = np.max(self.flow, axis=2)
    # flowScaling = self.terrain / ((self.flow[:, :, 0] + self.flow[:, :, 1] + self.flow[:, :, 2] + self.flow[:,
    #                                                                                                   :,
    #                                                                                                   3] + 0.001) * self.deltaT)
    flowScaling = terrain[:, :, iLayer] / ((flow[:, :, 0] + flow[:, :, 1] + flow[:, :,
                                                                                           2] + flow[:, :,
                                                                                                3] + flow[:, :,
                                                                                                     4] + flow[:,
                                                                                                          :,
                                                                                                          5] + flow[
                                                                                                               :, :,
                                                                                                               6] + flow[
                                                                                                                    :,
                                                                                                                    :,
                                                                                                                    7] + 0.001) * self.deltaT)
    flowScaling[flowScaling > 1] = 1
    # flowScaling *= 3
    flow[:, :, 0] *= flowScaling
    flow[:, :, 1] *= flowScaling
    flow[:, :, 2] *= flowScaling
    flow[:, :, 3] *= flowScaling
    flow[:, :, 4] *= flowScaling
    flow[:, :, 5] *= flowScaling
    flow[:, :, 6] *= flowScaling
    flow[:, :, 7] *= flowScaling

    self.inFlowRight = np.concatenate((flow[:, 1:NColons, 0],
                                       flow[:, 0:1, 0]),
                                      axis=1)
    self.inFlowLeft = np.concatenate((flow[:, NColons - 1:NColons, 1],
                                      flow[:, 0:-1, 1]),
                                     axis=1)
    self.inFlowBottom = np.concatenate((flow[NRows - 1:NRows, :, 2],
                                        flow[0:-1, :, 2]),
                                       axis=0)
    self.inFlowTop = np.concatenate((flow[1:NRows, :, 3],
                                     flow[0:1, :, 3]),
                                    axis=0)

    # top left
    self.inFlowTopLeft = np.concatenate((flow[:, NColons - 1:NColons, 4],
                                         flow[:, 0:-1, 4]),
                                        axis=1)
    self.inFlowTopLeft = np.concatenate((self.inFlowTopLeft[1:NRows, :],
                                         self.inFlowTopLeft[NRows - 1:NRows, :]),
                                        axis=0)
    # bottom right
    self.inFlowBottomRight = np.concatenate((flow[:, 1:NColons, 5],
                                             flow[:, 0:1, 5]),
                                            axis=1)
    self.inFlowBottomRight = np.concatenate((self.inFlowBottomRight[0:1, :],
                                             self.inFlowBottomRight[0:NRows - 1, :]),
                                            axis=0)
    # bottom left
    self.inFlowBottomLeft = np.concatenate((flow[:, NColons - 1:NColons, 6],
                                            flow[:, 0:-1, 6]),
                                           axis=1)
    self.inFlowBottomLeft = np.concatenate((self.inFlowBottomLeft[0:1, :],
                                            self.inFlowBottomLeft[0:NRows - 1, :]),
                                           axis=0)
    # top right
    self.inFlowTopRight = np.concatenate((flow[:, 1:NColons, 7],
                                          flow[:, 0:1, 7]),
                                         axis=1)
    self.inFlowTopRight = np.concatenate((self.inFlowTopRight[1:NRows, :],
                                          self.inFlowTopRight[NRows - 1:NRows, :]),
                                         axis=0)


@nb.jit(nopython = True)
#@nb.vectorize(['float32(float32, float32, float32, float32, string)'], target='cuda')
def _CalculateDeltaHeight(terrain, NRows, NColons, iLayer, direction='left'):
    totalHeight = np.sum(terrain[:, :, 0:iLayer+1], axis=2)
    if direction == 'left':
        totalHeightWrapped = np.concatenate((totalHeight[:, NColons - 1:NColons],
                                             totalHeight[:, 0:-1]),
                                            axis=1)
    elif direction == 'right':
        totalHeightWrapped = np.concatenate((totalHeight[:, 1:NColons],
                                             totalHeight[:, 0:1]),
                                            axis=1)
    elif direction == 'top':
        totalHeightWrapped = np.concatenate((totalHeight[1:NRows, :],
                                             totalHeight[NRows - 1:NRows, :]),
                                            axis=0)
    elif direction == 'bottom':
        totalHeightWrapped = np.concatenate((totalHeight[0:1, :],
                                             totalHeight[0:NRows - 1, :]),
                                            axis=0)
    elif direction == 'top_left':
        totalHeightWrapped = np.concatenate((totalHeight[:, NColons - 1:NColons],
                                             totalHeight[:, 0:-1]),
                                            axis=1)
        totalHeightWrapped = np.concatenate((totalHeightWrapped[1:NRows, :],
                                             totalHeightWrapped[NRows - 1:NRows, :]),
                                            axis=0)
    elif direction == 'bottom_right':
        totalHeightWrapped = np.concatenate((totalHeight[:, 1:NColons],
                                             totalHeight[:, 0:1]),
                                            axis=1)
        totalHeightWrapped = np.concatenate((totalHeightWrapped[0:1, :],
                                             totalHeightWrapped[0:NRows - 1, :]),
                                            axis=0)
    elif direction == 'bottom_left':
        totalHeightWrapped = np.concatenate((totalHeight[:, NColons - 1:NColons],
                                             totalHeight[:, 0:-1]),
                                            axis=1)
        totalHeightWrapped = np.concatenate((totalHeightWrapped[0:1, :],
                                             totalHeightWrapped[0:NRows - 1, :]),
                                            axis=0)
    elif direction == 'top_right':
        totalHeightWrapped = np.concatenate((totalHeight[:, 1:NColons],
                                             totalHeight[:, 0:1]),
                                            axis=1)
        totalHeightWrapped = np.concatenate((totalHeightWrapped[1:NRows, :],
                                             totalHeightWrapped[NRows - 1:NRows, :]),
                                            axis=0)
    deltaH = totalHeight - totalHeightWrapped
    return deltaH

#@numba.jitclass(spec=spec)
class ThermalErosionNumba():
    def __init__(self,
                 terrain,
                 NRows,
                 NColons,
                 NLayers,
                 deltaT = 1,
                 flowSpeed = 0.5,
                 maximumSlope = 30,
                 gridLength = 1):
        self.NRows = NRows
        self.NColons = NColons

        self.deltaT = deltaT
        self.gridLength = gridLength
        self.flowSpeed = flowSpeed
        self.maximumSlopeDegree = np.array(maximumSlope, dtype=np.float32)
        self.maximumSlope = np.pi*self.maximumSlopeDegree/180
        self.maximumDeltaHeight = gridLength * np.tan(self.maximumSlope)

        self.terrain = terrain
        self.flow = np.zeros((self.NRows, self.NColons, 8))  # Left, Right, Top, Bottom, Top_Left, Bottom_Right, Bottom_Left, Top_Right

        self.numberOfLayers = NLayers

    def UpdateFlow(self, iLayer):
        #deltaHeightLeft = self.CalculateDeltaHeight(iLayer, 'left')
        deltaHeightLeft = _CalculateDeltaHeight(terrain=self.terrain, NRows=self.NRows, NColons=self.NColons, iLayer=iLayer, direction='left')
        newFlowLeft = self.flowSpeed*(deltaHeightLeft - self.maximumDeltaHeight[iLayer])
        newFlowLeft[newFlowLeft < 0] = 0
        self.flow[:, :, 0] = newFlowLeft

        #deltaHeightRight = self.CalculateDeltaHeight(iLayer, 'right')
        deltaHeightRight = _CalculateDeltaHeight(terrain=self.terrain, NRows=self.NRows, NColons=self.NColons,
                                                iLayer=iLayer, direction='right')
        newFlowRight = self.flowSpeed*(deltaHeightRight - self.maximumDeltaHeight[iLayer])
        newFlowRight[newFlowRight < 0] = 0
        self.flow[:, :, 1] = newFlowRight

        #deltaHeightTop = self.CalculateDeltaHeight(iLayer, 'top')
        deltaHeightTop = _CalculateDeltaHeight(terrain=self.terrain, NRows=self.NRows, NColons=self.NColons,
                                                iLayer=iLayer, direction='top')
        newFlowTop = self.flowSpeed*(deltaHeightTop - self.maximumDeltaHeight[iLayer])
        newFlowTop[newFlowTop < 0] = 0
        self.flow[:, :, 2] = newFlowTop

        #deltaHeightBottom = self.CalculateDeltaHeight(iLayer, 'bottom')
        deltaHeightBottom = _CalculateDeltaHeight(terrain=self.terrain, NRows=self.NRows, NColons=self.NColons,
                                                iLayer=iLayer, direction='bottom')
        newFlowBottom = self.flowSpeed*(deltaHeightBottom - self.maximumDeltaHeight[iLayer])
        newFlowBottom[newFlowBottom < 0] = 0
        self.flow[:, :, 3] = newFlowBottom

        #deltaHeightTopLeft = self.CalculateDeltaHeight(iLayer, 'bottom_right')
        deltaHeightTopLeft = _CalculateDeltaHeight(terrain=self.terrain, NRows=self.NRows, NColons=self.NColons,
                                                iLayer=iLayer, direction='bottom_right')
        newFlowTopLeft = self.flowSpeed*(deltaHeightTopLeft - np.sqrt(2)*self.maximumDeltaHeight[iLayer])
        newFlowTopLeft[newFlowTopLeft < 0] = 0
        self.flow[:, :, 4] = newFlowTopLeft

        #deltaHeightBottomRight = self.CalculateDeltaHeight(iLayer, 'top_left')
        deltaHeightBottomRight = _CalculateDeltaHeight(terrain=self.terrain, NRows=self.NRows, NColons=self.NColons,
                                                iLayer=iLayer, direction='top_left')
        newFlowBottomRight = self.flowSpeed*(deltaHeightBottomRight - np.sqrt(2)*self.maximumDeltaHeight[iLayer])
        newFlowBottomRight[newFlowBottomRight < 0] = 0
        self.flow[:, :, 5] = newFlowBottomRight

        #deltaHeightBottomLeft = self.CalculateDeltaHeight(iLayer, 'top_right')
        deltaHeightBottomLeft = _CalculateDeltaHeight(terrain=self.terrain, NRows=self.NRows, NColons=self.NColons,
                                                iLayer=iLayer, direction='top_right')
        newFlowBottomLeft = self.flowSpeed*(deltaHeightBottomLeft - np.sqrt(2)*self.maximumDeltaHeight[iLayer])
        newFlowBottomLeft[newFlowBottomLeft < 0] = 0
        self.flow[:, :, 6] = newFlowBottomLeft

        #deltaHeightTopRight = self.CalculateDeltaHeight(iLayer, 'bottom_left')
        deltaHeightTopRight = _CalculateDeltaHeight(terrain=self.terrain, NRows=self.NRows, NColons=self.NColons,
                                                iLayer=iLayer, direction='bottom_left')
        newFlowTopRight = self.flowSpeed*(deltaHeightTopRight - np.sqrt(2)*self.maximumDeltaHeight[iLayer])
        newFlowTopRight[newFlowTopRight < 0] = 0
        self.flow[:, :, 7] = newFlowTopRight

        #a = np.max(self.flow, axis=2)
        #flowScaling = self.terrain / ((self.flow[:, :, 0] + self.flow[:, :, 1] + self.flow[:, :, 2] + self.flow[:,
        #                                                                                                   :,
        #                                                                                                   3] + 0.001) * self.deltaT)
        flowScaling = self.terrain[:, :, iLayer] / ((self.flow[:, :, 0] + self.flow[:, :, 1] + self.flow[:, :, 2] + self.flow[:, :, 3] + self.flow[:, :, 4] + self.flow[:, :, 5] + self.flow[:, :, 6] + self.flow[:, :, 7] + 0.001) * self.deltaT)
        flowScaling[flowScaling > 1] = 1
        #flowScaling *= 3
        self.flow[:, :, 0] *= flowScaling
        self.flow[:, :, 1] *= flowScaling
        self.flow[:, :, 2] *= flowScaling
        self.flow[:, :, 3] *= flowScaling
        self.flow[:, :, 4] *= flowScaling
        self.flow[:, :, 5] *= flowScaling
        self.flow[:, :, 6] *= flowScaling
        self.flow[:, :, 7] *= flowScaling

        self.inFlowRight = np.concatenate((self.flow[:, 1:self.NColons, 0],
                                           self.flow[:, 0:1, 0]),
                                          axis=1)
        self.inFlowLeft = np.concatenate((self.flow[:, self.NColons - 1:self.NColons, 1],
                                          self.flow[:, 0:-1, 1]),
                                         axis=1)
        self.inFlowBottom = np.concatenate((self.flow[self.NRows - 1:self.NRows, :, 2],
                                            self.flow[0:-1, :, 2]),
                                           axis=0)
        self.inFlowTop = np.concatenate((self.flow[1:self.NRows, :, 3],
                                         self.flow[0:1, :, 3]),
                                        axis=0)

        # top left
        self.inFlowTopLeft = np.concatenate((self.flow[:, self.NColons - 1:self.NColons, 4],
                                             self.flow[:, 0:-1, 4]),
                                            axis=1)
        self.inFlowTopLeft = np.concatenate((self.inFlowTopLeft[1:self.NRows, :],
                                             self.inFlowTopLeft[self.NRows - 1:self.NRows, :]),
                                            axis=0)
        # bottom right
        self.inFlowBottomRight = np.concatenate((self.flow[:, 1:self.NColons, 5],
                                             self.flow[:, 0:1, 5]),
                                            axis=1)
        self.inFlowBottomRight = np.concatenate((self.inFlowBottomRight[0:1, :],
                                             self.inFlowBottomRight[0:self.NRows - 1, :]),
                                            axis=0)
        # bottom left
        self.inFlowBottomLeft = np.concatenate((self.flow[:, self.NColons - 1:self.NColons, 6],
                                             self.flow[:, 0:-1, 6]),
                                            axis=1)
        self.inFlowBottomLeft = np.concatenate((self.inFlowBottomLeft[0:1, :],
                                             self.inFlowBottomLeft[0:self.NRows - 1, :]),
                                            axis=0)
        # top right
        self.inFlowTopRight = np.concatenate((self.flow[:, 1:self.NColons, 7],
                                             self.flow[:, 0:1, 7]),
                                            axis=1)
        self.inFlowTopRight = np.concatenate((self.inFlowTopRight[1:self.NRows, :],
                                             self.inFlowTopRight[self.NRows - 1:self.NRows, :]),
                                            axis=0)

    def CalculateDeltaHeight(self, iLayer, direction='left'):
        totalHeight = np.sum(self.terrain[:, :, 0:iLayer+1], axis=2)
        if direction == 'left':
            totalHeightWrapped = np.concatenate((totalHeight[:, self.NColons - 1:self.NColons],
                                                 totalHeight[:, 0:-1]),
                                                axis=1)
        elif direction == 'right':
            totalHeightWrapped = np.concatenate((totalHeight[:, 1:self.NColons],
                                                 totalHeight[:, 0:1]),
                                                axis=1)
        elif direction == 'top':
            totalHeightWrapped = np.concatenate((totalHeight[1:self.NRows, :],
                                                 totalHeight[self.NRows - 1:self.NRows, :]),
                                                axis=0)
        elif direction == 'bottom':
            totalHeightWrapped = np.concatenate((totalHeight[0:1, :],
                                                 totalHeight[0:self.NRows - 1, :]),
                                                axis=0)
        elif direction == 'top_left':
            totalHeightWrapped = np.concatenate((totalHeight[:, self.NColons - 1:self.NColons],
                                                 totalHeight[:, 0:-1]),
                                                axis=1)
            totalHeightWrapped = np.concatenate((totalHeightWrapped[1:self.NRows, :],
                                                 totalHeightWrapped[self.NRows - 1:self.NRows, :]),
                                                axis=0)
        elif direction == 'bottom_right':
            totalHeightWrapped = np.concatenate((totalHeight[:, 1:self.NColons],
                                                 totalHeight[:, 0:1]),
                                                axis=1)
            totalHeightWrapped = np.concatenate((totalHeightWrapped[0:1, :],
                                                 totalHeightWrapped[0:self.NRows - 1, :]),
                                                axis=0)
        elif direction == 'bottom_left':
            totalHeightWrapped = np.concatenate((totalHeight[:, self.NColons - 1:self.NColons],
                                                 totalHeight[:, 0:-1]),
                                                axis=1)
            totalHeightWrapped = np.concatenate((totalHeightWrapped[0:1, :],
                                                 totalHeightWrapped[0:self.NRows - 1, :]),
                                                axis=0)
        elif direction == 'top_right':
            totalHeightWrapped = np.concatenate((totalHeight[:, 1:self.NColons],
                                                 totalHeight[:, 0:1]),
                                                axis=1)
            totalHeightWrapped = np.concatenate((totalHeightWrapped[1:self.NRows, :],
                                                 totalHeightWrapped[self.NRows - 1:self.NRows, :]),
                                                axis=0)
        deltaH = totalHeight - totalHeightWrapped
        return deltaH

    def UpdateTerrainHeight(self, iLayer):
        self.terrain[:, :, iLayer] -= self.deltaT*(self.flow[:, :, 0] + self.flow[:, :, 1] + self.flow[:, :, 2] + self.flow[:, :, 3] + self.flow[:, :, 4] + self.flow[:, :, 5] + self.flow[:, :, 6] + self.flow[:, :, 7])
        self.terrain[:, :, iLayer] += self.deltaT*(self.inFlowLeft + self.inFlowRight + self.inFlowTop + self.inFlowBottom + self.inFlowTopLeft + self.inFlowBottomRight + self.inFlowBottomLeft + self.inFlowTopRight)

    def __call__(self, *args, **kwargs):
        for iLayer in range(self.numberOfLayers):
            if self.maximumSlopeDegree[iLayer] < 90:
                self.UpdateFlow(iLayer)
                self.UpdateTerrainHeight(iLayer)

class ThermalWeathering():
    def __init__(self,
                 terrain,
                 weatheringRate = 1):
        self.weatheringRate = np.array(weatheringRate)
        self.numberOfLayers = np.size(terrain, axis=2)
        self.layerShape = (np.size(terrain, 0), np.size(terrain, 1))
        self.terrain = terrain

    def Weather(self, amount):
        '''
        NOTE THAT CURRENTLY ONLY WORKS FOR 2 LAYERS, IT WOULD BE SIMPLE TO CORRECT THIS THOU.
        '''
        amountToWeather = amount * np.ones(self.layerShape)
        for iLayer in np.linspace(self.numberOfLayers-1, 0, self.numberOfLayers, dtype=int):
            if iLayer == self.numberOfLayers-1:
                amountToWeather -= self.terrain[:, :, iLayer]
                amountToWeather[amountToWeather < 0] = 0
            else:
                self.terrain[:, :, iLayer] -= self.weatheringRate[iLayer]*amountToWeather
                self.terrain[:, :, iLayer+1] += self.weatheringRate[iLayer]*amountToWeather



