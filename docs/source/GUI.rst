.. _GUI:

GUI
===

The structure of the graphical user interface can be described as follows: The outermost layer is a simple launcher,
that deploys the main Qt application and loads the main window.

.. autoclass:: GUI.Launcher.Launcher
   :members:

The main window then controls the different experiment pages :py:mod:`GUI.ExperimentPages`, one for each
experimentation step, with a stacked layout and manages the switching between those pages. The pages are built up
from a series of widgets as defined ADDREFERENCEHERE

Main Window
***********

.. autoclass:: GUI.Launcher.MainWindow
   :members:
   :private-members:

Widgets
*******

.. autoclass:: GUI.CustomWidgets.Widgets.FancyPointCounter
   :members:
   :private-members:

.. autoclass:: GUI.CustomWidgets.Widgets.CompetitionWidget
   :members:
   :private-members:

.. autoclass:: GUI.CustomWidgets.Widgets.StatusWidget
   :members:
   :private-members:

Live Plots
**********

.. autoclass:: GUI.CustomWidgets.LivePlots.LivePlotSignal
   :members:
   :private-members:

.. autoclass:: GUI.CustomWidgets.LivePlots.LivePlotWidget
   :members:
   :private-members:

.. autoclass:: GUI.CustomWidgets.LivePlots.LivePlotWidgetCompetition
   :members:
   :private-members:

.. autoclass:: GUI.CustomWidgets.LivePlots.PlotWidgetFactory
   :members:
   :private-members:


