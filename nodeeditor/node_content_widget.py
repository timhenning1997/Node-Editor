# -*- coding: utf-8 -*-
"""A module containing the base class for the Node's content graphical representation. It also contains an example of
an overridden Text Widget, which can pass a notification to it's parent about being modified."""
from collections import OrderedDict

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor

from nodeeditor.node_serializable import Serializable
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QTextEdit, QDoubleSpinBox, QSpinBox, QLineEdit, QCheckBox, \
    QRadioButton, QDial, QSlider

from nodeeditor.utils_no_qt import dumpException


class QDMNodeContentWidget(QWidget, Serializable):
    """Base class for representation of the Node's graphics content. This class also provides layout
    for other widgets inside of a :py:class:`~nodeeditor.node_node.Node`"""
    def __init__(self, node:'Node', parent:QWidget=None):
        """
        :param node: reference to the :py:class:`~nodeeditor.node_node.Node`
        :type node: :py:class:`~nodeeditor.node_node.Node`
        :param parent: parent widget
        :type parent: QWidget

        :Instance Attributes:
            - **node** - reference to the :class:`~nodeeditor.node_node.Node`
            - **layout** - ``QLayout`` container
        """
        self.node = node
        super().__init__(parent)

        self.setMinimumSize(1, 1)

        self.initUI()

    def initUI(self):
        """Sets up layouts and widgets to be rendered in :py:class:`~nodeeditor.node_graphics_node.QDMGraphicsNode` class.
        """
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0,0,0,0)
        self.setLayout(self.layout)

    def setEditingFlag(self, value:bool):
        """
        .. note::

            If you are handling keyPress events by default Qt Window's shortcuts and ``QActions``, you will not
             need to use this method.

        Helper function which sets editingFlag inside :py:class:`~nodeeditor.node_graphics_view.QDMGraphicsView` class.

        This is a helper function to handle keys inside nodes with ``QLineEdits`` or ``QTextEdits`` (you can
        use overridden :py:class:`QDMTextEdit` class) and with QGraphicsView class method ``keyPressEvent``.

        :param value: new value for editing flag
        """
        self.node.scene.getView().editingFlag = value

    def showNode(self):
        self.show()

    def hideNode(self):
        self.show()

    def closeNode(self):
        self.hide()

    def removeContent(self):
        pass

    def lockNode(self):
        pass

    def editNode(self):
        pass

    def saveLayout(self, layout):
        if not layout:
            return None
        contentParts = []
        for layoutItemCount in range(0, layout.count()):
            layoutItem = layout.itemAt(layoutItemCount)
            if layoutItem == layoutItem.layout():
                contentParts += self.saveLayout(layoutItem.layout())
            else:
                tempContentPart = self.saveContentPartWidget(layoutItem.widget())
                if tempContentPart:
                    contentParts.append(tempContentPart)
        return contentParts

    def saveContentPartWidget(self, widget: QWidget):
        if isinstance(widget, QDoubleSpinBox):
            return {"ContentPartType": "QDoubleSpinBox", "value": widget.value()}
        elif isinstance(widget, QSpinBox):
            return {"ContentPartType": "QSpinBox", "value": widget.value()}
        elif isinstance(widget, QLineEdit):
            return {"ContentPartType": "QLineEdit", "value": widget.text()}
        elif isinstance(widget, QCheckBox):
            return {"ContentPartType": "QCheckBox", "value": widget.isChecked()}
        elif isinstance(widget, QRadioButton):
            return {"ContentPartType": "QRadioButton", "value": widget.isChecked()}
        elif isinstance(widget, QTextEdit):
            return {"ContentPartType": "QTextEdit", "value": widget.toPlainText()}
        elif isinstance(widget, QDial):
            return {"ContentPartType": "QDial", "value": widget.value()}
        elif isinstance(widget, QLabel):
            return {"ContentPartType": "QLabel", "value": widget.text()}
        elif isinstance(widget, QSlider):
            return {"ContentPartType": "QSlider", "value": widget.value()}
        return None

    def loadLayout(self, layout, content):
        if not layout:
            return None
        for layoutItemCount in range(0, layout.count()):
            layoutItem = layout.itemAt(layoutItemCount)
            if layoutItem == layoutItem.layout():
                self.loadLayout(layoutItem.layout(), content)
            else:
                self.loadContentPartWidget(layoutItem.widget(), content)
        return True

    def loadContentPartWidget(self, widget: QWidget, content):
        if len(content) == 0:
            return None

        if isinstance(widget, QDoubleSpinBox):
            widget.setValue(content.pop(0)["value"])
        elif isinstance(widget, QSpinBox):
            widget.setValue(content.pop(0)["value"])
        elif isinstance(widget, QLineEdit):
            widget.setText(content.pop(0)["value"])
        elif isinstance(widget, QCheckBox):
            widget.setChecked(content.pop(0)["value"])
        elif isinstance(widget, QRadioButton):
            widget.setChecked(content.pop(0)["value"])
        elif isinstance(widget, QTextEdit):
            widget.setPlainText(content.pop(0)["value"])
        elif isinstance(widget, QDial):
            widget.setValue(content.pop(0)["value"])
        elif isinstance(widget, QLabel):
            widget.setText(content.pop(0)["value"])
        elif isinstance(widget, QSlider):
            widget.setValue(content.pop(0)["value"])
        return None

    def serialize(self) -> OrderedDict:
        serializeableLayout = None
        try:
            try: serializeableLayout = self.layout
            except Exception as e: pass
            serializeableLayout = self.layout()
        except Exception as e: pass

        serializedContent = self.saveLayout(serializeableLayout)

        return OrderedDict([
            ('serializedContent', serializedContent)
        ])

    def deserialize(self, data:dict, hashmap:dict={}, restore_id:bool=True) -> bool:
        serializeableLayout = None
        try:
            try: serializeableLayout = self.layout
            except Exception as e: pass
            serializeableLayout = self.layout()
        except Exception as e: pass

        serializableContent = data["serializedContent"]
        if serializableContent:
            self.loadLayout(serializeableLayout, serializableContent)

        return True

class QDMTextEdit(QTextEdit):
    """
        .. note::

            This class is an example of a ``QTextEdit`` modification that handles the `Delete` key event with an overridden
            Qt's ``keyPressEvent`` (when not using ``QActions`` in menu or toolbar)

        Overridden ``QTextEdit`` which sends a notification about being edited to its parent's container :py:class:`QDMNodeContentWidget`
    """

    def focusInEvent(self, event:'QFocusEvent'):
        """Example of an overridden focusInEvent to mark the start of editing

        :param event: Qt's focus event
        :type event: QFocusEvent
        """
        self.parentWidget().setEditingFlag(True)
        super().focusInEvent(event)

    def focusOutEvent(self, event:'QFocusEvent'):
        """Example of an overridden focusOutEvent to mark the end of editing

        :param event: Qt's focus event
        :type event: QFocusEvent
        """
        self.parentWidget().setEditingFlag(False)
        super().focusOutEvent(event)
