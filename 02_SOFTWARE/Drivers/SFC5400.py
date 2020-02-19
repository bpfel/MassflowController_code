from sensirion_shdlc_driver import ShdlcSerialPort, ShdlcConnection, ShdlcDevice
from sensirion_shdlc_driver.command import ShdlcCommand
from struct import pack, unpack

import logging
from . import SensorBase

logging.basicConfig(level=logging.INFO)

FLOW_UNIT = 0  # 0 = Normalized (0..1) / 1 = Physical / 2 = User Defined


class Sfc5400ShdlcCmdSetSetpoint(ShdlcCommand):
    def __init__(self, setpoint_normalized):
        super(Sfc5400ShdlcCmdSetSetpoint, self).__init__(
            id=0x00,
            data=pack(">Bf", FLOW_UNIT, setpoint_normalized),
            max_response_time=5e-3,
        )


class Sfc5400ShdlcCmdReadMeasuredFlow(ShdlcCommand):
    def __init__(self):
        super(Sfc5400ShdlcCmdReadMeasuredFlow, self).__init__(
            id=0x08,
            data=[FLOW_UNIT],
            max_response_time=5e-3,
        )

    def interpret_response(self, data):
        return unpack('>f', data)[0]

class Sfc5400(SensorBase):

