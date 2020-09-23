from panda3d.core import TextNode
from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectGui import *
from panda3d.core import TransparencyAttrib
import panda3d.core as p3d
import sys
import numpy as np
import matplotlib
from scipy import interpolate

import Root_Directory
import Library.TileClass as TileClass

class GUIClass():
    def __init__(self, base, mainProgram, debugText = False):
        self.mainProgram = mainProgram

        if debugText:
            self.escapeEvent = OnscreenText(
                text="ESC: Quit", parent=base.a2dTopLeft,
                style=1, fg=(1, 1, 1, 1), pos=(0.05, -0.1),
                align=TextNode.ALeft, scale=.05)

            self.selectedTileText = OnscreenText(
                text="Row : 0 \nColon : 0 \nElevation : 0\nTerrain : None",
                parent=base.a2dTopLeft,
                style=1, fg=(1, 1, 1, 1), pos=(0.05, -0.2),
                align=TextNode.ALeft, scale=0.05, mayChange=True
            )

            self.fpsCounter = OnscreenText(
                text="FPS : ",
                parent=base.a2dTopLeft,
                style=1, fg=(1, 1, 1, 1), pos=(0.05, -0.9),
                align=TextNode.ALeft, scale=0.05, mayChange=True
            )

        self.windowSize = (base.win.getXSize(), base.win.getYSize())

        self.windowRatio = self.windowSize[0] / self.windowSize[1]
        self.frameWidth = self.mainProgram.settings.RELATIVE_SELECTION_FRAME_WIDTH * self.windowRatio

        self.unitFrame = UnitFrame(base = base,
                        parent = base.a2dBottomLeft,
                        size = [-self.frameWidth, self.frameWidth, -0.1, 0.1],
                        position = (self.windowRatio, 0, 0.1),
                        mainProgram = mainProgram,
                        windowRatio = self.windowRatio)
        self.tileFrame = TileFrame(base = base,
                        parent = base.a2dBottomLeft,
                        size = [-self.frameWidth, self.frameWidth, -0.1, 0.1],
                        position = (self.windowRatio, 0, 0.1),
                        mainProgram = mainProgram,
                        windowRatio = self.windowRatio)

        # The scale of the button is the radii of the button, measured in units in windowHeight/2. A button with scale 1
        # will cover the entire height of the window if placed in the center of the screen.
        #
        self.unitFrame.frame.hide()
        self.tileFrame.frame.hide()

        GUIDataDirectoryPath = Root_Directory.Path(style='unix') + '/Data/GUI/'


        self.minimap = Minimap(self.windowRatio, mainProgram=mainProgram)

        self.add_unit_button = DirectCheckButton(boxImage=(GUIDataDirectoryPath + "add_unit_button.png",
                                                GUIDataDirectoryPath + "add_unit_button_pressed.png",
                                                GUIDataDirectoryPath + "add_unit_button.png",
                                                GUIDataDirectoryPath + "add_unit_button.png"),
                                                 scale=self.mainProgram.settings.BUTTON_SCALE,
                                                 pos=(-0.7*self.windowRatio - self.mainProgram.settings.BUTTON_SCALE, 0, 0.8),
                                                 relief=None,
                                                 boxRelief=None,
                                                 boxPlacement = 'right',
                                                 command = TileClass.UnitClass.AddUnitButtonFunction)
        self.add_unit_button.setTransparency(TransparencyAttrib.MAlpha)

        self.quitButton = DirectButton(image=(GUIDataDirectoryPath + "quit_button.png",
                                        GUIDataDirectoryPath + "quit_button.png",
                                        GUIDataDirectoryPath + "quit_button.png",
                                        GUIDataDirectoryPath + "quit_button.png"),
                                       scale=self.mainProgram.settings.BUTTON_SCALE,
                                       pos=(0.9*self.windowRatio, 0, 0.9),
                                       relief=None,
                                       command = sys.exit)
        self.quitButton.setTransparency(TransparencyAttrib.MAlpha)


        self.displayFeaturesPositionRelative = [1.85, 0, 0.45]
        self.displayFeaturesPosition = (self.displayFeaturesPositionRelative[0]*self.windowRatio,
                                        0,
                                        self.displayFeaturesPositionRelative[2]*self.windowRatio)
        self.displayFeaturesButton = DirectCheckButton(boxImage=(GUIDataDirectoryPath + "feature_toggle.png",
                                                           GUIDataDirectoryPath + "feature_toggle_pressed.png",
                                                           GUIDataDirectoryPath + "feature_toggle.png",
                                                           GUIDataDirectoryPath + "feature_toggle.png"),
                                                 scale=self.mainProgram.settings.BUTTON_SCALE,
                                                 pos=self.displayFeaturesPosition,
                                                 relief=None,
                                                 boxRelief=None,
                                                 boxPlacement='right',
                                                 parent=base.a2dBottomLeft,
                                                 command=self.DisplayFeatureFunction)
        self.displayFeaturesButton.setTransparency(TransparencyAttrib.MAlpha)

    def window_update(self):

        self.tileFrame.constructionMenuFrameSize[0] /= self.windowRatio
        self.tileFrame.constructionMenuFrameSize[1] /= self.windowRatio

        #self.windowSize = newWindowSize
        self.windowRatio = self.windowSize[0] / self.windowSize[1]
        self.frameWidth = self.mainProgram.settings.RELATIVE_SELECTION_FRAME_WIDTH * self.windowRatio

        self.tileFrame.constructionMenuFrameSize[0] *= self.windowRatio
        self.tileFrame.constructionMenuFrameSize[1] *= self.windowRatio

        self.minimap.OnWindowRatioUpdate(newWindowRatio = self.windowRatio)

        self.unitFrame.windowRatio = self.windowRatio
        self.unitFrame.frameWidth = self.frameWidth

        self.unitFrame.frame["frameSize"] = (-self.frameWidth, self.frameWidth, -0.1, 0.1)
        self.unitFrame.frame.setPos(self.windowRatio, 0, 0.1)

        self.tileFrame.frame["frameSize"] = (-self.frameWidth, self.frameWidth, -0.1, 0.1)
        self.tileFrame.frame.setPos(self.windowRatio, 0, 0.1)
        self.tileFrame.constructionMenu["frameSize"] = self.tileFrame.constructionMenuFrameSize

        self.displayFeaturesPosition = (self.displayFeaturesPositionRelative[0]*self.windowRatio,
                                        0,
                                        self.displayFeaturesPositionRelative[2]*self.windowRatio)
        self.displayFeaturesButton.setPos(self.displayFeaturesPosition)

        self.unitFrame.PositionButtonsInFrame()
        self.tileFrame.PositionButtonsInFrame()

        self.add_unit_button.setPos(-0.7*self.windowRatio - self.mainProgram.settings.BUTTON_SCALE, 0, 0.8)
        self.quitButton.setPos(0.9*self.windowRatio, 0, 0.9)

    def window_task(self, task):
        '''sd
        Checks if the window size has been changed
        :param task:
        :return:
        '''

        if self.windowSize[0] != base.win.getXSize() or self.windowSize[1] != base.win.getYSize():
            self.windowSize = (base.win.getXSize(), base.win.getYSize())
            self.window_update()
        return task.again

    def DisplayFeatureFunction(self, value):
        if value == 1:
            self.mainProgram.featureRoot.hide()
        elif value == 0:
            self.mainProgram.featureRoot.show()

class CustomFrame():
    def __init__(self, base, parent, size, position, mainProgram, windowRatio):
        self.frame = DirectFrame(parent = parent,
                                 frameColor=(0, 0, 0, 1),
                                 frameSize=size,
                                 pos=position)
        self.mainProgram = mainProgram
        self.windowRatio = windowRatio
        self.frameWidth = mainProgram.settings.RELATIVE_SELECTION_FRAME_WIDTH * windowRatio
        self.buttonScale = self.mainProgram.settings.BUTTON_SCALE

        self.GUIDataDirectoryPath = Root_Directory.Path(style='unix') + '/Data/GUI/'

        self.buttons = {}
        self.UpdateButtonPosition = None
        self.buttonOffset = [0, 0, 0]

        #self.size = None
        #self.position = None

    def PositionButtonsInFrame(self):
        '''
        Positions the buttons evenly spaced on a horizontal line.
        :param frame:
        :param buttonList:
        :return:
        '''
        numberOfButtons = len(self.buttons)
        for i, key in enumerate(self.buttons):
            button = self.buttons[key]
            button.setPos(2 * self.frameWidth * ((i+1)/(numberOfButtons+1)-0.5) - self.mainProgram.settings.BUTTON_SCALE, 0, 0)
        button.setPos(2 * self.frameWidth * ((i + 1) / (numberOfButtons + 1) - 0.5), 0, 0)

    def PositionButtonsInFrameVertically(self, offset):
        numberOfButtons = len(self.buttons)
        frameWidth = (self.size[1]-self.size[0])
        frameHeight = (self.size[3] - self.size[2])
        buttonPositionsVertical = self.position[2] + np.linspace(-frameHeight/2 + frameWidth/2, frameHeight/2 - frameWidth/2, numberOfButtons)
        for i, key in enumerate(self.buttons):
            button = self.buttons[key]
            button.setPos(self.position[0] + offset[0], + offset[1], buttonPositionsVertical[i] + offset[2])

    def UnToggleButtons(self):
        '''
        Untoggles all the check buttons of the frame object.
        :return:
        '''
        for i, key in enumerate(self.buttons):
            button = self.buttons[key]
            if isinstance(button, DirectCheckButton):
                button['indicatorValue'] = False
                button.setIndicatorValue()

    def UpdatePositionAndSize(self):
        pass

    def OnWindowRatioUpdate(self, newWindowRatio):
        '''
        this function should be called when the ratio of the window changes. It updates the size and positin of the
        object. Thus enabling it to always be positioned in the correct relative location in the window.
        :param newWindowRatio:
        :return:
        '''
        self.windowRatio = newWindowRatio

        self.UpdatePositionAndSize(newWindowRatio)
        self.UpdateButtonPosition(self.buttonOffset)

        self.frame["frameSize"] = self.size
        self.frame.setPos(self.position)

class UnitFrame(CustomFrame):
    def __init__(self, base, parent, size, position, mainProgram, windowRatio):
        super().__init__(base, parent, size, position, mainProgram, windowRatio)

        self.MoveUnitFunction = None

        self.buttons['move'] = DirectCheckButton(boxImage=(self.GUIDataDirectoryPath + 'unit_move_marker.png',
                                                       self.GUIDataDirectoryPath + 'unit_move_marker_pressed.png',
                                                       self.GUIDataDirectoryPath + 'unit_move_marker.png',
                                                       self.GUIDataDirectoryPath + 'unit_move_marker.png'),
                                             scale=self.buttonScale,
                                             pos=(0 - self.buttonScale, 0, 0),
                                             relief=None,
                                             boxRelief=None,
                                             parent=self.frame,
                                             boxPlacement='right',
                                             command=self.MoveUnitButtonFunction)
        self.buttons['move'].setTransparency(TransparencyAttrib.MAlpha)


        self.buttons['information'] = DirectCheckButton(boxImage=(self.GUIDataDirectoryPath + "information_marker.jpg",
                                                              self.GUIDataDirectoryPath + "information_marker_pressed.jpg",
                                                              self.GUIDataDirectoryPath + "information_marker.jpg",
                                                              self.GUIDataDirectoryPath + "information_marker.jpg"),
                                                    scale=self.buttonScale,
                                                    pos=(0.4 * self.windowRatio - self.buttonScale, 0, 0),
                                                    relief=None,
                                                    boxRelief=None,
                                                    parent=self.frame,
                                                    boxPlacement='right')


        self.DestroyUnitFunction = None
        self.buttons['destroy'] = DirectButton(image=(self.GUIDataDirectoryPath + "button_marker_skull.png",
                                                       self.GUIDataDirectoryPath + "button_marker_skull_selected.png",
                                                       self.GUIDataDirectoryPath + "button_marker_skull.png",
                                                       self.GUIDataDirectoryPath + "button_marker_skull.png"),
                                                scale=self.buttonScale,
                                                pos=(-0.4 * self.windowRatio - self.buttonScale, 0, 0),
                                                relief=None,
                                                parent=self.frame,
                                                command=self.DestroyUnitButtonFunction)

        self.buttons['destroy'].setTransparency(TransparencyAttrib.MAlpha)

        self.PositionButtonsInFrame()

    def MoveUnitButtonFunction(self, value):
        self.MoveUnitFunction(value)

    def DestroyUnitButtonFunction(self):
        self.DestroyUnitFunction()


class TileFrame(CustomFrame):
    def __init__(self, base, parent, size, position, mainProgram, windowRatio):
        super().__init__(base, parent, size, position, mainProgram, windowRatio)

        self.buttons['Construct'] = DirectCheckButton(boxImage=(self.GUIDataDirectoryPath + 'construct_building.png',
                                                       self.GUIDataDirectoryPath + 'construct_building_pressed.png',
                                                       self.GUIDataDirectoryPath + 'construct_building.png',
                                                       self.GUIDataDirectoryPath + 'construct_building.png'),
                                             scale=self.buttonScale,
                                             pos=(0 - self.buttonScale, 0, 0),
                                             relief=None,
                                             boxRelief=None,
                                             parent=self.frame,
                                             boxPlacement='right',
                                             command=self.OpenCloseConstructionMenu)
        self.RemoveFeatureFunction = None
        self.buttons['remove_feature'] = DirectButton(image=(self.GUIDataDirectoryPath + "remove_feature.png",
                                                       self.GUIDataDirectoryPath + "remove_feature_pressed.png",
                                                       self.GUIDataDirectoryPath + "remove_feature.png",
                                                       self.GUIDataDirectoryPath + "remove_feature.png"),
                                                scale=self.buttonScale,
                                                pos=(-0.4 * self.windowRatio - self.buttonScale, 0, 0),
                                                relief=None,
                                                parent=self.frame,
                                                command=self.RemoveFeatureButtonFunction)

        self.PositionButtonsInFrame()

        self.ConstructionMenuFunction = None
        self.constructionMenuFrameSize = [0, 0.4*windowRatio, -0.7, 0.7]
        self.constructionMenu = DirectScrolledFrame(canvasSize=(0, 0.4, -4, 0),
                                      frameSize=self.constructionMenuFrameSize,
                                      parent=base.a2dBottomLeft)
        self.constructionMenu.setPos(0, 0, 1)
        DirectButton(text = 'FARM',
                     scale=0.1,
                     pos=(0.275, 0, -0.2),
                     command=self.ConstructionMenuButtonFunction,
                     extraArgs = [0],
                     parent=self.constructionMenu.getCanvas())
        DirectButton(text='TOWN',
                     scale=0.1,
                     pos=(0.275, 0, -0.4),
                     command=self.ConstructionMenuButtonFunction,
                     extraArgs=[1],
                     parent=self.constructionMenu.getCanvas())
        DirectButton(text='JUNGLE',
                     scale=0.1,
                     pos=(0.275, 0, -0.6),
                     command=self.ConstructionMenuButtonFunction,
                     extraArgs=[2],
                     parent=self.constructionMenu.getCanvas())
        DirectButton(text='CONIFER\nFOREST',
                     scale=0.1,
                     pos=(0.275, 0, -0.8),
                     command=self.ConstructionMenuButtonFunction,
                     extraArgs=[3],
                     parent=self.constructionMenu.getCanvas())
        DirectButton(text='TEMPERATE\nFOREST',
                     scale=0.1,
                     pos=(0.275, 0, -1.1),
                     command=self.ConstructionMenuButtonFunction,
                     extraArgs=[4],
                     parent=self.constructionMenu.getCanvas())
        #self.constructionMenu = DirectDialog(dialogName = 'Construct menu',
        #                                     buttonTextList = ['farm', 'town', 'jungle', 'conifer forest', 'temperate forest'],
        #                                     command = self.ConstructionMenuButtonFunction,
        #                                     pos = (0, 0, 1))
        self.constructionMenu.hide()

    def ConstructionMenuButtonFunction(self, value):
        self.ConstructionMenuFunction(value)

    def OpenCloseConstructionMenu(self, value):
        if value == 1:
            self.constructionMenu.show()
        else:
            self.constructionMenu.hide()

    def RemoveFeatureButtonFunction(self):
        self.RemoveFeatureFunction()

class MinimapSelectionFrame(CustomFrame):
    def __init__(self, base, parent, mainProgram, windowRatio, minimap):
        GUIDataDirectoryPath = Root_Directory.Path(style='unix') + '/Data/GUI/'
        self.widthRelative = 0.05
        self.heightRelative = 0.2
        self.minimap = minimap

        self.UpdatePositionAndSize(windowRatio)
        super().__init__(base, parent, self.size, self.position, mainProgram, windowRatio)

        self.buttonScale = self.mainProgram.settings.MINIMAP_SELECTION_BUTTON_SCALE*(self.size[1] - self.size[0])/2
        self.buttonOffset = [self.buttonScale, 0, 0]
        '''
        self.buttons['Biome'] = DirectRadioButton(boxImage=(GUIDataDirectoryPath + 'minimap_selection_biome.png',
                                                       GUIDataDirectoryPath + 'minimap_selection_biome_pressed.png', None),
                                             scale=self.buttonScale,
                                             pos=(-0.4 * self.windowRatio - 0.1, 0, 0),
                                             relief=None,
                                             parent=base.a2dBottomLeft,
                                             variable = self.minimap.minimapFilter,
                                                  value = ['biome'],
                                            indicatorValue = 1,
                                             command=self.minimap.UpdateMinimap)
        '''
        self.buttons['Elevation'] = DirectRadioButton(boxImage=(GUIDataDirectoryPath + 'minimap_selection_elevation.png',
                                                       GUIDataDirectoryPath + 'minimap_selection_elevation_pressed.png', None),
                                                scale=self.buttonScale,
                                                pos=(-0.4 * self.windowRatio - 0.1, 0, 0),
                                                relief=None,
                                                parent=base.a2dBottomLeft,
                                                     variable=self.minimap.minimapFilter,
                                                     value=['elevation'],
                                                      indicatorValue=0,
                                                command=self.minimap.UpdateMinimap)
        self.buttons['Fertility'] = DirectRadioButton(boxImage=(GUIDataDirectoryPath + 'minimap_selection_fertility.png',
                                                            GUIDataDirectoryPath + 'minimap_selection_fertility_pressed.png', None),
                                                     scale=self.buttonScale,
                                                     pos=(-0.4 * self.windowRatio - 0.1, 0, 0),
                                                     relief=None,
                                                     parent=base.a2dBottomLeft,
                                                      variable=self.minimap.minimapFilter,
                                                      value=['fertility'],
                                                      indicatorValue=0,
                                                     command=self.minimap.UpdateMinimap)
        self.buttons['Roughness'] = DirectRadioButton(boxImage=(GUIDataDirectoryPath + 'minimap_selection_roughness.png',
                                                             GUIDataDirectoryPath + 'minimap_selection_roughness_pressed.png', None),
                                                      scale=self.buttonScale,
                                                      pos=(-0.4 * self.windowRatio - 0.1, 0, 0),
                                                      relief=None,
                                                      parent=base.a2dBottomLeft,
                                                      variable=self.minimap.minimapFilter,
                                                      value=['roughness'],
                                                      indicatorValue=0,
                                                      command=self.minimap.UpdateMinimap)
        self.buttons['temperature'] = DirectRadioButton(boxImage=(GUIDataDirectoryPath + 'minimap_selection_temperature.png',
                                                             GUIDataDirectoryPath + 'minimap_selection_temperature_pressed.png', None),
                                                      scale=self.buttonScale,
                                                      pos=(-0.4 * self.windowRatio - 0.1, 0, 0),
                                                      relief=None,
                                                      parent=base.a2dBottomLeft,
                                                      variable=self.minimap.minimapFilter,
                                                      value=['temperature'],
                                                      indicatorValue=0,
                                                      command=self.minimap.UpdateMinimap)

        # Links the radio buttons together.
        buttons = []
        for key in self.buttons:
            button = self.buttons[key]
            buttons.append(button)
        for key in self.buttons:
            button = self.buttons[key]
            button.indicator['text'] = ('', '') # Disables the default asterix
            button.setOthers(buttons)

        self.UpdateButtonPosition = self.PositionButtonsInFrameVertically
        self.UpdateButtonPosition(offset = self.buttonOffset)

    def UpdatePositionAndSize(self, windowRatio):
        self.size = [-self.widthRelative * windowRatio,
                     self.widthRelative * windowRatio,
                     -self.heightRelative * windowRatio,
                     self.heightRelative * windowRatio]
        self.position = ((2 - 2*self.heightRelative - self.widthRelative) * windowRatio,
                         0,
                         self.heightRelative * windowRatio)

class Minimap():
    def __init__(self, windowRatio, mainProgram):
        self.GUIDataDirectoryPath = Root_Directory.Path(style='unix') + '/Data/GUI/'

        self.windowRatio = windowRatio
        self.mainProgram = mainProgram

        self.sizeRelative = 0.2
        self.leftPositionRelative = 2-self.sizeRelative

        self.size = self.sizeRelative * self.windowRatio
        self.position = (self.leftPositionRelative * self.windowRatio, 0, self.sizeRelative * self.windowRatio)

        self.minimapFilter = [''] # Changed by the selection buttons
        self.minimapFilterUpToDate = {}
        self.minimapFilterUpToDate['biome'] = False
        self.minimapFilterUpToDate['fertility'] = False
        self.minimapFilterUpToDate['roughness'] = False
        self.minimapFilterUpToDate['elevation'] = False
        self.minimapFilterUpToDate['temperature'] = False

        self.minimap = DirectButton(image=(self.GUIDataDirectoryPath + "remove_feature.png",
                                           self.GUIDataDirectoryPath + "remove_feature_pressed.png",
                                           self.GUIDataDirectoryPath + "remove_feature.png",
                                           self.GUIDataDirectoryPath + "remove_feature.png"),
                                    scale=self.size,
                                    pos=self.position,
                                    relief=None,
                                    pressEffect = 0,
                                    parent=base.a2dBottomLeft,
                                    command = None)
        self.selectionFrame = MinimapSelectionFrame(base=base,
                                                    parent=base.a2dBottomLeft,
                                                    mainProgram=self.mainProgram,
                                                    windowRatio=self.windowRatio,
                                                    minimap = self)

    def OnWindowRatioUpdate(self, newWindowRatio):
        '''
        This function should be called when the size of the window has been changed. This function recomputes the size
        of position of the minimap and updates the object accordingly.
        :param newWindowRatio:
        :return:
        '''
        self.windowRatio = newWindowRatio

        self.size = self.sizeRelative * self.windowRatio
        self.position = (self.leftPositionRelative * self.windowRatio, 0, self.sizeRelative * self.windowRatio)

        self.minimap.setPos(self.position)
        self.minimap.setScale(self.size)

        self.selectionFrame.OnWindowRatioUpdate(newWindowRatio)

    def UpdateMinimapImage(self, type = 'biome'):

        if type == 'biome':
            #baseMap =
            pass
        elif type == 'elevation':
            baseMap = self.mainProgram.world.elevation
            colourRamp = self.mainProgram.settings.ELEVATION_MINIMAP_COLOURS
            colourBounds = self.mainProgram.settings.ELEVATION_MINIMAP_COLOURS_BOUNDS
            numberOfValues = self.mainProgram.settings.ELEVATION_LEVELS
            colourSteps = np.linspace(0, self.mainProgram.settings.ELEVATION_LEVELS-1,
                                      self.mainProgram.settings.ELEVATION_LEVELS)
        elif type == 'fertility':
            baseMap = self.mainProgram.world.soilFertility
            colourRamp = self.mainProgram.settings.SOIL_FERTILITY_MINIMAP_COLOURS
            colourBounds = self.mainProgram.settings.SOIL_FERTILITY_MINIMAP_COLOURS_BOUNDS
            numberOfValues = self.mainProgram.settings.SOIL_FERTILITY_LEVELS
            colourSteps = np.linspace(0, self.mainProgram.settings.SOIL_FERTILITY_LEVELS - 1,
                                      self.mainProgram.settings.SOIL_FERTILITY_LEVELS)
        elif type == 'roughness':
            baseMap = self.mainProgram.world.topographyRoughness
            colourRamp = self.mainProgram.settings.TOPOGRAPHY_ROUGHNESS_MINIMAP_COLOURS
            colourBounds = self.mainProgram.settings.TOPOGRAPHY_ROUGHNESS_MINIMAP_COLOURS_BOUNDS
            numberOfValues = self.mainProgram.settings.TOPOGRAPHY_ROUGHNESS_LEVELS
            colourSteps = np.linspace(0, self.mainProgram.settings.TOPOGRAPHY_ROUGHNESS_LEVELS - 1,
                                      self.mainProgram.settings.TOPOGRAPHY_ROUGHNESS_LEVELS)
        elif type == 'temperature':
            baseMap = self.mainProgram.world.temperature
            colourRamp = self.mainProgram.settings.TEMPERATURE_MINIMAP_COLOURS
            colourBounds = self.mainProgram.settings.TEMPERATURE_MINIMAP_COLOURS_BOUNDS
            #numberOfValues = self.mainProgram.settings.TOPOGRAPHY_ROUGHNESS_LEVELS
            colourSteps = np.linspace(self.mainProgram.settings.TEMPERATURE_MIN_VALUE,
                                      self.mainProgram.settings.TEMPERATURE_MAX_VALUE,
                                      np.size(colourRamp, 0))


        interpolatedMap = self.GetInterpolatedMap(baseMap = baseMap)

        #MapToImage()
        #EncodeColours()

        imageArray = np.zeros((self.mainProgram.settings.MINIMAP_RESOLUTION[0], self.mainProgram.settings.MINIMAP_RESOLUTION[1], 3))
        interpolatorRed = interpolate.interp1d(colourSteps,
                                 colourRamp[:, 0],
                                 bounds_error=False,
                                 fill_value=(colourBounds[0, 0],
                                             colourBounds[1, 0]))
        redMap = interpolatorRed(np.reshape(interpolatedMap, (self.mainProgram.settings.MINIMAP_RESOLUTION[0] * self.mainProgram.settings.MINIMAP_RESOLUTION[1], 1)))
        redMap = np.reshape(redMap, (self.mainProgram.settings.MINIMAP_RESOLUTION[0], self.mainProgram.settings.MINIMAP_RESOLUTION[1]))

        interpolatorGreen = interpolate.interp1d(colourSteps,
                                 colourRamp[:, 1],
                                 bounds_error=False,
                                 fill_value=(colourBounds[0, 1],
                                             colourBounds[1, 1]))
        greenMap = interpolatorGreen(np.reshape(interpolatedMap, (self.mainProgram.settings.MINIMAP_RESOLUTION[0] * self.mainProgram.settings.MINIMAP_RESOLUTION[1], 1)))
        greenMap = np.reshape(greenMap, (self.mainProgram.settings.MINIMAP_RESOLUTION[0], self.mainProgram.settings.MINIMAP_RESOLUTION[1]))

        interpolatorBlue = interpolate.interp1d(colourSteps,
                                 colourRamp[:, 2],
                                 bounds_error=False,
                                 fill_value=(colourBounds[0, 2],
                                             colourBounds[1, 2]))
        blueMap = interpolatorBlue(np.reshape(interpolatedMap, (self.mainProgram.settings.MINIMAP_RESOLUTION[0] * self.mainProgram.settings.MINIMAP_RESOLUTION[1], 1)))
        blueMap = np.reshape(blueMap, (self.mainProgram.settings.MINIMAP_RESOLUTION[0], self.mainProgram.settings.MINIMAP_RESOLUTION[1]))

        imageArray[:, :, 0] = redMap
        imageArray[:, :, 1] = greenMap
        imageArray[:, :, 2] = blueMap

        tmpDataPath = Root_Directory.Path() + '/Data/tmp_Data/'
        matplotlib.image.imsave(tmpDataPath + 'minimap_image_' + type + '.png', imageArray)


    def GetInterpolatedMap(self, baseMap):
        '''
        The basemap is used as a low resolution template from which a high resolution interpolation is made. The high
        resolution interpolated map is returned. Linear interpolation is used.
        '''
        maxMapSize = np.max((self.mainProgram.settings.N_ROWS, self.mainProgram.settings.N_COLONS))

        xGap = (1-self.mainProgram.settings.N_COLONS/maxMapSize)/2
        yGap = (1-self.mainProgram.settings.N_ROWS/maxMapSize)/2
        interpolator = interpolate.interp2d(np.linspace(xGap, 1-xGap, self.mainProgram.settings.N_COLONS),
                                            np.linspace(yGap, 1-yGap, self.mainProgram.settings.N_ROWS),
                                            np.flip(baseMap, 0), kind='linear', fill_value=-1)

        return interpolator(np.linspace(0, 1, self.mainProgram.settings.MINIMAP_RESOLUTION[0]), np.linspace(0, 1, self.mainProgram.settings.MINIMAP_RESOLUTION[1]))

    def UpdateMinimap(self):
        '''
        The image displayed in the minimap is changed according to the button pushed.
        '''
        if self.minimapFilterUpToDate[self.minimapFilter[0]] == False:
            self.UpdateMinimapImage(type=self.minimapFilter[0])
            self.minimapFilterUpToDate[self.minimapFilter[0]] = True


        tmpDataPath = Root_Directory.Path(style='unix') + '/Data/tmp_Data/'
        self.minimap.setImage(tmpDataPath + 'minimap_image_' + self.minimapFilter[0] + '.png')

        # All teaxtures are released (removed from RAM) to enable the minimap image to change. This however is probably
        # not good for performance since textures of trees/houses and other features are removed aswell. Optimally only
        # the minimap textures should be released.
        p3d.TexturePool.releaseAllTextures()
