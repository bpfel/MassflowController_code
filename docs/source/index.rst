Software Documentation: Air Mass Flow Sensor
============================================

This project contains the software for a student experiment at ETH Zürich based on sponsorship
by Sensirion AG. The student experiment aims to illustrate the sensor principle of a thermal air mass flow meter,
which is investigated mainly from the control point of view. The students are required to implement control algorithms
for the regulation of the heater.

The software provided here mainly does two things:

#. Communication with all attached devices:

   #. Sensirion SHT temperature sensors connected to a Sensirion Sensor Bridge
   #. A Sensirion SFM massflow meter
   #. A custom built heater being driven with a PWM signal

   This task is taken over by the :ref:`setup` class. It handles all interactions with the hardware and
   for this purpose makes use of the different drivers, as seen on page :ref:`drivers`.

#. Allowing interactions:

   #. Displaying the current system status
   #. Walking the student through different steps of the experimentation
   #. Handling interactions with the setup

   These tasks are solved with a PyQt5 based graphical user interface as described in section :ref:`GUI`.

Troubleshooting
***************

When experiencing issues with soft- or hardware consider section :ref:`troubleshooting`.

Acknowledgements
****************

The icons in the GUI are made by `Yusuke Kamiyamane <https://p.yusukekamiyamane.com>`_ and used under
`CC BY 3.0 <https://p.yusukekamiyamane.com>`_.

The GUI frontend, `QT 5.0 <https://www.qt.io>`_ is used under `LGPL 3.0 <https://www.gnu.org/licenses/lgpl-3.0.html>`_.

.. toctree::
   :hidden:

   installation
   setup
   drivers
   GUI
   troubleshooting
