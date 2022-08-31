from collections import OrderedDict

import cv2
import numpy as np
from PyQt5.QtCore import Qt

from PyQt5.QtWidgets import QLabel, QGridLayout, QSlider
from nodeeditor.Abstract_Node import Abstract_Node
from nodeeditor.color_button import ColorButton
from nodeeditor.node_content_widget import QDMNodeContentWidget
from nodeeditor.node_graphics_node import QDMGraphicsNode
from nodeeditor.utils_no_qt import clamp
from nodeeditor.var_type_conf import *



class Content(QDMNodeContentWidget):
    def initUI(self):
        label1 = QLabel("mask color low")
        label2 = QLabel("Threshold")

        self.colorButton = ColorButton(QColor(Qt.white))
        self.colorButton.newColor.connect(self.changeColor)

        self.thresholdSlider = QSlider(Qt.Horizontal)
        self.thresholdSlider.setRange(0, 90)
        self.thresholdSlider.setValue(10)
        self.thresholdSlider.valueChanged.connect(self.changeThreshold)

        self.thresholdColor = QColor(Qt.white)
        self.threshold = 0

        layout = QGridLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(label1, 0, 0)
        layout.addWidget(self.colorButton, 0, 1)
        layout.addWidget(label2, 1, 0)
        layout.addWidget(self.thresholdSlider, 1, 1)
        self.setLayout(layout)

    def changeColor(self, color: QColor):
        self.thresholdColor = color

    def changeThreshold(self):
        self.threshold = self.thresholdSlider.value()

    def serialize(self) -> OrderedDict:
        orderedDict = super().serialize()
        orderedDict["thresholdColor"] = self.thresholdColor.name(QColor.HexArgb)
        return orderedDict

    def deserialize(self, data: dict, hashmap: dict = {}, restore_id: bool = True) -> bool:
        super().deserialize(data, hashmap, restore_id)
        self.colorButton.setColor(QColor(data["thresholdColor"]))
        return True


class GraphicsNode(QDMGraphicsNode):
    def initSizes(self):
        super().initSizes()
        self.setShownSize(190, 114)
        self.setHiddenSize(190, 80)
        self.setClosedSize(30, 30)

        self.hidden_edge_padding = 5
        self.hidden_title_height = 0

        self.setShowAndHiddenSameSize = True


class Node_ImageOpenCVColorFilter(Abstract_Node):
    def __init__(self, scene: 'Scene', title: str = "OpenCV Color Filter", inputs: list = [VAR_TYPE_LIST], outputs: list = [VAR_TYPE_LIST]):
        super().__init__(scene, title, inputs, outputs)

    def initInnerClasses(self):
        self.content = Content(self)
        self.grNode = GraphicsNode(self)

    def initSettings(self):
        super().initSettings()
        self.output_socket_position = RIGHT_CENTER
        self.input_socket_position = LEFT_CENTER

    def receiveData(self, data, inputSocketIndex):
        super().receiveData(data, inputSocketIndex)

        hsv = cv2.cvtColor(data, cv2.COLOR_RGB2HSV)
        h = self.content.thresholdColor.hsvHue() // 2
        t = self.content.threshold

        sLow = clamp(self.content.thresholdColor.hsvSaturation()-100, 0, 255)
        sHigh = clamp(self.content.thresholdColor.hsvSaturation() + 100, 0, 255)
        vLow = clamp(self.content.thresholdColor.value() - 100, 0, 255)
        vHigh = clamp(self.content.thresholdColor.value() + 100, 0, 255)

        mask1 = mask2 = None
        if h-t < 0:
            lower_filter = np.array([180+(h-t), sLow, vLow])
            upper_filter = np.array([180, sHigh, vHigh])
            mask1 = cv2.inRange(hsv, lower_filter, upper_filter)
        if h+t > 180:
            lower_filter = np.array([0, sLow, vLow])
            upper_filter = np.array([(h+t) - 180, sHigh, vHigh])
            mask2 = cv2.inRange(hsv, lower_filter, upper_filter)
        lower_filter = np.array([h-t, sLow, vLow])
        upper_filter = np.array([h+t, sHigh, vHigh])
        mask = cv2.inRange(hsv, lower_filter, upper_filter)
        img = cv2.bitwise_and(data, data, mask=mask)

        if mask1 is not None: img = img + cv2.bitwise_and(data, data, mask=mask1)
        if mask2 is not None: img = img + cv2.bitwise_and(data, data, mask=mask2)

        self.sendDataFromSocket(img)

