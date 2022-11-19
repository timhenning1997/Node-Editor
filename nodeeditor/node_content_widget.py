# -*- coding: utf-8 -*-
"""A module containing the base class for the Node's content graphical representation. It also contains an example of
an overridden Text Widget, which can pass a notification to it's parent about being modified."""
from collections import OrderedDict

from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtGui import QColor, QWheelEvent, QCloseEvent, QContextMenuEvent

from nodeeditor.node_serializable import Serializable
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QTextEdit, QDoubleSpinBox, QSpinBox, QLineEdit, QCheckBox, \
    QRadioButton, QDial, QSlider, QLayout, QHBoxLayout, QAbstractSpinBox, QSizePolicy, QComboBox, QListView

from nodeeditor.utils_no_qt import dumpException
from nodeeditor.var_type_conf import *


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

        self.socketInputPosition = LEFT_CENTER
        self.socketOutputPosition = RIGHT_CENTER

        self.setMinimumSize(1, 1)

        self.initLayouts()
        self.initUI()
        self.addStretchToLayouts()

    def initLayouts(self):
        self.inputLayout = QVBoxLayout()
        self.inputLayout.setContentsMargins(0, 0, 0, 0)
        self.mainLayout = QVBoxLayout()
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.outputLayout = QVBoxLayout()
        self.outputLayout.setContentsMargins(0, 0, 0, 0)

        self.inputLayoutWidget = QWidget()
        self.inputLayoutWidget.setLayout(self.inputLayout)
        self.outputLayoutWidget = QWidget()
        self.outputLayoutWidget.setLayout(self.outputLayout)

    def initUI(self):
        """Sets up layouts and widgets to be rendered in :py:class:`~nodeeditor.node_graphics_node.QDMGraphicsNode` class.
        """
        pass

    def addStretchToLayouts(self):
        if self.layout() is None:
            if self.socketInputPosition == LEFT_TOP:
                self.inputLayout.addStretch()
            if self.socketOutputPosition == RIGHT_TOP:
                self.outputLayout.addStretch()

            layout = QHBoxLayout()
            layout.setContentsMargins(0, 0, 0, 0)
            if self.inputLayout.count() > 0: layout.addWidget(self.inputLayoutWidget)
            layout.addLayout(self.mainLayout)
            if self.outputLayout.count() > 0: layout.addWidget(self.outputLayoutWidget)
            self.setLayout(layout)
            self.totalMinimumWidth = self.layout().totalMinimumSize().width()
            self.totalMinimumHeight = self.layout().totalMinimumSize().height()

    def setInputLayoutWidth(self, width: int = 50):
        self.inputLayoutWidget.setFixedWidth(width)

    def setOutputLayoutWidth(self, width: int = 50):
        self.outputLayoutWidget.setFixedWidth(width)

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

    def addInputLayout(self, layout: QLayout = None) -> QLayout:
        self.inputLayout.addLayout(layout)
        self.socketInputPosition = LEFT_TOP
        return layout

    def addInputWidget(self, widget: QWidget = None) -> QWidget:
        widget.setFixedHeight(20)
        self.inputLayout.addWidget(widget)
        self.socketInputPosition = LEFT_TOP
        return widget

    def addInputLabel(self, text: str = "") -> QLabel:
        widget = QLabel(text)
        return self.addInputDescriptionLabel(widget)

    def addInputLineEdit(self, text: str = "", readOnly: bool = False, descriptionText: str = "", descriptionTextPositionLeft: bool = True) -> QLineEdit:
        widget = QLineEdit(text)
        widget.setReadOnly(readOnly)
        return self.addInputDescriptionLabel(widget, descriptionText, descriptionTextPositionLeft)


    def addInputSpinBox(self, value: int = 0, minValue: int = 0, maxValue: int = 99, readOnly: bool = False, descriptionText: str = "", descriptionTextPositionLeft: bool = True) -> QSpinBox:
        widget = QSpinBox()
        widget.setRange(minValue, maxValue)
        widget.setValue(value)
        widget.setButtonSymbols(QAbstractSpinBox.NoButtons)
        widget.setReadOnly(readOnly)
        return self.addInputDescriptionLabel(widget, descriptionText, descriptionTextPositionLeft)

    def addInputDoubleSpinBox(self, value: float = 0, minValue: float = 0, maxValue: float = 99, decimals: int = 2, readOnly: bool = False, descriptionText: str = "", descriptionTextPositionLeft: bool = True) -> QDoubleSpinBox:
        widget = QDoubleSpinBox()
        widget.setRange(minValue, maxValue)
        widget.setValue(value)
        widget.setDecimals(decimals)
        widget.setButtonSymbols(QAbstractSpinBox.NoButtons)
        widget.setReadOnly(readOnly)
        return self.addInputDescriptionLabel(widget, descriptionText, descriptionTextPositionLeft)

    def addInputCheckBox(self, text: str = "", checked: bool = False, checkable: bool = True, descriptionText: str = "", descriptionTextPositionLeft: bool = True) -> QCheckBox:
        widget = QCheckBox(text)
        widget.setChecked(checked)
        widget.setEnabled(checkable)
        return self.addInputDescriptionLabel(widget, descriptionText, descriptionTextPositionLeft)

    def addInputDescriptionLabel(self, widget: QWidget, descriptionText: str = "", descriptionTextPositionLeft: bool = True):
        widget.setFixedHeight(20)
        widget.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
        if descriptionText != "":
            layout = QHBoxLayout()
            label = QLabel(descriptionText)
            label.setFixedHeight(20)
            if descriptionTextPositionLeft:
                layout.addWidget(label)
            layout.addWidget(widget)
            if not descriptionTextPositionLeft:
                layout.addWidget(label)
            self.addInputLayout(layout)
            return widget
        return self.addInputWidget(widget)

    def addMainLayout(self, layout: QLayout = None) -> QLayout:
        self.mainLayout.addLayout(layout)
        return layout

    def addMainWidget(self, widget: QWidget = None) -> QWidget:
        self.mainLayout.addWidget(widget)
        return widget

    def addOutputLayout(self, layout: QLayout = None) -> QLayout:
        self.outputLayout.addLayout(layout)
        self.socketOutputPosition = LEFT_TOP
        return layout

    def addOutputWidget(self, widget: QWidget = None) -> QWidget:
        widget.setFixedHeight(20)
        if hasattr(widget, "alignment"):
            widget.setAlignment(Qt.AlignVCenter | Qt.AlignRight)

        self.outputLayout.addWidget(widget)
        self.socketOutputPosition = RIGHT_TOP
        return widget

    def addOutputLabel(self, text: str = "") -> QLabel:
        widget = QLabel(text)
        return self.addOutputDescriptionLabel(widget)

    def addOutputLineEdit(self, text: str = "", readOnly: bool = False, descriptionText: str = "", descriptionTextPositionLeft: bool = False) -> QLineEdit:
        widget = QLineEdit(text)
        widget.setReadOnly(readOnly)
        return self.addOutputDescriptionLabel(widget, descriptionText, descriptionTextPositionLeft)


    def addOutputSpinBox(self, value: int = 0, minValue: int = 0, maxValue: int = 99, readOnly: bool = False, descriptionText: str = "", descriptionTextPositionLeft: bool = False) -> QSpinBox:
        widget = QSpinBox()
        widget.setRange(minValue, maxValue)
        widget.setValue(value)
        widget.setButtonSymbols(QAbstractSpinBox.NoButtons)
        widget.setReadOnly(readOnly)
        return self.addOutputDescriptionLabel(widget, descriptionText, descriptionTextPositionLeft)

    def addOutputDoubleSpinBox(self, value: float = 0, minValue: float = 0, maxValue: float = 99, decimals: int = 2, readOnly: bool = False, descriptionText: str = "", descriptionTextPositionLeft: bool = False) -> QDoubleSpinBox:
        widget = QDoubleSpinBox()
        widget.setRange(minValue, maxValue)
        widget.setValue(value)
        widget.setDecimals(decimals)
        widget.setButtonSymbols(QAbstractSpinBox.NoButtons)
        widget.setReadOnly(readOnly)
        return self.addOutputDescriptionLabel(widget, descriptionText, descriptionTextPositionLeft)

    def addOutputCheckBox(self, text: str = "", checked: bool = False, checkable: bool = True, descriptionText: str = "", descriptionTextPositionLeft: bool = False) -> QCheckBox:
        widget = QCheckBox(text)
        widget.setChecked(checked)
        widget.setEnabled(checkable)
        return self.addOutputDescriptionLabel(widget, descriptionText, descriptionTextPositionLeft)

    def addOutputDescriptionLabel(self, widget: QWidget, descriptionText: str = "", descriptionTextPositionLeft: bool = False):
        widget.setFixedHeight(20)
        widget.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
        if descriptionText != "":
            layout = QHBoxLayout()
            label = QLabel(descriptionText)
            label.setFixedHeight(20)
            label.setAlignment(Qt.AlignVCenter | Qt.AlignRight)
            if descriptionTextPositionLeft:
                layout.addWidget(label)
            layout.addWidget(widget)
            if not descriptionTextPositionLeft:
                layout.addWidget(label)
            self.addOutputLayout(layout)
            return widget
        return self.addOutputWidget(widget)

    def saveLayout(self, layout):
        if not layout:
            return None
        contentParts = []
        for layoutItemCount in range(0, layout.count()):
            layoutItem = layout.itemAt(layoutItemCount)
            if layoutItem == layoutItem.layout():
                if layoutItem.count() > 0:
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


class ListView(QListView):
    def __init__(self, parent=None):
        super(QListView, self).__init__(parent)

    def wheelEvent(self, event: QWheelEvent):
        super().wheelEvent(event)
        event.accept()

class QDMComboBox(QComboBox):

    def __init__(self):
        super().__init__()

        listview = ListView()
        self.setView(listview)
    def showPopup(self):
        self.parentWidget().setEditingFlag(True)
        super().showPopup()

    def hidePopup(self):
        try:
            self.parentWidget().setEditingFlag(False)
            super().hidePopup()
        except Exception as e:
            pass
