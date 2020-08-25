from setup import Setup
from Utility.Logger import setup_custom_logger
from GUI.Launcher import Launcher
from logging import getLevelName

logger = setup_custom_logger(name="root", level=getLevelName("DEBUG"))

if __name__ == "__main__":
    serials = {"EKS": "EKS23Z8C1I", "SFC": "FT1PXV63", "Heater": "AM01ZB7J"}
    with Setup(serials=serials, t_sampling_s=0.25, interval_s=50) as setup:
        setup.open()
        setup.start_measurement_thread()
        launcher = Launcher(setup=setup)
