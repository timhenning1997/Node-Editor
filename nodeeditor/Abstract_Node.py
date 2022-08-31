from nodeeditor.node_node import Node
from nodeeditor.utils_no_qt import dumpException
from nodeeditor.var_type_conf import RIGHT_TOP, LEFT_TOP


class Abstract_Node(Node):
    def __init__(self, scene: 'Scene', title: str="Abstract_Node", inputs: list = [], outputs: list = []):
        super().__init__(scene, title, inputs, outputs)

    def initSettings(self):
        super().initSettings()
        self.grNode.drawEvaluationIcon = False
        self.input_socket_position = LEFT_TOP
        self.output_socket_position = RIGHT_TOP