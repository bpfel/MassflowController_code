Installation
============

Windows 10
##########

#. `Install python 3.8 <https://www.python.org/>`_ or newer.
#. Set your PATH variable such that it includes the `Scripts` folder of your python installation.
#. Go to `01_SETUP/WINDOWS` and run `py -m setup` in the cmd shell.
#. Install `Sensirion Control Center <ttps://www.sensirion.com/de/controlcenter/>`_ to allow the sensor bridge to
   communication with the computer. Important: Select yes when asked for driver installation at the end of the process.
#. Find the finished executable at `02_SOFTWARE/disp`.

.. _debugging:

Debugging
*********

The installation is based on pyinstaller. It is configured via the `02_SOFTWARE/main.spec` file. Set `debug=True`
and `console=True` to receive informative output on the cmd shell upon launching the program.

