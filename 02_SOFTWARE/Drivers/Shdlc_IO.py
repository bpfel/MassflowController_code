from struct import unpack, pack
from sensirion_shdlc_driver import ShdlcConnection, ShdlcDevice, ShdlcSerialPort

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

    def get_digital_io(self, io_bit):
        """

        Parameters
        ----------
        io_bit: Output bit to read

        Returns: True if digital bit is set.
        -------

        """
        p_level = self._connection.transceive(0x28, [io_bit], self._slave_address)
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
        data = self._connection.transceive(
            command_id=0x2b,
            data=[],
            slave_address=self._slave_address,
            response_timeout=1)
        adc_value = unpack('>H', data)[0] / 65535.0 * 10.0
        return adc_value

    def get_analog_output(self):
        """
        Get actual voltage for DAC output

        Returns A voltage between 0-10V
        -------

        """
        data = self._connection.transceive(
            command_id=0x2a,
            data=[],
            salve_address=self._slave_address,
            response_timeout=1)
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
        p_dutycycle = self._connection.transceive(
            command_id=0x29,
            data=[pwm_bit],
            slave_address=self._slave_address,
            response_timeout=1)
        return unpack('>H', p_dutycycle)[0]
