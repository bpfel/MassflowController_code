import logging
import numpy as np

logger = logging.getLogger("root")


class LivePlotHandler:
    def __init__(
        self,
        ax,
        fig,
        title,
        ylabel,
        ylims,
        signal_buffers,
        time_buffer,
        line_styles,
        legend_entries,
        interval,
    ):
        # Check input validity
        if len(signal_buffers) != len(line_styles) != len(legend_entries):
            raise AttributeError(
                "Number of signal buffers must be equal to number of line styles and number of legend entries."
            )
        # Set up line artists
        self.lines = []
        for line_style, legend_entry in zip(line_styles, legend_entries):
            (line,) = ax.plot([], [], line_style, label=legend_entry)
            self.lines.append(line)
        # Register members
        self.axis = ax
        self.interval = interval
        self.time_buffer = time_buffer
        self.signal_buffers = signal_buffers

        # Set the axis and plot titles
        self.axis.set_title(title)
        self.axis.set_xlabel("Time [s]")
        self.axis.set_ylabel(ylabel)

        # Set axis limits
        self.axis.set_xlim(0, self.interval)
        self.axis.set_ylim(ylims)

        # Set up the legend
        self.leg = fig.legend(
            handles=self.lines, loc="upper right", bbox_to_anchor=(0.9, 0.88)
        )

        # Counter for missing values
        self._missing_values = 0

    def __call__(self, i):
        if i == 0:
            for line in self.lines:
                line.set_data([], [])
            return self.lines
        if self.time_buffer:
            # Shift time such that the most up-to-date measurement is at the left of the plot
            t = np.array(self.time_buffer) - self.time_buffer[-1] + self.interval
            # Select only times that lie within the specified interval
            chosen_indices = t >= 0
            t_chosen = t[chosen_indices]
            # Go through all lines, draw the data, but only for the selected indices
            for line, signal_buffer in zip(self.lines, self.signal_buffers):
                line.set_data(t_chosen, np.array(signal_buffer)[chosen_indices])
        else:
            if self._missing_values < 10:
                self._missing_values += 1
            else:
                logger.warning("Empty measurement buffer!")
                self._missing_values = 0

        return self.lines
