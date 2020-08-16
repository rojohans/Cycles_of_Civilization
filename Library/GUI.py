from panda3d.core import TextNode
from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectGui import *
from panda3d.core import TransparencyAttrib
import sys

import TileClass

class GUIClass():
    def __init__(self, base, debugText = False):



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
        self.buttonScale = 0.08
        self.frameWidth = 0.6*self.windowRatio



        # parent=base.a2dTopLeft,
        #self.myFrame = DirectFrame(parent = aspect2d,
        #                      frameColor=(0, 0, 0, 1),
        #                      frameSize=(-0.6*self.windowRatio, 0.6*self.windowRatio, -0.1, 0.1),
        #                      pos=(0, 0, -0.9))
        self.myFrame = DirectFrame(parent = base.a2dBottomLeft,
                              frameColor=(0, 0, 0, 1),
                              frameSize=(-self.frameWidth, self.frameWidth, -0.1, 0.1),
                              pos=(self.windowRatio, 0, 0.1))
        #self.myFrame = DirectFrame(parent = render2d,
        #                      frameColor=(0, 0, 0, 1),
        #                      frameSize=(-1, 1, -1, 0),
        #                      pos=(0, 0, 0))

        # b = DirectButton(image = "panda3d-master/samples/chessboard/models/unit_move_marker.jpg", scale = 0.5, pos = (0, -1, 0), relief = None)
        #
        # The scale of the button is the radii of the button, measured in units in windowHeight/2. A button with scale 1
        # will cover the entire height of the window if placed in the center of the screen.
        #
        self.MoveUnitFunction = None
        self.move_button = DirectCheckButton(boxImage=("panda3d-master/samples/chessboard/models/unit_move_marker.png",
                                            "panda3d-master/samples/chessboard/models/unit_move_marker_pressed.png",
                                            "panda3d-master/samples/chessboard/models/unit_move_marker.png",
                                            "panda3d-master/samples/chessboard/models/unit_move_marker.png"),
                                             scale=self.buttonScale,
                                             pos=(0 - self.buttonScale, 0, 0),
                                             relief=None,
                                             boxRelief=None,
                                             parent=self.myFrame,
                                             boxPlacement = 'right',
                                             command = self.MoveUnitButtonFunction)
        self.move_button.setTransparency(TransparencyAttrib.MAlpha)

        self.information_button = DirectCheckButton(boxImage=("panda3d-master/samples/chessboard/models/information_marker.jpg",
                                        "panda3d-master/samples/chessboard/models/information_marker_pressed.jpg",
                                        "panda3d-master/samples/chessboard/models/information_marker.jpg",
                                        "panda3d-master/samples/chessboard/models/information_marker.jpg"),
                                                    scale=self.buttonScale,
                                                    pos = (0.4*self.windowRatio - self.buttonScale, 0, 0),
                                                    relief=None,
                                                    boxRelief=None,
                                                    parent=self.myFrame,
                                                    boxPlacement = 'right')

        #self.destroy_unit_button = DirectButton(boxImage=("panda3d-master/samples/chessboard/models/button_marker_skull.png",
        #                                "panda3d-master/samples/chessboard/models/button_marker_skull_selected.png",
        #                                "panda3d-master/samples/chessboard/models/button_marker_skull.png",
        #                                "panda3d-master/samples/chessboard/models/button_marker_skull.png"),
        #                                             scale=self.buttonScale,
        #                                             pos=(-0.4*self.windowRatio - self.buttonScale, 0, 0),
        #                                             relief=None,
        #                                             boxRelief=None,
        #                                             parent=self.myFrame,
        #                                             boxPlacement = 'right')
        self.DestroyUnitFunction = None
        self.destroy_unit_button = DirectButton(image=("panda3d-master/samples/chessboard/models/button_marker_skull.png",
                                                "panda3d-master/samples/chessboard/models/button_marker_skull_selected.png",
                                                "panda3d-master/samples/chessboard/models/button_marker_skull.png",
                                                "panda3d-master/samples/chessboard/models/button_marker_skull.png"),
                                                scale=self.buttonScale,
                                                pos=(-0.4*self.windowRatio - self.buttonScale, 0, 0),
                                                relief=None,
                                                parent=self.myFrame,
                                                command = self.DestroyUnitButtonFunction)

        self.destroy_unit_button.setTransparency(TransparencyAttrib.MAlpha)

        self.PositionButtonsInFrame(self.myFrame, [self.move_button, self.information_button, self.destroy_unit_button])


        self.add_unit_button = DirectCheckButton(boxImage=("panda3d-master/samples/chessboard/models/add_unit_button.png",
                                                "panda3d-master/samples/chessboard/models/add_unit_button_pressed.png",
                                                "panda3d-master/samples/chessboard/models/add_unit_button.png",
                                                "panda3d-master/samples/chessboard/models/add_unit_button.png"),
                                                 scale=self.buttonScale,
                                                 pos=(-0.9*self.windowRatio - self.buttonScale, 0, 0.5),
                                                 relief=None,
                                                 boxRelief=None,
                                                 boxPlacement = 'right',
                                                 command = TileClass.UnitClass.AddUnitButtonFunction)
        self.add_unit_button.setTransparency(TransparencyAttrib.MAlpha)




        self.quitButton = DirectButton(image=("panda3d-master/samples/chessboard/models/quit_button.png",
                                        "panda3d-master/samples/chessboard/models/quit_button.png",
                                        "panda3d-master/samples/chessboard/models/quit_button.png",
                                        "panda3d-master/samples/chessboard/models/quit_button.png"),
                                       scale=self.buttonScale,
                                       pos=(0.9*self.windowRatio, 0, 0.9),
                                       relief=None,
                                       command = sys.exit)
        self.quitButton.setTransparency(TransparencyAttrib.MAlpha)

    def MoveUnitButtonFunction(self, value):
        self.MoveUnitFunction(value)

    def DestroyUnitButtonFunction(self):
        self.DestroyUnitFunction()

    def PositionButtonsInFrame(self, frame, buttonList):
        '''
        Positions the buttons evenly spaced on a horizontal line.
        :param frame:
        :param buttonList:
        :return:
        '''
        numberOfButtons = len(buttonList)
        for i, button in enumerate(buttonList):
            button.setPos(2 * self.frameWidth * ((i+1)/(numberOfButtons+1)-0.5) - self.buttonScale, 0, 0)
        button.setPos(2 * self.frameWidth * ((i + 1) / (numberOfButtons + 1) - 0.5), 0, 0)

    def window_update(self):
        #self.windowSize = newWindowSize
        self.windowRatio = self.windowSize[0] / self.windowSize[1]
        self.frameWidth = 0.6 * self.windowRatio

        self.myFrame["frameSize"] = (-0.6*self.windowRatio, 0.6*self.windowRatio, -0.1, 0.1)
        self.myFrame.setPos(self.windowRatio, 0, 0.1)

        self.PositionButtonsInFrame(self.myFrame, [self.move_button, self.information_button, self.destroy_unit_button])

        self.add_unit_button.setPos(-0.9*self.windowRatio - self.buttonScale, 0, 0.5)
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
