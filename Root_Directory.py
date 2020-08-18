import os

def Path(style = None):
    #
    # This function is used to get the path of the project directory. This is useful when files are to be saved/loaded.
    # There is an option to return the path in the unix format.
    #
    path = os.path.dirname(__file__)

    if style == 'unix':
        d, p = path.split(':')
        path = '/' + d.lower() + p.replace('\\', '/')

    return path
