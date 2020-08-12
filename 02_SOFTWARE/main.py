from setup import Setup
from Utility.Logger import setup_custom_logger
from logging import getLevelName
from GUI.ExperimentOverview import ExperimentOverview

logger = setup_custom_logger(name="root", level=getLevelName("WARNING"))

if __name__ == "__main__":
    serials = {"EKS": "EKS23Z8C1I", "SFC": "FT1PXV63", "Heater": "AM01ZB7J"}
    with Setup(serials=serials, t_sampling_s=0.25, interval_s=50) as setup:
        setup.open()
        setup.start_measurement_thread()
        # Start up GUI
        GUI = ExperimentOverview(setup=setup)
