from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import logging

logger = logging.getLogger("root")


class FramedWidget(QFrame):
    def __init__(self, *args, **kwargs):
        super(FramedWidget, self).__init__(*args, **kwargs)
        self.setStyleSheet(
            """
        QFrame {
            background: rgb(255, 255, 255);
        }
        """
        )
        # Set up frame style
        self.setFrameStyle(QFrame.Box | QFrame.Sunken)


class AnnotatedSlider(FramedWidget):
    def __init__(self, min, max, title, label_factor=1, label_string="{:.2f}"):
        super(AnnotatedSlider, self).__init__()

        self.min = min
        self.max = max
        self.label_factor = label_factor
        self.label_string = label_string

        # Configure slider
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(100)
        self.slider.setSingleStep(1)
        self.slider.setPageStep(10)
        self.slider.setTickInterval(10)
        self.slider.setTickPosition(QSlider.TicksBelow)
        # Set up layouts
        vbox = QVBoxLayout()
        hbox = QHBoxLayout()
        vbox.setContentsMargins(5, 5, 5, 5)
        hbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(5)
        # Define labels
        label_minimum = QLabel()
        label_minimum.setAlignment(Qt.AlignLeft)
        label_minimum.setText(self.label_string.format(min * label_factor))
        label_maximum = QLabel()
        label_maximum.setAlignment(Qt.AlignRight)
        label_maximum.setText(self.label_string.format(max * label_factor))
        self.label_current = QLabel()
        self.label_current.setAlignment(Qt.AlignCenter)
        self.label_current.setText(self.label_string.format(self.min))
        label_title = QLabel()
        label_title.setAlignment(Qt.AlignCenter)
        label_title.setText(title)
        # Assemble widgets
        vbox.addWidget(label_title)
        vbox.addWidget(self.slider)
        vbox.addLayout(hbox)
        hbox.addWidget(label_minimum, Qt.AlignLeft)
        hbox.addWidget(label_maximum, Qt.AlignRight)
        vbox.addWidget(self.label_current, Qt.AlignCenter)
        self.slider.valueChanged.connect(self.set_label_value)
        self.setLayout(vbox)

    def set_label_value(self):
        self.label_current.setText(
            self.label_string.format(self.value * self.label_factor)
        )

    @property
    def value(self):
        # Linear interpolation of the output value between minimum and maximum values
        return self.min + self.slider.value() / 100.0 * (self.max - self.min)

    @value.setter
    def value(self, value):
        if self.min <= value <= self.max:
            slider_value = int((value - self.min) * 100 / (self.max - self.min))
            self.slider.setValue(slider_value)
        else:
            logger.error(
                "Slider set value must be between {} and {}".format(self.min, self.max)
            )


class LabelledQLCD(QWidget):
    def __init__(self, title, signal, *args, **kwargs):
        super(LabelledQLCD, self).__init__(*args, **kwargs)
        self.signal = signal
        self.label = QLabel(title)
        self.number = QLCDNumber()
        self.number.setFixedHeight(48)
        self.number.setFixedWidth(128)
        self._layout = QVBoxLayout()
        self._layout.addWidget(self.label)
        self._layout.addWidget(self.number)
        self.setLayout(self._layout)

    @property
    def layout(self):
        return self._layout
