from setup import Setup
from GUI.LivePlots import LivePlotWidget, LivePlotSignal
import pyqtgraph as pg
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5.QtCore import *
from PyQt5.QtGui import *


class Color(QWidget):
    def __init__(self, color, *args, **kwargs):
        super(Color, self).__init__(*args, **kwargs)
        self.setAutoFillBackground(True)

        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(color))
        self.setPalette(palette)

        label = QLabel(self)
        label.setText('bla')


class MainWindow(QMainWindow):

    def __init__(self, setup: Setup, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setup = setup

        self.setWindowTitle("Mass Flow Sensor")

        toolbar = QToolBar("MyMainToolbar")
        toolbar.setIconSize(QSize(16, 16))
        self.addToolBar(toolbar)

        self.stack = QStackedWidget()
        self.stack.addWidget(ExperimentPageOne(setup=self.setup))
        self.setCentralWidget(self.stack)

        sensirion_img = QPixmap('GUI/sensirion.png')
        sensirion_logo = QLabel(self)
        sensirion_logo.setPixmap(sensirion_img.scaledToHeight(32))
        sensirion_logo.setAlignment(Qt.AlignLeft)
        sensirion_logo.setStatusTip("Sensirion helping us.")
        eth_img = QPixmap('GUI/eth.png')
        eth_logo = QLabel(self)
        eth_logo.setPixmap(eth_img.scaledToHeight(32))
        eth_logo.setAlignment(Qt.AlignRight)
        status_bar = QStatusBar(self)
        status_bar.addPermanentWidget(sensirion_logo)
        status_bar.addPermanentWidget(eth_logo)
        self.setStatusBar(status_bar)


class ExperimentPageOne(QWidget):
    def __init__(self, setup):
        super(ExperimentPageOne, self).__init__()
        self.setup = setup
        # Create controls
        self.pwm = AnnotatedSlider(min=0, max=100, title="Heating Power [%]")
        self.pwm.slider.setSingleStep(1)
        self.pwm.slider.setPageStep(10)
        self.pwm.slider.setValue(self.setup._current_pwm_value)
        self.pwm.slider.setTickInterval(10)
        self.pwm.slider.setTickPosition(QSlider.TicksBelow)
        self.pwm.slider.valueChanged.connect(self.set_pwm_value)
        # Create visualization
        self.graphWidget = LivePlotWidget(setup=self.setup, title="Temperature Plot", ylabel="Temperature [°C]", ylims=(20, 40))
        first_signal = LivePlotSignal(name="T 1", identifier="Temperature 1", color='b')
        second_signal = LivePlotSignal(name="T 2", identifier="Temperature 2", color='r')
        self.graphWidget.add_signals([first_signal, second_signal])
        # Add widgets to layout
        horizontal_layout = QHBoxLayout()
        vertical_layout = QVBoxLayout()
        vertical_layout.addWidget(self.pwm)
        vertical_layout.addWidget(QLabel(), 1)
        horizontal_layout.addLayout(vertical_layout)
        horizontal_layout.addWidget(self.graphWidget)
        self.setLayout(horizontal_layout)

    def set_pwm_value(self):
        self.setup.wrap_set_pwm(value=self.pwm.slider.value() / 100.0)


class AnnotatedSlider(QWidget):
    def __init__(self, min, max, title):
        super(AnnotatedSlider, self).__init__()
        # Configure slider
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(min)
        self.slider.setMaximum(max)
        # Set up layouts
        vbox = QVBoxLayout()
        hbox = QHBoxLayout()
        vbox.setContentsMargins(0, 0, 0, 0)
        hbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(0)
        # Define labels
        label_minimum = QLabel()
        label_minimum.setAlignment(Qt.AlignLeft)
        label_minimum.setNum(min)
        label_maximum = QLabel()
        label_maximum.setAlignment(Qt.AlignRight)
        label_maximum.setNum(max)
        label_current = QLabel()
        label_current.setAlignment(Qt.AlignCenter)
        label_current.setNum(0)
        label_title = QLabel()
        label_title.setAlignment(Qt.AlignCenter)
        label_title.setText(title)
        # Assemble widgets
        vbox.addWidget(label_title)
        vbox.addWidget(self.slider)
        vbox.addLayout(hbox)
        hbox.addWidget(label_minimum, Qt.AlignLeft)
        hbox.addWidget(label_current, Qt.AlignCenter)
        hbox.addWidget(label_maximum, Qt.AlignRight)
        self.slider.valueChanged.connect(label_current.setNum)
        vbox.setGeometry(QRect(300, 300, 300, 140))
        self.setLayout(vbox)


class Launcher(object):
    def __init__(self, setup: Setup):
        self.setup = setup

        app = QApplication([])
        window = MainWindow(setup=setup)
        window.show()
        app.exec_()
