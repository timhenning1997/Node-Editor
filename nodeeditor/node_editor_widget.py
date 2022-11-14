# -*- coding: utf-8 -*-
"""
A module containing ``NodeEditorWidget`` class
"""
import json
import os
import pyclbr
import re
import sys
import pip
from os import listdir
from os.path import isfile, join, abspath

from PyQt5.QtCore import Qt, QPropertyAnimation, QRect, pyqtProperty
from PyQt5.QtGui import QBrush, QPen, QFont, QColor, QIcon, QMouseEvent
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QApplication, QMessageBox, QLabel, QGraphicsItem, QTextEdit, \
    QPushButton, QGraphicsProxyWidget, QMenu, QAction, QLineEdit, QWidgetAction

from nodeeditor.node_scene import Scene, InvalidFile
from nodeeditor.node_node import Node
from nodeeditor.node_edge import Edge, EDGE_TYPE_BEZIER, EDGE_TYPE_DIRECT, EDGE_TYPE_SQUARE
from nodeeditor.node_graphics_view import QDMGraphicsView
from nodeeditor.utils import dumpException
from nodeeditor.utils_no_qt import getNodeEditorDirectory, getStartNodeEditorDirectory


class NodeEditorWidget(QWidget):
    Scene_class = Scene
    GraphicsView_class = QDMGraphicsView

    """The ``NodeEditorWidget`` class"""
    def __init__(self, parent:QWidget=None):
        """
        :param parent: parent widget
        :type parent: ``QWidget``

        :Instance Attributes:

        - **filename** - currently graph's filename or ``None``
        """
        super().__init__(parent)

        self.filename = None

        self.initUI()

    def initUI(self):
        """Set up this ``NodeEditorWidget`` with its layout,  :class:`~nodeeditor.node_scene.Scene` and
        :class:`~nodeeditor.node_graphics_view.QDMGraphicsView`"""
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        # crate graphics scene
        self.scene = self.__class__.Scene_class()

        # create graphics view
        self.view = self.__class__.GraphicsView_class(self.scene.grScene, self)
        self.layout.addWidget(self.view)

    def isModified(self) -> bool:
        """Has the `Scene` been modified?

        :return: ``True`` if the `Scene` has been modified
        :rtype: ``bool``
        """
        return self.scene.isModified()

    def isFilenameSet(self) -> bool:
        """Do we have a graph loaded from file or are we creating a new one?

        :return: ``True`` if filename is set. ``False`` if it is a new graph not yet saved to a file
        :rtype: ''bool''
        """
        return self.filename is not None

    def getSelectedItems(self) -> list:
        """Shortcut returning `Scene`'s currently selected items

        :return: list of ``QGraphicsItems``
        :rtype: list[QGraphicsItem]
        """
        return self.scene.getSelectedItems()

    def hasSelectedItems(self) -> bool:
        """Is there something selected in the :class:`nodeeditor.node_scene.Scene`?

        :return: ``True`` if there is something selected in the `Scene`
        :rtype: ``bool``
        """
        return self.getSelectedItems() != []

    def canUndo(self) -> bool:
        """Can Undo be performed right now?

        :return: ``True`` if we can undo
        :rtype: ``bool``
        """
        return self.scene.history.canUndo()

    def canRedo(self) -> bool:
        """Can Redo be performed right now?

        :return: ``True`` if we can redo
        :rtype: ``bool``
        """
        return self.scene.history.canRedo()

    def getUserFriendlyFilename(self) -> str:
        """Get user friendly filename. Used in the window title

        :return: just a base name of the file or `'New Graph'`
        :rtype: ``str``
        """
        name = os.path.basename(self.filename) if self.isFilenameSet() else "New Graph"
        return name + ("*" if self.isModified() else "")

    def fileNew(self):
        """Empty the scene (create new file)"""
        self.scene.clear()
        self.filename = None
        self.scene.history.clear()

        # set default scene colors like socketColors, edgeColors , evalHighlightColor, ...
        self.scene.initGlobalColors()

        self.scene.history.storeInitialHistoryStamp()

    def fileLoad(self, filename:str):
        """Load serialized graph from JSON file

        :param filename: file to load
        :type filename: ``str``
        """
        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            self.scene.loadFromFile(filename)
            self.filename = filename
            self.scene.history.clear()
            self.scene.history.storeInitialHistoryStamp()
            return True
        except FileNotFoundError as e:
            dumpException(e)
            QMessageBox.warning(self, "Error loading %s" % os.path.basename(filename), str(e).replace('[Errno 2]',''))
            return False
        except InvalidFile as e:
            dumpException(e)
            # QApplication.restoreOverrideCursor()
            QMessageBox.warning(self, "Error loading %s" % os.path.basename(filename), str(e))
            return False
        finally:
            QApplication.restoreOverrideCursor()

    def fileSave(self, filename:str=None, asNodeGroup: bool = False):
        """Save serialized graph to JSON file. When called with an empty parameter, we won't store/remember the filename.

        :param filename: file to store the graph
        :type filename: ``str``
        :param asNodeGroup: if gets stored as node group or as file
        :type filename: ``bool``
        """
        if filename is not None and not asNodeGroup:
            self.filename = filename
        QApplication.setOverrideCursor(Qt.WaitCursor)
        if asNodeGroup:
            self.scene.saveToFileAsNodeGroup(filename)
        else:
            self.scene.saveToFile(self.filename)
        QApplication.restoreOverrideCursor()
        return True

    def contextMenuEvent(self, event):
        try:
            item = self.scene.getItemAt(event.pos())

            if type(item) == QGraphicsProxyWidget:
                item = item.widget()

            if hasattr(item, 'node'):
                try:
                    if item.node.grNode.contextMenuInteractable:
                        self.handleNewNodeContextMenu(event)
                except Exception as e: dumpException(e)
                pass
                # self.handleNodeContextMenu(event)
            elif hasattr(item, 'socket'):
                self.handleSocketContextMenu(event, item)
            elif hasattr(item, 'edge'):
                self.handleEdgeContextMenu(event, item)
            # elif item is None:
            else:
                self.handleNewNodeContextMenu(event)

            return super().contextMenuEvent(event)
        except Exception as e:
            dumpException(e)

    def recursiveDirSearch(self, path, menu: QMenu, mainMenu: QMenu):
        for d in [name for name in os.listdir(path) if os.path.isdir(os.path.join(path, name))]:
            allFiles = []
            for path2, subdirs, files in os.walk(path + "/" + d):
                allFiles += [f for f in files if os.path.splitext(f)[1] in [".py", ".json"]]
            if allFiles:
                tempMenu = QMenu(d, menu)
                menu3 = menu.addMenu(tempMenu)
                menu3.setProperty("menuType", "menu")
                self.recursiveDirSearch(path + "/" + d, tempMenu, mainMenu)

        for file in [f for f in listdir(path) if isfile(join(path, f)) and os.path.splitext(f)[1] in [".py", ".json"]]:
            if file != "__init__.py":
                if os.path.splitext(file)[1] == ".py":
                    action = menu.addAction(file.replace(".py", "").replace("Node_", ""))
                    action.setProperty("menuType", "item")
                    action.setProperty("fileType", "py")
                    action.setProperty("path", path)
                    action.setProperty("fileName", file.replace(".py", ""))
                elif os.path.splitext(file)[1] == ".json":
                    action = menu.addAction(file.replace(".json", "").replace("Node_", "").replace("Nodes_", ""))
                    action.setProperty("menuType", "item")
                    action.setProperty("fileType", "json")
                    action.setProperty("path", path)
                    action.setProperty("fileName", file)
        return menu

    def secondRecursiveDirSearch(self, path, mainMenu: QMenu):
        for d in [name for name in os.listdir(path) if os.path.isdir(os.path.join(path, name))]:
            allFiles = []
            for path2, subdirs, files in os.walk(path + "/" + d):
                allFiles += [f for f in files if os.path.splitext(f)[1] == ".py"]
            if allFiles:
                self.secondRecursiveDirSearch(path + "/" + d, mainMenu)

        section = mainMenu.addSection(path.split("/")[-1])
        section.setProperty("menuType", "section")
        for file in [f for f in listdir(path) if isfile(join(path, f)) and os.path.splitext(f)[1] in [".py", ".json"]]:
            if file != "__init__.py":
                if os.path.splitext(file)[1] == ".py":
                    action2 = mainMenu.addAction(file.replace(".py", "").replace("Node_", ""))
                    action2.setVisible(False)
                    action2.setProperty("menuType", "item")
                    action2.setProperty("fileType", "py")
                    action2.setProperty("itemType", "second")
                    action2.setProperty("path", path)
                    action2.setProperty("fileName", file.replace(".py", ""))
                elif os.path.splitext(file)[1] == ".json":
                    action2 = mainMenu.addAction(file.replace(".json", "").replace("Node_", "").replace("Nodes_", ""))
                    action2.setVisible(False)
                    action2.setProperty("menuType", "item")
                    action2.setProperty("fileType", "json")
                    action2.setProperty("itemType", "second")
                    action2.setProperty("path", path)
                    action2.setProperty("fileName", file)

        return mainMenu

    def initNodesContextMenu(self):
        self.context_menu = QMenu()

        act = self.context_menu.addAction("Add note")
        act.setProperty("menuType", "heading")
        act.setEnabled(False)
        actionFont = QFont()
        actionFont.setUnderline(True)
        act.setFont(actionFont)

        searchLineEdit = QLineEdit()
        searchLineEdit.setMinimumWidth(0)
        searchLineEdit.textChanged.connect(self.menuLineEditTextChanged)
        searchAction = QWidgetAction(self)
        searchAction.setDefaultWidget(searchLineEdit)
        searchAction.setProperty("menuType", "searchLineEdit")
        self.context_menu.addAction(searchAction)
        searchLineEdit.setFocus()

        # @ TODO properly make path out of this next function
        # getNodeEditorDirectory()

        # path = getStartNodeEditorDirectory() + "/nodes"
        # path = "../../nodeeditor/nodes"
        path = "nodeeditor/nodes"

        context_menu = self.recursiveDirSearch(path, self.context_menu, self.context_menu)
        self.secondRecursiveDirSearch(path, self.context_menu)

        return context_menu

    def menuLineEditTextChanged(self, text):
        counter = 1
        tempSection = None
        for action in self.context_menu.actions():
            if action.property("menuType") in ["item", "menu"]:
                if text not in action.text():
                    action.setVisible(False)
                else:
                    action.setVisible(True)
                    counter += 1
            if text == "" and action.property("itemType") == "second":
                action.setVisible(False)
            if action.property("menuType") == "section":
                if tempSection:
                    if counter == 0:
                        tempSection.setVisible(False)
                    else:
                        tempSection.setVisible(True)
                tempSection = action
                counter = 0

    def handleNewNodeContextMenu(self, event):
        context_menu = self.initNodesContextMenu()
        action = context_menu.exec_(self.mapToGlobal(event.pos()))
        if action and action.property("fileType") == "py" and action.property("path") and action.property("fileName"):
            new_node = self.getNodeClassFromPath(action.property("path"), action.property("fileName"))
            if new_node is None:
                print("New node class is None: node_editor_widget | handleNewNodeContextMenu")
                return None
            new_node = new_node(self.scene)
            scene_pos = self.scene.getView().mapToScene(event.pos())
            new_node.setPos(scene_pos.x(), scene_pos.y())
            new_node._path = action.property("path")
            new_node._filename = action.property("fileName")
            self.scene.doDeselectItems()
            new_node.grNode.doSelect(True)
            new_node.grNode.onSelected()
        elif action and action.property("fileType") == "json" and action.property("path") and action.property("fileName"):
            with open(action.property("path") + "/" + action.property("fileName"), "r") as file:
                raw_data = file.read()
                try:
                    if sys.version_info >= (3, 9):
                        data = json.loads(raw_data)
                    else:
                        data = json.loads(raw_data, encoding='utf-8')
                    self.scene.clipboard.deserializeFromClipboard(data)
                    self.scene.has_been_modified = True
                except Exception as e:
                    dumpException(e)

    def handleSocketContextMenu(self, event, socket_item):
        context_menu = QMenu()

        act = context_menu.addAction("Show")
        act.setProperty("type", "show")
        act = context_menu.addAction("Hide")
        act.setProperty("type", "hide")

        action = context_menu.exec_(self.mapToGlobal(event.pos()))

        if action:
            if action.property("type") == "hide":
                for socket in (socket_item.socket.node.inputs+socket_item.socket.node.outputs):
                    socket.grSocket.hiddenStatus = True
            elif action.property("type") == "show":
                for socket in (socket_item.socket.node.inputs + socket_item.socket.node.outputs):
                    socket.grSocket.hiddenStatus = False

    def getNodeClassFromPath(self, path: str, fileName: str):
        noteClass = None

        try:
            keys = list(pyclbr.readmodule(fileName, path=[path]).keys())
            r = re.compile("Node_.*")
            noteClasses = list(filter(r.match, keys))
            if noteClasses:
                noteClass = noteClasses[0]

            if noteClass:
                module = __import__(path.replace(".", "").lstrip("/").replace("/", ".").replace("\\", ".") + "." + fileName, fromlist=[path.replace("/", ".")])
                node_class = getattr(module, noteClass)
                return node_class
        except ImportError:
            print("ImportError")
        except Exception as e:
            dumpException(e)
        return None

    def handleEdgeContextMenu(self, event, edge_item):

        context_menu = QMenu()

        act = context_menu.addAction("Show")
        act.setProperty("type", "show")
        act = context_menu.addAction("Hide")
        act.setProperty("type", "hide")
        act = context_menu.addAction("Lock")
        act.setProperty("type", "lock")
        act = context_menu.addAction("Edit")
        act.setProperty("type", "edit")

        context_menu.addSeparator()
        typeMenu = context_menu.addMenu("Type")
        bezierAct = typeMenu.addAction("Bezier Edge")
        directAct = typeMenu.addAction("Direct Edge")
        squareAct = typeMenu.addAction("Square Edge")

        action = context_menu.exec_(self.mapToGlobal(event.pos()))

        if action:
            if action.property("type") == "hide":
                edge_item.hiddenStatus = True
            elif action.property("type") == "show":
                edge_item.hiddenStatus = False
            elif action.property("type") == "lock":
                edge_item.setLockedStatus(True)
            elif action.property("type") == "edit":
                edge_item.setLockedStatus(False)
            elif action == bezierAct:
                edge_item.edge.edge_type = EDGE_TYPE_BEZIER
            elif action == directAct:
                edge_item.edge.edge_type = EDGE_TYPE_DIRECT
            elif action == squareAct:
                edge_item.edge.edge_type = EDGE_TYPE_SQUARE
