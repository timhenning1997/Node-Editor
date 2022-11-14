# -*- encoding: utf-8 -*-
"""
Module with some helper functions
"""
import sys
import subprocess
import pkg_resources

from PyQt5.QtCore import QFile
from PyQt5.QtWidgets import QApplication, QMessageBox

from nodeeditor.utils_no_qt import pp, dumpException

def checkForRequiredModules(*requiredModules):
    requiredList = []
    for modules in requiredModules:
        requiredList.append(modules)

    required = set(requiredList)
    installed = {pkg.key for pkg in pkg_resources.working_set}
    missing = required - installed

    if missing:
        print("installed: ", installed)
        print("missing: ", missing)
        try:
            ret = QMessageBox.question(None,
                                       'Missing modules',
                                       "Some modules are missing. \n\nModules:\n" + ', '.join(missing) + "\n\nDo you want to install them now?",
                                       QMessageBox.Yes | QMessageBox.No)
            if ret == QMessageBox.No:
                return False

            python = sys.executable
            subprocess.check_call([python, '-m', 'pip', 'install', *missing], stdout=subprocess.DEVNULL)
            QMessageBox.information(None, 'Modules installed', "Modules:\n" ', '.join(missing) + "\n\n sucessfully installed.", QMessageBox.Ok)
        except Exception as e:
            print(e)
            return False

    return True


def loadStylesheet(filename: str):
    """
    Loads an qss stylesheet to the current QApplication instance

    :param filename: Filename of qss stylesheet
    :type filename: str
    """
    print('STYLE loading:', filename)
    file = QFile(filename)
    file.open(QFile.ReadOnly | QFile.Text)
    stylesheet = file.readAll()
    QApplication.instance().setStyleSheet(str(stylesheet, encoding='utf-8'))

def loadStylesheets(*args):
    """
    Loads multiple qss stylesheets. Concatenates them together and applies the final stylesheet to the current QApplication instance

    :param args: variable number of filenames of qss stylesheets
    :type args: str, str,...
    """
    res = ''
    for arg in args:
        file = QFile(arg)
        file.open(QFile.ReadOnly | QFile.Text)
        stylesheet = file.readAll()
        res += "\n" + str(stylesheet, encoding='utf-8')
    QApplication.instance().setStyleSheet(res)
