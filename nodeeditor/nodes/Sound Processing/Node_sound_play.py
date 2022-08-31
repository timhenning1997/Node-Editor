import time
from pycaw.pycaw import AudioUtilities, ISimpleAudioVolume

from PyQt5.QtCore import Qt, QTimer
from pysinewave import SineWave

from PyQt5.QtWidgets import QPushButton, QVBoxLayout, QSlider, QHBoxLayout, QLabel, QDoubleSpinBox
from nodeeditor.Abstract_Node import Abstract_Node
from nodeeditor.node_content_widget import QDMNodeContentWidget
from nodeeditor.node_graphics_node import QDMGraphicsNode
from nodeeditor.var_type_conf import *


class Content(QDMNodeContentWidget):
    def initUI(self):
        self.sinewave = SineWave(pitch=12, pitch_per_second=10)

        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.setInterval(1000000000)
        self.timer.timeout.connect(self.stopTone)

        self.playToneButton = QPushButton("Play Tone")
        self.playToneButton.pressed.connect(self.playTone)

        self.stopToneButton = QPushButton("Stop Tone")
        self.stopToneButton.pressed.connect(self.stopTone)

        self.frequencySlider = QSlider(Qt.Horizontal)
        self.frequencySlider.setRange(0, 2000)
        self.frequencySlider.setValue(523)
        self.frequencySlider.valueChanged.connect(self.changeFrequency)

        self.volumeSlider = QSlider(Qt.Horizontal)
        self.volumeSlider.setRange(0, 100)
        self.volumeSlider.setValue(100)
        self.volumeSlider.valueChanged.connect(self.changeVolume)

        self.pitchPerSecondSlider = QSlider(Qt.Horizontal)
        self.pitchPerSecondSlider.setRange(0, 20)
        self.pitchPerSecondSlider.setValue(10)
        self.pitchPerSecondSlider.valueChanged.connect(self.changepitchPerSecond)

        self.timeDurationSpinBox = QDoubleSpinBox()
        self.timeDurationSpinBox.setRange(0, 60)
        self.timeDurationSpinBox.setValue(0)
        self.timeDurationSpinBox.setDecimals(1)
        self.timeDurationSpinBox.valueChanged.connect(self.changetimeDuration)

        self.frequencyLabel = QLabel("Freq.: 523")
        self.frequencyLabel.setFixedWidth(60)
        self.volumeLabel = QLabel("Vol.: 100")
        self.volumeLabel.setFixedWidth(60)
        self.pitchPerSecondLabel = QLabel("PpS.: 10")
        self.pitchPerSecondLabel.setFixedWidth(60)
        self.timeDurationLabel = QLabel("time.: 0.0s")
        self.timeDurationLabel.setFixedWidth(60)

        hlayout1 = QHBoxLayout()
        hlayout1.addWidget(self.frequencySlider)
        hlayout1.addWidget(self.frequencyLabel)

        hlayout2 = QHBoxLayout()
        hlayout2.addWidget(self.volumeSlider)
        hlayout2.addWidget(self.volumeLabel)

        hlayout3 = QHBoxLayout()
        hlayout3.addWidget(self.pitchPerSecondSlider)
        hlayout3.addWidget(self.pitchPerSecondLabel)

        hlayout4 = QHBoxLayout()
        hlayout4.addWidget(self.timeDurationSpinBox)
        hlayout4.addWidget(self.timeDurationLabel)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.playToneButton)
        layout.addWidget(self.stopToneButton)
        layout.addLayout(hlayout1)
        layout.addLayout(hlayout2)
        layout.addLayout(hlayout3)
        layout.addLayout(hlayout4)
        self.setLayout(layout)

    def playTone(self):
        self.timer.start()
        self.sinewave.play()

    def stopTone(self):
        self.sinewave.stop()

    def changeFrequency(self):
        self.sinewave.set_frequency(self.frequencySlider.value())
        self.frequencyLabel.setText("Freq.: " + str(self.frequencySlider.value()))

    def changeVolume(self):
        sessions = AudioUtilities.GetAllSessions()
        for session in sessions:
            volume = session._ctl.QueryInterface(ISimpleAudioVolume)
            if session.Process:
                volume.SetMasterVolume(self.volumeSlider.value() / 100.0, None)
        self.volumeLabel.setText("Vol.: " + str(self.volumeSlider.value()))

    def changepitchPerSecond(self):
        if self.pitchPerSecondSlider.value() == 0:
            self.sinewave.sinewave_generator.pitch_per_second = 10000
        else:
            self.sinewave.sinewave_generator.pitch_per_second = self.pitchPerSecondSlider.value()
        self.pitchPerSecondLabel.setText("PpS.: " + str(self.pitchPerSecondSlider.value()))

    def changetimeDuration(self):
        if self.timeDurationSpinBox.value() == 0:
            self.timer.setInterval(1000000000)
        else:
            self.timer.setInterval(self.timeDurationSpinBox.value() * 1000)
        self.timeDurationLabel.setText("Time.: " + str(self.timeDurationSpinBox.value()) + "s")

    def removeContent(self):
        self.stopTone()
        super().removeContent()


class GraphicsNode(QDMGraphicsNode):
    def initSizes(self):
        super().initSizes()
        self.setShownSize(180, 186)
        self.setHiddenSize(180, 162)
        self.setClosedSize(30, 30)

        self.hidden_edge_padding = 10
        self.hidden_title_height = 0

        self.setShowAndHiddenSameSize = True


class Node_SoundPlayNode(Abstract_Node):
    def __init__(self, scene: 'Scene', title: str = "Sound Play",
                 inputs: list = [VAR_TYPE_NOT_DEFINED,
                                 VAR_TYPE_NOT_DEFINED,
                                 [VAR_TYPE_INT, VAR_TYPE_FLOAT],
                                 [VAR_TYPE_INT, VAR_TYPE_FLOAT],
                                 [VAR_TYPE_INT, VAR_TYPE_FLOAT],
                                 [VAR_TYPE_FLOAT, VAR_TYPE_INT]],
                 outputs: list = []):
        super().__init__(scene, title, inputs, outputs)

    def initInnerClasses(self):
        self.content = Content(self)
        self.grNode = GraphicsNode(self)

    def initSettings(self):
        super().initSettings()
        self._socket_y_offset = self.socket_y_offset = 8
        self._socket_spacing = self.socket_spacing = 24
        self.grNode.updateSocketsAndEdgesPositions()

    def receiveData(self, data, inputSocketIndex):
        super().receiveData(data, inputSocketIndex)
        if inputSocketIndex == 0 and self.inputValues[0]:
            self.content.playTone()
        elif inputSocketIndex == 1 and self.inputValues[1]:
            self.content.stopTone()
        elif inputSocketIndex == 2 and self.inputValues[2] is not None:
            self.content.frequencySlider.setValue(int(self.inputValues[2]))
            self.content.changeFrequency()
        elif inputSocketIndex == 3 and self.inputValues[3] is not None:
            self.content.volumeSlider.setValue(int(self.inputValues[3]))
            self.content.changeVolume()
        elif inputSocketIndex == 4 and self.inputValues[4] is not None:
            self.content.pitchPerSecondSlider.setValue(int(self.inputValues[4]))
            self.content.changepitchPerSecond()
        elif inputSocketIndex == 5 and self.inputValues[5] is not None:
            self.content.timeDurationSpinBox.setValue(self.inputValues[5])
            self.content.changetimeDuration()
