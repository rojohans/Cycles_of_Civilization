import numpy as np
#from ... import FluidDynamics as FluidDynamics # Be aware that this needs to change if the folder structure were to change,
import matplotlib.pyplot as plt
import scipy.interpolate as interpolate


class HydrolicErosion():
    def __init__(self,
                 terrain,
                 evaporationRate = 0.05,
                 deltaT = 1,
                 flowSpeed = 0.5,
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
        self.gridLength = gridLength
        self.carryCapacityLimit = carryCapacityLimit
        self.erosionRate = erosionRate
        self.depositionRate = depositionRate
        self.maximumErosionDepth = maximumErosionDepth
        self.minimumErosionAngle = np.pi*minimumErosionAngle/180

        self.terrain = terrain
        self.water = np.zeros((self.NRows, self.NColons, 2))

        #self.water[200, 200, 0] = 100
        #self.water[201, 200, 0] = 100
        #self.water[200, 201, 0] = 100
        #self.water[201, 201, 0] = 100

        self.suspendedSediment = np.zeros((self.NRows, self.NColons, 2))

        self.flow = np.zeros((self.NRows, self.NColons, 4)) # Left, Right, Top, Bottom
        self.velocity = np.zeros((self.NRows, self.NColons, 2)) # x, y
        self.slope = np.zeros((self.NRows, self.NColons))
        self.carryCapacity = np.zeros((self.NRows, self.NColons))

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

        flowScaling = 0.5*self.water[:, :, 0]/((self.flow[:, :, 0] + self.flow[:, :, 1] + self.flow[:, :, 2] + self.flow[:, :, 3]+0.001)*self.deltaT)
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
        totalHeight =self.terrain + self.water[:, :, 0]

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
        self.water[:, :, 1] = self.water[:, :, 0] - (
                self.flow[:, :, 0] + self.flow[:, :, 1] + self.flow[:, :, 2] + self.flow[:, :,3]) + \
                              self.inFlowLeft + self.inFlowRight + self.inFlowTop + self.inFlowBottom

    def UpdateVelocity(self):
        #self.velocity[:, :, 0] = (self.flow[:, :, 1] - self.flow[:, :, 0] + self.inFlowLeft - self.inFlowRight)
        #self.velocity[:, :, 1] = (self.flow[:, :, 2] - self.flow[:, :, 3] + self.inFlowBottom - self.inFlowTop)
        self.velocity[:, :, 0] = (self.flow[:, :, 1] - self.flow[:, :, 0] + self.inFlowLeft - self.inFlowRight)/\
                                 (self.water[:, :, 0] + self.water[:, :, 1]+0.001)
        self.velocity[:, :, 1] = (self.flow[:, :, 2] - self.flow[:, :, 3] + self.inFlowBottom - self.inFlowTop)/\
                                 (self.water[:, :, 0] + self.water[:, :, 1]+0.001)

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

    def UpdateCarryCapacity(self):
        '''
        The carry capacity depends on the water depth. At water > mamimumErosionDepth the capacity is zero.
        :return:
        '''
        waterDepthMultiplier = self.water[:, :, 1]*2.5
        #waterDepthMultiplier = 10*self.water[:, :, 1]*(1-self.water[:, :, 1]/self.maximumErosionDepth)/self.maximumErosionDepth
        #waterDepthMultiplier[self.water[:, :, 1] > self.maximumErosionDepth] = 0
        #slopeMultiplier = np.sin(self.slope)
        slopeMultiplier = np.sin((self.slope - self.minimumErosionAngle) /
                                 (np.pi / 2 - self.minimumErosionAngle) * np.pi / 2)
        slopeMultiplier[self.slope < self.minimumErosionAngle] = 0
        self.carryCapacity =  waterDepthMultiplier * self.carryCapacityLimit * slopeMultiplier * np.sqrt(self.velocity[:, :, 0]**2 + self.velocity[:, :, 1]**2)
        self.suspendedSediment[:, :, 1] = self.suspendedSediment[:, :, 0]

    def Erode(self):
        erodedSediment = self.erosionRate*(self.carryCapacity - self.suspendedSediment[:, :, 0])
        erodedSediment[erodedSediment < 0] = 0

        lowestAdjacentHeight = np.zeros((self.NRows, self.NColons, 4))
        lowestAdjacentHeight[:, :, 0] = self.terrainLeft
        lowestAdjacentHeight[:, :, 1] = self.terrainRight
        lowestAdjacentHeight[:, :, 2] = self.terrainTop
        lowestAdjacentHeight[:, :, 3] = self.terrainBottom
        lowestAdjacentHeight = np.min(lowestAdjacentHeight, axis=2)

        maximumErosion = self.terrain-lowestAdjacentHeight
        erodedSediment[erodedSediment > maximumErosion] = maximumErosion[erodedSediment > maximumErosion]

        self.terrain -= erodedSediment
        self.suspendedSediment[:, :, 1] += erodedSediment

    def Deposit(self):
        depositedSediment = self.depositionRate * (self.suspendedSediment[:, :, 0] - self.carryCapacity)
        depositedSediment[depositedSediment < 0] = 0

        highestAdjacentHeight = np.zeros((self.NRows, self.NColons, 4))
        highestAdjacentHeight[:, :, 0] = self.terrainLeft
        highestAdjacentHeight[:, :, 1] = self.terrainRight
        highestAdjacentHeight[:, :, 2] = self.terrainTop
        highestAdjacentHeight[:, :, 3] = self.terrainBottom
        highestAdjacentHeight = np.max(highestAdjacentHeight, axis=2)

        maximumDeposition = highestAdjacentHeight - self.terrain
        depositedSediment[depositedSediment > maximumDeposition] = maximumDeposition[depositedSediment > maximumDeposition]

        self.terrain += depositedSediment
        self.suspendedSediment[:, :, 1] -= depositedSediment

    def SedimentTransportation(self):
        flowScaling = self.suspendedSediment[:, :, 1] / ((self.flow[:, :, 0] + self.flow[:, :, 1] + self.flow[:, :,
                                                                                        2] + self.flow[:, :,
                                                                                             3] + 0.001) * self.deltaT)
        flowScaling[flowScaling > 1] = 1

        sedimentFlow = self.flow.copy()

        sedimentFlow[:, :, 0] *= flowScaling
        sedimentFlow[:, :, 1] *= flowScaling
        sedimentFlow[:, :, 2] *= flowScaling
        sedimentFlow[:, :, 3] *= flowScaling

        sedimentInFlowRight = np.concatenate((sedimentFlow[:, 1:self.NColons, 0],
                                           sedimentFlow[:, 0:1, 0]),
                                          axis=1)
        sedimentInFlowLeft = np.concatenate((sedimentFlow[:, self.NColons - 1:self.NColons, 1],
                                          sedimentFlow[:, 0:-1, 1]),
                                         axis=1)
        sedimentInFlowBottom = np.concatenate((sedimentFlow[self.NRows - 1:self.NRows, :, 2],
                                            sedimentFlow[0:-1, :, 2]),
                                           axis=0)
        sedimentInFlowTop = np.concatenate((sedimentFlow[1:self.NRows, :, 3],
                                         sedimentFlow[0:1, :, 3]),
                                        axis=0)

        self.suspendedSediment[:, :, 0] = self.suspendedSediment[:, :, 1] - (
                sedimentFlow[:, :, 0] + sedimentFlow[:, :, 1] + sedimentFlow[:, :, 2] + sedimentFlow[:, :, 3]) + \
                              sedimentInFlowLeft + sedimentInFlowRight + sedimentInFlowTop + sedimentInFlowBottom

    def Evaporation(self):
        self.water[:, :, 0] = self.water[:, :, 1]*(1 - self.evaporationRate*self.deltaT)

    def Visualize(self):
        if self.terrainplot == None:
            self.terrainplot = plt.imshow(self.terrain)

            '''
            fig, axs = plt.subplots(3, 2)

            self.terrainplot = axs[0][0].imshow(self.terrain)
            self.waterPlot = axs[0][1].imshow(self.water[:, :, 0])
            self.suspendedSedimentPlot = axs[1][0].imshow(self.suspendedSediment[:, :, 0])
            self.slopeplot = axs[1][1].imshow(self.slope)
            self.velocityPlot = axs[2, 0].imshow(np.sqrt(self.velocity[:, :, 0]**2 + self.velocity[:, :, 1]**2))
            '''
            plt.pause(0.00001)
        else:
            self.terrainplot.set_array(self.terrain)
            '''
            self.waterPlot.set_array(self.water[:, :, 0])
            #self.waterPlot.set_clim(vmin = 0, vmax = np.max(self.water[:, :, 0]))
            self.waterPlot.set_clim(vmin=0, vmax=10)
            self.suspendedSedimentPlot.set_array(self.suspendedSediment[:, :, 0])
            self.slopeplot.set_array(self.slope)
            self.velocityPlot.set_array(np.sqrt(self.velocity[:, :, 0]**2 + self.velocity[:, :, 1]**2))
            '''
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
        self.maximumSlope = np.pi*maximumSlope/180
        self.maximumDeltaHeight = gridLength * np.tan(self.maximumSlope)

        self.terrain = terrain
        self.flow = np.zeros((self.NRows, self.NColons, 4))  # Left, Right, Top, Bottom

    def UpdateSlope(self):
        terrainLeft = np.concatenate((self.terrain[:, self.NColons - 1:self.NColons],
                                      self.terrain[:, 0:-1]),
                                     axis=1)
        terrainRight = np.concatenate((self.terrain[:, 1:self.NColons],
                                       self.terrain[:, 0:1]),
                                      axis=1)
        xAngle = np.arctan((terrainRight-terrainLeft)/ (2*self.gridLength))

        terrainTop = np.concatenate((self.terrain[1:self.NRows, :],
                                     self.terrain[self.NRows-1:self.NRows, :]),
                                    axis=0)
        terrainBottom = np.concatenate((self.terrain[0:1, :],
                                        self.terrain[0:self.NRows-1, :]),
                                       axis = 0)
        yAngle = np.arctan((terrainTop-terrainBottom)/(2*self.gridLength))

        self.slope = np.sqrt(xAngle**2 + yAngle**2)/np.sqrt(2)

    def UpdateFlow(self):
        deltaHeightLeft = self.CalculateDeltaHeight('left')
        newFlowLeft = self.flow[:, :, 0] + self.deltaT * self.flowSpeed * deltaHeightLeft
        newFlowLeft[newFlowLeft < 0] = 0
        self.flow[:, :, 0] = newFlowLeft

        deltaHeightRight = self.CalculateDeltaHeight('right')
        newFlowRight = self.flow[:, :, 1] + self.deltaT * self.flowSpeed * deltaHeightRight
        newFlowRight[newFlowRight < 0] = 0
        self.flow[:, :, 1] = newFlowRight

        deltaHeightTop = self.CalculateDeltaHeight('top')
        newFlowTop = self.flow[:, :, 2] + self.deltaT * self.flowSpeed * deltaHeightTop
        newFlowTop[newFlowTop < 0] = 0
        self.flow[:, :, 2] = newFlowTop

        deltaHeightBottom = self.CalculateDeltaHeight('bottom')
        newFlowBottom = self.flow[:, :, 3] + self.deltaT * self.flowSpeed * deltaHeightBottom
        newFlowBottom[newFlowBottom < 0] = 0
        self.flow[:, :, 3] = newFlowBottom

        excessSlope = self.slope.copy()
        print(np.min(excessSlope))
        print(np.max(excessSlope))
        excessSlope[excessSlope < self.maximumSlope] = 0
        excessSlope[excessSlope > 0] -= self.maximumSlope
        excessSlope /= np.max(excessSlope)
        print(np.min(excessSlope))
        print(np.max(excessSlope))

        print(np.min(self.flow))
        print(np.max(self.flow))

        flowScaling = excessSlope / ((self.flow[:, :, 0] + self.flow[:, :, 1] + self.flow[:, :, 2] + self.flow[:, :, 3] + 0.001) * self.deltaT)
        flowScaling[flowScaling > 1] = 1
        self.flow[:, :, 0] *= flowScaling
        self.flow[:, :, 1] *= flowScaling
        self.flow[:, :, 2] *= flowScaling
        self.flow[:, :, 3] *= flowScaling
        print(np.min(self.flow))
        print(np.max(self.flow))
        print(' ')

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

    def CalculateDeltaHeight(self, direction='left'):
        if direction == 'left':
            totalHeightWrapped = np.concatenate((self.terrain[:, self.NColons - 1:self.NColons],
                                                 self.terrain[:, 0:-1]),
                                                axis=1)
        elif direction == 'right':
            totalHeightWrapped = np.concatenate((self.terrain[:, 1:self.NColons],
                                                 self.terrain[:, 0:1]),
                                                axis=1)
        elif direction == 'top':
            totalHeightWrapped = np.concatenate((self.terrain[1:self.NRows, :],
                                                 self.terrain[self.NRows - 1:self.NRows, :]),
                                                axis=0)
        elif direction == 'bottom':
            totalHeightWrapped = np.concatenate((self.terrain[0:1, :],
                                                 self.terrain[0:self.NRows - 1, :]),
                                                axis=0)
        deltaH = self.terrain - totalHeightWrapped
        #deltaH[deltaH > self.maximumDeltaHeight] = self.maximumDeltaHeight
        return deltaH

    def UpdateTerrainHeight(self):
        self.terrain -= self.flow[:, :, 0] + self.flow[:, :, 1] + self.flow[:, :, 2] + self.flow[:, :, 3]
        self.terrain += self.inFlowLeft + self.inFlowRight + self.inFlowTop + self.inFlowBottom

