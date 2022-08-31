from PyQt5.QtWidgets import QLabel, QVBoxLayout
from nodeeditor.Abstract_Node import Abstract_Node
from nodeeditor.node_content_widget import QDMNodeContentWidget
from nodeeditor.node_graphics_node import QDMGraphicsNode
from nodeeditor.var_type_conf import *



class Content(QDMNodeContentWidget):
    def initUI(self):
        self.input1Label = QLabel("")
        self.input2Label = QLabel("")

        self.operationLabel = QLabel("+")

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.input1Label)
        layout.addWidget(self.operationLabel)
        layout.addWidget(self.input2Label)

        self.setLayout(layout)


class GraphicsNode(QDMGraphicsNode):
    def initSizes(self):
        super().initSizes()
        self.setShownSize(120, 84)
        self.setHiddenSize(120, 50)
        self.setClosedSize(30, 30)

        self.hidden_edge_padding = 5
        self.hidden_title_height = 0

        self.setShowAndHiddenSameSize = True


class Node_MathAddNode(Abstract_Node):
    def __init__(self, scene: 'Scene', title: str = "Add", inputs: list = [[VAR_TYPE_FLOAT, VAR_TYPE_INT], [VAR_TYPE_FLOAT, VAR_TYPE_INT]], outputs: list = [[VAR_TYPE_FLOAT, VAR_TYPE_INT]]):
        super().__init__(scene, title, inputs, outputs)

    def initInnerClasses(self):
        self.content = Content(self)
        self.grNode = GraphicsNode(self)

    def initSettings(self):
        super().initSettings()
        self.output_socket_position = RIGHT_CENTER
        self.input_socket_position = LEFT_TOP

    def receiveData(self, data, inputSocketIndex):
        super().receiveData(data, inputSocketIndex)

        if self.inputValues[0] is not None:
            self.content.input1Label.setText(str(self.inputValues[0]))
        if self.inputValues[1] is not None:
            self.content.input2Label.setText(str(self.inputValues[1]))

        if self.inputValues[0] is not None and self.inputValues[1] is not None:
            self.sendDataFromSocket(self.inputValues[0] + self.inputValues[1])
