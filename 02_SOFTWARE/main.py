from setup import Setup
from Utility.Logger import setup_custom_logger
from Utility.ConfigurationHandler import ConfigurationHandler
from GUI.MainWindow import Launcher
from logging import getLevelName

logger = setup_custom_logger(name="root", level=getLevelName("DEBUG"))

if __name__ == "__main__":
    with Setup(config=ConfigurationHandler()) as setup:
        setup.open()
        setup.start_measurement_thread()
        launcher = Launcher(setup=setup)
