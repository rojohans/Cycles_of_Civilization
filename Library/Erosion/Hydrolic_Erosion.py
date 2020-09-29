




















import numpy as np
#from ... import FluidDynamics as FluidDynamics # Be aware that this needs to change if the folder structure were to change,


class WaterDrop():
    adjacentTilesTemplate = []
    erosionWeightTemplate = []
    erosionTileTemplate = []

    rockMap = []
    gridSize = []

    dropList = [] # Used when drops are to "kill" themself.

    def __init__(self,
                 inertia,
                 gravity,
                 evaporationRate,
                 capacityMultiplier,
                 minimumSlope,
                 erosionRadius,
                 depositionRate,
                 erosionRate,
                 numberOfSteps,
                 maximumUnimprovedSteps,
                 storeTrail,
                 maximumNumberOfSteps):

        self.xPreviousStep = None
        self.yPreviousStep = None
        self.zPreviousStep = None
        self.adjacentTilesPrevious = None # Used for deposition.
        self.adjacentHeightsPrevious = None # Used for deposition.
        self.heightDifference = None
        self.direction = np.array([0, 0])
        self.direction = self.adjacentTilesTemplate[np.random.randint(0, 4), :]#initially a random direction is choosen.

        self.storeTrail = storeTrail
        if self.storeTrail:
            self.trailData = np.zeros((3, numberOfSteps))
            self.step = 0 # The index used to access the trailData array.
        self.unimprovedSteps = 0
        self.maximumUnimprovedSteps = maximumUnimprovedSteps
        self.numberOfUnimprovedSteps = 0
        self.step = 0 # The number of steps taken
        self.maximumNumberOfSteps = maximumNumberOfSteps # The amount of steps taken before termination

        self.velocity = 0
        self.waterAmount = 1
        self.sedimentCapacity = 0
        self.sedimentAmount = 0

        self.inertia = inertia
        self.gravity = gravity
        self.capacityMultiplier = capacityMultiplier
        self.minimumSlope = minimumSlope
        self.depositionRate = depositionRate
        self.erosionRate = erosionRate
        self.erosionRadius = erosionRadius
        self.evaporationRate = 1+evaporationRate



    def StoreState(self):
        '''
        The coordinates of the drop is stored. This is done in order for certain methods (eg. Erode()) to use the
        previous coordinates. It is also done in order for complete trail data to be stored for visualization.
        :return:
        '''
        # The coordinates are stored for later use.
        self.xPreviousStep = self.x
        self.yPreviousStep = self.y
        self.zPreviousStep = self.z

        # Stores the adjacentTiles and heights for later use when doing deposition.
        self.adjacentTilesPrevious = self.adjacentTiles
        self.adjacentHeightsPrevious = self.adjacentHeights

        # Stores coordinates in array in order to visualize.
        if self.storeTrail:
            # x-, y- and z-coordinates are stored.
            self.trailData[0, self.step] = self.xPreviousStep
            self.trailData[1, self.step] = self.yPreviousStep
            self.trailData[2, self.step] = self.zPreviousStep
            self.step += 1


    def Move(self):
        return NotImplementedError


    def UpdateDirection(self):
        return NotImplementedError


    def UpdateVelocity(self):
        '''
        The increase or decrease of the velocity is determined by the heightdifference which corresponds to the slope
        of the terrain. The maximum velocity possible is set to be the gravity value given in the constructor.
        :param self:
        :return:
        '''
        # If the drop were to go uphill it loses all it's velocity (!!!THIS SHOULD BE MODIFIED!!!)

        if self.heightDifference>0:
            self.velocity /= 2
        else:
            #self.velocity = np.sqrt(self.velocity ** 2 - self.gravity * self.heightDifference)
            self.velocity = self.velocity/2 + np.arctan(-self.heightDifference) * self.gravity/np.pi


    def DepositOrErode(self):
        '''
        The Method Updates the amount of sediment the drop can carry. Based on this amount and wether or not the drop
        has travelled uphill it is determined if the drop should erode or deposit. In the case of uphill travel all
        sediment if possible is deposited. If the amount of sediment is less than the capacity the drop will erode,
        otherwise it will deposit.
        :return:
        '''

        # In the case of parallell drops the adjacentHeights and the heightDifference needs to be recalculated, these
        # values depends on the heightMap which could have been changed by another drop. If this is not taken into
        # account multiple drops can erode the same area creating a deep hole. (the depth of the hole will approach -inf).
        # An alternative approach is to limit the amount of deposition/erosion to 1/N of the highest allowed
        # deposition/erosion value for each drop. N is the number of drops, in that case it would require all N drops
        # to deposit/erode all the material, thusly no holes or peaks could be formed. A downside is that it lowers the
        # effect of each drop, thusly requiring more drops to get the same effect. If the code utilizes a GPU for
        # parallell computations this approach could be viable.


        # Determines if erosion or deposition should occur.
        if self.heightDifference > 0:
            self.Deposit(depositAll=True)
        else:
            #self.sedimentCapacity = np.max((-self.heightDifference, self.minimumSlope)) * self.velocity * \
            #                        self.waterAmount * self.capacityMultiplier
            # The sediment capacity is capped by the amount of water. Idealy It should be capped to a percentage,
            # 30% for example, of the water amount.
            #self.sedimentCapacity = np.min((self.waterAmount, np.max((-self.heightDifference, self.minimumSlope)) * self.velocity * self.capacityMultiplier))
            self.sedimentCapacity = np.max((-self.heightDifference, self.minimumSlope)) * self.velocity * self.waterAmount * self.capacityMultiplier
            #self.sedimentCapacity = self.velocity * self.waterAmount * self.capacityMultiplier
            #print(self.sedimentCapacity, np.max((-self.heightDifference, self.minimumSlope)), self.velocity, self.waterAmount)
            #self.sedimentCapacity = self.capacityMultiplier * np.min((self.waterAmount, np.max((-self.heightDifference, self.minimumSlope)) * self.velocity))
            #self.sedimentCapacity = np.max((-self.heightDifference, self.minimumSlope)) * self.velocity * self.capacityMultiplier * self.waterAmount

            if self.sedimentAmount < self.sedimentCapacity:
                self.Erode()
            else:
                self.Deposit()


    def Deposit(self):
        return NotImplementedError


    def Erode(self):
        return NotImplementedError


    #def CheckImprovement(self):
    def CheckForTermination(self):
        '''
        This method is used to determine if the drop should be terminated. This is the case if the drop has traveled
        uphill for too long.
        :return:
        '''

        nearestColumn = self._periodic(np.round(self.x)) # <--- column
        nearestRow = self._periodic(np.round(self.y)) # <--- row


        # If the number of steps has been reached the drop is terminated. (This is not optimal but it helps in avoiding
        # infinite drops.)
        self.step += 1
        if self.step >= self.maximumNumberOfSteps:
            self.Terminate()
        else:
            # Check if a water segment has been reached, if so the drop should be dissolved in the water.
            potentialIDOfCell = self.waterSegmentIdentificationMap[nearestRow.astype(int) + nearestColumn.astype(int) * self.gridSize]
            if potentialIDOfCell is not None:
                self.Terminate(potentialIDOfCell)
            else:
                # Check if the drop has traveled uphill, and if so for how many turns. The drop is detstroyed if it has
                # traveled uphill for too many steps.
                if self.heightDifference > 0:
                    self.unimprovedSteps += 1
                    if self.unimprovedSteps >= self.maximumUnimprovedSteps:
                        self.Terminate()
                else:
                    self.unimprovedSteps = 0


    def Evaporate(self):
        self.waterAmount /= self.evaporationRate


    def Terminate(self, waterSegmentID = None):
        '''
        Before the drop is terminated all the sediment is deposited.
        :return:
        '''
        nearestColumn = self._periodic(np.round(self.x)) # <--- column
        nearestRow = self._periodic(np.round(self.y)) # <--- row

        # Check if a waterSegmentID value was given as function input, in not a star cell is computed.
        if waterSegmentID is None:
            [a, b, waterSegmentID] = FluidDynamics.FluidSegment.GetStartCell(nearestRow, nearestColumn)


        '''
        NOTE THAT THE WATER CALCULATIONS HAS BEEN TURNED OFF. TO ENABLE THE CALCULATIONS THE '#' SIGNS SHOULD BE REMOVED
        FROM THE .INIITATEFLOW() METHOD CALLS.
        '''


        # Check if the start cell is part of a segment or not. If it is fluid will be added to that segment, if not a
        # new segment will be created.
        if waterSegmentID is None:
            # SEGMENT IS CREATED
            createdWaterSegment = FluidDynamics.FluidSegment(self.waterAmount, a[0, 0], a[0, 1])
            #createdWaterSegment.InitiateFlow()  # Makes the water flow and fill up adjacent tiles.

            # Adds the newly created water segment to the water segment list
            self.waterSegments.append(createdWaterSegment)
        else:
            # FLUID IS ADDED TO SEGMENT
            encounteredSegmentID = waterSegmentID

            # This could be done using a better search algorithm. The better search algorithm would start
            # the search in the middle of the list and then divide the list into two parts. The next step is
            # to repeat the procedure until the correct object has been found. This is an efficient search
            # mechanism but can only be performed if the objects are sorted by their ID.
            # Gets the specific segment object for which the ID is known.
            for waterSegment in self.waterSegments:
                if encounteredSegmentID == waterSegment.ID:
                    waterSegment.availableFluid = +self.waterAmount
                    #waterSegment.InitiateFlow()
                    break
        self.dropList.remove(self)


    #
    # The following part of the class consist of utility methods like getters and setters.
    #
    def __call__(self):
        '''
        Called to simulate a single step.
        :return:
        '''
        self.StoreState()
        self.Move()
        self.UpdateVelocity()
        self.DepositOrErode()
        #self.CheckImprovement()
        self.CheckForTermination()
        self.Evaporate()

    def __repr__(self):
        # This method is automatically used when an object of this
        # class is displayed using the print() function
        return("Drop is at x = {}, y = {}, z = {}".format(self.x, self.y, self.z))

    def _periodic(self, value):
        return (value + self.gridSize) % (self.gridSize)

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        self._x = self._periodic(value)

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, value):
        self._y = self._periodic(value)

    @classmethod
    def LinkToHeightMap(cls, rockMap, sedimentMap, totalHeightMap, waterMap, waterSegmentIdentificationMap):
        '''
        This is used in order for the drop to have access to the heightmap. If the heightMap were to be changed by
        one drop all other drops would also notice the change. When assigning the gridSize the heightMap is assumed
        to be cubic in shape.
        :param rockMap:
        :return:
        '''
        cls.rockMap = rockMap
        cls.sedimentMap = sedimentMap
        cls.totalHeightMap = totalHeightMap
        cls.waterMap = waterMap
        cls.gridSize = np.shape(rockMap)[0]
        # Used to identify which tiles are part of which water segments
        cls.waterSegmentIdentificationMap = waterSegmentIdentificationMap


    @classmethod
    def LinkToDrops(cls, dropList):
        # Gives all the drops access to the list of drops.
        # Used when drops are to "kill" themself.
        cls.dropList = dropList

    @classmethod
    def LinkToWaterSegments(cls, waterSegments):
        # Gives all the drops access to all the water segments.
        cls.waterSegments = waterSegments

    @classmethod
    def InitializeErosionTemplates(cls, maximumErosionRadius):
        # Initializes lists used as templates when eroding multiple tiles.
        for radius in range(0, maximumErosionRadius):
            rows = range(-radius, radius, 1)
            columns = range(-radius, radius, 1)
            rowGrid, columnGrid = np.meshgrid(rows, columns)
            rowList = np.reshape(rowGrid, [rowGrid.size, 1])
            columnList = np.reshape(columnGrid, [columnGrid.size, 1])
            distances = np.sqrt(rowList ** 2 + columnList ** 2)
            rowList = rowList[distances < radius]
            columnList = columnList[distances < radius]

            # The template lists are expanded.
            cls.erosionWeightTemplate.append(
                (radius - distances[distances < radius]) / np.sum(radius - distances[distances < radius]))

            erosionTiles = np.zeros((cls.erosionWeightTemplate[radius].shape[0], 2))
            erosionTiles[:, 0] = rowList
            erosionTiles[:, 1] = columnList
            cls.erosionTileTemplate.append(erosionTiles)


    @classmethod
    def InitializeAdjacentTileTemplate(cls):
        return NotImplementedError


# ======================================================================================================================
# ======================================================================================================================
class ContinuousDrop(WaterDrop):
    '''

    # -------------------TO DO-----------------------
    When using the CalculateZ method the values other than z can be stored tp be used in the next move step, this would
    increase performance as the same values do not need to be calculated twice.

    Look into if the erosionAmount calculation in the Erode() method needs to be altered.
    '''

    def __init__(self,
                 x = None,
                 y = None,
                 inertia = 0.3,
                 gravity = 4,
                 evaporationRate = 0.02,
                 capacityMultiplier = 40,
                 minimumSlope = 0.005,
                 erosionRadius = 4,
                 depositionRate = 0.1,
                 erosionRate = 0.1,
                 numberOfSteps = 64,
                 maximumUnimprovedSteps = 1,
                 storeTrail = False,
                 maximumNumberOfSteps = 100):
        '''
        :param gridSize:
        :param x:
        :param y:
        :param inertia: Determines how easily the drop changes direction.
        :param gravity: Sets the maximum velocity
        :param evaporationRate:
        :param capacityMultiplier:
        :param minimumSlope: Prevents the sediment capacity from becoming negative.
        :param erosionradius:
        :param depositionRate:
        :param erosionRate:
        :param numberOfSteps:
        :param storeTrail: A boolean value indicating if the trail is to be stored or not.
        '''

        super().__init__(inertia,
                         gravity,
                         evaporationRate,
                         capacityMultiplier,
                         minimumSlope,
                         erosionRadius,
                         depositionRate,
                         erosionRate,
                         numberOfSteps,
                         maximumUnimprovedSteps,
                         storeTrail,
                         maximumNumberOfSteps)

        # If x and y values are not given they will be randomized to be within the grid.
        if x is None:
            self.x = self.gridSize * np.random.rand()
        else:
            self.x = x
        if y is None:
            self.y = self.gridSize * np.random.rand()
        else:
            self.y = y

        self.xWholePart = np.floor(self.x)
        self.yWholePart = np.floor(self.y)
        self.xDecimalPart = self.x - self.xWholePart
        self.yDecimalPart = self.y - self.yWholePart

        self.adjacentTiles = np.zeros((4, 2))
        self.adjacentTiles[:, 0] = self._periodic(self.adjacentTilesTemplate[:, 0] + self.yWholePart)
        self.adjacentTiles[:, 1] = self._periodic(self.adjacentTilesTemplate[:, 1] + self.xWholePart)
        self.adjacentHeights = self.totalHeightMap[self.adjacentTiles[:, 0].astype(int), self.adjacentTiles[:, 1].astype(int)]

        # Interpolates the z coordinate value of the drop based on the surrounding heights.
        self.z = (1-self.xDecimalPart) * (self.adjacentHeights[0]*(1-self.yDecimalPart) + self.adjacentHeights[2]*self.yDecimalPart) \
            + self.xDecimalPart * (self.adjacentHeights[1] * (1-self.yDecimalPart) + self.adjacentHeights[3]*self.yDecimalPart)


    def Move(self):
        '''
        The drop is moved according to the gradient at the current coordinates. The gradient is calculated using the
        heightvalues of the 4 adjacent tiles.
        '''

        # The direction is updated
        self.UpdateDirection(self.xDecimalPart, self.yDecimalPart, self.adjacentHeights)

        # The drop is moved
        self.x += self.direction[0]
        self.y += self.direction[1]

        # The whole and decimal parts of the coordinates are updated
        self.xWholePart = np.floor(self.x)
        self.yWholePart = np.floor(self.y)
        self.xDecimalPart = self.x - self.xWholePart
        self.yDecimalPart = self.y - self.yWholePart

        # The adjacent tiles are selected using the adjacent tile template.
        self.adjacentTiles = np.zeros((4, 2))
        self.adjacentTiles[:, 0] = self._periodic(self.adjacentTilesTemplate[:, 0] + self.yWholePart)
        self.adjacentTiles[:, 1] = self._periodic(self.adjacentTilesTemplate[:, 1] + self.xWholePart)
        # Retrieves the map height for the adjacent tiles and interpolates the height of the water drop.
        self.adjacentHeights = self.totalHeightMap[self.adjacentTiles[:, 0].astype(int), self.adjacentTiles[:, 1].astype(int)]

        # Interpolates the z coordinate value of the drop based on the surrounding heights.
        self.z = (1-self.xDecimalPart) * (self.adjacentHeights[0]*(1-self.yDecimalPart) + self.adjacentHeights[2]*self.yDecimalPart) \
            + self.xDecimalPart * (self.adjacentHeights[1] * (1-self.yDecimalPart) + self.adjacentHeights[3]*self.yDecimalPart)
        self.heightDifference = self.z - self.zPreviousStep


    def UpdateDirection(self, xDecimalPart, yDecimalPart, adjacentHeights):
        #
        #:param xDecimalPart:
        #:param yDecimalPart:
        #:param adjacentHeights:
        #:return:
        #
        # The gradient is computed. If necessary the gradient can be randomized in the case that it's a null vector.
        xGradient1 = adjacentHeights[1] - adjacentHeights[0]
        xGradient2 = adjacentHeights[3] - adjacentHeights[2]
        yGradient1 = adjacentHeights[2] - adjacentHeights[0]
        yGradient2 = adjacentHeights[3] - adjacentHeights[1]
        gradient = np.array([xGradient1*(1-yDecimalPart) + xGradient2*yDecimalPart, \
                             yGradient1 * (1 - xDecimalPart) + yGradient2 * xDecimalPart])

        # If the gradient is a null vector a random unit vector is choosen.
        gradientNorm = np.linalg.norm(gradient)
        if gradientNorm == 0:
            randomAngle = 2*np.pi * np.random.rand()
            gradient[0] = np.cos(randomAngle)
            gradient[1] = np.sin(randomAngle)
        else:
            gradient /= gradientNorm

        # The direction of the water drop is updated. This should depend on the drops inertia (velocity and mass), right
        #  now a constant inertia is used.
        #self.direction = self.direction * self.inertia - gradient * (1-self.inertia)
        self.direction = self.direction * self.inertia * self.velocity**2 - gradient * (1-self.inertia)

        self.direction /= np.linalg.norm(self.direction)


    def Deposit(self, depositAll=False):
        '''
        :param depositAll:
        :return:
        '''
        # The difference between the current z position and the previous adjacentTile heights. These differences
        # will be used in order to fill in the hole.
        heightDifferences = self.z - self.adjacentHeightsPrevious
        tilesToDeposit = self.adjacentTilesPrevious[heightDifferences > 0]
        heightDifferences = heightDifferences[heightDifferences > 0]

        # Determines how much sediment to deposit.
        if depositAll:
            if np.sum(heightDifferences) > self.sedimentAmount:
                # All sediment is deposited. (The hole can not be completely filled.)
                depositionAmount = self.sedimentAmount
            else:
                # Only a part of the sediment is deposited. (Enough to fill the hole.)
                depositionAmount = np.sum(heightDifferences)
        else:
            depositionAmount = (self.sedimentAmount - self.sedimentCapacity) * self.depositionRate

        # Material is added to the map and sediment is removed from the drop.
        self.rockMap[tilesToDeposit[:, 0].astype(int), tilesToDeposit[:, 1].astype(int)] += \
            depositionAmount * heightDifferences / np.sum(heightDifferences)

        # --------# --------# --------
        #self.sedimentMap[tilesToDeposit[:, 0].astype(int), tilesToDeposit[:, 1].astype(int)] += \
        #    depositionAmount * heightDifferences / np.sum(heightDifferences)
        # --------# --------# --------
        self.totalHeightMap[tilesToDeposit[:, 0].astype(int), tilesToDeposit[:, 1].astype(int)] += \
            depositionAmount * heightDifferences / np.sum(heightDifferences)


        # One could probably optimize this step and not change values in both the sedimentMap and the totalHeightMap.
        self.sedimentAmount -= depositionAmount


    def Erode(self):
        '''
        :return:
        '''
        # Select tiles to erode using templates.
        xWholePart = np.floor(self.xPreviousStep)
        yWholePart = np.floor(self.yPreviousStep)
        tilesToErode = np.zeros((self.erosionTileTemplate[self.erosionRadius].shape[0], 2))
        tilesToErode[:, 0] = self._periodic(self.erosionTileTemplate[self.erosionRadius][:, 0] + yWholePart)
        tilesToErode[:, 1] = self._periodic(self.erosionTileTemplate[self.erosionRadius][:, 1] + xWholePart)

        # Determines the amount of material to remove.
        erosionAmount = np.min(((self.sedimentCapacity-self.sedimentAmount)*self.erosionRate,-self.heightDifference))
        erosionWeights = self.erosionWeightTemplate[self.erosionRadius]

        # Determines which tiles are rock and which are sediment.
        a = np.sign(self.sedimentMap[tilesToErode[:, 0].astype(int), tilesToErode[:, 1].astype(int)])
        rockTilesToErode = tilesToErode[a<1, :]
        sedimentTilesToErode = tilesToErode[a==1, :]

        # There is a minor problem in this part, it is possible to remove more sediment than there is sediment present.
        # This problem should be very minor until the weathering process is implemented.

        # Material is removed from the map and sediment is added to the drop.

        # --------#--------#--------
        #self.rockMap[rockTilesToErode[:, 0].astype(int), rockTilesToErode[:, 1].astype(int)] -=\
        #    erosionAmount * erosionWeights[a<1]
        #self.sedimentMap[sedimentTilesToErode[:, 0].astype(int), sedimentTilesToErode[:, 1].astype(int)] -= \
        #    erosionAmount * erosionWeights[a==1]
        # --------#--------#--------

        self.rockMap[tilesToErode[:, 0].astype(int), tilesToErode[:, 1].astype(int)] -= \
            erosionAmount * erosionWeights
        self.totalHeightMap[tilesToErode[:, 0].astype(int), tilesToErode[:, 1].astype(int)] -= \
            erosionAmount * erosionWeights
        self.sedimentAmount += erosionAmount


    @classmethod
    def InitializeAdjacentTileTemplate(cls):
        # This is used as a template every time adjacent tiles are to be selected.
        cls.adjacentTilesTemplate = np.array([[0, 0], [0, 1], [1, 0], [1, 1]])


# ======================================================================================================================
# ======================================================================================================================
class DiscreteDrop(WaterDrop):
    '''
    The direction might have to be initialized as one of the four directions.
    '''
    def __init__(self,
                 x=None,
                 y=None,
                 inertia=0.3,
                 gravity=10,
                 evaporationRate=0.02,
                 capacityMultiplier=40,
                 minimumSlope=0.005,
                 erosionRadius=4,
                 depositionRate=0.1,
                 erosionRate=0.1,
                 numberOfSteps=64,
                 maximumUnimprovedSteps=1,
                 storeTrail=False):


        super().__init__(inertia,
                         gravity,
                         evaporationRate,
                         capacityMultiplier,
                         minimumSlope,
                         erosionRadius,
                         depositionRate,
                         erosionRate,
                         numberOfSteps,
                         maximumUnimprovedSteps,
                         storeTrail)

        # If x and y values are not given they will be randomized to be within the grid.
        if x is None:
            self.x = np.random.randint(0, self.gridSize)
        else:
            self.x = x
        if y is None:
            self.y = np.random.randint(0, self.gridSize)
        else:
            self.y = y
        self.z = self.rockMap[self.y, self.x]

        self.adjacentTiles = np.zeros((5, 2))
        self.adjacentTiles[:, 0] = self._periodic(self.adjacentTilesTemplate[:, 0] + self.y)
        self.adjacentTiles[:, 1] = self._periodic(self.adjacentTilesTemplate[:, 1] + self.x)
        self.adjacentHeights = self.rockMap[self.adjacentTiles[:, 0].astype(int), self.adjacentTiles[:, 1].astype(int)]


    def Move(self):
        '''
        :return:
        '''
        # Depending on the inertia parameter it is more or less likely that the direction will be updated.
        if np.random.rand() > self.inertia:
            # New direction is calculated.
            self.UpdateDirection()

        # The drop is moved
        self.x += self.direction[1]
        self.y += self.direction[0]
        self.z = self.rockMap[self.y, self.x]
        self.heightDifference = self.z - self.zPreviousStep

        # The adjacent tiles are selected using the adjacent tile template.
        self.adjacentTiles = np.zeros((5, 2))
        self.adjacentTiles[:, 0] = self._periodic(self.adjacentTilesTemplate[:, 0] + self.y)
        self.adjacentTiles[:, 1] = self._periodic(self.adjacentTilesTemplate[:, 1] + self.x)
        self.adjacentHeights = self.rockMap[self.adjacentTiles[:, 0].astype(int), self.adjacentTiles[:, 1].astype(int)]


    def UpdateDirection(self):
        '''
        If there are any lower tiles one of these will be selected as the new tile. The selection is done using the
        height differences between the adjacent and the current tile as weights.
        :return:
        '''
        lowerTiles = self.adjacentTilesTemplate[self.adjacentHeights < self.z]
        heightDifference = self.z - self.adjacentHeights[self.adjacentHeights < self.z]

        if np.size(lowerTiles) > 0:
            randomValue = np.random.rand()
            for iTile in range(np.shape(lowerTiles)[0]):
                if randomValue <= np.sum(heightDifference[0:iTile+1])/np.sum(heightDifference):
                    self.direction = lowerTiles[iTile,:]
                    break


    def Deposit(self, depositAll=False):
        '''
        :param depositAll:
        :return:
        '''

        # The difference between the current z position and the previous adjacentTile heights. These differences
        # will be used in order to fill in the hole.
        heightDifferences = self.z - self.adjacentHeightsPrevious
        tilesToDeposit = self.adjacentTilesPrevious[heightDifferences > 0]
        heightDifferences = heightDifferences[heightDifferences > 0]

        # Determines how much sediment to deposit.
        if depositAll:
            if np.sum(heightDifferences) > self.sedimentAmount:
                # All sediment is deposited. (The hole can not be completely filled.)
                depositionAmount = self.sedimentAmount
            else:
                # Only a part of the sediment is deposited. (Enough to fill the hole.)
                depositionAmount = np.sum(heightDifferences)
        else:
            depositionAmount = (self.sedimentAmount - self.sedimentCapacity) * self.depositionRate

        # Material is added to the map and sediment is removed from the drop.
        self.rockMap[tilesToDeposit[:, 0].astype(int), tilesToDeposit[:, 1].astype(int)] += \
            depositionAmount * heightDifferences / np.sum(heightDifferences)
        self.sedimentAmount -= depositionAmount



    def Erode(self):
        '''
        :return:
        '''
        # Select tiles to erode using templates.
        tilesToErode = np.zeros((self.erosionTileTemplate[self.erosionRadius].shape[0], 2))
        tilesToErode[:, 0] = self._periodic(self.erosionTileTemplate[self.erosionRadius][:, 0] + self.yPreviousStep)
        tilesToErode[:, 1] = self._periodic(self.erosionTileTemplate[self.erosionRadius][:, 1] + self.xPreviousStep)

        # Determines the amount of material to remove.
        erosionAmount = np.min(((self.sedimentCapacity-self.sedimentAmount)*self.erosionRate,-self.heightDifference))

        # Material is removed from the map and sediment is added to the drop.
        self.rockMap[tilesToErode[:, 0].astype(int), tilesToErode[:, 1].astype(int)] -=\
            erosionAmount*self.erosionWeightTemplate[self.erosionRadius]
        self.sedimentAmount += erosionAmount


    @classmethod
    def InitializeAdjacentTileTemplate(cls):
        # This is used as a template every time adjacent tiles are to be selected.
        # The tiles are in the order: right, up, left, down, center.
        cls.adjacentTilesTemplate = np.array([[0, 1], [1, 0], [0, -1], [-1, 0], [0, 0]])




