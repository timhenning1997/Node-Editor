import os
import sys
import traceback
from pprint import PrettyPrinter


def dumpException(e=None):
    """
    Prints out an Exception message with a traceback to the console

    :param e: Exception to print out
    :type e: Exception
    """
    # print("%s EXCEPTION:" % e.__class__.__name__, e)
    # traceback.print_tb(e.__traceback__)
    traceback.print_exc()

_path = os.path.abspath(os.getcwd() + "/nodeeditor")
def getStartNodeEditorDirectory():
    return _path


def getNodeEditorDirectory():
    return _path
    return os.path.abspath(os.getcwd() + "/../../nodeeditor")


def suppress_stdout():
    with open(os.devnull, "w") as devnull:
        old_stdout = sys.stdout
        sys.stdout = devnull
        try:
            yield
        finally:
            sys.stdout = old_stdout


def clamp(n, smallest, largest):
    return max(smallest, min(n, largest))


pp = PrettyPrinter(indent=4).pprint
installed_packages = sys.modules.keys()

def isFloat(s: str):
    try:
        float(s)
    except ValueError:
        return False
    return True


def isInt(s: str):
    try:
        int(s)
    except ValueError:
        return False
    return True


def returnFloat(s: str):
    try:
        float(s)
    except ValueError:
        return -1
    return float(s)


def returnInt(s: str):
    try:
        int(s)
    except ValueError:
        return -1
    return int(s)

