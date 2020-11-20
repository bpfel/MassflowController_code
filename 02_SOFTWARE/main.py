from setup import Setup
from Utility.Logger import setup_custom_logger
from GUI.Launcher import Launcher
from logging import getLevelName
from yaml import load, CLoader as Loader

logger = setup_custom_logger(name="root", level=getLevelName("DEBUG"))

if __name__ == "__main__":
    # load configuration
    config = load(open('Utility/config.yaml'), Loader=Loader)
    with Setup(config=config) as setup:
        setup.open()
        setup.start_measurement_thread()
        launcher = Launcher(setup=setup)
