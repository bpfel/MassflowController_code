import logging
from collections import deque

logger = logging.getLogger("root")


class MeasurementBuffer(object):
    def __init__(self, signals, sampling_time_s, buffer_interval_s):
        self._signals = signals
        self._data = dict()
        buffer_length = int(buffer_interval_s / sampling_time_s)
        for signal in signals:
            self._data[signal] = deque(maxlen=buffer_length)

    def update(self, measurement: dict):
        if set(measurement.keys()) != set(self._signals):
            logger.error("Incorrect set of signals supplied!")
        for signal, value in measurement.items():
            self._data[signal].append(value)

    def __getitem__(self, item):
        if item in self._signals:
            return self._data[item]
        else:
            raise KeyError("Signal {} is not available!".format(item))
