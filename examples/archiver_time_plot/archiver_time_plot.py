from pydm import Display

from qtpy import QtCore
from qtpy.QtWidgets import QHBoxLayout, QApplication
from pydm.widgets import PyDMArchiverTimePlot


class archiver_time_plot_example(Display):
    def __init__(self, parent=None, args=None, macros=None):
        super(archiver_time_plot_example, self).__init__(
            parent=parent, args=args, macros=None
        )
        self.app = QApplication.instance()
        self.setup_ui()

    def minimumSizeHint(self):
        return QtCore.QSize(100, 100)

    def ui_filepath(self):
        return None

    def setup_ui(self):
        self.main_layout = QHBoxLayout()
        self.setLayout(self.main_layout)
        self.plot_live = PyDMArchiverTimePlot(background=[255, 255, 255, 255])
        self.plot_archived = PyDMArchiverTimePlot(background=[255, 255, 255, 255])
        self.main_layout.addWidget(self.plot_live)
        self.main_layout.addWidget(self.plot_archived)

        self.plot_live.createCurveItem(
            y_channel="ca://DEMO:ANGLE",
            name="name",
            color="red",
            plot_by_timestamps=True,
            yAxisName="Axis",
            useArchiveData=True,
            noLiveData=False,
        )
        # self.plot.addCurve(curve_item)
        self.plot_live.addYChannel(
            y_channel="XCOR:LI29:302:IACT",
            name="name",
            color="red",
            yAxisName="Axis",
            useArchiveData=True,
            noLiveData=False,
        )

        self.plot_archived.createCurveItem(
            y_channel="ca://DEMO:ANGLE",
            name="name",
            color="blue",
            plot_by_timestamps=True,
            yAxisName="Axis",
            useArchiveData=True,
            noLiveData=True,
        )
        # self.plot.addCurve(curve_item)
        self.plot_archived.addYChannel(
            y_channel="XCOR:LI29:302:IACT",
            name="name",
            color="blue",
            yAxisName="Axis",
            useArchiveData=True,
            noLiveData=True,
        )
        self.plot_live.updateXAxis(True)


