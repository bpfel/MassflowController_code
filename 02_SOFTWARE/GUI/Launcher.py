from setup import Setup
from PyQt5.QtCore import Qt
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from GUI.ExperimentPages import *

logger = logging.getLogger("root")


class MainWindow(QMainWindow):
    def __init__(self, setup: Setup, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setup = setup

        self.setWindowTitle("Mass Flow Sensor")
        self.setup_tool_bar()
        self.setup_status_bar()

        # Main stack
        self.stack = QStackedWidget()
        self.stack.addWidget(PWMSetting(setup=self.setup))
        self.stack.addWidget(PIDSetting(setup=self.setup))
        self.setCentralWidget(self.stack)
        self.stack.currentWidget().enter()

    def setup_tool_bar(self):
        toolbar = QToolBar("MyMainToolbar")
        toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(toolbar)

        # Set up actions
        self.action_stop_recording = QAction(
            QIcon("./GUI/Icons/control-stop-square.png"), "Stop recording", self
        )
        self.action_stop_recording.setStatusTip("Stop recording measurements")
        self.action_stop_recording.triggered.connect(self._stop_recording)
        toolbar.addAction(self.action_stop_recording)

        self.action_start_recording = QAction(
            QIcon("./GUI/Icons/control.png"), "Start recording", self
        )
        self.action_start_recording.setStatusTip("Start recording measurements")
        self.action_start_recording.triggered.connect(self._start_recording)
        self.action_start_recording.setDisabled(True)
        toolbar.addAction(self.action_start_recording)

        toolbar.addSeparator()

        self.action_previous_view = QAction(
            QIcon("./GUI/Icons/arrow-180.png"), "Previous View", self
        )
        self.action_previous_view.setStatusTip("Go to previous view")
        self.action_previous_view.triggered.connect(self._go_to_previous_view)
        self.action_previous_view.setDisabled(True)
        toolbar.addAction(self.action_previous_view)

        self.action_next_view = QAction(
            QIcon("./GUI/Icons/arrow.png"), "Next View", self
        )
        self.action_next_view.setStatusTip("Go to next view")
        self.action_next_view.triggered.connect(self._go_to_next_view)
        toolbar.addAction(self.action_next_view)

        toolbar.addSeparator()

        self.action_reset_plots = QAction(
            QIcon("./GUI/Icons/application-monitor.png"), "Reset Plots", self
        )
        self.action_reset_plots.setStatusTip("Reset plots to original axis limits")
        self.action_reset_plots.triggered.connect(self._reset_plots)
        toolbar.addAction(self.action_reset_plots)

    def _stop_recording(self):
        self.action_stop_recording.setDisabled(True)
        self.setup.stop_measurement_thread()
        self.action_start_recording.setEnabled(True)

    def _start_recording(self):
        self.action_start_recording.setDisabled(True)
        self.setup.start_measurement_thread()
        self.action_stop_recording.setEnabled(True)

    def _go_to_previous_view(self):
        if self.stack.currentIndex() == 0:
            pass
        else:
            self.stack.currentWidget().leave()
            self.stack.setCurrentIndex(self.stack.currentIndex() - 1)
            self.stack.currentWidget().enter()
            if self.stack.currentIndex() == 0:
                self.action_previous_view.setDisabled(True)
                self.action_next_view.setEnabled(True)

    def _go_to_next_view(self):
        if self.stack.currentIndex() == self.stack.count() - 1:
            pass
        else:
            self.stack.currentWidget().leave()
            self.stack.setCurrentIndex(self.stack.currentIndex() + 1)
            self.stack.currentWidget().enter()
            if self.stack.currentIndex() == self.stack.count() - 1:
                self.action_next_view.setDisabled(True)
                self.action_previous_view.setEnabled(True)

    def _reset_plots(self):
        self.stack.currentWidget().reset_plots()

    def setup_status_bar(self):
        sensirion_img = QPixmap("GUI/Icons/sensirion.png")
        sensirion_logo = QLabel(self)
        sensirion_logo.setPixmap(sensirion_img.scaledToHeight(32))
        sensirion_logo.setAlignment(Qt.AlignLeft)
        eth_img = QPixmap("GUI/Icons/eth.png")
        eth_logo = QLabel(self)
        eth_logo.setPixmap(eth_img.scaledToHeight(32))
        eth_logo.setAlignment(Qt.AlignRight)
        status_bar = QStatusBar(self)
        status_bar.addPermanentWidget(sensirion_logo)
        status_bar.addPermanentWidget(eth_logo)
        self.setStatusBar(status_bar)


class Launcher(object):
    def __init__(self, setup: Setup):
        self.setup = setup

        app = QApplication([])
        window = MainWindow(setup=setup)
        window.showMaximized()
        app.exec_()
