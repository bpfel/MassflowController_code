from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import logging

logger = logging.getLogger("root")


class AnnotatedSlider(QFrame):
    def __init__(self, min, max, title):
        super(AnnotatedSlider, self).__init__()
        self.setStyleSheet("""
        QFrame {
            background: rgb(255, 255, 255);
        }
        """)
        self.min = min
        self.max = max
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
        label_minimum.setNum(min)
        label_maximum = QLabel()
        label_maximum.setAlignment(Qt.AlignRight)
        label_maximum.setNum(max)
        self.label_current = QLabel()
        self.label_current.setAlignment(Qt.AlignCenter)
        self.label_current.setNum(self.min)
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
        # Set up frame style
        self.setFrameStyle(QFrame.Box | QFrame.Sunken)

    def set_label_value(self):
        self.label_current.setNum(self.value)

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
