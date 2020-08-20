from PyQt5.QtWidgets import *
from GUI.LivePlots import LivePlotWidget, LivePlotSignal
from GUI.CustomWidgets import AnnotatedSlider


class ExperimentPageOne(QWidget):
    def __init__(self, setup):
        super(ExperimentPageOne, self).__init__()
        self.setup = setup
        # Create controls
        self.pwm = AnnotatedSlider(min=0, max=100, title="Heating Power [%]")
        self.pwm.value = self.setup._current_pwm_value
        self.pwm.slider.valueChanged.connect(self.set_pwm_value)

        # Create visualization
        self.graph_delta_t = LivePlotWidget(
            setup=self.setup,
            title="Temperature Difference",
            ylabel="Temperature Difference [°C]",
            ylims=(0, 10),
        )
        signal_actual_delta_t = LivePlotSignal(
            name="Actual Delta T", identifier="Temperature Difference", color="b"
        )
        signal_target_delta_t = LivePlotSignal(
            name="Target Delta T", identifier="Target Delta T", color="r"
        )
        self.graph_delta_t.add_signals([signal_actual_delta_t, signal_target_delta_t])

        self.graph_power = LivePlotWidget(
            setup=self.setup, title="Power", ylabel="Power [%]", ylims=(0, 100)
        )
        signal_power = LivePlotSignal(name="Power", identifier="PWM", color="k")
        self.graph_power.add_signals([signal_power])

        # Add widgets to layout
        horizontal_layout = QHBoxLayout()
        vertical_layout_control = QVBoxLayout()
        vertical_layout_control.addWidget(self.pwm)
        vertical_layout_control.addWidget(QLabel(), 1)
        vertical_layout_plots = QVBoxLayout()
        vertical_layout_plots.addWidget(self.graph_delta_t)
        vertical_layout_plots.addWidget(self.graph_power)
        horizontal_layout.addLayout(vertical_layout_control, 1)
        horizontal_layout.addLayout(vertical_layout_plots, 3)
        self.setLayout(horizontal_layout)

    def set_pwm_value(self):
        self.setup.wrap_set_pwm(value=self.pwm.value)


class ExperimentPageTwo(QWidget):
    def __init__(self, setup):
        super(ExperimentPageTwo, self).__init__()
        self.setup = setup

        # Create controls
        self.p_gain = AnnotatedSlider(min=0, max=0.1, title="K_p")
        self.i_gain = AnnotatedSlider(min=0, max=0.1, title="K_i")
        self.d_gain = AnnotatedSlider(min=0, max=0.1, title="K_d")

        # Create Visualization
        self.graphWidget = LivePlotWidget(
            setup=self.setup, title="Flow Plot", ylabel="Flow [slm]", ylims=(0, 100)
        )
        first_signal = LivePlotSignal(
            name="Flow Reference", identifier="Flow", color="b"
        )
        second_signal = LivePlotSignal(
            name="Flow Estimate", identifier="Flow Estimate", color="r"
        )
        self.graphWidget.add_signals([first_signal, second_signal])

        # Add widgets to layout
        horizontal_layout = QHBoxLayout()
        vertical_layout = QVBoxLayout()
        vertical_layout.addWidget(self.p_gain)
        vertical_layout.addWidget(self.i_gain)
        vertical_layout.addWidget(self.d_gain)
        vertical_layout.addWidget(QLabel(), 1)
        horizontal_layout.addLayout(vertical_layout, 1)
        horizontal_layout.addWidget(self.graphWidget, 3)
        self.setLayout(horizontal_layout)
