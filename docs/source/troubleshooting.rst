.. _troubleshooting:

FAQ
===

Below known issues, their possible causes and subsequent fixes are listed. The fixes are ordered by decreasing
likelihood so go from top to bottom retrying if the problem has been solved after every step.

Why don't I see real data?
**************************

Whenever the GUI is launched the setup tries to connect to all sensors. If that fails only simulated measurement
values are shown. This can happen for the following reasons:

* The hardware does not have power.

   #. Check whether the experiment is plugged in.

   #. Check whether the power switch on the back is turned on.

   #. Check whether the fuses are intact.

* One of the USB devices is not connected.

   #. Connect the setup to your computer and validate that new devices are registered. Check the serials entry in
      ``Utility\config.json`` to see how many devices are expected to connect.

   #. When working on Windows, it can happen that two devices are registered under the same comport ID. To check,
      open the device manager and see if a comport ID appears twice. To fix either reassign one of the comport IDs
      manually or simply reboot your computer.

Why does the temperature difference decrease when heating?
**********************************************************

* The temperature sensors are registered in the wrong order.

   #. Navigate to the dropdown menu on the top left ``Configuration -> Reverse Temperature Sensors``.

Why ... ?
*********

* The program runs, the sensors are connected but nothing works as expected.

   #. Turn on debug mode, which allows you to view real time logs. See section :ref:`debugging`.
