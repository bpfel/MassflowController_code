import collections

class RingBuffer(object):
    """
    A simple circular buffer to store the most up-to-date part of a time series.
    #todo: Decide whether to use extra interface to collections
    """

    def __init__(self, maxlen):
        self.maxlen = maxlen
        self.data = collections.deque(maxlen=maxlen)


