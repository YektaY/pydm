from pydm import Display

from qtpy import QtCore
from qtpy.QtWidgets import QHBoxLayout, QApplication
from pydm.widgets import PyDMArchiverTimePlot


class archive_time_plot_example(Display):
    def __init__(self, parent=None, args=None, macros=None):
        super(archive_time_plot_example, self).__init__(
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
        self.plot = PyDMArchiverTimePlot(background=[255, 255, 255, 255])
        self.main_layout.addWidget(self.plot)
        self.plot.createCurveItem(
            y_channel="ca://DEMO:ANGLE",
            name="name",
            color="red",
            plot_by_timestamps=True,
            yAxisName="Axis",
            useArchiveData=True,
            noLiveData=True,
        )
        # self.plot.addCurve(curve_item)
        self.plot.addYChannel(
            y_channel="XCOR:LI29:302:IACT",
            name="name",
            color="red",
            yAxisName="Axis",
            useArchiveData=True,
            noLiveData=True,
        )
        self.plot.updateXAxis(True)
