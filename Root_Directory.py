import os
import System_Information

def Path(style = None):
    #
    # This function is used to get the path of the project directory. This is useful when files are to be saved/loaded.
    # There is an option to return the path in the unix format.
    #
    path = os.path.dirname(__file__)

    if System_Information.OPERATING_SYSTEM == 'unix':
        return path
    else:
        if style == 'unix':
            d, p = path.split(':')
            path = '/' + d.lower() + p.replace('\\', '/')

    return path
