from struct import unpack, pack
from sensirion_shdlc_driver import ShdlcConnection, ShdlcDevice, ShdlcSerialPort
from DeviceIdentifier import DeviceIdentifier
from serial.serialutil import SerialException
import time

import logging

logger = logging.getLogger(__name__)

SHDLC_IO_ERROR_CODES = {
    0x20: 'sensor busy',
    0x21: 'no ack from sensor',
    0x22: 'i2c crc false',
    0x23: 'sensor timeout',
    0x24: 'no measurement started'
}


class ShdlcIoModule(ShdlcDevice):
    """
    SHDLC driver for the IO box
    """

    def __init__(self, serial_port, baudrate=115200, slave_address=0, input_pins=None):
        """
        Parameters
        ----------
        serial_port: Comport the IO box is connected to
        baudrate: Baudrate of the connection
        slave_address: Slave address
        input_pins: list of integers of the input pins
        """
        shdlc_port = ShdlcSerialPort(port=serial_port, baudrate=baudrate)
        connection = ShdlcConnection(port=shdlc_port)

        super(ShdlcIoModule, self).__init__(connection=connection, slave_address=slave_address)

        if input_pins is None:
            input_pins = range(0, 6)

        self._input_pins = input_pins
        logger.debug("SHDLC box connected.")

    def is_connected(self):
        try:
            self.get_serial_number()
        except SerialException:
            return False
        return True


    def disconnect(self):
        self.set_all_digital_io_off()
        time.sleep(0.1)
        self.set_analog_output(value=0.0)
        time.sleep(0.1)
        self.set_pwm(pwm_bit=0, dc=0)
        time.sleep(0.1)
        self.set_pwm(pwm_bit=1, dc=0)
        logger.debug("SHDLC box disconnected.")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()

    def get_digital_io(self, io_bit):
        """

        Parameters
        ----------
        io_bit: Output bit to read

        Returns: True if digital bit is set.
        -------

        """
        p_level, err = self._connection.transceive(
            command_id=0x28,
            data=[io_bit],
            slave_address=self._slave_address,
            response_timeout=1
        )
        if err:
            logger.error('Digital IO {} could not be read'.format(io_bit))
            return -1
        else:
            return unpack('?', p_level)[0]

    def set_digital_io(self, io_bit, value):
        """

        Parameters
        ----------
        io_bit: The digital bit number to set
        value: True if set to on

        Returns
        -------

        """
        data = 1 if value else 0
        self._connection.transceive(
            command_id=0x28,
            data=[io_bit, data],
            slave_address=self._slave_address,
            response_timeout=1
        )

    def set_all_digital_io_off(self):
        for i in self._input_pins:
            self.set_digital_io(i, False)

    def get_analog_input(self):
        """
        Measure actual voltage on ADC input

        Returns: A voltage between 0-10V
        -------

        """
        data, err = self._connection.transceive(
            command_id=0x2b,
            data=[],
            slave_address=self._slave_address,
            response_timeout=1)
        if err:
            logger.error('Analog input could not be read.')
            return -1
        else:
            adc_value = unpack('>H', data)[0] / 65535.0 * 10.0
            return adc_value

    def get_analog_output(self):
        """
        Get actual voltage for DAC output

        Returns A voltage between 0-10V
        -------

        """
        data, err = self._connection.transceive(
            command_id=0x2a,
            data=[],
            slave_address=self._slave_address,
            response_timeout=1)
        if err:
            logger.error('Analog output could not be read.')
            return -1
        else:
            dac_value = unpack('>H', data)[0] / 65535.0 / 10.0
            return dac_value

    def set_analog_output(self, value):
        """
        Set the analog output

        Parameters
        ----------
        value: A voltage between 0-10V

        """
        adc_value = int(value / 10.0 * 65535)
        data = bytearray(pack('>H', adc_value))
        self._connection.transceive(
            command_id=0x2a,
            data=data,
            slave_address=self._slave_address,
            response_timeout=1)

    def set_pwm(self, pwm_bit, dc):
        """
        Set the pwm output

        Parameters
        ----------
        pwm_bit: The PWM bit (0, 1)
        dc: A duty cycle value between 0 - 65535

        """
        data = [pwm_bit] + list(bytearray(pack('>H', dc)))
        self._connection.transceive(
            command_id=0x29,
            data=data,
            slave_address=self._slave_address,
            response_timeout=1)

    def get_pwm(self, pwm_bit):
        """
        Parameters
        ----------
        pwm_bit: The PWM bit (0, 1)

        Returns A duty cycle value between 0 - 65535
        -------

        """
        p_dutycycle, err = self._connection.transceive(
            command_id=0x29,
            data=[pwm_bit],
            slave_address=self._slave_address,
            response_timeout=1)
        if err:
            logger.error('PWM {} could not be read'.format(pwm_bit))
            return -1
        else:
            return unpack('>H', p_dutycycle)[0]


if __name__ == "__main__":
    serials = {
        'Heater': 'AM01ZB7J'
    }
    devices = DeviceIdentifier(serials=serials)
    with ShdlcIoModule(serial_port=devices.serial_ports['Heater']) as h:
        # Testing digital io
        print(h.get_digital_io(io_bit=0))
        h.set_digital_io(io_bit=0, value=True)
        print(h.get_digital_io(io_bit=0))
        h.set_all_digital_io_off()
        print(h.get_digital_io(io_bit=0))

        # Testing analog io
        print(h.get_analog_input())
        h.set_analog_output(value=1.0)
        print(h.get_analog_output())
        h.set_analog_output(value=0.0)

        # Testing PWM io
        print(h.get_pwm(pwm_bit=0))
        h.set_pwm(pwm_bit=0, dc=1000)
        print(h.get_pwm(pwm_bit=0))
        h.set_pwm(pwm_bit=0, dc=0)
