from Drivers import Sht3x
from Drivers import Sfc5400
from Drivers import ShdlcIoModule
from Drivers import DeviceIdentifier

import logging
import sys
logger = logging.getlogger(__name__)


class Setup(object):
    # Standard methods
    def __init__(self, serials):
        # Setup logging
        ch = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        logger.setLevel(logging.DEBUG)

        # allocate member variables
        self._serials = serials
        self._devices = None

    def open(self):
        # Find all USB devices and identify them
        self._devices = DeviceIdentifier(serials=self._serials)

        # Connect all sensors / actuators
        self._sht_one = Sht3x(serial_port=self._devices.serial_ports['EKS'], device_port='ONE')
        self._sht_one.open()
        self._sht_two = Sht3x(serial_port=self._devices.serial_ports['EKS'], device_port='TWO')
        self._sht_two.open()
        self._sfc = Sfc5400(serial_port=self._devices.serial_ports['SFC'])
        self._sfc.open()
        self._heater = ShdlcIoModule(serial_port=self._devices.serial_ports['Heater'])

    def close(self):
        self._sht_one.disconnect()
        self._sht_two.disconnect()
        self._sfc.disconnect()
        self._heater.disconnect()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if isinstance(exc_val, KeyboardInterrupt):
            logger.info("Experiment aborted with Keyboard-Interrupt!")
            self.close()
            return True
        elif isinstance(exc_val, BaseException) or isinstance(exc_val, Exception):
            logger.info("An unhandled error of type '{}' occured. "
                        "Please check console output!".format(exc_type.__name__))
            self.close()
        else:
            self.close()

    # API
    def measure(self):
        pass

    def start_pid_controller(self):
        pass

    def start_direct_power_setting(self):
        pass
