import logging
from collections import deque

logger = logging.getLogger("root")


class MeasurementBuffer(object):
    """
    The MeasurementBuffer holds a number of deque instances, one for each recorded signal and manages them as a
    ring buffer, always keeping a record of the most up to date measurements, reaching back `buffer_interval_s` seconds.

    :type signals: list
    :param signals: List of signal names.
    :type sampling_time_s: float
    :param sampling_time_s: Measurement sampling time in seconds.
    :type buffer_interval_s: float
    :param buffer_interval_s: Total buffered time interval in seconds which together with the sampling time defines the
       number of measurements to be stored.
    """

    def __init__(
        self, signals: list, sampling_time_s: float, buffer_interval_s: float
    ) -> None:
        self._signals = signals
        self._data = dict()
        buffer_length = int(buffer_interval_s / sampling_time_s)
        for signal in signals:
            self._data[signal] = deque(maxlen=buffer_length)

    def update(self, measurement: dict) -> None:
        """
        A buffer update is done by adding an entry to each signal buffer. Before the buffer is full this leads
        to an increase in length, afterwards the deque instances automatically forget their oldest entry in favor
        of the new one.

        :type measurement: object
        :param measurement: Dictionary containing a value for each signal name
        """
        if set(measurement.keys()) != set(self._signals):
            logger.error("Incorrect set of signals supplied!")
            raise AttributeError("Incorrect number of signals applied!")
        for signal, value in measurement.items():
            self._data[signal].append(value)

    def __getitem__(self, item: str) -> deque:
        """
        Allows access of the individual signals via the __getitem__ operator.

        :type item: str
        :param item: Identifier of the desired signal.
        :return: A deque instance containing the requested signal.

        :raises KeyError: If the supplied string is not a key in the _data dictionary a KeyError is raised.
        """
        if item in self._signals:
            return self._data[item]
        else:
            logger.error("Signal {} is not available!".format(item))
            raise KeyError("Signal {} is not available!".format(item))

    def clear(self) -> None:
        """
        Clears the buffer.
        """
        logger.info("Clearing the measurement buffer.")
        for signal in self._signals:
            self._data[signal].clear()
