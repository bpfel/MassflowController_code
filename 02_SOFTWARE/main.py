from Drivers.SHT31 import Sht3x
from Drivers.SFC5400 import Sfc5400

import logging
import sys
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    # Setup logging
    ch = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    logger.setLevel(logging.DEBUG)

    # Connect sensors
    sht1 = Sht3x(serial_port='/dev/ttyUSB2', device_port='ONE')
    sht1.open()
    print(sht1.measure())

    sfc1 = Sfc5400(port='/dev/ttyUSB0')
    sfc1.open()
    print(sfc1.measure())
    pass
