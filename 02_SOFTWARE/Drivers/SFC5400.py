from sensirion_shdlc_driver import ShdlcSerialPort, ShdlcConnection, ShdlcDevice
from sensirion_shdlc_driver.command import ShdlcCommand
from struct import pack, unpack

import logging
from Drivers.SensorBase import SensorBase

logging.basicConfig(level=logging.INFO)

FLOW_UNIT = 0  # 0 = Normalized (0..1) / 1 = Physical / 2 = User Defined
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
            id=0xD0,
            data=[index],
            max_response_time=10e-3
        )


class Sfc5400ShdlcCmdReadMeasuredFlow(ShdlcCommand):
    def __init__(self):
        super(Sfc5400ShdlcCmdReadMeasuredFlow, self).__init__(
            id=0x08,
            data=[FLOW_UNIT],
            max_response_time=5e-3
        )

    def interpret_response(self, data):
        return unpack('>f', data)[0]


class Sfc5400(SensorBase):
    def __init__(self, serial_port, name="Sfc5400"):
        super(Sfc5400, self).__init__(name)
        self.port = serial_port
        self.ShdlcPort = None
        self.ShdlcDevice = None

    def connect(self):
        try:
            self.ShdlcPort = ShdlcSerialPort(port=self.port, baudrate=115200)
            self.ShdlcDevice = ShdlcDevice(ShdlcConnection(self.ShdlcPort), slave_address=0)
        except Exception as e:
            return e
        return True

    def disconnect(self):
        self.port.close()

    def measure(self):
        result = self.ShdlcDevice.execute(Sfc5400ShdlcCmdReadMeasuredFlow())
        return {FLOW_MEASUREMENT_NAME: result}

    def set_flow(self, setpoint_normalized):
        self.ShdlcDevice.execute(Sfc5400ShdlcCmdSetSetpoint(setpoint_normalized))

    def get_device_information(self, index):
        """
        Returns device information
        Parameters
        ----------
        index
            1 : Product Name
            2 : Article Code
            3 : Serial number
        """
        self.ShdlcDevice.execute(Sfc5400ShdlcCmdGetDeviceInformation(index))

    def is_connected(self):
        #todo: implement check whether connected
        pass


if __name__ == "__main__":
    with Sfc5400(port="/dev/ttyUSB0") as sfc:
        sfc.open()
        print(sfc.measure())
