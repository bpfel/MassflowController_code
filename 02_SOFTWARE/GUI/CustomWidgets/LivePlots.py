import pyqtgraph
from setup import Setup
from PyQt5.QtCore import QTimer
from typing import Tuple
import numpy
import logging

logger = logging.getLogger("root")


class LivePlotSignal(object):
    """
    A LivePlotSignal stores all the information needed to identify and plot a single signal.

    :type name: str
    :param name: Name of the signal, to be displayed on the legend of the plot the signal is shown on
    :type identifier: str
    :param identifier: Identifier of the signal, used to retrieve the signal from the measurement buffer of the setup
    :type color: str
    :param color: Color of the plotted line used to instantiate the corresponding pen
    :type width: float
    :param width: Width of the plotted line used to instantiate the corresponding pen

    .. note::
       Selecting integer values for the width parameter results in smoother plots.
    """

    def __init__(self, name: str, identifier: str, color: str, width=1):
        self.name = name
        self.identifier = identifier
        self.pen = pyqtgraph.mkPen(color=color, width=width)
        self.data_line = None


class LivePlotWidget(pyqtgraph.PlotWidget):
    """
    The LivePlotWidget makes use of pyqtgraph to allow plotting a number of signals. It automatically updates.

    :type setup: Setup
    :param setup: Instance of the current setup to allow access to the measurement buffer
    :type title: str
    :param title: Title of the plot
    :type ylabel: str
    :param ylabel: Label of the y-axis
    :type ylims: Tuple
    :param ylims: Limits of the y-axis
    """

    def __init__(
        self, setup: Setup, title: str, ylabel: str, ylims: Tuple, *args, **kwargs
    ) -> None:
        super(LivePlotWidget, self).__init__(*args, **kwargs)
        self.setup = setup
        self.signals = []
        self.ylims = ylims
        self.title = title

        # Standard visual setup for plots:
        self.showGrid(x=True, y=True, alpha=0.7)
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

    def add_signals(self, signals: list) -> None:
        """
        Add a list of signals to the plot.

        :type signals: list
        :param signals: List of LivePlotSignals
        """
        self.addLegend()
        for signal in signals:
            # Create a line in the plot
            signal.data_line = pyqtgraph.PlotCurveItem(
                [], [], pen=signal.pen, name=signal.name
            )
            # Add the signal
            self.signals.append(signal)
            self.addItem(signal.data_line)

    def update_plot_data(self):
        """
        Handles the updating of a LivePLotWidget.
        """
        if self.setup.measurement_buffer["Time"]:
            if self.signals:
                shifted_time_axis = (
                    numpy.array(self.setup.measurement_buffer["Time"])
                    - self.setup.measurement_buffer["Time"][-1]
                    + self.setup.interval_s
                )
                n_entries = len(shifted_time_axis)
                for signal in self.signals:
                    signal.data_line.setData(
                        numpy.asarray(shifted_time_axis).flatten(),
                        numpy.asarray(
                            self.setup.measurement_buffer[signal.identifier]
                        ).flatten()[0:n_entries],
                    )
            else:
                # No signals added yet
                pass
        else:
            # No signals recorded yet
            pass

    def reset_plot_layout(self) -> None:
        """
        Allows to reset the plot layout to the original view
        """
        if self.ylims is not None:
            self.setYRange(self.ylims[0], self.ylims[1])
        else:
            logger.error(
                "Use set_ylims to define y-axis limits before reseting the plot layout for plot {}".format(
                    self.title
                )
            )
        self.setXRange(0, self.setup.interval_s)


class LivePlotWidgetCompetition(LivePlotWidget):
    """
    Specialized LivePLotWidget allowing only two signals and adding color between the two corresponding lines.
    Used to visualize the integral of the control error.
    """

    def __init__(self, setup: Setup, title, ylabel, ylims, *args, **kwargs) -> None:
        super(LivePlotWidgetCompetition, self).__init__(
            setup=setup, title=title, ylabel=ylabel, ylims=ylims, *args, **kwargs
        )
        self.fill_between = None

    def add_signals(self, reference_signal, actual_signal):
        self.addLegend()
        reference_signal.data_line = pyqtgraph.PlotCurveItem(
            [], [], pen=reference_signal.pen, name=reference_signal.name
        )
        actual_signal.data_line = pyqtgraph.PlotCurveItem(
            [], [], pen=actual_signal.pen, name=actual_signal.name
        )
        brush = pyqtgraph.mkBrush(color=(255, 0, 0, 50))
        self.fill_between = pyqtgraph.FillBetweenItem(
            curve1=reference_signal.data_line,
            curve2=actual_signal.data_line,
            brush=brush,
        )
        self.signals.append(reference_signal)
        self.signals.append(actual_signal)
        self.addItem(actual_signal.data_line)
        self.addItem(reference_signal.data_line)
        self.addItem(self.fill_between)

    def update_plot_data(self):
        if self.setup.measurement_buffer["Time"]:
            if self.signals:
                shifted_time_axis = (
                    numpy.array(self.setup.measurement_buffer["Time"])
                    - self.setup.measurement_buffer["Time"][-1]
                    + self.setup.interval_s
                )
                n_entries = len(shifted_time_axis)
                for signal in self.signals:
                    signal.data_line.setData(
                        numpy.asarray(shifted_time_axis).flatten(),
                        numpy.asarray(
                            self.setup.measurement_buffer[signal.identifier]
                        ).flatten()[0:n_entries],
                    )
                self.fill_between.setCurves(
                    curve1=self.signals[0].data_line, curve2=self.signals[1].data_line
                )


class PlotWidgetFactory:
    """
    The PlotWidgetFactory defines a simple interface for creating instances of previously defined LivePlotWidgets.
    """

    def __init__(self, setup):
        self.setup = setup

    def delta_t(self):
        graph_delta_t = LivePlotWidget(
            setup=self.setup,
            title="Temperature Difference",
            ylabel="Temperature Difference [°C]",
            ylims=(0, self.setup.temperature_difference_setpoint + 5),
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
            ylims=(20, 40),
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
            name="PID", identifier="Controller Output", color="k", width=2
        )
        graph_pid.add_signals([singal_p, signal_i, signal_d, signal_pid])
        return graph_pid

    def power(self):
        graph_power = LivePlotWidget(
            setup=self.setup, title="Power", ylabel="Power [%]", ylims=(0, 1)
        )
        signal_power = LivePlotSignal(name="Power", identifier="PWM", color="k")
        graph_power.add_signals([signal_power])
        return graph_power

    def delta_t_competition(self):
        graph_delta_t = LivePlotWidgetCompetition(
            setup=self.setup,
            title="Temperature Difference",
            ylabel="Temperature Difference [°C]",
            ylims=(0, self.setup.temperature_difference_setpoint + 5),
        )
        signal_actual_delta_t = LivePlotSignal(
            name="Actual Delta T", identifier="Temperature Difference", color="b"
        )
        signal_target_delta_t = LivePlotSignal(
            name="Target Delta T", identifier="Target Delta T", color="r"
        )
        graph_delta_t.add_signals(
            actual_signal=signal_actual_delta_t, reference_signal=signal_target_delta_t
        )
        return graph_delta_t
