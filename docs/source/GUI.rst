.. _GUI:

GUI
===

The structure of the graphical user interface can be described as follows: The outermost layer is a simple launcher,
that deploys the main Qt application and loads the main window.

.. autoclass:: GUI.Launcher.Launcher
   :members:

The main window then controls the different experiment pages :py:class:`GUI.ExperimentPages.ExperimentPage`, one for
each experimentation step, with a stacked layout and manages the switching between those pages. The pages are built up
from a series of widgets as defined in sections :ref:`widgets` and :ref:`liveplots`.

Main Window
***********

.. autoclass:: GUI.Launcher.MainWindow
   :members:
   :private-members:

.. _widgets:

Widgets
*******

.. autoclass:: GUI.CustomWidgets.Widgets.FancyPointCounter
   :members:
   :private-members:
   :show-inheritance:

.. autoclass:: GUI.CustomWidgets.Widgets.CompetitionWidget
   :members:
   :private-members:
   :show-inheritance:

.. autoclass:: GUI.CustomWidgets.Widgets.StatusWidget
   :members:
   :private-members:
   :show-inheritance:

.. _liveplots:

Live Plots
**********

.. autoclass:: GUI.CustomWidgets.LivePlots.LivePlotSignal
   :members:
   :private-members:

.. autoclass:: GUI.CustomWidgets.LivePlots.LivePlotWidget
   :members:
   :private-members:
   :show-inheritance:

.. autoclass:: GUI.CustomWidgets.LivePlots.LivePlotWidgetCompetition
   :members:
   :private-members:
   :show-inheritance:

.. autoclass:: GUI.CustomWidgets.LivePlots.PlotWidgetFactory
   :members:
   :private-members:
   :show-inheritance:


