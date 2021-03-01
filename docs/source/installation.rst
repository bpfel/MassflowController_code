Installation
============

Windows 10
##########

Setup GUI
*********

#. `Install python 3.8 <https://www.python.org/>`_ or newer.
#. Set your PATH variable such that it includes the `Scripts` folder of your python installation.
#. Go to `01_SETUP/WINDOWS` and run `py -m setup` in the cmd shell.
#. Install `Sensirion Control Center <https://www.sensirion.com/de/controlcenter/>`_ to allow the sensor bridge to
   communication with the computer. Important: Select yes when asked for driver installation at the end of the process.
#. Find the finished executable at `02_SOFTWARE/disp`.

Setup Sensirion USB Sensor Viewer
*********************************

#. Install the `Sensirion USB Sensor Viewer <https://www.sensirion.com/en/environmental-sensors/usb-sensor-viewer/>`_.
#. Select COM HARDWARE: `RS485/USB Sensor Cable`.
#. Select Sensor Product: `DP Sensors (SDP3x/SDP8xx)`.
#. Execute `Drivers/identify_differential_pressure_sensor.py` with a local python environment.
   This will give you an overview of all connected sensors and print the comport ID of the pressure sensor in the final
   line.
#. Enter the previously found comport number in the RS485 Sensor viewer and connect.

.. _debugging:

Debugging
*********

The installation is based on pyinstaller. It is configured via the `02_SOFTWARE/main.spec` file. Set `debug=True`
and `console=True` to receive informative output on the cmd shell upon launching the program.

