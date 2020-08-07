from Drivers.SHT31 import EKS
from Drivers.SFC5400 import Sfc5400
from Drivers.Shdlc_IO import ShdlcIoModule
from Drivers.DeviceIdentifier import DeviceIdentifier
from Utility.MeasurementBuffer import MeasurementBuffer
from Utility.Timer import RepeatTimer
from Utility.Controller import pid_controller, p_controller
import logging
import time
from enum import Enum


class Mode(Enum):
    IDLE = 0
    FORCE_PWM = 2
    PID = 3


logger = logging.getLogger('root')


class Setup(object):
    # Standard methods
    def __init__(self, serials):
        # allocate member variables
        self._serials = serials
        self._devices = None
        signals = {
            'Temperature 1', 'Temperature 2', 'Humidity 1',
            'Humidity 2', 'Flow', 'Time', 'Temperature Difference',
            'PWM', 'Flow Estimate'
        }
        self.measurement_buffer = MeasurementBuffer(signals=signals, buffer_length=100)
        # Initialize members
        self._measurement_timer = None
        self._eks = None
        self._sfc = None
        self._heater = None
        self._sdp = None
        self._current_pwm_value = 0
        self._current_mode = 'Idle'
        self._setpoint = 0
        self._initial_time = time.time()
        # self.controller = pid_controller(k_p=0.3, k_i=0, k_d=0, tau=4, t_s=0.3, lower_limit=0, upper_limit=1)
        self.controller = p_controller(k_p=0.3, lower_limit=0, upper_limit=1)
        self.controller.assign_buffers(value_buffer=self.measurement_buffer['Temperature Difference'])

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
        results_timestamp = time.time() - self._initial_time
        delta_T = results_eks[1]['Temperature'] - results_eks[0]['Temperature']
        results = {
            'Temperature 1': results_eks[0]['Temperature'],
            'Temperature 2': results_eks[1]['Temperature'],
            'Humidity 1': results_eks[0]['Humidity'],
            'Humidity 2': results_eks[1]['Humidity'],
            'Flow': results_sfc['Flow'],
            'Time': results_timestamp,
            'Temperature Difference': delta_T,
            'PWM': self._current_pwm_value,
            'Flow Estimate': 46432.0*self._current_pwm_value*24.0*24.0/(11.0*1006.0*delta_T)
        }
        logger.info('Measuring once...')
        self.measurement_buffer.update(results)
        if self._current_mode is Mode.PID:
            desired_pwm = self.controller.update(target_value=self._setpoint)
            self.set_pwm(desired_pwm)

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

    def set_pwm(self, value):
        value = float(value)
        if not 0.0 <= value <= 1.0:
            raise ValueError('PWM value: {} has to be between 0 and 1'.format(value))
        self._current_pwm_value = value
        # convert to heater units:
        value = int(value * 65535.0)
        self._heater.set_pwm(pwm_bit=0, dc=value)

    def wrap_set_pwm(self, value):
        if self._current_mode is not Mode.FORCE_PWM:
            raise RuntimeError('PWM cannot be forced if system is not in FORCE_PWM mode!')
        self.set_pwm(value)

    def start_pid_controller(self, setpoint):
        self._current_mode = Mode.PID
        self._setpoint = setpoint

    def start_direct_power_setting(self):
        self._current_mode = Mode.FORCE_PWM
        self.set_pwm(value=0)
