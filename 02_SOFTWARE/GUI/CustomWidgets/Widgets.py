from GUI.CustomWidgets.Basis import *
import logging
import numpy
import time

logger = logging.getLogger("root")


class FancyPointCounter(QLCDNumber):
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
    def __init__(
        self, setup, start_action, stop_action, enable_output_action, *args, **kwargs
    ):
        super(CompetitionWidget, self).__init__(*args, **kwargs)
        self.setup = setup
        self.stop = stop_action
        self.start = start_action
        self.output = enable_output_action

        self.fancy_counter = FancyPointCounter(setup=setup)
        self.start_button = QPushButton(
            QIcon("./GUI/Icons/control-record.png"), "", self
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

    def _start_recording(self):
        if self.setup.results["Temperature Difference"] < 0.5:
            self.initial_time = time.time()
            self.timer.start()
            self.fancy_counter.start()
            self.progressbar.setValue(0)
            self.start()
            self.setup.measurement_buffer.clear()
            self.output(True)
            self.start_button.setDisabled(True)
        else:
            self.error_message.showMessage(
                "Recording a game is only possible if the current temperature difference is smaller 0.5°C!"
            )

    def _update_progress(self):
        running_time_s = time.time() - self.initial_time
        if running_time_s < self.wait_time_s:
            self.progressbar.setValue(time.time() - self.initial_time)
        else:
            self.timer.stop()
            self.fancy_counter.stop()
            self.progressbar.setValue(self.progressbar.maximum())
            self.stop()
            self.output(False)
            self.start_button.setEnabled(True)
            self.success_message.showMessage(
                "Congratulations, you accumulated only {} points!".format(
                    self.fancy_counter.value
                )
            )

    def reset(self):
        self.fancy_counter.reset()


class StatusWidget(FramedWidget):
    def __init__(self, setup, *args, **kwargs):
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

    def _update_lcds(self):
        for key, lcd in self.lcds.items():
            if key == "FL":
                lcd.number.display("{:.1f}".format(self.setup.results[lcd.signal]))
            else:
                lcd.number.display("{:.2f}".format(self.setup.results[lcd.signal]))
