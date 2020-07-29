import collections
import logging

logger = logging.getLogger('root')

class RingBuffer(object):
    """
    A simple circular buffer to store the most up-to-date part of a time series.
    """

    def __init__(self, maxlen):
        self.maxlen = maxlen
        self._data = collections.deque(maxlen=maxlen)

    def update(self, value):
        self._data.append(value)

    @property
    def data(self):
        return list(self._data)


