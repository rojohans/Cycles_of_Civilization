import numpy as np

from scipy import interpolate


class Perlin2D():
    def __init__(self, maxOctaves = 5):

        self.maxOctaves = maxOctaves
        self.gridSize = 2**maxOctaves + 1

        graidentAngles = 2 * np.pi * np.random.rand(self.gridSize**2, 1)[:, 0]
        self.gradients = [[[] for colon in range(self.gridSize)] for row in range(self.gridSize)]

        i = 0
        for row in range(self.gridSize):
            for colon in range(self.gridSize):
                self.gradients[row][colon] = [np.cos(graidentAngles[i]), np.sin(graidentAngles[i])]
                i += 1
            self.gradients[row][-1] = self.gradients[row][0]
        for colon in range(self.gridSize):
            self.gradients[-1][colon] = self.gradients[0][colon]

    def Sample(self, x, y, resolution):
        '''
        :param x: [0, 1]
        :param y: [0, 1]
        :param resolution:
        :return: The interpolated noise at the given coordinates and resolution. The output is not normalized and will
                 be in the range [-1, 1].
        '''

        scale = 2**self.maxOctaves / resolution

        xScaled = x * resolution
        yScaled = y * resolution

        colonLower = np.floor(xScaled)
        rowLower = np.floor(yScaled)
        colonUpper = colonLower + 1
        rowUpper = rowLower + 1

        colonLowerMaxResolution = int(colonLower * scale)
        rowLowerMaxResolution = int(rowLower * scale)
        colonUpperMaxResolution = int(colonUpper * scale)
        rowUpperMaxResolution = int(rowUpper * scale)

        # Indices of the gradients
        # 2 ----- 3
        # :       :
        # :       :
        # 0 ----- 1
        gradients = [self.gradients[rowLowerMaxResolution][colonLowerMaxResolution],
                     self.gradients[rowLowerMaxResolution][colonUpperMaxResolution],
                     self.gradients[rowUpperMaxResolution][colonLowerMaxResolution],
                     self.gradients[rowUpperMaxResolution][colonUpperMaxResolution]]
        distances = [[xScaled - colonLower, yScaled - rowLower],
                     [xScaled - colonUpper, yScaled - rowLower],
                     [xScaled - colonLower, yScaled - rowUpper],
                     [xScaled - colonUpper, yScaled - rowUpper]]

        influenceValues = []
        for i in range(4):
            influenceValues.append(self.ListDot(gradients[i], distances[i]))
        u = self.SmoothInterpolant(xScaled - colonLower)
        v = self.SmoothInterpolant(yScaled - rowLower)

        bottomValue = self.LinearInterpolation(influenceValues[0], influenceValues[1], u)
        topValue = self.LinearInterpolation(influenceValues[2], influenceValues[3], u)
        middleValue = self.LinearInterpolation(bottomValue, topValue, v)
        return middleValue

    def SampleOctaves(self, x, y, persistance = 0.5, initialOctavesToSkip = 0):
        '''
        Samples the noise at different resolutions. The different noise values are weighted and then summed.
        :param x:
        :param y:
        :param persistance: The change in amplitude between each resolution. If <1 layers of higher resolution will be
                            weighted less.
        :param initialOctavesToSkip:
        :return: A weighted sum of the noise at the given coordinate for different resolutions (octaves)
        '''

        amplitude = 1
        totalValue = 0
        for octave in np.linspace(initialOctavesToSkip, self.maxOctaves, self.maxOctaves-initialOctavesToSkip+1):
            totalValue += amplitude * self.Sample(x, y, 2**octave)
            amplitude *= persistance

        return totalValue

    def ListDot(self, v1, v2):
        # Performs the dot product on two lists of length 2.
        return v1[0] * v2[0] + v1[1] * v2[1]

    def LinearInterpolation(self, a, b, u):
        return b*u + a * (1-u)

    def SmoothInterpolant(self, a):
        '''
        Scales the a value such that the interpolation will appear more smooth. a* = 6a^5 - 15a^4 + 10a^3
        :param a:
        :return:
        '''
        return 6*a**5 - 15*a**4 + 10*a**3
















def SimpleNoise(gridSize, numberOfInitialIterationsToSkip = 1, amplitudeReduction = 2):

    '''

    # --------ALGORITHM SUMMARY---------

    # An underlying noise array is created with values uniformly distributed between 0 and 1. The underlying noise is

    # sampled at different frequencies and interpolated to give rise to different layers of noise. Each layer is an

    # interpretation of the underlying noise at a certain resolution. The layers are weighted according to their

    # resolution and then combined to form a final multi-layered noise array. The multi-layered noise contain

    # information from all resolutions in varying amount depending on the weights. The noise is naturally periodic.

    #

    # NOTE THAT THIS FUNCTION DO NOT GENERATE PERFECTLY PERIODIC NOISE VALUES.

    #

    # ------------PARAMETERS------------

    # gridSize: [int]

    #   The gridSize indicates the size of the noise array to generate. The value has to be on the form 2^k, where k

    #   is a positive integer.

    #

    # numberOfInitialIterationsToSkip: [int] optional

    #   The initial layers has a great impact on the final noise and may give rise to artifacts, to avoid these

    #   artifacts a set number of initial layers can be left out.

    #   By default the first layer is always skipped since it's constant.

    #

    # amplitudeReduction: [float] optional

    #   By default the amplitude is halved between each layer. Lowering this value will make the final noise more

    #   random. Increasing the value has the opposite effect

    #

    # -------------OUTPUT---------------

    # generatedNoise: [float array]

    #   A [gridSize,gridSize] numpy array containing noise values between 0 and 1. The noise is periodic.

    '''



    samplingInterval = gridSize / pow(2, numberOfInitialIterationsToSkip)

    samplingAmplitude = 1

    generatedNoise = np.zeros([gridSize+1, gridSize+1]) # This array will contain the final multi-layered noise.

    singleNoiseLayer = np.zeros([gridSize+1, gridSize+1])



    # The underlying noise is the noise which is sampled at different frequencies in order to create the multi-layered noise.

    # The underlying noise is periodic.

    underlyingNoise = np.random.rand(gridSize+1, gridSize+1)

    underlyingNoise[:, -1] = underlyingNoise[:, 0]

    underlyingNoise[-1, :] = underlyingNoise[0, :]



    while samplingInterval >= 1:

        # Determines the rows and columns of the elements which are to be used for the current sampling frequency.

        sampleRows = range(0, gridSize+1, int(samplingInterval))

        sampleColumns = range(0, gridSize+1, int(samplingInterval))

        sampleRowGrid, sampleColumnGrid = np.meshgrid(sampleRows, sampleColumns)

        sampleRowList = np.reshape(sampleRowGrid, [sampleRowGrid.size, 1])

        sampleColumnList = np.reshape(sampleColumnGrid, [sampleColumnGrid.size, 1])



        # Extracts the random samples to be used to create the current layer.

        noiseSamples = underlyingNoise[sampleRowList, sampleColumnList]

        noiseSamples = np.reshape(noiseSamples, [int(np.sqrt(noiseSamples.size)), int(np.sqrt(noiseSamples.size))])



        # The sampled noise values are used to interpolate a whole layer that will be added to the multi-layered noise.

        # The RectBivariateSpline function can not handle input with less then/equal to 3 coordinates. When this is the

        # case the slower interp2d function is used instead, it uses linear interpolation.

        if len(sampleRows)>3:

            f = interpolate.RectBivariateSpline(sampleRows, sampleColumns, noiseSamples)

        else:

            f = interpolate.interp2d(sampleRowList, sampleColumnList, noiseSamples)

        layerRows = range(0, gridSize + 1, 1)

        layerColumns = range(0, gridSize + 1, 1)

        singleNoiseLayer = f(layerRows, layerColumns)



        generatedNoise += samplingAmplitude * singleNoiseLayer

        samplingInterval /= 2

        samplingAmplitude /= amplitudeReduction





    # The last row and column is removed to change the array to it's proper size. The noise is also normalized.

    generatedNoise = np.delete(generatedNoise, -1, axis=0)

    generatedNoise = np.delete(generatedNoise, -1, axis=1)

    generatedNoise -= np.min(generatedNoise)

    generatedNoise /= np.max(generatedNoise)

    return generatedNoise



def FractalNoise3D(gridSize, numberOfInitialIterationsToSkip = 1, amplitudeReduction = 2):



    samplingInterval = gridSize / pow(2, numberOfInitialIterationsToSkip)

    samplingAmplitude = 1 # This will decrease in each iteration.

    generatedNoise = np.zeros([gridSize+1, gridSize+1, gridSize+1])



    # The basic noise is sampled at different frequencies in order to create the final noise. The basic noise is periodic.

    basicNoise = np.random.rand(gridSize+1, gridSize+1, gridSize+1)

    basicNoise[-1, :, :] = basicNoise[0, :, :]

    basicNoise[:, -1, :] = basicNoise[:, 0, :]

    basicNoise[:, :, -1] = basicNoise[:, :, 0]



    #print(basicNoise)





    xFineMesh, yFineMesh, zFineMesh = np.meshgrid(range(0, gridSize+1), range(0, gridSize+1), range(0, gridSize+1))



    xFineVector = np.reshape(xFineMesh, ((gridSize + 1) ** 3, 1))

    yFineVector = np.reshape(yFineMesh, ((gridSize + 1) ** 3, 1))

    zFineVector = np.reshape(zFineMesh, ((gridSize + 1) ** 3, 1))



    #print(np.shape(np.transpose(xFineVector)))



    #finePoints = np.array([[np.transpose(xFineVector)], [np.transpose(yFineVector)], [np.transpose(zFineVector)]])

    #print(finePoints)

    #print(np.shape(finePoints))



    #np.append([[1, 2, 3], [4, 5, 6]], [[7, 8, 9]], axis=0)



    # finePoints is a n^3x3 array, each row corresponds to coordinates of the points in the basicNoise array.

    finePoints = np.append(xFineVector, yFineVector, axis = 1)

    finePoints = np.append(finePoints, zFineVector, axis = 1)



    #fig2 = mlab.figure()

    #fig2.scene.interactor.interactor_style = tvtk.InteractorStyleTerrain()

    #mlab.points3d(finePoints[:, 0], finePoints[:, 1], finePoints[:, 2],

    #              basicNoise[finePoints[:, 0], finePoints[:, 1], finePoints[:, 2]], scale_factor=1.5, opacity=1)



    while samplingInterval >= 1:

        sampleX = range(0, gridSize + 1, int(samplingInterval))

        sampleY = range(0, gridSize + 1, int(samplingInterval))

        sampleZ = range(0, gridSize + 1, int(samplingInterval))

        sampleValues = basicNoise[0::int(samplingInterval), 0::int(samplingInterval), 0::int(samplingInterval)]



        print(np.shape(sampleValues))





        # The sampleX, sampleY and sampleZ values may be wrong.

        my_interpolating_function = interpolate.RegularGridInterpolator((sampleX, sampleY, sampleZ), sampleValues)

        interpolatedValues = my_interpolating_function(finePoints)

        #interpolatedValues = interpolate.interpn((sampleX, sampleY, sampleZ), sampleValues, finePoints)

        singleNoiseLayer = np.reshape(interpolatedValues, (gridSize+1, gridSize+1, gridSize+1))



        generatedNoise += samplingAmplitude * singleNoiseLayer

        samplingInterval /= 2

        samplingAmplitude /= amplitudeReduction



        #fig2 = mlab.figure()

        #fig2.scene.interactor.interactor_style = tvtk.InteractorStyleTerrain()

        #mlab.points3d(finePoints[:, 0], finePoints[:, 1], finePoints[:, 2],

        #            singleNoiseLayer[finePoints[:, 0], finePoints[:, 1], finePoints[:, 2]], scale_factor=1.5, opacity = 1)



    #print(basicNoise[0:, 0:, 0:])

    #print('----------------------------------------')

    #print(basicNoise[0::2, 0::2, 0::2])

    #print('----------------------------------------')

    #print(basicNoise[0::4, 0::4, 0::4])



    generatedNoise -= np.min(generatedNoise)

    generatedNoise /= np.max(generatedNoise)



    #fig2 = mlab.figure()

    #fig2.scene.interactor.interactor_style = tvtk.InteractorStyleTerrain()

    #mlab.points3d(finePoints[:, 0], finePoints[:, 1], finePoints[:, 2],

    #              generatedNoise[finePoints[:, 0], finePoints[:, 1], finePoints[:, 2]], scale_factor=1.5, opacity=1)

    #mlab.show()



    return finePoints, basicNoise, interpolatedValues, generatedNoise





def FractalNoiseSpherical(gridSize, sphericalPoints, numberOfInitialIterationsToSkip = 1, amplitudeReduction = 2):

    samplingInterval = gridSize / pow(2, numberOfInitialIterationsToSkip)

    samplingAmplitude = 1 # This will decrease in each iteration.

    generatedNoise = np.zeros((np.size(sphericalPoints, 0), 1))



    # The basic noise is sampled at different frequencies in order to create the final noise. The basic noise is periodic.

    basicNoise = np.random.rand(gridSize+1, gridSize+1, gridSize+1)

    basicNoise[-1, :, :] = basicNoise[0, :, :]

    basicNoise[:, -1, :] = basicNoise[:, 0, :]

    basicNoise[:, :, -1] = basicNoise[:, :, 0]



    while samplingInterval >= 1:

        sampleX = range(0, gridSize + 1, int(samplingInterval))

        sampleY = range(0, gridSize + 1, int(samplingInterval))

        sampleZ = range(0, gridSize + 1, int(samplingInterval))

        sampleValues = basicNoise[0::int(samplingInterval), 0::int(samplingInterval), 0::int(samplingInterval)]



        # The sampleX, sampleY and sampleZ values may be wrong.

        my_interpolating_function = interpolate.RegularGridInterpolator((sampleX, sampleY, sampleZ), sampleValues)

        sphereCoordinates = gridSize / 2 + 0.7 * gridSize * sphericalPoints / 2

        singleNoiseLayer = my_interpolating_function(sphereCoordinates)



        generatedNoise[:, 0] += samplingAmplitude * singleNoiseLayer

        samplingInterval /= 2

        samplingAmplitude /= amplitudeReduction

    generatedNoise -= np.min(generatedNoise)

    generatedNoise /= np.max(generatedNoise)



    return generatedNoise













def PerlinNoiseSpherical(gridSize, sphericalPoints, numberOfInitialIterationsToSkip = 1, amplitudeScaling = 2):

    multiLayerNoise = np.zeros((np.size(sphericalPoints, 0),1))



    xGradient = 2 * np.random.rand(gridSize + 1, gridSize + 1, gridSize + 1) - 1

    yGradient = 2 * np.random.rand(gridSize + 1, gridSize + 1, gridSize + 1) - 1

    zGradient = 2 * np.random.rand(gridSize + 1, gridSize + 1, gridSize + 1) - 1

    gradientMagnitude = np.sqrt(xGradient ** 2 + yGradient ** 2 + zGradient ** 2)

    xGradient /= gradientMagnitude

    yGradient /= gradientMagnitude

    zGradient /= gradientMagnitude

    xGradient[:, :, -1] = xGradient[:, :, 0]

    yGradient[:, :, -1] = yGradient[:, :, 0]

    zGradient[:, :, -1] = zGradient[:, :, 0]

    xGradient[:, -1, :] = xGradient[:, 0, :]

    yGradient[:, -1, :] = yGradient[:, 0, :]

    zGradient[:, -1, :] = zGradient[:, 0, :]

    xGradient[-1, :, :] = xGradient[0, :, :]

    yGradient[-1, :, :] = yGradient[0, :, :]

    zGradient[-1, :, :] = zGradient[0, :, :]

    noiseAmplitude = 1



    # The sphereRadius is used to change the radius of the sphere such that the sphere lies within the cube of

    # gradient vectors.

    sphereRadius = np.sum(np.sqrt(np.sum(sphericalPoints ** 2, 1))) / np.size(sphericalPoints, 0)

    while gridSize > 2 ** numberOfInitialIterationsToSkip:

        print('gridsize = ', gridSize)



        #sphericalPoints /= sphereRadius

        #sphereRadius = 0.9 * (gridSize / 2 - 0.5)

        #sphericalPoints *= sphereRadius

        #sphericalPoints += 0.1



        # Used to store the noise for a single resolution layer.

        singleLayerNoise = np.zeros((np.size(sphericalPoints, 0), 1))

        for iPoint, point in enumerate(sphericalPoints):

            flooredPoint = np.floor(point)

            pointOffset = point - flooredPoint

            # pointOffset = 0.5-np.cos(pointOffset*np.pi)/2;

            pointOffset = 6 * pointOffset ** 5 - 15 * pointOffset ** 4 + 10 * pointOffset ** 3  # standard smooth interpolation.



            # The indexing needs to be 'ij' in order for the indexing to match with other arrays in the code.

            # By default it is 'xy'

            adjacentGridx, adjacentGridy, adjacentGridz = np.meshgrid(

                np.linspace(flooredPoint[0], flooredPoint[0] + 1, 2),

                np.linspace(flooredPoint[1], flooredPoint[1] + 1, 2),

                np.linspace(flooredPoint[2], flooredPoint[2] + 1, 2), indexing='ij')



            adjacentGradientx = xGradient[

                adjacentGridx.astype(int), adjacentGridy.astype(int), adjacentGridz.astype(int)]

            adjacentGradienty = yGradient[

                adjacentGridx.astype(int), adjacentGridy.astype(int), adjacentGridz.astype(int)]

            adjacentGradientz = zGradient[

                adjacentGridx.astype(int), adjacentGridy.astype(int), adjacentGridz.astype(int)]



            distanceVectorx = adjacentGridx - point[0]

            distanceVectory = adjacentGridy - point[1]

            distanceVectorz = adjacentGridz - point[2]



            # These are the noise values at each grid point. To create the final noise one has to inperpolate between these.

            influenceValues = adjacentGradientx * distanceVectorx + adjacentGradienty * distanceVectory + adjacentGradientz * distanceVectorz



            # Performs the trilinear interpolation.

            influenceValues = influenceValues[0, :, :] * (1 - pointOffset[0]) + influenceValues[1, :, :] * pointOffset[

                0]

            influenceValues = influenceValues[0, :] * (1 - pointOffset[1]) + influenceValues[1, :] * pointOffset[1]

            influenceValues = influenceValues[0] * (1 - pointOffset[2]) + influenceValues[1] * pointOffset[2]



            singleLayerNoise[iPoint, 0] = influenceValues



        multiLayerNoise += singleLayerNoise * noiseAmplitude

        noiseAmplitude *= amplitudeScaling



        # Every second gradient is discarded, this changes the resolution of the noise.

        gridSize /= 2

        xGradient = xGradient[0::2, 0::2, 0::2]

        yGradient = yGradient[0::2, 0::2, 0::2]

        zGradient = zGradient[0::2, 0::2, 0::2]



    # The noise is normalized before being returned

    multiLayerNoise -= np.min(multiLayerNoise)

    multiLayerNoise /= np.max(multiLayerNoise)



    # print(np.shape(multiLayerNoise))

    multiLayerNoise = multiLayerNoise[:, 0]



    return multiLayerNoise



    '''

    if False:

        # Indicates the location of the gradient vectors.

        xMesh, yMesh, zMesh = np.meshgrid(np.linspace(-1, 1, gridSize+1),

                                          np.linspace(-1, 1, gridSize+1),

                                          np.linspace(-1, 1, gridSize+1))

        xGradient = 2 * np.random.rand(gridSize + 1, gridSize + 1, gridSize + 1) - 1

        yGradient = 2 * np.random.rand(gridSize + 1, gridSize + 1, gridSize + 1) - 1

        zGradient = 2 * np.random.rand(gridSize + 1, gridSize + 1, gridSize + 1) - 1

        gradientMagnitude = np.sqrt(xGradient ** 2 + yGradient ** 2 + zGradient ** 2)

        xGradient /= gradientMagnitude

        yGradient /= gradientMagnitude

        zGradient /= gradientMagnitude

        xGradient[:, :, -1] = xGradient[:, :, 0]

        yGradient[:, :, -1] = yGradient[:, :, 0]

        zGradient[:, :, -1] = zGradient[:, :, 0]

        xGradient[:, -1, :] = xGradient[:, 0, :]

        yGradient[:, -1, :] = yGradient[:, 0, :]

        zGradient[:, -1, :] = zGradient[:, 0, :]

        xGradient[-1, :, :] = xGradient[0, :, :]

        yGradient[-1, :, :] = yGradient[0, :, :]

        zGradient[-1, :, :] = zGradient[0, :, :]



        meshDistance = xMesh[0, 1, 0] - xMesh[0, 0, 0]

        xMesh /= meshDistance

        yMesh /= meshDistance

        zMesh /= meshDistance

        sphericalPoints /= meshDistance

        minimumMeshValue = np.min(xMesh)

        xMesh -= minimumMeshValue

        yMesh -= minimumMeshValue

        zMesh -= minimumMeshValue

        sphericalPoints -= minimumMeshValue

        sphericalPoints *= 0.98

        sphericalPoints += 0.01 * sphericalPoints



        generatedNoise = np.zeros((np.size(sphericalPoints, 0), 1))



        basisFunctionDistance = np.zeros((8, 1))

        basisTemplate = np.array([[0, 0, 0],

                                              [1, 0, 0],

                                              [0, 1, 0],

                                              [0, 0, 1],

                                              [1, 1, 0],

                                              [1, 0, 1],

                                              [0, 1, 1],

                                              [1, 1, 1],

                                             ])



        for point, iPoint in zip(sphericalPoints, range(0, np.size(sphericalPoints, 0))):

            flooredPoint = np.floor(point)

            pointOffset = point - flooredPoint

            pointOffset = 6*pointOffset**5 - 15*pointOffset**4 + 10*pointOffset**3 # standard smooth interpolation.





            for i in range(8):

                basisFunctionDistance[i, 0] = np.sqrt((basisTemplate[i, 0]-pointOffset[0])**2

                                                      +(basisTemplate[i, 1]-pointOffset[1])**2

                                                      +(basisTemplate[i, 2]-pointOffset[2])**2)



            #pointOffset[:] /= np.sqrt(pointOffset[0]**2 + pointOffset[1]**2 + pointOffset[2]**2)

            #pointOffset[:] *= basisFunctionDistance[basisFunctionDistance == np.min(basisFunctionDistance)]

            #pointOffset[:] /= np.max(pointOffset)

            #print(basisFunctionDistance)

            #quit()

            #pointOffset = (np.sin(pointOffset*np.pi-np.pi/2)+1)/2

            # Meshes for the surrounding gradients coordinates.

            minorxMesh, minoryMesh, minorzMesh = np.meshgrid(

                np.linspace(flooredPoint[0], flooredPoint[0]+1, 2),

                np.linspace(flooredPoint[1], flooredPoint[1]+1, 2),

                np.linspace(flooredPoint[2], flooredPoint[2]+1, 2))



            minorxGradient = xGradient[minorxMesh.astype(int), minoryMesh.astype(int), minorzMesh.astype(int)]

            minoryGradient = yGradient[minorxMesh.astype(int), minoryMesh.astype(int), minorzMesh.astype(int)]

            minorzGradient = zGradient[minorxMesh.astype(int), minoryMesh.astype(int), minorzMesh.astype(int)]



            xDistanceVector = minorxMesh - point[0]

            yDistanceVector = minoryMesh - point[1]

            zDistanceVector = minorzMesh - point[2]

            # These 4 lines can be used to normalize the distance vectors.

            #r = np.sqrt(xDistanceVector**2 + yDistanceVector**2 + zDistanceVector**2)

            #xDistanceVector /= r

            #yDistanceVector /= r

            #zDistanceVector /= r



            influenceValues = minorxGradient*xDistanceVector + minoryGradient*yDistanceVector + minorzGradient*zDistanceVector



            # Performs the trilinear interpolation.

            influenceValues = influenceValues[0, :, :] * (1 - pointOffset[1]) + influenceValues[1, :, :] * pointOffset[1]

            influenceValues = influenceValues[0, :] * (1 - pointOffset[0]) + influenceValues[1, :] * pointOffset[0]

            #influenceValues = influenceValues[0, :, :] * (1 - pointOffset[0]) + influenceValues[1, :, :] * pointOffset[0]

            #influenceValues = influenceValues[0, :] * (1 - pointOffset[1]) + influenceValues[1, :] * pointOffset[1]

            influenceValues = influenceValues[0] * (1 - pointOffset[2]) + influenceValues[1] * pointOffset[2]



            # ---------------------------------------------

            # ---------------------------------------------

            generatedNoise[iPoint, 0] = influenceValues

            #generatedNoise[iPoint, 0] = np.sum(influenceValues) * basisFunctionDistance[basisFunctionDistance == np.min(basisFunctionDistance)]

            #generatedNoise[iPoint, 0] =  basisFunctionDistance[basisFunctionDistance == np.min(basisFunctionDistance)]

            #generatedNoise[iPoint, 0] = 2*np.sum(influenceValues) + np.sum(basisFunctionDistance)

            #print(basisFunctionDistance[basisFunctionDistance == np.min(basisFunctionDistance)])

            # ---------------------------------------------

            # ---------------------------------------------

    else:



        

        quit()

        # ==============================================================================================================

        # ==============================================================================================================

        # ==============================================================================================================



        #print(gridSize)



        # Indicates the location of the gradient vectors.

        xMesh, yMesh, zMesh = np.meshgrid(np.linspace(-1, 1, gridSize + 1),

                                          np.linspace(-1, 1, gridSize + 1),

                                          np.linspace(-1, 1, gridSize + 1),indexing = 'ij')



        # Consider creating the gradient vectors by initializing vectors within the unit cube, and only keeping the

        # vectors inside the unit sphere.

        xGradient = 2 * np.random.rand(gridSize + 1, gridSize + 1, gridSize + 1) - 1

        yGradient = 2 * np.random.rand(gridSize + 1, gridSize + 1, gridSize + 1) - 1

        zGradient = 2 * np.random.rand(gridSize + 1, gridSize + 1, gridSize + 1) - 1

        gradientMagnitude = np.sqrt(xGradient ** 2 + yGradient ** 2 + zGradient ** 2)

        xGradient /= gradientMagnitude

        yGradient /= gradientMagnitude

        zGradient /= gradientMagnitude



        # Makes the gradient matrices periodical

        xGradient[:, :, -1] = xGradient[:, :, 0]

        yGradient[:, :, -1] = yGradient[:, :, 0]

        zGradient[:, :, -1] = zGradient[:, :, 0]

        xGradient[:, -1, :] = xGradient[:, 0, :]

        yGradient[:, -1, :] = yGradient[:, 0, :]

        zGradient[:, -1, :] = zGradient[:, 0, :]

        xGradient[-1, :, :] = xGradient[0, :, :]

        yGradient[-1, :, :] = yGradient[0, :, :]

        zGradient[-1, :, :] = zGradient[0, :, :]



        # Scales the gradient mesh so that each point is separated by a value 1 from the closest point. The sphere is

        # also placed within the cube of gradient vectors.

        meshDistance = xMesh[0, 1, 0] - xMesh[0, 0, 0]

        xMesh /= meshDistance

        yMesh /= meshDistance

        zMesh /= meshDistance

        sphericalPoints /= meshDistance

        minimumMeshValue = np.min(xMesh)

        xMesh -= minimumMeshValue

        yMesh -= minimumMeshValue

        zMesh -= minimumMeshValue

        sphericalPoints -= minimumMeshValue

        sphericalPoints *= 0.98

        sphericalPoints += 0.01 * sphericalPoints



        generatedNoise = np.zeros((np.size(sphericalPoints, 0), 1))



        basisFunctionDistance = np.zeros((8, 1))

        basisTemplate = np.array([[0, 0, 0],

                                  [1, 0, 0],

                                  [0, 1, 0],

                                  [0, 0, 1],

                                  [1, 1, 0],

                                  [1, 0, 1],

                                  [0, 1, 1],

                                  [1, 1, 1],

                                  ])



        for iPoint, point in enumerate(sphericalPoints):

            flooredPoint = np.floor(point)

            pointOffset = point - flooredPoint

            #pointOffset = 0.5-np.cos(pointOffset*np.pi)/2;

            pointOffset = 6 * pointOffset ** 5 - 15 * pointOffset ** 4 + 10 * pointOffset ** 3  # standard smooth interpolation.

            #pointOffset = 6 * pointOffset ** 5 - 15 * pointOffset ** 4 + 10 * pointOffset ** 3

            #pointOffset = 6 * pointOffset ** 5 - 15 * pointOffset ** 4 + 10 * pointOffset ** 3



            #for i in range(8):

            #    basisFunctionDistance[i, 0] = np.sqrt((basisTemplate[i, 0] - pointOffset[0]) ** 2

            #                                          + (basisTemplate[i, 1] - pointOffset[1]) ** 2

            #                                          + (basisTemplate[i, 2] - pointOffset[2]) ** 2)



            # The indexing needs to be 'ij' in order for the indexing to match with other arrays in the code.

            minorxMesh, minoryMesh, minorzMesh = np.meshgrid(

                np.linspace(flooredPoint[0], flooredPoint[0] + 1, 2),

                np.linspace(flooredPoint[1], flooredPoint[1] + 1, 2),

                np.linspace(flooredPoint[2], flooredPoint[2] + 1, 2),indexing = 'ij')



            minorxGradient = xGradient[minorxMesh.astype(int), minoryMesh.astype(int), minorzMesh.astype(int)]

            minoryGradient = yGradient[minorxMesh.astype(int), minoryMesh.astype(int), minorzMesh.astype(int)]

            minorzGradient = zGradient[minorxMesh.astype(int), minoryMesh.astype(int), minorzMesh.astype(int)]



            xDistanceVector = minorxMesh - point[0]

            yDistanceVector = minoryMesh - point[1]

            zDistanceVector = minorzMesh - point[2]

            # These 4 lines can be used to normalize the distance vectors. This should not be done.

            #r = np.sqrt(xDistanceVector**2 + yDistanceVector**2 + zDistanceVector**2)

            #xDistanceVector /= r

            #yDistanceVector /= r

            #zDistanceVector /= r



            influenceValues = minorxGradient * xDistanceVector + minoryGradient * yDistanceVector + minorzGradient * zDistanceVector

            #print(influenceValues)



            # This is proven to work, but it is unsure why.

            if True:

                

                # Performs the trilinear interpolation.

                #influenceValues = influenceValues[0, :, :] * (1 - pointOffset[1]) + influenceValues[1, :, :] * pointOffset[1]

                #print(influenceValues)

                #influenceValues = influenceValues[0, :] * (1 - pointOffset[0]) + influenceValues[1, :] * pointOffset[0]

                ##print(influenceValues)

                # influenceValues = influenceValues[0, :, :] * (1 - pointOffset[0]) + influenceValues[1, :, :] * pointOffset[0]

                # influenceValues = influenceValues[0, :] * (1 - pointOffset[1]) + influenceValues[1, :] * pointOffset[1]

                #influenceValues = influenceValues[0] * (1 - pointOffset[2]) + influenceValues[1] * pointOffset[2]

                

                # Performs the trilinear interpolation.

                influenceValues = influenceValues[0, :, :] * (1 - pointOffset[0]) + influenceValues[1, :, :] * pointOffset[0]

                influenceValues = influenceValues[0, :] * (1 - pointOffset[1]) + influenceValues[1, :] * pointOffset[1]

                influenceValues = influenceValues[0] * (1 - pointOffset[2]) + influenceValues[1] * pointOffset[2]



            else:



                print(point)

                print(minorxMesh)

                print(minoryMesh)

                print(minorzMesh)

                quit()







                pointOffset = [0.1, 0.1, 0.1]

                #print(pointOffset)

                #print(influenceValues)



                testArray = np.zeros((2, 3, 4))

                for x in range(2):

                    for y in range(3):

                        #testArray[x, y] = influenceValues[x, y, 0] * 0.9 + influenceValues[x, y, 1] * 0.1

                        for z in range(4):

                            testArray[x, y, z] = z

                print('==========================')

                print(testArray)

                print('------------------------------')

                print(testArray[0, :, :])

                print(testArray[:, 0, :])

                print(testArray[:, :, 1])

                quit()



                print(0.9*influenceValues[:, :, 0])

                print(' ')

                print(0.1*influenceValues[:, :, 1])

                print(' ')

                print(0.9*influenceValues[:, :, 0] + 0.1*influenceValues[:, :, 1])

                #print(testArray)

                print('-------------------------')

                # X layers are combined

                influenceValues = influenceValues[0, :, :] + pointOffset[0] * (influenceValues[1, :, :] - influenceValues[0, :, :])

                print(influenceValues)

                print('-------------------------')

                influenceValues = influenceValues[:, 0] + pointOffset[0] * (influenceValues[:, 1] - influenceValues[:, 0])

                print(influenceValues)

                print('-------------------------')

                influenceValues = influenceValues[0] + pointOffset[1] * (influenceValues[1] - influenceValues[0])

                print(influenceValues)

                quit()

                #print('--------------------------------------')



                minorGridPoints = np.zeros((8, 3))

                #print(minorGridPoints)

                #print(np.reshape(minorxMesh, (8, 1)))

                #print(np.shape(np.reshape(minorxMesh, (8, 1))))

                #print(np.shape(minorGridPoints[:, 0]))

                minorGridPoints[:, 0:1] = np.reshape(minorxMesh, (8, 1))

                minorGridPoints[:, 1:2] = np.reshape(minoryMesh, (8, 1))

                minorGridPoints[:, 2:3] = np.reshape(minorzMesh, (8, 1))



                minorGridValues = np.reshape(minorxGradient * xDistanceVector + minoryGradient * yDistanceVector + minorzGradient * zDistanceVector, (8, 1))



                #print(minorGridPoints)

                #print(type(minorGridPoints))

                #print(np.shape(minorGridPoints))



                #print(minorGridValues)

                #print(type(minorGridValues))

                #print(np.shape(minorGridValues))





                #print('===========================================')

                #intp = interpolate.LinearNDInterpolator(minorGridPoints, minorGridValues[:, 0])

                #intp = interpolate.NearestNDInterpolator(minorGridPoints, minorGridValues[:, 0])

                #print(intp(point))

                #point = flooredPoint + pointOffset

                #influenceValues = intp(point)



                

                #r = np.sqrt(xDistanceVector**2 + yDistanceVector**2 + zDistanceVector**2)

                #rSum = sum(sum(sum(r)))

                #minorGridValues = minorxGradient * xDistanceVector + minoryGradient * yDistanceVector + minorzGradient * zDistanceVector

                #influenceValues = sum(sum(sum(r * minorGridValues / rSum)))

                





            # ---------------------------------------------

            # ---------------------------------------------

            generatedNoise[iPoint, 0] = influenceValues

            # generatedNoise[iPoint, 0] = np.sum(influenceValues) * basisFunctionDistance[basisFunctionDistance == np.min(basisFunctionDistance)]

            # generatedNoise[iPoint, 0] =  basisFunctionDistance[basisFunctionDistance == np.min(basisFunctionDistance)]

            # generatedNoise[iPoint, 0] = 2*np.sum(influenceValues) + np.sum(basisFunctionDistance)

            # print(basisFunctionDistance[basisFunctionDistance == np.min(basisFunctionDistance)])

            # ---------------------------------------------

            # ---------------------------------------------



    generatedNoise -= np.min(generatedNoise)

    generatedNoise /= np.max(generatedNoise)



    return generatedNoise

    '''





def PerlinNoise3DFlow(gridSize,

                      vertices,

                      numberOfInitialIterationsToSkip = 1,

                      amplitudeScaling = 1.5,

                      projectOnSphere = False,

                      normalizedVectors = False):

    xFlow = 2 * np.sqrt(1 / 3) * PerlinNoiseSpherical(gridSize,

                                                      vertices.copy(),

                                                      numberOfInitialIterationsToSkip = numberOfInitialIterationsToSkip,

                                                      amplitudeScaling = amplitudeScaling) - np.sqrt(1 / 3)

    yFlow = 2 * np.sqrt(1 / 3) * PerlinNoiseSpherical(gridSize,

                                                      vertices.copy(),

                                                      numberOfInitialIterationsToSkip = numberOfInitialIterationsToSkip,

                                                      amplitudeScaling = amplitudeScaling) - np.sqrt(1 / 3)

    zFlow = 2 * np.sqrt(1 / 3) * PerlinNoiseSpherical(gridSize,

                                                      vertices.copy(),

                                                      numberOfInitialIterationsToSkip = numberOfInitialIterationsToSkip,

                                                      amplitudeScaling = amplitudeScaling) - np.sqrt(1 / 3)

    if projectOnSphere:

        # Projects the vectors onto a sphere.

        r = np.sqrt((xFlow + vertices[:, 0]) ** 2

                    + (yFlow + vertices[:, 1]) ** 2

                    + (zFlow + vertices[:, 2]) ** 2)

        xFlow = (xFlow + vertices[:, 0]) / r - vertices[:, 0]

        yFlow = (yFlow + vertices[:, 1]) / r - vertices[:, 1]

        zFlow = (zFlow + vertices[:, 2]) / r - vertices[:, 2]

    if normalizedVectors:

        # Normalizes flow vectors.

        r = np.sqrt(xFlow ** 2 + yFlow ** 2 + zFlow ** 2)

        xFlow /= r

        yFlow /= r

        zFlow /= r

    return xFlow, yFlow, zFlow

