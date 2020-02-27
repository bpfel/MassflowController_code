from abc import ABC, abstractmethod
import logging
logger = logging.getLogger(__name__)
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
        logger.info('Creating Sensor "{}"'.format(self.name))

    def open(self):
        logger.info('Connecting Sensor "{}"...'.format(self.name))
        answer = self.connect()
        if answer:
            logger.info('... connected {} successfully!'.format(self.name))
        else:
            logger.info('... could not connect {}! {}'.format(self.name, answer))

    def close(self):
        if self.is_connected():
            self.disconnect()
        logger.info('Closing Sensor "{}"'.format(self.name))

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
