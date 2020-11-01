from setup import Setup
from GUI.ExperimentPages import *
from GUI.Utils import resource_path

logger = logging.getLogger("root")


class MainWindow(QMainWindow):
    """
    Defines the main window of the application.

    :type setup: Setup
    :param setup: Instance of Setup to allow access to sensors and actuators.
    """

    def __init__(self, setup: Setup, *args, **kwargs) -> None:
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setup = setup
        self.setStyleSheet(
            """
        QMainWindow {
            background-color: rgb(255, 255, 255);
        }
        """
        )

        self.setWindowTitle("Mass Flow Sensor")
        self.setup_tool_bar()
        self.setup_status_bar()

        # Main layout
        self.stack = QStackedWidget()
        self.stack.addWidget(
            PWMSetting(
                setup=self.setup,
                start_recording_action=self._start_recording,
                stop_recording_action=self._stop_recording,
                enable_output_action=self._toggle_output,
            )
        )
        self.stack.addWidget(
            PIDSetting(
                setup=self.setup,
                start_recording_action=self._start_recording,
                stop_recording_action=self._stop_recording,
                enable_output_action=self._toggle_output,
            )
        )
        self.setCentralWidget(self.stack)
        self.stack.currentWidget().enter()

    def setup_tool_bar(self) -> None:
        """
        Adds a toolbar to the main window and defines a set of actions for it.
        """
        toolbar = QToolBar("MyMainToolbar")
        toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(toolbar)

        # Set up actions
        self.action_stop_recording = QAction(
            QIcon(resource_path("Icons\\control-stop-square.png")),
            "Stop recording",
            self,
        )
        self.action_stop_recording.setStatusTip("Stop recording measurements")
        self.action_stop_recording.triggered.connect(self._stop_recording)
        toolbar.addAction(self.action_stop_recording)

        self.action_start_recording = QAction(
            QIcon(resource_path("Icons\\control.png")), "Start recording", self
        )
        self.action_start_recording.setStatusTip("Start recording measurements")
        self.action_start_recording.triggered.connect(self._start_recording)
        self.action_start_recording.setDisabled(True)
        toolbar.addAction(self.action_start_recording)

        toolbar.addSeparator()

        self.action_previous_view = QAction(
            QIcon(resource_path("Icons\\arrow-180.png")), "Previous View", self
        )
        self.action_previous_view.setStatusTip("Go to previous view")
        self.action_previous_view.triggered.connect(self._go_to_previous_view)
        self.action_previous_view.setDisabled(True)
        toolbar.addAction(self.action_previous_view)

        self.action_next_view = QAction(
            QIcon(resource_path("Icons\\arrow.png")), "Next View", self
        )
        self.action_next_view.setStatusTip("Go to next view")
        self.action_next_view.triggered.connect(self._go_to_next_view)
        toolbar.addAction(self.action_next_view)

        toolbar.addSeparator()

        self.action_reset_plots = QAction(
            QIcon(resource_path("Icons\\application-monitor.png")), "Reset Plots", self
        )
        self.action_reset_plots.setStatusTip("Reset plots to original axis limits")
        self.action_reset_plots.triggered.connect(self._reset_plots)
        toolbar.addAction(self.action_reset_plots)

        toolbar.addSeparator()

        self.action_competition_mode = QPushButton("Competition Mode", self)
        self.action_competition_mode.setStatusTip("Win a Sensirion Humi Gadget!")
        self.action_competition_mode.setCheckable(True)
        self.action_competition_mode.setChecked(False)
        self.action_competition_mode.clicked.connect(self._change_competition_mode)
        toolbar.addWidget(self.action_competition_mode)

        self.action_toggle_output = QPushButton("Toggle Output", self)
        self.action_toggle_output.setStatusTip("Turn the heater on or off.")
        self.action_toggle_output.setCheckable(True)
        self.action_toggle_output.setStyleSheet(
            """
        QPushButton {
            background: rgba(0, 102, 255, 50);
        }
        """
        )
        self.action_toggle_output.setChecked(False)
        self.action_toggle_output.clicked.connect(self._toggle_output)
        toolbar.addWidget(self.action_toggle_output)

        toolbar.addSeparator()

        self.action_set_temp_calibration = QAction(
            QIcon(resource_path("Icons\\thermometer--pencil.png")), "Set Temperature Calibration", self
        )
        self.action_set_temp_calibration.setStatusTip("Force the current delta T to be zero.")
        self.action_set_temp_calibration.triggered.connect(self._calibrate_temperature)
        toolbar.addAction(self.action_set_temp_calibration)

        self.action_reset_temp_calibration = QAction(
            QIcon(resource_path("Icons\\thermometer--exclamation.png")), "Reset Temperature Calibration", self
        )
        self.action_reset_temp_calibration.setStatusTip("Reset the temperature calibration.")
        self.action_reset_temp_calibration.triggered.connect(self._reset_temperature_calibration)
        toolbar.addAction(self.action_reset_temp_calibration)

    def _toggle_output(self, state=None) -> None:
        """
        Toolbar action; Allows to turn the pwm output on or off.

        :type state: bool
        :param state: Set True to turn the output state to on, or False vice versa.
        """
        if state is not None:
            self.action_toggle_output.setChecked(state)
        if self.action_toggle_output.isChecked():
            # Enable output
            self.setup.enable_output(self.stack.currentWidget().desired_pwm_output())
            # Change appearance of button
            self.action_toggle_output.setStyleSheet(
                """
            QPushButton {
                background: rgba(255, 51, 0, 100);
            }
            """
            )
        else:
            # Disable output
            self.setup.disable_output()
            # Change appearance of button
            self.action_toggle_output.setStyleSheet(
                """
            QPushButton {
                background: rgba(0, 102, 255, 100);
            }
            """
            )

    def _change_competition_mode(self) -> None:
        """
        Toolbar action; Allows to set the current view to competition mode.
        """
        if self.action_competition_mode.isChecked():
            # enter competition mode
            self.stack.currentWidget().switch_to_competition_mode()
        else:
            # leave competition mode
            self.stack.currentWidget().switch_to_normal_mode()

    def _stop_recording(self) -> None:
        """
        Toolbar action; Allows to stop recording measurements and thus freeze the plots.
        :return:
        """
        self.action_stop_recording.setDisabled(True)
        self.setup.stop_buffering()
        self.stack.currentWidget().pause()
        self.action_start_recording.setEnabled(True)

    def _start_recording(self) -> None:
        """
        Toolbar action; Allows to restart recording measurements. Clears the buffer.
        """
        self.action_start_recording.setDisabled(True)
        self.setup.start_buffering()
        self.action_stop_recording.setEnabled(True)

    def _go_to_previous_view(self) -> None:
        """
        Toolbar action; Switches to the previous view in the main layout stack.
        """
        if self.stack.currentIndex() == 0:
            pass
        else:
            self.action_competition_mode.setChecked(False)
            self.stack.currentWidget().leave()
            self.stack.setCurrentIndex(self.stack.currentIndex() - 1)
            self.stack.currentWidget().enter()
            if self.stack.currentIndex() == 0:
                self.action_previous_view.setDisabled(True)
                self.action_next_view.setEnabled(True)

    def _go_to_next_view(self) -> None:
        """
        Toolbar action; Switches to the next view in the main layout stack.
        """
        if self.stack.currentIndex() == self.stack.count() - 1:
            pass
        else:
            self.action_competition_mode.setChecked(False)
            self.stack.currentWidget().leave()
            self.stack.setCurrentIndex(self.stack.currentIndex() + 1)
            self.stack.currentWidget().enter()
            if self.stack.currentIndex() == self.stack.count() - 1:
                self.action_next_view.setDisabled(True)
                self.action_previous_view.setEnabled(True)

    def _reset_plots(self) -> None:
        """
        Toolbar action; Allows to reset all visible plots to their original view.
        """
        self.stack.currentWidget().reset_plots()

    def _calibrate_temperature(self) -> None:
        """
        Toolbar action; Allows to set the current delta T to zero by saving the current
        temperature difference and subtracting it from the second temperature measurement.
        """
        self.setup.set_temperature_calibration()

    def _reset_temperature_calibration(self) -> None:
        """
        Toolbar action; Allows to reset the calibration temperature difference to zero.
        """
        self.setup.reset_temperature_calibration()

    def setup_status_bar(self) -> None:
        """
        Sets up a status bar displaying sponsor layouts and tips for hovered over widgets.
        """
        sensirion_img = QPixmap(resource_path("Icons\\sensirion.png"))
        sensirion_logo = QLabel(self)
        sensirion_logo.setPixmap(sensirion_img.scaledToHeight(32))
        sensirion_logo.setAlignment(Qt.AlignLeft)
        eth_img = QPixmap(resource_path("Icons\\eth.png"))
        eth_logo = QLabel(self)
        eth_logo.setPixmap(eth_img.scaledToHeight(32))
        eth_logo.setAlignment(Qt.AlignRight)
        status_bar = QStatusBar(self)
        status_bar.addPermanentWidget(sensirion_logo)
        status_bar.addPermanentWidget(eth_logo)
        self.setStatusBar(status_bar)


class Launcher(object):
    """
    Wrapper for the main window, simply launches the Qt application.

    :type setup: Setup
    :param setup: Instance of Setup to allow access to sensors and actuators.
    """

    def __init__(self, setup: Setup):
        self.setup = setup

        app = QApplication([])
        window = MainWindow(setup=setup)
        window.showMaximized()
        app.exec_()
