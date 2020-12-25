from panda3d.core import TextNode
from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectGui import *
from panda3d.core import TransparencyAttrib
import panda3d.core as p3d
import sys
import numpy as np
import matplotlib
from scipy import interpolate
from matplotlib import image

import Root_Directory
import Library.Texture as Texture
import Library.TileClass as TileClass

if False:
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

    class CustomFrame:
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
            self.buttons['moisture'] = DirectRadioButton(boxImage=(GUIDataDirectoryPath + 'minimap_selection_moisture.png',
                                                                 GUIDataDirectoryPath + 'minimap_selection_moisture_pressed.png', None),
                                                          scale=self.buttonScale,
                                                          pos=(-0.4 * self.windowRatio - 0.1, 0, 0),
                                                          relief=None,
                                                          parent=base.a2dBottomLeft,
                                                          variable=self.minimap.minimapFilter,
                                                          value=['moisture'],
                                                          indicatorValue=0,
                                                          command=self.minimap.UpdateMinimap)
            self.buttons['vegetation'] = DirectRadioButton(boxImage=(GUIDataDirectoryPath + 'feature_toggle.png',
                                                                   GUIDataDirectoryPath + 'feature_toggle.png',
                                                                   None),
                                                         scale=self.buttonScale,
                                                         pos=(-0.4 * self.windowRatio - 0.1, 0, 0),
                                                         relief=None,
                                                         parent=base.a2dBottomLeft,
                                                         variable=self.minimap.minimapFilter,
                                                         value=['vegetation'],
                                                         indicatorValue=0,
                                                         command=self.minimap.UpdateMinimap)
            self.buttons['fauna'] = DirectRadioButton(boxImage=(GUIDataDirectoryPath + 'button_marker_skull.png',
                                                                     GUIDataDirectoryPath + 'button_marker_skull.png',
                                                                     None),
                                                           scale=self.buttonScale,
                                                           pos=(-0.4 * self.windowRatio - 0.1, 0, 0),
                                                           relief=None,
                                                           parent=base.a2dBottomLeft,
                                                           variable=self.minimap.minimapFilter,
                                                           value=['fauna'],
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
            self.minimapFilterUpToDate['elevation'] = False
            self.minimapFilterUpToDate['temperature'] = False
            self.minimapFilterUpToDate['moisture'] = False
            self.minimapFilterUpToDate['vegetation'] = False
            self.minimapFilterUpToDate['fauna'] = False

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
                colourSteps = np.linspace(0, self.mainProgram.settings.ELEVATION_LEVELS-1,
                                          self.mainProgram.settings.ELEVATION_LEVELS)
            elif type == 'temperature':
                baseMap = self.mainProgram.world.temperature
                colourRamp = self.mainProgram.settings.TEMPERATURE_MINIMAP_COLOURS
                colourBounds = self.mainProgram.settings.TEMPERATURE_MINIMAP_COLOURS_BOUNDS
                colourSteps = [-40, -30, -20, -10, 2, 13, 20, 30]
            elif type == 'moisture':
                baseMap = self.mainProgram.world.moisture
                colourRamp = self.mainProgram.settings.MOISTURE_MINIMAP_COLOURS
                colourBounds = self.mainProgram.settings.MOISTURE_MINIMAP_COLOURS_BOUNDS
                colourSteps = np.linspace(0, 1, np.size(self.mainProgram.settings.MOISTURE_MINIMAP_COLOURS, 0))
            elif type == 'vegetation':
                baseMap = self.mainProgram.Ecosystem.Vegetation.GetImage(densityScaling=False)
                baseMap = np.mean(baseMap, axis=2)

                colourRamp = np.array([(0.1, 0.3, 0.1),
                                       (0.2, 0.8, 0.2)])
                colourBounds = np.array([(0.0, 0.0, 0.0),
                                         (0.0, 0.0, 0.0)])
                colourSteps = [0.15, 0.9]
            elif type == 'fauna':
                baseMap = self.mainProgram.Ecosystem.Animal.GetImage(densityScaling=False)
                baseMap = np.mean(baseMap, axis=2)

                colourRamp = np.array([(0.1, 0.3, 0.1),
                                       (0.2, 0.8, 0.2)])
                colourBounds = np.array([(0.0, 0.0, 0.0),
                                         (0.0, 0.0, 0.0)])
                colourSteps = [0.15, 0.9]


            interpolatedMap = self.GetInterpolatedMap(baseMap = baseMap)

            #MapToImage()
            #EncodeColours()

            imageArray = np.zeros((self.mainProgram.settings.MINIMAP_RESOLUTION[0], self.mainProgram.settings.MINIMAP_RESOLUTION[1], 3))
            interpolatorRed = interpolate.interp1d(colourSteps,
                                     colourRamp[:, 0],
                                     bounds_error=False,
                                                   kind='linear',
                                     fill_value=(colourBounds[0, 0],
                                                 colourBounds[1, 0]))
            redMap = interpolatorRed(np.reshape(interpolatedMap, (self.mainProgram.settings.MINIMAP_RESOLUTION[0] * self.mainProgram.settings.MINIMAP_RESOLUTION[1], 1)))
            redMap = np.reshape(redMap, (self.mainProgram.settings.MINIMAP_RESOLUTION[0], self.mainProgram.settings.MINIMAP_RESOLUTION[1]))

            interpolatorGreen = interpolate.interp1d(colourSteps,
                                     colourRamp[:, 1],
                                     bounds_error=False,
                                                     kind='linear',
                                     fill_value=(colourBounds[0, 1],
                                                 colourBounds[1, 1]))
            greenMap = interpolatorGreen(np.reshape(interpolatedMap, (self.mainProgram.settings.MINIMAP_RESOLUTION[0] * self.mainProgram.settings.MINIMAP_RESOLUTION[1], 1)))
            greenMap = np.reshape(greenMap, (self.mainProgram.settings.MINIMAP_RESOLUTION[0], self.mainProgram.settings.MINIMAP_RESOLUTION[1]))

            interpolatorBlue = interpolate.interp1d(colourSteps,
                                     colourRamp[:, 2],
                                     bounds_error=False,
                                                    kind='linear',
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
                                                np.flip(baseMap, 0), kind='linear', fill_value=-10000)

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
















import Library.GUI_Components as GUI_Components

class Interface():
    def __init__(self, base, mainProgram):
        self.mainProgram = mainProgram
        self.base = base

        self.windowSize = (base.win.getXSize(), base.win.getYSize())
        self.windowRatio = self.windowSize[0] / self.windowSize[1]

        GUIDataDirectoryPath = Root_Directory.Path(style='unix') + '/Data/GUI/'

        self.frames = {}
        self.labels = {}
        self.buttons = {}

        self.frames['tileInformation'] = CustomFrame(position=self.mainProgram.settings.tileInformationFramePosition,
                                                     size=self.mainProgram.settings.tileInformationFrameSize,
                                                     color=(1, 1, 1, 1))
        self.frames['tileInformation'].node.hide()
        self.labels['tileInformation'] = CustomLabel(position=(self.mainProgram.settings.tileInformationFrameSize[0] + self.mainProgram.settings.tileInformationMargin,
                                                               0,
                                                               self.mainProgram.settings.tileInformationFrameSize[3] - self.mainProgram.settings.tileInformationMargin-0.05),
                                                     text="iTile : 0 \nElevation : 0 \nTemperature : 0\nForest coverage : None\nForest coverage : None\nForest coverage : None\nForest coverage : None\nForest coverage : None\nForest coverage : None\nForest coverage : None\nForest coverage : None",
                                                     parent=self.frames['tileInformation'].node)


        self.frames['tileAction'] = CustomFrame(position=self.mainProgram.settings.tileActionFramePosition,
                                                     size=self.mainProgram.settings.tileActionFrameSize,
                                                     color=(1, 1, 1, 1))
        self.frames['tileAction'].node.hide()
        self.buttons['addFeature'] = CustomCheckButton(parent=self.frames['tileAction'].node,
                                                  images=['add_feature.png', 'add_feature_pressed.png'],
                                                  callbackFunction=self.mainProgram.featureInteractivity.AddFeature,
                                                  position=(-0.08, 0, 0),
                                                  scale = 0.07)
        self.buttons['infoFeature'] = CustomCheckButton(parent=self.frames['tileAction'].node,
                                                  images=['info_feature.png', 'info_feature_pressed.png'],
                                                  callbackFunction=self.mainProgram.featureInteractivity.FeatureInformationCallback,
                                                  position=(0, 0, 0),
                                                  scale = 0.07)
        self.buttons['removeFeature'] = CustomCheckButton(parent=self.frames['tileAction'].node,
                                                    images=['remove_feature.png', 'remove_feature_pressed.png'],
                                                    callbackFunction=self.mainProgram.featureInteractivity.RemoveFeature,
                                                    position=(0.08, 0, 0),
                                                    scale = 0.07)

        self.frames['addFeatureMenu'] = CustomScrolledFrame(position=self.mainProgram.settings.addFeatureFramePosition,
                                                            canvasSize=self.mainProgram.settings.addFeatureFrameCanvasSize,
                                                            size=self.mainProgram.settings.addFeatureFrameSize,
                                                            color=(1, 1, 1, 1),
                                                            childrenGap=self.mainProgram.settings.addFeatureFrameChildrenGap)
        self.frames['addFeatureMenu'].node.hide()


        for key in self.mainProgram.featureTemplate:
            feature = self.mainProgram.featureTemplate[key]
            self.buttons['selectFeature_' + key] = CustomButton(parent=self.frames['addFeatureMenu'].node.getCanvas(),
                                                                position=(0.2, 0, -0.3),
                                                                scale=0.06,
                                                                images=None,
                                                                callbackFunction=self.mainProgram.featureInteractivity.PlaceFeature,
                                                                commandInput=[key],
                                                                text=feature.GUILabel)
            self.frames['addFeatureMenu'].children.append(self.buttons['selectFeature_' + key])
        self.frames['addFeatureMenu'].PositionChildren()



        self.featureInformation = GUI_Components.FeatureInformation(mainProgram=self.mainProgram)
        self.featureInformation.Initialize(self)

        self.toolMenu = GUI_Components.ToolMenu(mainProgram=self.mainProgram)
        self.toolMenu.Initialize(self)


        self.buttons['end_turn'] = CustomCheckButton(parent=base.a2dBottomRight,
                                                            position=(-0.15+0.075, 0, 0.15),
                                                            scale=0.15,
                                                            images=['end_turn.png', 'end_turn_pressed.png'],
                                                            callbackFunction=self.mainProgram.Turn,
                                                            commandInput=[])
        self.labels['end_turn'] = CustomLabel(position=(-0.16, 0, 0.33),
                                              text="TURN : 0",
                                              scale = .06,
                                              parent=base.a2dBottomRight)
        '''
        self.quitButton = DirectButton(image=(GUIDataDirectoryPath + "quit_button.png",
                                              GUIDataDirectoryPath + "quit_button.png",
                                              GUIDataDirectoryPath + "quit_button.png",
                                              GUIDataDirectoryPath + "quit_button.png"),
                                       scale=self.mainProgram.settings.buttonSize,
                                       pos=(self.windowRatio * self.mainProgram.settings.quitButtonPosition[0],
                                            self.mainProgram.settings.quitButtonPosition[1],
                                            self.mainProgram.settings.quitButtonPosition[2]),
                                       relief=None,
                                       command = sys.exit)
        '''

        self.mainProgram.add_task(self.window_task, 'window_update')

        self.Update()

    def window_task(self, task):
        '''sd
        Checks if the window size has been changed
        :param task:
        :return:
        '''

        if self.windowSize[0] != base.win.getXSize() or self.windowSize[1] != base.win.getYSize():
            self.windowSize = (base.win.getXSize(), base.win.getYSize())
            self.Update()
        return task.again

    def Update(self):
        self.windowRatio = self.windowSize[0] / self.windowSize[1]

        #self.quitButton.setPos(self.windowRatio * self.mainProgram.settings.quitButtonPosition[0],
        #                       self.mainProgram.settings.quitButtonPosition[1],
        #                       self.mainProgram.settings.quitButtonPosition[2])

        for frameKey in self.frames:
            self.frames[frameKey].Update(self.windowRatio)

        for labelKey in self.labels:
            self.labels[labelKey].Update(self.windowRatio)

        for buttonKey in self.buttons:
            self.buttons[buttonKey].Update(self.windowRatio)

        self.toolMenu.UpdateStatisticsGraph()




class CustomFrame():
    def __init__(self, position, size, color = (0, 0, 0, 1), textureImage = 'frame_background.png'):
        if textureImage == None:
            self.node = DirectFrame(frameColor=color,
                                    frameSize=size,
                                    pos=position)
        else:
            t = Texture.Texture({'water': image.imread(Root_Directory.Path() + "/Data/GUI/" + textureImage)})
            self.node = DirectFrame(frameTexture = t.stitchedTexture,
                                    frameColor=color,
                                    frameSize=size,
                                    pos=position)
        self.position = position
        self.size = size

    def Update(self, newWindowRatio):
        '''
        this function should be called when the ratio of the window changes. It updates the size and positin of the
        object. Thus enabling it to always be positioned in the correct relative location in the window.
        :param newWindowRatio:
        :return:
        '''
        self.node["frameSize"] = (newWindowRatio*self.size[0], newWindowRatio*self.size[1], self.size[2], self.size[3])
        self.node.setPos((newWindowRatio*self.position[0], self.position[1], self.position[2]))

class CustomScrolledFrame():
    def __init__(self, position, size, canvasSize, color = (0, 0, 0, 1), textureImage = 'frame_background.png', childrenGap = 0.2):
        t = Texture.Texture({'water': image.imread(Root_Directory.Path() + "/Data/GUI/" + textureImage)})

        GUIDataDirectoryPath = Root_Directory.Path(style='unix') + '/Data/GUI/'
        self.node = DirectScrolledFrame(frameTexture = t.stitchedTexture,
                                                    canvasSize=canvasSize,
                                                    frameColor = color,
                                                    frameSize=size,
                                                    pos = position)
        #verticalScroll_thumb_image = (GUIDataDirectoryPath + textureImage,
        #                              GUIDataDirectoryPath + textureImage,
        #                              GUIDataDirectoryPath + textureImage,
        #                              GUIDataDirectoryPath + textureImage),
        #verticalScroll_thumb_image_scale = (0.05, 0.05, 0.05)
        self.childrenGap = childrenGap
        self.children = []
        self.canvasSize = canvasSize
        self.position = position
        self.size = size

    def PositionChildren(self):
        verticalPosition = -self.childrenGap
        horizontalMiddlePosition = (self.canvasSize[1]-self.canvasSize[0])/2
        for child in self.children:
            verticalPosition -= self.childrenGap
            child.position = (horizontalMiddlePosition, 0, verticalPosition)
            child.Update()

    def Update(self, newWindowRatio):
        '''
        this function should be called when the ratio of the window changes. It updates the size and positin of the
        object. Thus enabling it to always be positioned in the correct relative location in the window.
        :param newWindowRatio:
        :return:
        '''
        self.node["frameSize"] = (newWindowRatio*self.size[0], newWindowRatio*self.size[1], self.size[2], self.size[3])
        self.node.setPos((newWindowRatio*self.position[0], self.position[1], self.position[2]))

class CustomLabel():
    def __init__(self, text, position, parent, scale = 0.05):
        self.node = DirectLabel(
                                scale=scale,
                                pos=position,
                                frameColor=(0, 0, 0, 0),
                                text_align=TextNode.ALeft,
                                text=text,
                                text_fg=(0, 0, 0, 1),
                                )
        self.node.reparentTo(parent)
        self.position = position

    def Update(self, newWindowRatio):
        '''
        this function should be called when the ratio of the window changes. It updates the size and positin of the
        object. Thus enabling it to always be positioned in the correct relative location in the window.
        :param newWindowRatio:
        :return:
        '''
        self.node.setPos((newWindowRatio*self.position[0], self.position[1], self.position[2]))

class CustomButton():
    def __init__(self, images, position, callbackFunction, parent, scale = 0.05, text = '', commandInput = []):
        GUIDataDirectoryPath = Root_Directory.Path(style='unix') + '/Data/GUI/'
        if images != None:
            imageList = (GUIDataDirectoryPath + images[0],
             GUIDataDirectoryPath + images[1],
             GUIDataDirectoryPath + images[0],
             GUIDataDirectoryPath + images[0])
        else:
            imageList = None
        self.node = DirectButton(parent = parent,
                                 image=imageList,
                                 text = text,
                                 extraArgs=commandInput,
                                 scale=scale,
                                 pos=(position[0], position[1], position[2]),
                                 relief=None,
                                 command=callbackFunction)
        self.node.setTransparency(TransparencyAttrib.MAlpha)
        self.position = position
        self.scale = scale

    def Update(self, newWindowRatio=1):
        '''
        this function should be called when the ratio of the window changes. It updates the size and positin of the
        object. Thus enabling it to always be positioned in the correct relative location in the window.
        :param newWindowRatio:
        :return:
        '''
        self.node.setPos((newWindowRatio*self.position[0], self.position[1], self.position[2]))

class CustomCheckButton():
    def __init__(self, images, position, callbackFunction, parent, scale = 0.05, text = '', commandInput = []):
        GUIDataDirectoryPath = Root_Directory.Path(style='unix') + '/Data/GUI/'
        if images != None:
            imageList = (GUIDataDirectoryPath + images[0],
             GUIDataDirectoryPath + images[1],
             GUIDataDirectoryPath + images[0],
             GUIDataDirectoryPath + images[0])
        else:
            imageList = None
        self.node = DirectCheckButton(parent = parent,
                                      boxImage=imageList,
                                      text = text,
                                      extraArgs=commandInput,
                                      scale=scale,
                                      pos=(position[0]-scale, position[1], position[2]),
                                      relief=None,
                                      boxRelief=None,
                                      boxPlacement='right',
                                      command=callbackFunction)
        self.node.setTransparency(TransparencyAttrib.MAlpha)
        self.position = position
        self.scale = scale

    def Update(self, newWindowRatio):
        '''
        this function should be called when the ratio of the window changes. It updates the size and positin of the
        object. Thus enabling it to always be positioned in the correct relative location in the window.
        :param newWindowRatio:
        :return:
        '''
        self.node.setPos((newWindowRatio*self.position[0]-self.scale, self.position[1], self.position[2]))
