import os, sys, inspect
from PyQt5.QtWidgets import QApplication

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from nodeeditor.utils import loadStylesheet
from nodeeditor.node_editor_window import NodeEditorWindow


if __name__ == '__main__':
    app = QApplication(sys.argv)

    wnd = NodeEditorWindow()
    # wnd.nodeeditor.addNodes()
    QApplication.setStyle("Fusion")

    module_path = os.path.dirname(inspect.getfile(wnd.__class__))
    loadStylesheet(os.path.join(module_path, 'qss/nodeeditor-dark.qss'))

    sys.exit(app.exec_())

    # @ TODO Ein paar Nodes gestalten. Z.B. Ein paar Mathe Nodes. Input mit QSpinBox Output mit Label mit größerer Schrift oder so.
    # @ TODO Make path dependent on utils_no_qt "getNodeEditorDirectory" function

