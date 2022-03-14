from qtpy.QtWidgets import QWidget, QLayout, QLayoutItem
from qtpy.QtCore import Qt, QRect, QSize
from qtpy.QtGui import QFont
import typing


class PYDMLayout(QLayout):
    """
    A layout to handle relative scaling.

    Parameters
    ----------
    parent : QLayout
        The parent layout
    """

    def __init__(self, parent: QWidget = None, margin: int = -1):
        super().__init__(parent)

        self._item_list = list()
        self._child_widget_dict = dict()
        self.setContentsMargins(margin, margin, margin, margin)

    def addItem(self, item: QLayoutItem):
        """

        Parameters
        ----------
        """
        self._item_list.append(item)

        if hasattr(item, 'widget'):
            self.storeOriginalPosition(item.widget())

    def addLayout(self, layout: QLayout, stretch: int = 0):
        """

        Parameters
        ----------
        """
        for index in range(0, layout.count()):
            item = layout.itemAt(index)
            self.addItem(item)

        #self._item_list.append(layout)

    def storeOriginalPosition(self, widget):
        """

        Parameters
        ----------
        """
        print(widget.x(), widget.y(), widget.width(), widget.height(), "ogp")
        self._child_widget_dict[widget] = (widget.x(), widget.y(), widget.width(), widget.height())

    def setGeometry(self, rect: QRect) -> None:
        """

        Parameters
        ----------
        """

        super(PYDMLayout, self).setGeometry(rect)
        print(self._item_list[-1].geometry(), "set")
        self.maintainLayout(rect)

    def sizeHint(self) -> QSize:
        """

        Parameters
        ----------
        """
        return self.minimumSize()

    def itemAt(self, index: int) -> typing.Union[QLayoutItem, None]:
        """

        Parameters
        ----------
        """
        if 0 <= index < len(self._item_list):
            return self._item_list[index]
        else:
            return None

    def takeAt(self, index: int) -> typing.Union[QLayoutItem, None]:
        """

        Parameters
        ----------
        """
        if 0 <= index < len(self._item_list):
            return self._item_list.pop(index)
        else:
            return None

    def minimumSize(self) -> QSize:
        """

        Parameters
        ----------
        """

        size = QSize()
        for item in self._item_list:
            if hasattr(item, 'addItem'):
                print(item.geometry().size(), "size")
                size = item.geometry().size()
            else:
                size = item.widget().geometry().size()

        margins = self.contentsMargins()
        size += QSize(margins.left() + margins.right(), margins.top() + margins.bottom())
        return size

    def count(self) -> int:
        return len(self._item_list)

    def maintainLayout(self, rect) -> int:
        """
        layouts the logic for scaling the window as the screen changes size.
        This layout designed for relative scaling.
        """

        reference_width = 640
        reference_height = 480

        height = 0
        effective_rect = rect

        scale_factor_w = effective_rect.width() / reference_width
        scale_factor_h = effective_rect.height() / reference_height

        if scale_factor_w > scale_factor_h:
            scale_factor = scale_factor_w
        else:
            scale_factor = scale_factor_h

        for item in self._item_list:
            if hasattr(item, 'addItem'):
                continue

            child_widget = item.widget()

            if child_widget.width() == 0 or child_widget.height() == 0:
                continue

            child_widget_original_state = self._child_widget_dict[child_widget]
            child_x = child_widget_original_state[0]
            child_y = child_widget_original_state[1]
            child_width = child_widget_original_state[2]
            child_height = child_widget_original_state[3]

            width = child_width * scale_factor
            height = child_height * scale_factor
            x = child_x * scale_factor
            y = child_y * scale_factor

            scaled_item = QRect(x, y, width, height)

            if True:
                child_widget.resize(scaled_item.size())
            else:
                item.setGeometry(scaled_item)

            #if hasattr(child_widget, 'updateGeomerty'):
            #    child_widget.updateGeomerty()

            if hasattr(child_widget, 'text'):
                # should get font form the stylesheet?
                child_widget.setFont(QFont("Times New Roman", 13*scale_factor))

        return height
