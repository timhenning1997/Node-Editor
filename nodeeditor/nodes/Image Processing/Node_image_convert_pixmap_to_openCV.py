import cv2
import numpy as np

from PyQt5.QtWidgets import QHBoxLayout, QLabel
from nodeeditor.Abstract_Node import Abstract_Node
from nodeeditor.node_content_widget import QDMNodeContentWidget
from nodeeditor.node_graphics_node import QDMGraphicsNode
from nodeeditor.var_type_conf import *



class Content(QDMNodeContentWidget):
    def initUI(self):
        self.label = QLabel("Pixmap --> OpenCV")
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addStretch()
        layout.addWidget(self.label)
        layout.addStretch()
        self.setLayout(layout)


class GraphicsNode(QDMGraphicsNode):
    def initSizes(self):
        super().initSizes()
        self.setShownSize(150, 64)
        self.setHiddenSize(150, 30)
        self.setClosedSize(30, 30)

        self.hidden_edge_padding = 5
        self.hidden_title_height = 0

        self.setShowAndHiddenSameSize = True


class Node_ImageConvertPixmapToOpenCVNode(Abstract_Node):
    def __init__(self, scene: 'Scene', title: str = "Pixmap To OpenCV", inputs: list = [VAR_TYPE_PIXMAP], outputs: list = [VAR_TYPE_LIST]):
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

        qimg = data.toImage()
        temp_shape = (qimg.height(), qimg.bytesPerLine() * 8 // qimg.depth(), 4)
        ptr = qimg.bits()
        ptr.setsize(qimg.byteCount())
        npArray = np.array(ptr, dtype=np.uint8).reshape(temp_shape)[..., :3]
        cvImg = cv2.cvtColor(npArray, cv2.COLOR_RGB2BGR)

        self.sendDataFromSocket(cvImg)

