from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QPushButton, QColorDialog


class ColorButton(QPushButton):
    newColor = pyqtSignal(QColor)

    def __init__(self, color: QColor, parent=None):
        super().__init__(parent)
        self.clicked.connect(self.openColorDialog)
        self.setText(color.name(QColor.HexArgb))
        self.color = color
        self.setStyleSheet("ColorButton{color : black; background-color :" + self.color.name() + "}" +
                           "ColorButton::hover{color : white; background-color :" + self.color.name() + "}")

    def openColorDialog(self):
        color = QColorDialog().getColor(initial=self.color, options=QColorDialog.ShowAlphaChannel)
        if color.isValid():
            self.color = color
            self.setStyleSheet("ColorButton{color : black; background-color :" + self.color.name() + "}" +
                               "ColorButton::hover{color : white; background-color :" + self.color.name() + "}")
            self.setText(color.name(QColor.HexArgb))
            self.newColor.emit(self.color)

    def setColor(self, color: QColor):
        self.color = color
        self.newColor.emit(self.color)
        self.setStyleSheet("ColorButton{color : black; background-color :" + color.name() + "}" +
                           "ColorButton::hover{color : white; background-color :" + color.name() + "}")
        self.setText(color.name(QColor.HexArgb))
