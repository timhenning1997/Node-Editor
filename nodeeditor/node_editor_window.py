# -*- coding: utf-8 -*-
"""
A module containing the Main Window class
"""
import os, json
from PyQt5.QtCore import QSize, QSettings, QPoint, Qt
from PyQt5.QtGui import QColor, QPaintEvent, QPainter, QPen, QKeySequence
from PyQt5.QtWidgets import QMainWindow, QLabel, QAction, QMessageBox, QFileDialog, QApplication, QGraphicsProxyWidget, \
    QMenu, QColorDialog, QShortcut

from nodeeditor.appearance_color_widget import AppearanceColorWindow
from nodeeditor.node_edge import Edge
from nodeeditor.node_editor_widget import NodeEditorWidget
from nodeeditor.utils_no_qt import dumpException

from nodeeditor.node_edge_validators import (
    edge_validator_debug,
    edge_cannot_connect_two_outputs_or_two_inputs,
    edge_cannot_connect_input_and_output_of_same_node,
    edge_cannot_connect_input_and_output_of_different_type,
    edge_cannot_connect_input_and_output_of_different_supported_type
)

# Edge.registerEdgeValidator(edge_validator_debug)
Edge.registerEdgeValidator(edge_cannot_connect_two_outputs_or_two_inputs)
Edge.registerEdgeValidator(edge_cannot_connect_input_and_output_of_same_node)
# Edge.registerEdgeValidator(edge_cannot_connect_input_and_output_of_different_type)
Edge.registerEdgeValidator(edge_cannot_connect_input_and_output_of_different_supported_type)


class NodeEditorWindow(QMainWindow):
    NodeEditorWidget_class = NodeEditorWidget

    """Class representing NodeEditor's Main Window"""
    def __init__(self):
        """
        :Instance Attributes:

        - **name_company** - name of the company, used for permanent profile settings
        - **name_product** - name of this App, used for permanent profile settings
        """
        super().__init__()

        self.name_company = 'Blenderfreak'
        self.name_product = 'NodeEditor'

        self.sceneMousePosX = 0
        self.sceneMousePosY = 0
        self.sceneScale = 100

        self.initUI()

        self.readSettings()

    def paintEvent(self, event: QPaintEvent):
        painter = QPainter(self)
        painter.setOpacity(0.1)
        painter.setBrush(Qt.white)
        painter.setPen(QPen(Qt.white))
        painter.drawRect(self.rect())

    def initUI(self):
        """Set up this ``QMainWindow``. Create :class:`~nodeeditor.node_editor_widget.NodeEditorWidget`, Actions and Menus"""
        self.createActions()
        self.createMenus()
        self.createShortcuts()

        # create node editor widget
        self.nodeeditor = self.__class__.NodeEditorWidget_class(self)
        self.nodeeditor.scene.addHasBeenModifiedListener(self.setTitle)
        self.setCentralWidget(self.nodeeditor)

        self.createStatusBar()

        # set window properties
        # self.setGeometry(200, 200, 800, 600)
        self.setTitle()
        self.show()

    def sizeHint(self):
        return QSize(800, 600)

    def createShortcuts(self):
        self.selAllSc = QShortcut(QKeySequence('Ctrl+A'), self)
        self.selAllSc.activated.connect(self.onSelectAll)

    def createStatusBar(self):
        """Create Status bar and connect to `Graphics View` scenePosChanged event"""
        self.statusBar().showMessage("")
        self.status_bar_label = QLabel("")
        self.statusBar().addPermanentWidget(self.status_bar_label)
        self.nodeeditor.view.scenePosChanged.connect(self.onScenePosChanged)
        self.nodeeditor.view.sceneScaleChanged.connect(self.onSceneScaleChanged)

    def createActions(self):
        """Create basic `File` and `Edit` and `View` actions"""
        self.actNew = QAction('&New', self, shortcut='Ctrl+N', statusTip="Create new graph", triggered=self.onFileNew)
        self.actOpen = QAction('&Open', self, shortcut='Ctrl+O', statusTip="Open file", triggered=self.onFileOpen)
        self.actSave = QAction('&Save', self, shortcut='Ctrl+S', statusTip="Save file", triggered=self.onFileSave)
        self.actSaveAs = QAction('Save &As...', self, shortcut='Ctrl+Shift+S', statusTip="Save file as...", triggered=self.onFileSaveAs)
        self.actSaveAsNodeGroup = QAction('Save As Node &Group', self, shortcut='Ctrl+Shift+G', statusTip="Save all nodes as node group", triggered=self.onFileSaveAsNodeGroup)
        self.actExit = QAction('E&xit', self, shortcut='Ctrl+Q', statusTip="Exit application", triggered=self.close)

        self.actUndo = QAction('&Undo', self, shortcut='Ctrl+Z', statusTip="Undo last operation", triggered=self.onEditUndo)
        self.actRedo = QAction('&Redo', self, shortcut='Ctrl+Shift+Z', statusTip="Redo last operation", triggered=self.onEditRedo)
        self.actCut = QAction('Cu&t', self, shortcut='Ctrl+X', statusTip="Cut to clipboard", triggered=self.onEditCut)
        self.actCopy = QAction('&Copy', self, shortcut='Ctrl+C', statusTip="Copy to clipboard", triggered=self.onEditCopy)
        self.actPaste = QAction('&Paste', self, shortcut='Ctrl+V', statusTip="Paste from clipboard", triggered=self.onEditPaste)
        self.actDelete = QAction('&Delete', self, shortcut='Del', statusTip="Delete selected items", triggered=self.onEditDelete)

        self.actFullScreen = QAction('&FullScreen', self, shortcut='F11', statusTip="Toggle fullscreen mode", triggered=self.onToggleFullScreen)
        self.actAppearance = QAction('&Appearance', self, statusTip="Edit application appearance", triggered=self.onAppearance)
        self.actHideSockets = QAction('Sockets', self, shortcut='Ctrl+H', statusTip="Hide all sockets", triggered=self.onHideSockets)
        self.actShowSockets = QAction('Sockets', self, shortcut='Ctrl+Shift+H', statusTip="Show all sockets", triggered=self.onShowSockets)
        self.actLockNodesAndEdges = QAction('Lock Nodes && Edges', self, statusTip="Lock all nodes and edges", triggered=self.onLockNodesAndEdges)
        self.actEditNodesAndEdges = QAction('Edit Nodes && Edges', self, statusTip="Make all nodes and edges editable", triggered=self.onEditNodesAndEdges)
        self.actHideEvalIcons = QAction('Eval Icons', self, shortcut='Ctrl+I', statusTip="Hide all eval icons", triggered=self.onHideEvalIcons)
        self.actShowEvalIcons = QAction('Eval Icons', self, shortcut='Ctrl+Shift+I', statusTip="Show all eval icons", triggered=self.onShowEvalIcons)
        self.actHideEdges = QAction('Edges', self, shortcut='Ctrl+E', statusTip="Hide all edges", triggered=self.onHideEdges)
        self.actShowEdges = QAction('Edges', self, shortcut='Ctrl+Shift+E', statusTip="Show all edges", triggered=self.onShowEdges)

        self.actSnapToGrid = QAction('Snap To &Grid', self, statusTip="Toggles node snapping to grid", triggered=self.onSnapToGrid, checkable=True)
        self.actSnapToGridSquare = QAction('Snan To Grid &Square', self, statusTip="Toggles node snapping to grid squares", triggered=self.onSnapToGridSquare, checkable=True)

    def createMenus(self):
        """Create Menus for `File` and `Edit`"""
        self.createFileMenu()
        self.createEditMenu()
        self.createViewMenu()
        self.createToolsMenu()

    def createFileMenu(self):
        menubar = self.menuBar()
        self.fileMenu = menubar.addMenu('&File')
        self.fileMenu.addAction(self.actNew)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.actOpen)
        self.fileMenu.addAction(self.actSave)
        self.fileMenu.addAction(self.actSaveAs)
        self.fileMenu.addAction(self.actSaveAsNodeGroup)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.actExit)

    def createEditMenu(self):
        menubar = self.menuBar()
        self.editMenu = menubar.addMenu('&Edit')
        self.editMenu.addAction(self.actUndo)
        self.editMenu.addAction(self.actRedo)
        self.editMenu.addSeparator()
        self.editMenu.addAction(self.actCut)
        self.editMenu.addAction(self.actCopy)
        self.editMenu.addAction(self.actPaste)
        self.editMenu.addSeparator()
        self.editMenu.addAction(self.actDelete)

    def createViewMenu(self):
        menubar = self.menuBar()
        self.viewMenu = menubar.addMenu('&View')
        self.viewMenu.addAction(self.actFullScreen)
        self.viewMenu.addAction(self.actAppearance)

        self.viewMenu.addSeparator()
        self.viewShowMenu = self.viewMenu.addMenu("Show")
        self.viewShowMenu.addAction(self.actShowSockets)
        self.viewShowMenu.addAction(self.actShowEdges)
        self.viewShowMenu.addAction(self.actShowEvalIcons)

        self.viewHideMenu = self.viewMenu.addMenu("Hide")
        self.viewHideMenu.addAction(self.actHideSockets)
        self.viewHideMenu.addAction(self.actHideEdges)
        self.viewHideMenu.addAction(self.actHideEvalIcons)

        self.viewMenu.addSeparator()
        self.viewMenu.addAction(self.actLockNodesAndEdges)
        self.viewMenu.addAction(self.actEditNodesAndEdges)

    def createToolsMenu(self):
        menubar = self.menuBar()
        self.toolsMenu = menubar.addMenu('&Tools')
        self.toolsMenu.addAction(self.actSnapToGrid)
        self.toolsMenu.addAction(self.actSnapToGridSquare)

    def setTitle(self):
        """Function responsible for setting window title"""
        title = "Node Editor - "
        title += self.getCurrentNodeEditorWidget().getUserFriendlyFilename()

        self.setWindowTitle(title)


    def closeEvent(self, event):
        """Handle close event. Ask before we loose work"""
        if self.maybeSave():
            self.writeSettings()
            for node in self.nodeeditor.scene.nodes:
                if node.content:
                    node.content.removeContent()
            event.accept()
        else:
            event.ignore()

    def isModified(self) -> bool:
        """Has current :class:`~nodeeditor.node_scene.Scene` been modified?

        :return: ``True`` if current :class:`~nodeeditor.node_scene.Scene` has been modified
        :rtype: ``bool``
        """
        nodeeditor = self.getCurrentNodeEditorWidget()
        return nodeeditor.scene.isModified() if nodeeditor else False

    def getCurrentNodeEditorWidget(self) -> NodeEditorWidget:
        """get current :class:`~nodeeditor.node_editor_widget`

        :return: get current :class:`~nodeeditor.node_editor_widget`
        :rtype: :class:`~nodeeditor.node_editor_widget`
        """
        return self.centralWidget()

    def maybeSave(self) -> bool:
        """If current `Scene` is modified, ask a dialog to save the changes. Used before
        closing window / mdi child document

        :return: ``True`` if we can continue in the `Close Event` and shutdown. ``False`` if we should cancel
        :rtype: ``bool``
        """
        if not self.isModified():
            return True

        res = QMessageBox.warning(self, "About to loose your work?",
                "The document has been modified.\n Do you want to save your changes?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
              )

        if res == QMessageBox.Save:
            return self.onFileSave()
        elif res == QMessageBox.Cancel:
            return False

        return True


    def onScenePosChanged(self, x:int, y:int):
        """Handle event when cursor position changed on the `Scene`

        :param x: new cursor x position
        :type x:
        :param y: new cursor y position
        :type y:
        """
        self.sceneMousePosX = x
        self.sceneMousePosY = y
        self.status_bar_label.setText("Zoom: [%d%%]  " % (self.sceneScale) + "Scene Pos: [%d, %d]" % (self.sceneMousePosX, self.sceneMousePosY))

    def onSceneScaleChanged(self, scale:float):
        """Handle event when scale changed on the `Scene`

        :param scale: new scene scale
        :type scale:
        """
        zoom = int(self.nodeeditor.scene.getView().zoom - 10)
        faktor = self.nodeeditor.scene.getView().zoomInFactor
        self.sceneScale = int(float(faktor)**zoom * 100)
        self.status_bar_label.setText("Zoom: [%d%%]  " % (self.sceneScale) + "Scene Pos: [%d, %d]" % (self.sceneMousePosX, self.sceneMousePosY))

    def getFileDialogDirectory(self):
        """Returns starting directory for ``QFileDialog`` file open/save"""
        return ''

    def getFileDialogFilter(self):
        """Returns ``str`` standard file open/save filter for ``QFileDialog``"""
        return 'Graph (*.json);;All files (*)'

    def onFileNew(self):
        """Hande File New operation"""
        if self.maybeSave():
            self.getCurrentNodeEditorWidget().fileNew()
            self.setTitle()


    def onFileOpen(self):
        """Handle File Open operation"""

        if self.maybeSave():
            fname, filter = QFileDialog.getOpenFileName(self, 'Open graph from file', self.getFileDialogDirectory(), self.getFileDialogFilter(), "", QFileDialog.DontUseNativeDialog)
            if fname != '' and os.path.isfile(fname):
                self.getCurrentNodeEditorWidget().fileLoad(fname)
                self.setTitle()

    def onFileSave(self):
        """Handle File Save operation"""
        current_nodeeditor = self.getCurrentNodeEditorWidget()
        if current_nodeeditor is not None:
            if not current_nodeeditor.isFilenameSet(): return self.onFileSaveAs()

            current_nodeeditor.fileSave()
            self.statusBar().showMessage("Successfully saved %s" % current_nodeeditor.filename, 5000)

            # support for MDI app
            if hasattr(current_nodeeditor, "setTitle"): current_nodeeditor.setTitle()
            else: self.setTitle()
            return True

    def onFileSaveAs(self):
        """Handle File Save As operation"""
        current_nodeeditor = self.getCurrentNodeEditorWidget()
        if current_nodeeditor is not None:
            fname, filter = QFileDialog.getSaveFileName(self, 'Save graph to file', self.getFileDialogDirectory(), self.getFileDialogFilter(), "", QFileDialog.DontUseNativeDialog)
            if fname == '': return False

            self.onBeforeSaveAs(current_nodeeditor, fname)
            current_nodeeditor.fileSave(fname)
            self.statusBar().showMessage("Successfully saved as %s" % current_nodeeditor.filename, 5000)

            # support for MDI app
            if hasattr(current_nodeeditor, "setTitle"): current_nodeeditor.setTitle()
            else: self.setTitle()
            return True

    def onFileSaveAsNodeGroup(self):
        current_nodeeditor = self.getCurrentNodeEditorWidget()
        if current_nodeeditor is not None:
            path = os.path.dirname(os.path.abspath(__file__)) + "/nodes"
            fname, filter = QFileDialog.getSaveFileName(self, 'Save selected nodes as node group', path, "NodeGroup (*.json)", "", QFileDialog.DontUseNativeDialog)
            if fname == '': return False

            fname = fname.split(".")[0] + ".json"
            current_nodeeditor.fileSave(fname, asNodeGroup=True)
            self.statusBar().showMessage("Successfully saved nodeGroup as %s" % fname, 5000)

    def onBeforeSaveAs(self, current_nodeeditor: 'NodeEditorWidget', filename: str):
        """
        Event triggered after choosing filename and before actual fileSave(). We are passing current_nodeeditor because
        we will loose focus after asking with QFileDialog and therefore getCurrentNodeEditorWidget will return None
        """
        pass

    def onEditUndo(self):
        """Handle Edit Undo operation"""
        if self.getCurrentNodeEditorWidget():
            self.getCurrentNodeEditorWidget().scene.history.undo()

    def onEditRedo(self):
        """Handle Edit Redo operation"""
        if self.getCurrentNodeEditorWidget():
            self.getCurrentNodeEditorWidget().scene.history.redo()

    def onEditDelete(self):
        """Handle Delete Selected operation"""
        if self.getCurrentNodeEditorWidget():
            self.getCurrentNodeEditorWidget().scene.getView().deleteSelected()

    def onEditCut(self):
        """Handle Edit Cut to clipboard operation"""
        if self.getCurrentNodeEditorWidget():
            data = self.getCurrentNodeEditorWidget().scene.clipboard.serializeSelected(delete=True)
            str_data = json.dumps(data, indent=4)
            QApplication.instance().clipboard().setText(str_data)

    def onEditCopy(self):
        """Handle Edit Copy to clipboard operation"""
        if self.getCurrentNodeEditorWidget():
            data = self.getCurrentNodeEditorWidget().scene.clipboard.serializeSelected(delete=False)
            str_data = json.dumps(data, indent=4)
            QApplication.instance().clipboard().setText(str_data)

    def onEditPaste(self):
        """Handle Edit Paste from clipboard operation"""
        if self.getCurrentNodeEditorWidget():
            raw_data = QApplication.instance().clipboard().text()

            try:
                data = json.loads(raw_data)
            except ValueError as e:
                print("Pasting of not valid json data!", e)
                return

            # check if the json data are correct
            if 'nodes' not in data:
                print("JSON does not contain any nodes!")
                return

            return self.getCurrentNodeEditorWidget().scene.clipboard.deserializeFromClipboard(data)

    def onToggleFullScreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def onAppearance(self):
        self.appearanceWindow = AppearanceColorWindow(self.nodeeditor.scene.socketColors,
                                                      self.nodeeditor.scene.edgeColor,
                                                      self.nodeeditor.scene.evalHighlightColor)
        self.appearanceWindow.edgeColorFromSocketCB.setChecked(self.nodeeditor.scene.isGetEdgeColorFromSocket)
        self.appearanceWindow.okButton.clicked.connect(self.getAppearanceSettingsAndClose)
        self.appearanceWindow.applyButton.clicked.connect(self.getAppearanceSettings)

    def getAppearanceSettingsAndClose(self):
        self.getAppearanceSettings()
        self.appearanceWindow.close()

    def getAppearanceSettings(self):
        for i in range(len(self.nodeeditor.scene.socketColors)):
            self.nodeeditor.scene.socketColors[i] = self.appearanceWindow.socketColorButtons[i].color
        self.nodeeditor.scene.updateSocketColors()
        self.nodeeditor.scene.edgeColor = self.appearanceWindow.edgeColorButton.color
        self.nodeeditor.scene.isGetEdgeColorFromSocket = self.appearanceWindow.edgeColorFromSocketCB.isChecked()
        self.nodeeditor.scene.updateEdgeColors()
        self.nodeeditor.scene.evalHighlightColor = self.appearanceWindow.evalHighlightColorButton.color
        self.nodeeditor.scene.updateEvalHighlightColors()

    def onHideSockets(self):
        self.changeSocketVisibility(True)

    def onShowSockets(self):
        self.changeSocketVisibility(False)

    def onLockNodesAndEdges(self):
        self.changeNodesLockStatus(True)
        self.changeEdgesLockStatus(True)

    def onEditNodesAndEdges(self):
        self.changeNodesLockStatus(False)
        self.changeEdgesLockStatus(False)

    def changeNodesLockStatus(self, value: bool):
        for node in self.nodeeditor.scene.nodes:
            node.grNode.setLockedStatus(value)
        self.nodeeditor.view.update()

    def changeEdgesLockStatus(self, value: bool):
        for node in self.nodeeditor.scene.nodes:
            for socket in node.inputs + node.outputs:
                for edge in socket.edges:
                    edge.grEdge.setLockedStatus(value)
        self.nodeeditor.view.update()

    def changeSocketVisibility(self, value: bool):
        sockets = []
        for node in self.nodeeditor.scene.nodes:
            for socket in node.inputs + node.outputs:
                sockets.append(socket)
        for socket in sockets:
            socket.grSocket.hiddenStatus = value
        self.nodeeditor.view.update()

    def onHideEvalIcons(self):
        self.changeEvalIconVisibility(False)

    def onShowEvalIcons(self):
        self.changeEvalIconVisibility(True)

    def changeEvalIconVisibility(self, value: bool):
        for node in self.nodeeditor.scene.nodes:
            node.grNode.evaluationIconVisibility = value
        self.nodeeditor.view.update()

    def onHideEdges(self):
        self.changeEdgeVisibility(True)

    def onShowEdges(self):
        self.changeEdgeVisibility(False)

    def onSnapToGrid(self):
        if self.actSnapToGrid.isChecked():
            self.actSnapToGridSquare.setChecked(False)
            self.nodeeditor.scene.grScene.isSnappingToGrid = True
        else:
            self.nodeeditor.scene.grScene.isSnappingToGrid = False
        self.nodeeditor.scene.grScene.isSnappingToGridSquares = False

    def onSnapToGridSquare(self):
        if self.actSnapToGridSquare.isChecked():
            self.actSnapToGrid.setChecked(False)
            self.nodeeditor.scene.grScene.isSnappingToGridSquares = True
        else:
            self.nodeeditor.scene.grScene.isSnappingToGridSquares = False
        self.nodeeditor.scene.grScene.isSnappingToGrid = False

    def onSelectAll(self):
        if self.getCurrentNodeEditorWidget():
            self.getCurrentNodeEditorWidget().scene.doSelectAllItems()


    def changeEdgeVisibility(self, value: bool):
        for node in self.nodeeditor.scene.nodes:
            for socket in (node.inputs+node.outputs):
                for edge in socket.edges:
                    edge.grEdge.hiddenStatus = value
        self.nodeeditor.view.update()

    def readSettings(self):
        """Read the permanent profile settings for this app"""
        settings = QSettings(self.name_company, self.name_product)
        if settings.value('maximized') == "true":
            self.showMaximized()
        else:
            self.move(settings.value('pos', QPoint(200, 200)))
            self.resize(settings.value('size', QSize(400, 400)))
        if settings.value('lastFilename'):
            self.getCurrentNodeEditorWidget().fileLoad(settings.value('lastFilename'))
            self.setTitle()

    def writeSettings(self):
        """Write the permanent profile settings for this app"""
        settings = QSettings(self.name_company, self.name_product)
        settings.setValue('pos', self.pos())
        settings.setValue('maximized', self.isMaximized())
        settings.setValue('size', self.size())
        settings.setValue('lastFilename', self.getCurrentNodeEditorWidget().filename)
