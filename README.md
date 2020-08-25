# Air Massflow Sensor Setup
Contains all the code needed to set up the computing platform and interact with the sensors for the mass flow experiment.

# Setup on Windows 10

1. [Install python 3.8](https://www.python.org/) or newer.
2. Set your PATH variable such that it includes the `Scripts` folder of your python installation.
3. Go to `01_SETUP/WINDOWS` and run `py -m setup` in the cmd shell.
4. Install [Sensirion Control Center](https://www.sensirion.com/de/controlcenter/) to allow the sensor bridge to communication with the computer. Important: Select yes when asked for driver installation at the end of the process.
5. Find the finished executable at `02_SOFTWARE/disp'.

## Debugging
The installation is based on pyinstaller. It is configured via the `02_SOFTWARE/main.spec` file. Set `debug=True` and `console=True` to receive informative output+ on the cmd shell upon launching the program.


# Acknowledgements
The icons in the GUI are made by [Yusuke Kamiyamane](https://p.yusukekamiyamane.com) and used under [CC BY 3.0](https://p.yusukekamiyamane.com).

The GUI frontend, [QT 5.0](https://www.qt.io) is used under [LGPL 3.0](https://www.gnu.org/licenses/lgpl-3.0.html).