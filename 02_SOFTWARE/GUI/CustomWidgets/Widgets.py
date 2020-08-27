from GUI.CustomWidgets.Basis import *
from GUI.Utils import resource_path
from setup import Setup
from typing import Callable
import logging
import numpy
import time

logger = logging.getLogger("root")


class FancyPointCounter(QLCDNumber):
    """
    Custom version of the QLCDNumber.
    """

    def __init__(self, setup, *args, **kwargs):
        super(FancyPointCounter, self).__init__(*args, **kwargs)
        self.setup = setup
        self._value = 0

        # configure counter
        self.setFixedHeight(180)
        self.setFixedWidth(300)

        # Set up timer for live updating
        self.timer = QTimer()
        self.timer.setInterval(300)
        self.timer.timeout.connect(self._update_counter)

    def _update_counter(self):
        delta_t = numpy.asarray(
            self.setup.measurement_buffer["Temperature Difference"]
        ).flatten()
        target_delta_t = numpy.asarray(
            self.setup.measurement_buffer["Target Delta T"]
        ).flatten()
        errors = delta_t - target_delta_t
        squared_sums = numpy.sum(errors ** 2)
        self._value = int(squared_sums)
        self.display(self._value)

    def start(self):
        self.timer.start()

    def stop(self):
        self.timer.stop()

    def reset(self):
        self.display(0)

    @property
    def value(self):
        return self._value


class CompetitionWidget(FramedWidget):
    """
    The CompetitionWidget allows to start a recording of the current performance and displays the number of points
    reached.
    """

    def __init__(
        self,
        setup: Setup,
        start_recording_action: Callable,
        stop_recording_action: Callable,
        enable_output_action: Callable,
        *args,
        **kwargs
    ) -> None:
        super(CompetitionWidget, self).__init__(*args, **kwargs)
        self.setup = setup
        self.stop_recording = stop_recording_action
        self.start_recording = start_recording_action
        self.output = enable_output_action

        self.fancy_counter = FancyPointCounter(setup=setup)
        self.start_button = QPushButton(
            QIcon(resource_path("Icons\\control-record.png")), "", self
        )
        self.start_button.setFixedSize(32, 32)
        self.start_button.setStatusTip(
            "Start recording points. Only possible if dT < 0.5!"
        )
        self.start_button.clicked.connect(self._start_recording)

        # Set up error message
        self.error_message = QErrorMessage()
        self.success_message = QErrorMessage()
        # Set up time progress bar
        self.wait_time_s = 50
        self.progressbar = QProgressBar()
        self.progressbar.setMinimum(0)
        self.progressbar.setMaximum(50)

        # Set up layout
        self.horizontal_layout = QHBoxLayout()
        self.vertical_layout = QVBoxLayout()
        self.button_layout = QVBoxLayout()
        self.button_layout.addWidget(self.start_button)
        self.button_layout.addWidget(QLabel(), 1)

        self.vertical_layout.addLayout(self.horizontal_layout)
        self.vertical_layout.addWidget(self.progressbar)
        self.horizontal_layout.addLayout(self.button_layout)
        self.horizontal_layout.addWidget(QLabel(), 1)
        self.horizontal_layout.addWidget(self.fancy_counter)

        self.setLayout(self.vertical_layout)

        # Set up timer for live updating
        self.timer = QTimer()
        self.timer.setInterval(100)
        self.timer.timeout.connect(self._update_progress)
        self.initial_time = None

    def _start_recording(self) -> None:
        """
        Takes control of the whole setup and GUI to start the recording.

        .. note::
           This function can only be called successifully if the current temperature difference is smaller 0.5 degrees.
           This is necessary to prevent cheating.
        """
        if self.setup.results["Temperature Difference"] < 0.5:
            # Set the initial time of the recording
            self.initial_time = time.time()
            # Start the QTimer that controls the update rate of the widget
            self.timer.start()
            # Start the internal QTimer of the point counter
            self.fancy_counter.start()
            # Set the progress bar to initial value 0
            self.progressbar.setValue(0)
            # Start the buffering of new measurements
            self.start_recording()
            # Clear the measurement buffer to get rid of old measurements
            self.setup.measurement_buffer.clear()
            # Set the pwm output to on
            self.output(True)
            # Disable the start button for the duration of the recording
            self.start_button.setDisabled(True)
        else:
            self.error_message.showMessage(
                "Recording a game is only possible if the current temperature difference is smaller 0.5°C!"
            )

    def _update_progress(self) -> None:
        """
        Update the progressbar to show the current remaining time. If the recording interval has passed the process
        is stopped.
        """
        running_time_s = time.time() - self.initial_time
        if running_time_s < self.wait_time_s:
            self.progressbar.setValue(time.time() - self.initial_time)
        else:
            # Stop the QTimer updating this widget
            self.timer.stop()
            # Stop the QTimer of the counter
            self.fancy_counter.stop()
            # Show the final value of the progressbar, process completed
            self.progressbar.setValue(self.progressbar.maximum())
            # Stop recording measurement values to allow the user to inspect the measurement plot
            self.stop_recording()
            # Turn of the pwm output
            self.output(False)
            # Re-enable the start button of this widget
            self.start_button.setEnabled(True)
            # Show the final number of points and declare success
            self.success_message.showMessage(
                "Congratulations, you accumulated only {} points!".format(
                    self.fancy_counter.value
                )
            )

    def reset(self) -> None:
        """
        Reset the competition widget upon reloading it.
        """
        self.fancy_counter.reset()


class StatusWidget(FramedWidget):
    """
    The StatusWidget displays the current temperatures, flow and temperature difference measured.
    """

    def __init__(self, setup, *args, **kwargs) -> None:
        super(StatusWidget, self).__init__(*args, **kwargs)

        self.setup = setup
        # Widgets
        grid = QGridLayout()
        gbox_temp1 = QGroupBox("Temperature Sensor 1")
        gbox_temp2 = QGroupBox("Temperature Senosr 2")
        gbox_flow = QGroupBox("Flow Sensor")
        gbox_delta_t = QGroupBox("Temperature Difference")
        # LCDs
        self.lcds = {
            "T1": LabelledQLCD(signal="Temperature 1", title="Temperature [°C]"),
            "T2": LabelledQLCD(signal="Temperature 2", title="Temperature [°C]"),
            "H1": LabelledQLCD(signal="Humidity 1", title="Humidity [%]"),
            "H2": LabelledQLCD(signal="Humidity 2", title="Humidity [%]"),
            "FL": LabelledQLCD(signal="Flow", title="Flow [slm]"),
            "DT": LabelledQLCD(signal="Temperature Difference", title="Delta T [°C]"),
        }
        # Layouts
        hlayout_temp1 = QHBoxLayout()
        hlayout_temp2 = QHBoxLayout()
        hlayout_flow = QHBoxLayout()
        hlayout_delta_t = QHBoxLayout()

        # Put stuff together
        hlayout_temp1.addWidget(self.lcds["T1"])
        hlayout_temp1.addWidget(self.lcds["H1"])
        hlayout_temp2.addWidget(self.lcds["T2"])
        hlayout_temp2.addWidget(self.lcds["H2"])
        hlayout_flow.addWidget(self.lcds["FL"])
        hlayout_delta_t.addWidget(self.lcds["DT"])

        gbox_temp1.setLayout(hlayout_temp1)
        gbox_temp2.setLayout(hlayout_temp2)
        gbox_flow.setLayout(hlayout_flow)
        gbox_delta_t.setLayout(hlayout_delta_t)

        grid.addWidget(gbox_temp1, 0, 0)
        grid.addWidget(gbox_temp2, 1, 0)
        grid.addWidget(gbox_flow, 0, 1)
        grid.addWidget(gbox_delta_t, 1, 1)

        self.setLayout(grid)

        # Set up timer for live updating
        self.timer = QTimer()
        self.timer.setInterval(300)
        self.timer.timeout.connect(self._update_lcds)
        self.timer.start()

    def _update_lcds(self) -> None:
        """
        Updates the displayed values.
        """
        for key, lcd in self.lcds.items():
            if key == "FL":
                lcd.number.display("{:.1f}".format(self.setup.results[lcd.signal]))
            else:
                lcd.number.display("{:.2f}".format(self.setup.results[lcd.signal]))
