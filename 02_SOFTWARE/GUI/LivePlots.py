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
        self.setBackground('w')
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
                shifted_time_axis = numpy.array(self.setup.measurement_buffer["Time"]) - \
                                    self.setup.measurement_buffer["Time"][
                                        -1] + self.setup.interval_s
                for signal in self.signals:
                    signal.data_line.setData(shifted_time_axis, self.setup.measurement_buffer[signal.identifier])
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
                "Use set_ylims to define y-axis limits before reseting the plot layout for plot {}".format(self.title))
        self.setXRange(0, self.setup.interval_s)
