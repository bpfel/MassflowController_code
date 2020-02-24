from abc import ABC, abstractmethod
import logging
from threading import RLock
import sys

class SensorBase(ABC):
    """
    Abstract base class for all sensors used in this project.
    """

    def __init__(self, name):
        self.name = name
        self._lock = RLock()
        # Set up sensor-specific logger
        self.logger = logging.getLogger("Sensor {}".format(name))
        self.logger.setLevel(logging.DEBUG)
        ch = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)
        self.logger.debug('Creating Sensor "{}"'.format(self.name))

    def open(self):
        self.logger.debug('Connecting Sensor "{}"...'.format(self.name))
        answer = self.connect()
        if answer:
            self.logger.info('... connected {} successfully!'.format(self.name))
        else:
            self.logger.info('... could not connect {}! {}'.format(self.name, answer))

    def close(self):
        if self.is_connected():
            self.disconnect()
        self.logger.debug('Closing Sensor "{}"'.format(self.name))

    @abstractmethod
    def disconnect(self):
        pass

    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def is_connected(self):
        pass

    @abstractmethod
    def measure(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

