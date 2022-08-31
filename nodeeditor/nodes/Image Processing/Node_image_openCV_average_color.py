import cv2
import numpy as np

from PyQt5.QtWidgets import QHBoxLayout, QLabel
from nodeeditor.Abstract_Node import Abstract_Node
from nodeeditor.node_content_widget import QDMNodeContentWidget
from nodeeditor.node_graphics_node import QDMGraphicsNode
from nodeeditor.var_type_conf import *



class Content(QDMNodeContentWidget):
    def initUI(self):
        self.label = QLabel("value: ")
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.label)
        layout.addStretch()
        self.setLayout(layout)


class GraphicsNode(QDMGraphicsNode):
    def initSizes(self):
        super().initSizes()
        self.setShownSize(130, 64)
        self.setHiddenSize(130, 30)
        self.setClosedSize(30, 30)

        self.hidden_edge_padding = 5
        self.hidden_title_height = 0

        self.setShowAndHiddenSameSize = True


class Node_ImageOpenCVAverageColorNode(Abstract_Node):
    def __init__(self, scene: 'Scene', title: str = "Average Color", inputs: list = [VAR_TYPE_LIST], outputs: list = [VAR_TYPE_LIST]):
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

        average_color_row = np.average(data, axis=0)
        average_color_value = np.average(average_color_row, axis=0)

        value = (int(average_color_value[0]), int(average_color_value[1]), int(average_color_value[2]))

        self.content.label.setText("value: " + str(value))

        self.sendDataFromSocket(value)

