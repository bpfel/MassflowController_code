from __future__ import annotations

from abc import ABC, abstractmethod
import logging
from threading import RLock

logger = logging.getLogger("root")


class SensorBase(ABC):
    """
    Abstract base class for all sensors used in this project.

    :type name: str
    :param name: Each sensor must have a unique name.
    """

    def __init__(self, name) -> None:
        self.name = name
        self._lock = RLock()
        # Set up sensor-specific logger
        logger.info('Creating Sensor "{}"'.format(self.name))

    def open(self) -> bool:
        """
        Attempts to connect the sensor and reports success.
        :return: True fi connected successifully, False otherwise
        """
        logger.info('Connecting Sensor "{}"...'.format(self.name))
        answer = self.connect()
        if answer:
            logger.info("... connected {} successfully!".format(self.name))
        else:
            logger.info("... could not connect {}! {}".format(self.name, answer))
        return answer

    def close(self) -> None:
        """
        Disconnects the sensor if it is currently connected.
        """
        if self.is_connected():
            self.disconnect()
        logger.info('Closing Sensor "{}"'.format(self.name))

    @abstractmethod
    def disconnect(self):
        raise NotImplementedError("'disconnect' not implemented for sensor {}".format(self.name))

    @abstractmethod
    def connect(self):
        raise NotImplementedError("'connect' not implemented for sensor {}".format(self.name))

    @abstractmethod
    def is_connected(self):
        raise NotImplementedError("'is_connected' not implemented for sensor {}".format(self.name))

    @abstractmethod
    def measure(self):
        raise NotImplementedError("'measure' not implemented for sensor {}".format(self.name))

    def __enter__(self) -> SensorBase:
        """
        Ensures compatibility with 'with' statement.
        :return: Returns a reference to the current instance.
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Called when exiting the context established by the 'with' statement.

        .. warning: Only use this class inside a 'with' statement to ensure calling the shut down procedure for every
           connected platform even upon an unscheduled end of the program.
        """
        self.close()
