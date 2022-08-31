import contextlib
import os
from collections import OrderedDict
from pathlib import Path

import dxcam
import numpy as np

from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QPoint
from PyQt5.QtGui import QPixmap, QResizeEvent, QMouseEvent, QImage, QPaintEvent, QPainter, QPen
from PyQt5.QtWidgets import QPushButton, QLabel, QSizePolicy, QVBoxLayout, QSpinBox, QCheckBox, QAbstractSpinBox, \
    QWidget, QMainWindow, QHBoxLayout
from nodeeditor.Abstract_Node import Abstract_Node
from nodeeditor.node_content_widget import QDMNodeContentWidget
from nodeeditor.node_graphics_node import QDMGraphicsNode
from nodeeditor.utils_no_qt import dumpException, suppress_stdout
from nodeeditor.var_type_conf import *


class ClickableLable(QLabel):
    rightMouseButtonclicked = pyqtSignal()

    def __init__(self):
        super().__init__()

    def mousePressEvent(self, event: QMouseEvent):
        super().mousePressEvent(event)
        if event.button() == Qt.RightButton:
            self.rightMouseButtonclicked.emit()


class TransparentWindow(QWidget):
    changeGeometry = pyqtSignal(int, int, int, int)

    def __init__(self):
        super().__init__()

        self.setWindowFlags(Qt.WindowStaysOnTopHint |
                            Qt.Window |
                            Qt.FramelessWindowHint |
                            # Qt.WindowTransparentForInput |
                            Qt.WindowDoesNotAcceptFocus)

        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)

        self.resizeFlag = False
        self.moveFlag = False

        self.oldMousePos = QPoint(0, 0)
        self.mouseOffset = QPoint(0, 0)
        self.oldSize = QPoint(self.width(), self.height())


        # self.setStyleSheet("#overlayWindow {background-color: transparent}")
        # self.setWindowFlag(Qt.FramelessWindowHint)
        # self.setObjectName("overlayWindow")
        # self.setWindowOpacity(0.2)
        # self.setAutoFillBackground(False)
        # self.setAttribute(Qt.WA_AlwaysStackOnTop, True)
        # self.setAttribute(Qt.WA_NoSystemBackground, True)
        # self.setAttribute(Qt.WA_TranslucentBackground, True)
        # self.setAttribute(Qt.WA_OpaquePaintEvent, True)
        # self.setAttribute(Qt.WA_NoSystemBackground, True)
        # self.setAttribute(Qt.WA_PaintOnScreen)
        # self.setAttribute(Qt.WA_TransparentForMouseEvents)
        # self.setStyleSheet("#overlayWindow {background-color: transparent}")

    def mousePressEvent(self, event: QMouseEvent):
        self.mouseOffset = event.pos()
        self.oldMousePos = self.mapToGlobal(event.pos())
        self.oldSize = QPoint(self.width(), self.height())
        if event.pos().x() > self.width()-10 and event.pos().y() > self.height()-10:
            self.resizeFlag = True

        if event.pos().x() < 10 and event.pos().y() < 10:
            self.moveFlag = True

    def mouseReleaseEvent(self, event: QMouseEvent):
        self.resizeFlag = False
        self.moveFlag = False

    def mouseMoveEvent(self, event: QMouseEvent):
        if not self.moveFlag and not self.resizeFlag:
            return
        if self.moveFlag:
            if self.width() > 20 or self.height() > 20:
                moveTo = self.mapToGlobal(event.pos()) - self.mouseOffset
                self.move(moveTo)
            else:
                self.moveFlag = False
        if self.resizeFlag:
            resizeTo = self.mapToGlobal(event.pos()) - self.oldMousePos + self.oldSize
            if resizeTo.x() < 10: resizeTo.setX(10)
            if resizeTo.y() < 10: resizeTo.setY(10)
            self.setFixedSize(resizeTo.x(), resizeTo.y())

        self.changeGeometry.emit(self.x(), self.y(), self.width(), self.height())

    def paintEvent(self, event: QPaintEvent):
        painter = QPainter(self)
        painter.setOpacity(0.5)
        painter.setBrush(Qt.transparent)

        pen = QPen(Qt.red)
        pen.setWidth(5)
        painter.setPen(pen)
        painter.drawRect(self.rect())

        painter.setOpacity(0.8)
        painter.setPen(Qt.transparent)
        painter.setBrush(Qt.black)
        painter.drawRect(self.rect().width() - 10, self.rect().height() - 10, self.rect().width(), self.rect().height())

        painter.setOpacity(0.1)
        painter.setPen(Qt.transparent)
        painter.setBrush(Qt.black)
        painter.drawRect(0, 0, 10, 10)
        painter.setOpacity(0.8)
        painter.drawEllipse(0, 0, 10, 10)

        return super().paintEvent(event)


class Content(QDMNodeContentWidget):
    def initUI(self):
        self.capture_x = -1
        self.capture_y = -1
        self.capture_x2 = -1
        self.capture_y2 = -1

        self.transparentWindowInteraction = False

        self.pixmapIsShown = True
        self.pixmap = None
        self.shot = None
        with contextlib.redirect_stdout(None):
            self.camera = dxcam.create()

        self.overlayWindow = TransparentWindow()
        self.overlayWindow.setGeometry(0, 0, self.camera.width, self.camera.height)
        self.overlayWindow.changeGeometry.connect(self.changeCaptureRegionViaTransparentWindow)

        self.showOverlayWindowCB = QCheckBox("Show Overlay")
        self.showOverlayWindowCB.setChecked(False)
        self.showOverlayWindowCB.stateChanged.connect(self.changeOverlayVisibility)

        self.showPreviewCB = QCheckBox("Show Preview")
        self.showPreviewCB.setChecked(True)
        self.showPreviewCB.stateChanged.connect(self.changePreviewVisibility)

        self.captureButton = QPushButton("Single Capture")
        self.captureButton.clicked.connect(self.loadImage)

        self.captureRegionLabel = QLabel("[x1|y1|x2|y2]")

        self.captureX1SpinBox = QSpinBox()
        self.captureX1SpinBox.setFixedWidth(40)
        self.captureX1SpinBox.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.captureX1SpinBox.setRange(0, self.camera.width - 1)
        self.captureX1SpinBox.setValue(0)
        self.captureX1SpinBox.valueChanged.connect(self.changeCaptureRegion)
        self.captureY1SpinBox = QSpinBox()
        self.captureY1SpinBox.setFixedWidth(40)
        self.captureY1SpinBox.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.captureY1SpinBox.setRange(0, self.camera.height - 1)
        self.captureY1SpinBox.setValue(0)
        self.captureY1SpinBox.valueChanged.connect(self.changeCaptureRegion)
        self.captureX2SpinBox = QSpinBox()
        self.captureX2SpinBox.setFixedWidth(40)
        self.captureX2SpinBox.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.captureX2SpinBox.setRange(1, self.camera.width)
        self.captureX2SpinBox.setValue(self.camera.width)
        self.captureX2SpinBox.valueChanged.connect(self.changeCaptureRegion)
        self.captureY2SpinBox = QSpinBox()
        self.captureY2SpinBox.setFixedWidth(40)
        self.captureY2SpinBox.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.captureY2SpinBox.setRange(1, self.camera.height)
        self.captureY2SpinBox.setValue(self.camera.height)
        self.captureY2SpinBox.valueChanged.connect(self.changeCaptureRegion)

        self.intervalSpinBox = QSpinBox()
        self.intervalSpinBox.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.intervalSpinBox.setRange(33, 1000000)
        self.intervalSpinBox.setValue(100)
        self.intervalSpinBox.setSuffix(" ms")
        self.intervalSpinBox.valueChanged.connect(self.changeInterval)

        self.continuousCaptureCB = QCheckBox("Continuous Capture")
        self.continuousCaptureCB.setChecked(False)
        self.continuousCaptureCB.stateChanged.connect(self.changeContinuousCapture)

        self.label = QLabel()
        self.label.setFrameStyle(1)
        self.label.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding))
        self.setLabelPixmap()
        self.label.setAlignment(Qt.AlignCenter)

        self.timer = QTimer()
        self.timer.timeout.connect(self.loadImage)
        self.timer.setInterval(self.intervalSpinBox.value())

        layoutH1 = QHBoxLayout()
        layoutH1.setContentsMargins(0, 0, 0, 0)
        layoutH1.addWidget(self.captureButton)
        layoutH1.addWidget(self.continuousCaptureCB)

        layoutH2 = QHBoxLayout()
        layoutH2.setContentsMargins(0, 0, 0, 0)
        layoutH2.addWidget(self.captureRegionLabel)
        layoutH2.addWidget(self.captureX1SpinBox)
        layoutH2.addWidget(self.captureY1SpinBox)
        layoutH2.addWidget(self.captureX2SpinBox)
        layoutH2.addWidget(self.captureY2SpinBox)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(layoutH1)
        layout.addWidget(self.intervalSpinBox)
        layout.addLayout(layoutH2)
        layout.addWidget(self.showOverlayWindowCB)
        layout.addWidget(self.showPreviewCB)
        layout.addWidget(self.label)
        self.setLayout(layout)

    def removeContent(self):
        del self.camera
        self.overlayWindow.deleteLater()
        self.overlayWindow = None

    def showNode(self):
        super().showNode()
        self.intervalSpinBox.show()
        self.captureRegionLabel.show()
        self.captureX1SpinBox.show()
        self.captureY1SpinBox.show()
        self.captureX2SpinBox.show()
        self.captureY2SpinBox.show()
        self.showOverlayWindowCB.show()
        self.changeOverlayVisibility(self.showOverlayWindowCB.isChecked())
        self.showPreviewCB.show()
        self.pixmapIsShown = self.showPreviewCB.isChecked()

    def hideNode(self):
        super().hideNode()
        self.intervalSpinBox.hide()
        self.captureRegionLabel.hide()
        self.captureX1SpinBox.hide()
        self.captureY1SpinBox.hide()
        self.captureX2SpinBox.hide()
        self.captureY2SpinBox.hide()
        self.showOverlayWindowCB.hide()
        self.changeOverlayVisibility(False)
        self.showPreviewCB.hide()
        self.pixmapIsShown = False

    def resizeEvent(self, event: QResizeEvent):
        if self.pixmapIsShown:
            self.setLabelPixmap()

    def sendData(self):
        if self.node.isChildrenAtSocket(0):
            self.node.sendDataFromSocket(self.pixmap, 0)
        if self.node.isChildrenAtSocket(1):
            self.node.sendDataFromSocket(self.shot, 1)

    def loadImage(self):
        """with mss.mss() as sct:
            monitor = {"top": self.capture_x, "left": self.capture_y, "width": self.capture_w, "height": self.capture_h}
            grab = sct.grab(monitor)
            img_array = np.array(grab)
            image = QImage(img_array, img_array.shape[1], img_array.shape[0], img_array.shape[1] * 4, QImage.Format_RGBA8888)
            self.pixmap = QPixmap(image)
            self.setLabelPixmap()"""

        """print("x", self.capture_x, "y", self.capture_y, "w", self.capture_w, "h", self.capture_h)
        self.pixmap = self.screen.grabWindow(self.capture_x, self.capture_y, self.capture_w, self.capture_h)
        print(self.pixmap.size())
        self.setLabelPixmap()"""
        if not hasattr(self, "camera"):
            return

        if self.capture_x == -1:
            self.shot = self.camera.grab()
        else:
            self.shot = self.camera.grab(region=(self.capture_x, self.capture_y, self.capture_x2, self.capture_y2))
        try:
            if not self.shot:
                return
        except:
            pass
        self.shot = np.require(self.shot, np.uint8, 'C')
        self.pixmap = QPixmap(QImage(self.shot, len(self.shot[0]), len(self.shot), len(self.shot[0]) * 3, QImage.Format_RGB888))

        if self.pixmapIsShown:
            self.setLabelPixmap()
        self.sendData()

    def setLabelPixmap(self):
        if self.pixmap:
            self.label.setPixmap(self.pixmap.scaled(self.label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def changeInterval(self):
        self.timer.setInterval(self.intervalSpinBox.value())

    def changeContinuousCapture(self, value: bool):
        if value:
            self.timer.start()
        else:
            self.timer.stop()

    def changeCaptureRegionViaTransparentWindow(self, x, y, w, h):
        self.capture_x = x
        self.capture_y = y
        self.capture_x2 = x + w
        self.capture_y2 = y + h

        self.captureX1SpinBox.setValue(self.capture_x)
        self.captureY1SpinBox.setValue(self.capture_y)
        self.captureX2SpinBox.setMinimum(self.capture_x + 1)
        self.captureY2SpinBox.setMinimum(self.capture_y + 1)
        self.captureX2SpinBox.setValue(self.capture_x2)
        self.captureY2SpinBox.setValue(self.capture_y2)

    def changeOverlayVisibility(self, value: bool):
        if value:
            self.overlayWindow.show()
        else:
            self.overlayWindow.hide()

    def changePreviewVisibility(self, value: bool):
        if value:
            self.pixmapIsShown = True
        else:
            self.pixmapIsShown = False
            self.label.setPixmap(QPixmap().scaled(self.label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def changeCaptureRegion(self):
        if not self.overlayWindow.resizeFlag and not self.overlayWindow.moveFlag:
            self.capture_x = self.captureX1SpinBox.value()
            self.capture_y = self.captureY1SpinBox.value()
            self.captureX2SpinBox.setMinimum(self.capture_x + 1)
            self.captureY2SpinBox.setMinimum(self.capture_y + 1)
            self.capture_x2 = self.captureX2SpinBox.value()
            self.capture_y2 = self.captureY2SpinBox.value()
            self.overlayWindow.move(self.capture_x, self.capture_y)
            self.overlayWindow.setFixedSize(self.capture_x2 - self.capture_x, self.capture_y2 - self.capture_y)


class GraphicsNode(QDMGraphicsNode):
    def initSizes(self):
        super().initSizes()
        self.setShownSize(270, 319)  # -34
        self.setHiddenSize(270, 185)
        self.setClosedSize(30, 30)

        self.hidden_edge_padding = 5
        self.hidden_title_height = 0

        self.setShowAndHiddenSameSize = True


class Node_ScreenCaptureDXcamNode(Abstract_Node):
    def __init__(self, scene: 'Scene', title: str = "Screen Capture DXcam", inputs: list = [],
                 outputs: list = [VAR_TYPE_PIXMAP, VAR_TYPE_LIST]):
        super().__init__(scene, title, inputs, outputs)

    def initInnerClasses(self):
        self.content = Content(self)
        self.grNode = GraphicsNode(self)

    def initSettings(self):
        super().initSettings()
        self.output_socket_position = RIGHT_CENTER
