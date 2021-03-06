import Root_Directory

from direct.showbase.ShowBase import ShowBase
import sys
from Library import GUI
import Settings

#from direct.gui.DirectGui import *
#import direct.directbase.DirectStart

class ChessboardDemo(ShowBase):
    def __init__(self):
        # Initialize the ShowBase class from which we inherit, which will
        # create a window and set up everything we need for rendering into it.
        ShowBase.__init__(self)

        # Changes the background colour of the scene.
        base.setBackgroundColor(0.1, 0.3, 0.6)

        self.settings = Settings.SettingsClass()

        self.GUIObject = GUI.GUIClass(base=base, mainProgram=self)
        self.GUIObject.tileFrame.frame.show()
        #self.add_task(self.camera_update, 'camera_update')
        self.add_task(self.GUIObject.window_task, 'window_update')


    def camera_update(self, task):
        '''This function is a task run each frame,
           it controls the camera movement/rotation/zoom'''
        # dt is 'delta time' - how much time elapsed since the last time the task ran
        # we will use it to keep the motion independent from the framerate
        dt = globalClock.get_dt()

        #self.GUIObject.fpsCounter.setText('FPS : ' + str(1/dt))
        return task.again





# Do the main initialization and start 3D rendering
demo = ChessboardDemo()
demo.run()