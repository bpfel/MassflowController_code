from struct import unpack, pack
from sensirion_shdlc_driver import ShdlcConnection, ShdlcDevice, ShdlcSerialPort
from sensirion_shdlc_driver.errors import ShdlcTimeoutError
from serial.serialutil import SerialException
from Drivers.PlatformBase import PlatformBase
import time
import logging

logger = logging.getLogger("root")

SHDLC_IO_ERROR_CODES = {
    0x20: "sensor busy",
    0x21: "no ack from sensor",
    0x22: "i2c crc false",
    0x23: "sensor timeout",
    0x24: "no measurement started",
}


class ShdlcIoModule(PlatformBase):
    """
    ShdlcIoModule represents the custom Sensirion HDLC IO Box that allows driving the heater with a PWM output.

    :type serial_port: str
    :param serial_port: Comport the IO box is connected to
    :type baudrate: int
    :param baudrate: Baudrate of the connection
    :type slave_address: int
    :param slave_address: Slave address
    :type input_pins: list
    :param input_pins: list of integers of the input pins
    """

    def __init__(
        self, serial_port: str, baudrate=115200, slave_address=0, input_pins=None
    ) -> None:
        self.ShdlcDevice = None
        self._serial_port = serial_port
        self._baudrate = baudrate
        self._slave_address = slave_address
        super(ShdlcIoModule, self).__init__(name="Heater")

        if input_pins is None:
            input_pins = range(0, 6)

        self._input_pins = input_pins
        logger.debug("SHDLC box connected.")

    def connect(self) -> bool:
        """
        Attempts to connect the ShdlcIoModule

        :return: True if connected successifully, False otherwise.
        """
        try:
            shdlc_port = ShdlcSerialPort(
                port=self._serial_port, baudrate=self._baudrate
            )
            connection = ShdlcConnection(port=shdlc_port)
            self.ShdlcDevice = ShdlcDevice(
                connection=connection, slave_address=self._slave_address
            )
        except Exception as e:
            logger.error("Could not connect ShdlcIoModule: {}".format(e))
            return False
        return True

    def is_connected(self) -> bool:
        """
        Attempts to read the serial number of the device to check if it is connected.

        :return: True if connected, False otherwise.
        """
        try:
            self.ShdlcDevice.get_serial_number()
        except (SerialException, ShdlcTimeoutError) as e:
            logger.error("Could not reach ShdlcIoBox: {}".format(e))
            return False
        return True

    def disconnect(self) -> None:
        """
        Sets all outputs of.
        """
        self.set_all_digital_io_off()
        time.sleep(0.1)
        self.set_analog_output(value=0.0)
        time.sleep(0.1)
        self.set_pwm(pwm_bit=0, dc=0)
        time.sleep(0.1)
        self.set_pwm(pwm_bit=1, dc=0)

    def __enter__(self):
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
        self.disconnect()

    def get_digital_io(self, io_bit: int) -> bool:
        """
        Reads a digital io pin.

        :type io_bit: int
        :param io_bit: Output bit to read
        :return: True if digital bit is set.
        """
        p_level, err = self.ShdlcDevice._connection.transceive(
            command_id=0x28,
            data=[io_bit],
            slave_address=self._slave_address,
            response_timeout=1,
        )
        if err:
            logger.error("Digital IO {} could not be read".format(io_bit))
            return -1
        else:
            return unpack("?", p_level)[0]

    def set_digital_io(self, io_bit: int, value: bool) -> None:
        """
        Sets a digital output pin.

        :type io_bit: int
        :param io_bit: The digital pin index to set
        :type value: bool
        :param value: True if set to on
        """
        data = 1 if value else 0
        self.ShdlcDevice._connection.transceive(
            command_id=0x28,
            data=[io_bit, data],
            slave_address=self._slave_address,
            response_timeout=1,
        )

    def set_all_digital_io_off(self) -> None:
        """
        Turns of all digital pins.
        """
        for i in self._input_pins:
            self.set_digital_io(i, False)

    def get_analog_input(self) -> float:
        """
        Measure actual voltage on ADC input

        :return: A voltage between 0-10V
        """
        data, err = self.ShdlcDevice._connection.transceive(
            command_id=0x2B,
            data=[],
            slave_address=self._slave_address,
            response_timeout=1,
        )
        if err:
            logger.error("Analog input could not be read.")
            return -1
        else:
            adc_value = unpack(">H", data)[0] / 65535.0 * 10.0
            return adc_value

    def get_analog_output(self) -> float:
        """
        Get actual voltage for DAC output

        :return: A voltage between 0-10V
        """
        data, err = self.ShdlcDevice._connection.transceive(
            command_id=0x2A,
            data=[],
            slave_address=self._slave_address,
            response_timeout=1,
        )
        if err:
            logger.error("Analog output could not be read.")
            return -1
        else:
            dac_value = unpack(">H", data)[0] / 65535.0 / 10.0
            return dac_value

    def set_analog_output(self, value: int) -> None:
        """
        Set the analog output

        :type value: int
        :param value: A voltage between 0-10V
        """
        adc_value = int(value / 10.0 * 65535)
        data = bytearray(pack(">H", adc_value))
        self.ShdlcDevice._connection.transceive(
            command_id=0x2A,
            data=data,
            slave_address=self._slave_address,
            response_timeout=1,
        )

    def set_pwm(self, pwm_bit: int, dc: int) -> None:
        """
        Set the pwm output

        :type pwm_bit: int
        :param pwm_bit: The index of the PWM channel to be used (0, 1)
        :type dc: int
        :param dc:
        :return: A duty cycle value between 0 - 65535
        """
        data = [pwm_bit] + list(bytearray(pack(">H", dc)))
        self.ShdlcDevice._connection.transceive(
            command_id=0x29,
            data=data,
            slave_address=self._slave_address,
            response_timeout=1,
        )

    def get_pwm(self, pwm_bit: int) -> int:
        """
        Read the current pwm setting.

        :type pwm_bit: int
        :param pwm_bit: The index of the PWM channel to be used (0, 1)
        :return: A duty cycle value between 0 - 65535
        """
        p_dutycycle, err = self.ShdlcDevice._connection.transceive(
            command_id=0x29,
            data=[pwm_bit],
            slave_address=self._slave_address,
            response_timeout=1,
        )
        if err:
            logger.error("PWM {} could not be read".format(pwm_bit))
            return -1
        else:
            return unpack(">H", p_dutycycle)[0]


if __name__ == "__main__":
    from Drivers.DeviceIdentifier import DeviceIdentifier
    from Utility.Logger import setup_custom_logger
    from logging import getLevelName

    logger = setup_custom_logger(name="root", level=getLevelName("DEBUG"))

    serials = {"Heater": "AM01ZB7J"}
    devices = DeviceIdentifier(serials=serials)
    with ShdlcIoModule(serial_port=str(devices.serial_ports["Heater"])) as h:
        h.connect()
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
