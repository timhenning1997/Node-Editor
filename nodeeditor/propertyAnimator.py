from PyQt5.QtCore import QTimer, pyqtSignal, QObject


class PropertyAnimator(QObject):
    start = pyqtSignal(float)
    update = pyqtSignal(float)
    stop = pyqtSignal(float)

    def __init__(self, startValue: float = 0.0, endValue: float = 100.0, duration: float = 1000.0, interval: int = 100):
        super().__init__()
        self._start_value = startValue
        self._end_value = endValue
        self._value = 0.0
        self._duration = duration
        self._current_time = 0.0
        self._interval = interval
        self._animation_timer = QTimer()
        self._animation_timer.timeout.connect(self.updateAnimationFrame)
        self._enable = True

    def updateAnimationFrame(self):
        if not self._enable:
            self._animation_timer.stop()
            self._current_time = 0
            self.stop.emit(self._end_value)
            return

        self._current_time += self._interval

        if self._duration == 0:
            self._value = self._end_value
        else:
            self._value = self._start_value + (self._end_value - self._start_value) * (self._current_time / self._duration)
        self._value = max(self._start_value, min(self._end_value, self._value))
        self.update.emit(self._value)

        if self._current_time >= self._duration:
            self._animation_timer.stop()
            self._current_time = 0
            self.stop.emit(self._value)

    def startAnimation(self, interval: int = -1):
        if not self._enable:
            return

        if interval != -1:
            self._interval = float(interval)
        self._current_time = 0.0
        self._value = self._start_value
        self.update.emit(self._value)
        self.start.emit(self._value)
        self._animation_timer.start(self._interval)

    def setStartValue(self, value: float):
        self._start_value = value

    def setEndValue(self, value: float):
        self._end_value = value

    def setDuration(self, value: float):
        self._duration = value

    def setInterval(self, value: float):
        self._interval = value

    def setEnable(self, b: bool = True):
        self._enable = b

    def isEnable(self):
        if self._enable:
            return True
        else:
            return False
