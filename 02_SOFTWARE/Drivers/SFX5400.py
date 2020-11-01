from sensirion_shdlc_driver import ShdlcSerialPort, ShdlcConnection, ShdlcDevice
from sensirion_shdlc_driver.errors import ShdlcTimeoutError
from sensirion_shdlc_driver.command import ShdlcCommand
from struct import pack, unpack
from Drivers.SensorBase import SensorBase
import logging

logger = logging.getLogger("root")

FLOW_UNIT = 1  # 0 = Normalized (0..1) / 1 = Physical / 2 = User Defined
MAXIMUM_FLOW_SLM = 100
FLOW_MEASUREMENT_NAME = "Flow"


class Sfc5400ShdlcCmdSetSetpoint(ShdlcCommand):
    def __init__(self, setpoint_normalized):
        super(Sfc5400ShdlcCmdSetSetpoint, self).__init__(
            id=0x00,
            data=pack(">Bf", FLOW_UNIT, setpoint_normalized),
            max_response_time=5e-3,
        )


class Sfc5400ShdlcCmdGetDeviceInformation(ShdlcCommand):
    def __init__(self, index):
        super(Sfc5400ShdlcCmdGetDeviceInformation, self).__init__(
            id=0xD0, data=[index], max_response_time=10e-3
        )


class Sfc5400ShdlcCmdReadMeasuredFlow(ShdlcCommand):
    def __init__(self):
        super(Sfc5400ShdlcCmdReadMeasuredFlow, self).__init__(
            id=0x08, data=[FLOW_UNIT], max_response_time=5e-3
        )

    def interpret_response(self, data):
        return unpack(">f", data)[0]


class SFX5400(SensorBase):
    """
    SFX5400 represents either a Sensirion Flow Controller (SFC) or a Sensirion Flow Meter (SFM) of type 5400.

    :type serial_port: str
    :param serial_port: Name of the comport the SFX is connected to.
    :type name: str
    :param name: Name of the device.
    """

    def __init__(self, serial_port: str, name="Sfc5400"):
        super(SFX5400, self).__init__(name)
        self.port = serial_port
        self.ShdlcPort = None
        self.ShdlcDevice = None

    def connect(self) -> bool:
        """
        Attempts to connect to the SFX and reports success.

        :return: True if connected successifully, False otherwise.
        """
        try:
            self.ShdlcPort = ShdlcSerialPort(port=self.port, baudrate=115200)
            self.ShdlcDevice = ShdlcDevice(
                ShdlcConnection(self.ShdlcPort), slave_address=0
            )
        except Exception as e:
            return e
        return True

    def disconnect(self) -> None:
        """
        Disconnects the device.
        """
        self.set_flow(0)
        self.ShdlcPort.close()

    def measure(self) -> dict:
        """
        Measures the current mass flow.

        :return: Dictionary containing the measurement.
        """
        result = self.ShdlcDevice.execute(Sfc5400ShdlcCmdReadMeasuredFlow())
        return {FLOW_MEASUREMENT_NAME: result}

    def set_flow(self, setpoint_normalized: float) -> bool:
        """
        Sets the current desired mass flow if a flow controller is connected.

        :type setpoint_normalized: float
        :param setpoint_normalized: Flow setpoint as normalized input between 0 and 1.
        :return: True if set successifully, False if exception occured.
        """
        if FLOW_UNIT == 1:
            setpoint_normalized *= MAXIMUM_FLOW_SLM
        try:
            self.ShdlcDevice.execute(Sfc5400ShdlcCmdSetSetpoint(setpoint_normalized))
        except Exception as e:
            logger.error(
                "Could not set the mass flow. Make sure there is a mass "
                "flow controller connected: {}".format(e)
            )
            return False
        return True

    def get_device_information(self, index: int) -> str:
        """
        Retrieves device information depending on the index given.

        :type index: int
        :param index: Integer between 1 and 3 to request on of the data below:

            #. Product Name
            #. Article Code
            #. Serial number

        :return: String containing the requested information.
        """
        return self.ShdlcDevice.execute(Sfc5400ShdlcCmdGetDeviceInformation(index))

    def is_connected(self):
        """
        Checks if the device is connected by reading its serial number.

        :return: True if connected, False if not.
        """
        try:
            self.ShdlcDevice.get_serial_number()
        except (TimeoutError, ShdlcTimeoutError, AttributeError):
            return False
        return True


if __name__ == "__main__":
    from Drivers.DeviceIdentifier import DeviceIdentifier
    from Utility.Logger import setup_custom_logger
    from logging import getLevelName

    logger = setup_custom_logger(name="root", level=getLevelName("DEBUG"))

    serials = {
        "SFC": "FTVQSB5S",
    }
    devices = DeviceIdentifier(serials=serials)
    with SFX5400(serial_port=devices.serial_ports["SFC"]) as sfc:
        sfc.open()
        print(sfc.measure())
