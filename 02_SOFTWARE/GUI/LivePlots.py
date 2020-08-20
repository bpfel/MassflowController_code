import pyqtgraph
from setup import Setup
from PyQt5.QtCore import QTimer
import numpy
import logging

logger = logging.getLogger("root")


class LivePlotSignal(object):
    def __init__(self, name, identifier, color):
        self.name = name
        self.identifier = identifier
        self.pen = pyqtgraph.mkPen(color=color)
        self.data_line = None


class LivePlotWidget(pyqtgraph.PlotWidget):
    def __init__(self, setup: Setup, title, ylabel, ylims, *args, **kwargs):
        super(LivePlotWidget, self).__init__(*args, **kwargs)
        self.setup = setup
        self.signals = []
        self.ylims = ylims
        self.title = title

        # Standard visual setup for plots:
        self.setBackground("w")
        self.setXRange(0, self.setup.interval_s)
        self.setYRange(ylims[0], ylims[1])
        self.setTitle(title)
        self.setLabel("bottom", "Time [s]")
        self.setLabel("left", ylabel)

        # Set up timer for live plotting
        self.timer = QTimer()
        self.timer.setInterval(50)
        self.timer.timeout.connect(self.update_plot_data)
        self.timer.start()

    def add_signals(self, signals):
        self.addLegend()
        for signal in signals:
            # Create a line in the plot
            signal.data_line = self.plot([], [], pen=signal.pen, name=signal.name)
            # Add the signal
            self.signals.append(signal)

    def update_plot_data(self):
        if self.setup.measurement_buffer["Time"]:
            if self.signals:
                shifted_time_axis = (
                    numpy.array(self.setup.measurement_buffer["Time"])
                    - self.setup.measurement_buffer["Time"][-1]
                    + self.setup.interval_s
                )
                for signal in self.signals:
                    signal.data_line.setData(
                        shifted_time_axis,
                        self.setup.measurement_buffer[signal.identifier],
                    )
            else:
                # No signals added yet
                pass
        else:
            # No signals recorded yet
            pass

    def reset_plot_layout(self):
        if self.ylims is not None:
            self.setYRange(self.ylims[0], self.ylims[1])
        else:
            logger.error(
                "Use set_ylims to define y-axis limits before reseting the plot layout for plot {}".format(
                    self.title
                )
            )
        self.setXRange(0, self.setup.interval_s)


class PlotWidgetFactory:
    def __init__(self, setup):
        self.setup = setup

    def delta_t(self):
        graph_delta_t = LivePlotWidget(
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
        graph_delta_t.add_signals([signal_actual_delta_t, signal_target_delta_t])
        return graph_delta_t

    def temperatures(self):
        graph_temperatures = LivePlotWidget(
            setup=self.setup,
            title="Temperatures",
            ylabel="Temperature [°C]°",
            ylimes=(20, 40),
        )
        signal_temperature_one = LivePlotSignal(
            name="Temperature 1", identifier="Temperature 1", color="b"
        )
        signal_temperature_two = LivePlotSignal(
            name="Temperature 2", identifier="Temperature 2", color="r"
        )
        graph_temperatures.add_signals([signal_temperature_one, signal_temperature_two])
        return graph_temperatures

    def flow(self):
        graph_flow = LivePlotWidget(
            setup=self.setup, title="Flow", ylabel="Flow [slm]", ylims=(0, 100)
        )
        signal_flow = LivePlotSignal(
            name="Flow Measurement", identifier="Flow", color="b"
        )
        signal_flow_estimate = LivePlotSignal(
            name="Flow Estimate", identifier="Flow Estimate", color="r"
        )
        graph_flow.add_signals([signal_flow, signal_flow_estimate])
        return graph_flow

    def pid(self):
        graph_pid = LivePlotWidget(
            setup=self.setup, title="PID Components", ylabel="Gain", ylims=(-1, 1)
        )
        singal_p = LivePlotSignal(name="P", identifier="Controller Output P", color="r")
        signal_i = LivePlotSignal(name="I", identifier="Controller Output I", color="g")
        signal_d = LivePlotSignal(name="D", identifier="Controller Output D", color="b")
        signal_pid = LivePlotSignal(
            name="PID", identifier="Controller Output", color="k"
        )
        graph_pid.add_signals([singal_p, signal_i, signal_d, signal_pid])
        return graph_pid

    def power(self):
        graph_power = LivePlotWidget(
            setup=self.setup, title="Power", ylabel="Power [%]", ylims=(0, 100)
        )
        signal_power = LivePlotSignal(name="Power", identifier="PWM", color="k")
        graph_power.add_signals([signal_power])
        return graph_power
