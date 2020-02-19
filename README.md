# MassflowController_code
Contains all the code needed to set up the computing platform and interact with the sensors for the mass flow experiment.

## Setup of the Raspberry Pi

1. Download [Raspbian Buster with desktop and recommended software](https://www.raspberrypi.org/downloads/raspbian/)
2. Follow the [installation guide](https://www.raspberrypi.org/documentation/installation/installing-images/README.md)
3. To ensure access when you have no peripherals, follow the [setup of a headless Raspberry Pi](https://www.raspberrypi.org/documentation/configuration/wireless/headless.md)
4. `git clone https://github.com/bpfel/MassflowController_code.git`
5. Install required packages using the setup script in this repository.
```
cd MassflowController_code/01_SETUP
sudo /bin/sh -c './setup.sh'
```
6. The RPi will reboot. After that connect all Sensors and execute `tty_setup.ssh`
7. Check if all sensors show up as tty_USB devices using 
```
python -m serial.tools.list_ports
```
