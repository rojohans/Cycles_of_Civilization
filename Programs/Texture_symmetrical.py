
import numpy as np
from panda3d import core as p3d

def CreateSymmetricalImage(file_path, scale_value = 1.0, shiftToZero = False):
    '''

    :param file_path:
    :param scale_value: A value which scales if teh pixel values up or down. A value of 2 would double all values.
    :return:
    '''
    inverseScaleValue = 1/scale_value
    image = p3d.PNMImage()
    image.read(file_path+'.jpg')
    RESOLUTION = image.getReadXSize()

    imageFlipx = p3d.PNMImage()
    imageFlipx.read(file_path+'.jpg')
    imageFlipx.flip(flip_x=False, flip_y=False, transpose=True)
    imageFlipx.flip(flip_x=False, flip_y=True, transpose=False)
    #imageFlipx.flip(flip_x=True, flip_y=False, transpose=False)

    imageFlipy = p3d.PNMImage()
    imageFlipy.read(file_path+'.jpg')
    #imageFlipy.flip(flip_x=False, flip_y=True, transpose=False)
    imageFlipy.flip(flip_x=True, flip_y=True, transpose=False)

    imageFlipxFlipy = p3d.PNMImage()
    imageFlipxFlipy.read(file_path+'.jpg')
    #imageFlipxFlipy.flip(flip_x=True, flip_y=True, transpose=False)
    imageFlipxFlipy.flip(flip_x=False, flip_y=True, transpose=False)
    imageFlipxFlipy.flip(flip_x=False, flip_y=False, transpose=True)




    imagex = p3d.PNMImage()
    imagex.read(file_path+'.jpg')
    imagex.flip(flip_x=True, flip_y=False, transpose=False)

    imageFlipxx = p3d.PNMImage()
    imageFlipxx.read(file_path+'.jpg')
    imageFlipxx.flip(flip_x=True, flip_y=False, transpose=False)
    imageFlipxx.flip(flip_x=False, flip_y=False, transpose=True)
    imageFlipxx.flip(flip_x=False, flip_y=True, transpose=False)

    imageFlipyx = p3d.PNMImage()
    imageFlipyx.read(file_path+'.jpg')
    imageFlipyx.flip(flip_x=True, flip_y=False, transpose=False)
    imageFlipyx.flip(flip_x=True, flip_y=True, transpose=False)

    imageFlipxFlipyx = p3d.PNMImage()
    imageFlipxFlipyx.read(file_path+'.jpg')
    imageFlipxFlipyx.flip(flip_x=True, flip_y=False, transpose=False)
    imageFlipxFlipyx.flip(flip_x=False, flip_y=True, transpose=False)
    imageFlipxFlipyx.flip(flip_x=False, flip_y=False, transpose=True)


    imagey = p3d.PNMImage()
    imagey.read(file_path+'.jpg')
    imagey.flip(flip_x=False, flip_y=True, transpose=False)

    imageFlipxy = p3d.PNMImage()
    imageFlipxy.read(file_path+'.jpg')
    imageFlipxy.flip(flip_x=False, flip_y=True, transpose=False)
    imageFlipxy.flip(flip_x=False, flip_y=False, transpose=True)
    imageFlipxy.flip(flip_x=False, flip_y=True, transpose=False)

    imageFlipyy = p3d.PNMImage()
    imageFlipyy.read(file_path+'.jpg')
    imageFlipyy.flip(flip_x=False, flip_y=True, transpose=False)
    imageFlipyy.flip(flip_x=True, flip_y=True, transpose=False)

    imageFlipxFlipyy = p3d.PNMImage()
    imageFlipxFlipyy.read(file_path+'.jpg')
    imageFlipxFlipyy.flip(flip_x=False, flip_y=True, transpose=False)
    imageFlipxFlipyy.flip(flip_x=False, flip_y=True, transpose=False)
    imageFlipxFlipyy.flip(flip_x=False, flip_y=False, transpose=True)


    imagexy = p3d.PNMImage()
    imagexy.read(file_path+'.jpg')
    imagexy.flip(flip_x=True, flip_y=True, transpose=False)

    imageFlipxxy = p3d.PNMImage()
    imageFlipxxy.read(file_path+'.jpg')
    imageFlipxxy.flip(flip_x=True, flip_y=True, transpose=False)
    imageFlipxxy.flip(flip_x=False, flip_y=False, transpose=True)
    imageFlipxxy.flip(flip_x=False, flip_y=True, transpose=False)

    imageFlipyxy = p3d.PNMImage()
    imageFlipyxy.read(file_path+'.jpg')
    imageFlipyxy.flip(flip_x=True, flip_y=True, transpose=False)
    imageFlipyxy.flip(flip_x=True, flip_y=True, transpose=False)

    imageFlipxFlipyxy = p3d.PNMImage()
    imageFlipxFlipyxy.read(file_path+'.jpg')
    imageFlipxFlipyxy.flip(flip_x=True, flip_y=True, transpose=False)
    imageFlipxFlipyxy.flip(flip_x=False, flip_y=True, transpose=False)
    imageFlipxFlipyxy.flip(flip_x=False, flip_y=False, transpose=True)

    imageSymmetrical = p3d.PNMImage(RESOLUTION, RESOLUTION)
    for x in range(RESOLUTION):
        for y in range(RESOLUTION):
            p1 = image.getXel(x, y)
            p2 = imageFlipx.getXel(x, y)
            p3 = imageFlipy.getXel(x, y)
            p4 = imageFlipxFlipy.getXel(x, y)
            p5 = imagex.getXel(x, y)
            p6 = imageFlipxx.getXel(x, y)
            p7 = imageFlipyx.getXel(x, y)
            p8 = imageFlipxFlipyx.getXel(x, y)
            p9 = imagey.getXel(x, y)
            p10 = imageFlipxy.getXel(x, y)
            p11 = imageFlipyy.getXel(x, y)
            p12 = imageFlipxFlipyy.getXel(x, y)
            p13 = imagexy.getXel(x, y)
            p14 = imageFlipxxy.getXel(x, y)
            p15 = imageFlipyxy.getXel(x, y)
            p16 = imageFlipxFlipyxy.getXel(x, y)
            #imageSymmetrical.setXel(x, y, (p1 + p2 + p3) / (3*inverseScaleValue))
            #imageSymmetrical.setXel(x, y, (p1 + p2 + p3 + p4) / (4 * inverseScaleValue))
            #imageSymmetrical.setXel(x, y, (p1 + p2 + p3 + p4 + p5 + p6 + p7 + p8) / (8 * inverseScaleValue))
            #imageSymmetrical.setXel(x, y, (p1 + p2 + p3 + p4 + p5 + p6 + p7 + p8 + p9 + p10 + p11 + p12) / (12 * inverseScaleValue))
            imageSymmetrical.setXel(x, y, (p1 + p2 + p3 + p4 + p5 + p6 + p7 + p8 + p9 + p10 + p11 + p12 + p13 + p14 + p15 + p16) / (16 * inverseScaleValue))

    def ShiftToZero():
        '''
        Shifts all the pixels such that the smallest value is zero.
        :return:
        '''
        minValue = 255
        #maxValue = 0
        for x in range(RESOLUTION):
            for y in range(RESOLUTION):
                p1 = imageSymmetrical.getXel(x, y)
                if p1[0]<minValue:
                    minValue = p1[0]
                #if p1[0]>maxValue:
                #    maxValue = p1[0]
        for x in range(RESOLUTION):
            for y in range(RESOLUTION):
                p1 = imageSymmetrical.getXel(x, y)
                imageSymmetrical.setXel(x, y, p1 - minValue)
                #imageSymmetrical.setXel(x, y, p1 + 1 - maxValue)

    if shiftToZero is True:
        ShiftToZero()
    imageSymmetrical.write(file_path+'_symmetrical.jpg')



# The .jpg should not be included in the file path
CreateSymmetricalImage(file_path="models/grass_4")
CreateSymmetricalImage(file_path="models/desert_1")
CreateSymmetricalImage(file_path="models/tundra_1")

CreateSymmetricalImage(file_path="models/grass_cliff_5")
CreateSymmetricalImage(file_path="models/desert_rock_2")
CreateSymmetricalImage(file_path="models/tundra_cliff_1")

CreateSymmetricalImage(file_path="models/topography_grass", scale_value = 1.5, shiftToZero = True)
CreateSymmetricalImage(file_path="models/topography_desert", scale_value= 1.5, shiftToZero = True)
CreateSymmetricalImage(file_path="models/topography_tundra", scale_value = 1.4, shiftToZero = True)

CreateSymmetricalImage(file_path="models/topography_grass_cliff", scale_value = 4.5, shiftToZero = True)







