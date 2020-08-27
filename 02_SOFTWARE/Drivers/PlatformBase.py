from __future__ import annotations

from abc import ABC, abstractmethod
import logging
from threading import RLock

logger = logging.getLogger("root")


class PlatformBase(ABC):
    """
    Abstract base class for all platforms used in this project.

    :type name: str
    :param name: Each platform must have a unique name.
    """

    def __init__(self, name: str) -> None:
        self.name = name
        self._lock = RLock()
        # Set up sensor-specific logger
        logger.info('Creating platform "{}"'.format(self.name))

    def open(self) -> bool:
        """
        Attempts to connect the platform and reports success.

        :return: True if connected succesifully, False otherwise.
        """
        logger.info('Connecting platform "{}"...'.format(self.name))
        answer = self.connect()
        if answer:
            logger.info("... connected {} successfully!".format(self.name))
        else:
            logger.info("... could not connect {}! {}".format(self.name, answer))
        return answer

    def close(self) -> None:
        """
        Disconnects the platform if it is currently connected.
        """
        if self.is_connected():
            self.disconnect()
        logger.info('Closing platform "{}"'.format(self.name))

    @abstractmethod
    def disconnect(self):
        raise NotImplementedError(
            "'disconnect' not implemented for platform {}".format(self.name)
        )

    @abstractmethod
    def connect(self):
        raise NotImplementedError(
            "'connect' not implemented for platform {}".format(self.name)
        )

    @abstractmethod
    def is_connected(self):
        raise NotImplementedError(
            "'is_connected' not implemented for platform {}".format(self.name)
        )

    def __enter__(self) -> PlatformBase:
        """
        Ensures compatibility with 'with' statement.

        :return: Returns a reference to the current instance.
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Called when exiting the context established by the 'with' statement.

        .. warning::
           Only use this class inside a 'with' statement to ensure calling the shut down procedure for every
           connected platform even upon an unscheduled end of the program.
        """
        self.close()
