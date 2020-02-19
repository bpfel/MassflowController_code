from abc import ABC, abstractmethod
import logging

logger = logging.getLogger("Massflow_INFO")


class SensorBase(object, ABC):
    """
    Abstract base class for all sensors used in this project.
    """

    def __init__(self, name):
        self.name = name

        logger.debug('Ceating Sensor "{}"'.format(self.name))

    @abstractmethod
    def open(self):
        logger.debug('Connecting Sensor "{}"...'.format(self.name))
        if self.connect():
            logger.info('... connected {} successfully!'.format(self.name))
        else:
            logger.info('... could not connect {}!'.format(self.name))

    @abstractmethod
    def close(self):
        # todo: find common closing actions
        if self.is_connected():
            self.disconnect()
        logger.debug('Closing Sensor "{}"'.format(self.name))

    @abstractmethod
    def is_connected(self):
        pass

    @abstractmethod
    def disconnect(self):
        pass

    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def measure(self):
        pass
