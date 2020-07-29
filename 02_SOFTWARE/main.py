from setup import Setup
from Utility.Logger import setup_custom_logger
from logging import getLevelName
import time

logger = setup_custom_logger(name='root', level=getLevelName('DEBUG'))

if __name__ == "__main__":
    # Get the comports
    serials = {
        'SDP': 'FTSTZ7P',
        'EKS': 'EKS231R5DL',
        'SFC': 'FTVQSB5S',
        'Heater': 'AM01ZB7J'
    }
    with Setup(serials=serials) as setup:
        setup.open()
        setup.measure()
        time.sleep(0.1)
        setup.start_measurement_thread(t_sampling_sec=1)
        time.sleep(3)
