from Drivers.SHT31 import EKS
from Drivers.SFC5400 import Sfc5400
from Drivers.Shdlc_IO import ShdlcIoModule
from Drivers.DeviceIdentifier import DeviceIdentifier
from Utility.MeasurementBuffer import MeasurementBuffer
from Utility.Timer import RepeatTimer
import logging

logger = logging.getLogger('root')

class Setup(object):
    # Standard methods
    def __init__(self, serials):
        # allocate member variables
        self._serials = serials
        self._devices = None
        signals = {
            'Temperature 1', 'Temperature 2', 'Humidity 1', 'Humidity 2', 'Flow'
        }
        self._measurement_buffer = MeasurementBuffer(signals=signals, buffer_length=200)
        self._measurement_timer = None

    def open(self):
        # Find all USB devices and identify them
        self._devices = DeviceIdentifier(serials=self._serials)

        # Connect all sensors / actuators
        self._eks = EKS(serial_port=self._devices.serial_ports['EKS'])
        self._eks.open()
        self._sfc = Sfc5400(serial_port=self._devices.serial_ports['SFC'])
        self._sfc.open()
        self._heater = ShdlcIoModule(serial_port=self._devices.serial_ports['Heater'])
        self._heater.open()

    def close(self):
        self.stop_measurement_thread()
        self._eks.close()
        self._sfc.close()
        self._heater.close()

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
        results_eks = self._eks.measure()
        results_sfc = self._sfc.measure()
        results = {
            'Temperature 1': results_eks[0]['Temperature'],
            'Temperature 2': results_eks[1]['Temperature'],
            'Humidity 1': results_eks[0]['Humidity'],
            'Humidity 2': results_eks[1]['Humidity'],
            'Flow': results_sfc['Flow'],
        }
        logger.info('Measuring once...')
        self._measurement_buffer.update(results)

    def start_measurement_thread(self, t_sampling_sec):
        if self._measurement_timer is None:
            self._measurement_timer = RepeatTimer(t_sampling_sec, self.measure)
            self._measurement_timer.start()
            logger.info('Started measurement thread running at t_s={} s'.format(t_sampling_sec))
        else:
            logger.error('Measurement thread already running!')

    def stop_measurement_thread(self):
        if self._measurement_timer is not None:
            self._measurement_timer.cancel()
            logger.info('Stopped measurement thread.')
        else:
            logger.error('Measurement thread not started yet!')

    def start_pid_controller(self):
        pass

    def start_direct_power_setting(self):
        pass
