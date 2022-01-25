from qtpy.QtWidgets import QWidget, QLayout, QLayoutItem, QStyle, QSizePolicy
from qtpy.QtCore import Qt, QPoint, QRect, QSize
import typing


class PYDMLayout(QLayout):
    """
    a layout to handle scaling without forcing a specific position for widgets inside the layout.

    Parameters
    ----------
    parent : QLayout
        The parent layout
    """
    def __init__(self, parent: QWidget = None, horizontal_spacing: int = -1, vertical_spacing: int = -1,
                 margin: int = -1):
        super().__init__(parent)

        self.itemList = list()
        self.m_hSpace = horizontal_spacing
        self.m_vSpace = vertical_spacing

        self.setContentsMargins(margin, margin, margin, margin)

    def addItem(self, item: QLayoutItem, position: tuple[int, int]):
        """

        Parameters
        ----------
        """
        self.itemList.append((item, position))  # you are re-writing this to take in the position of the object

    def setGeometry(self, rect: QRect) -> None:
        """

        Parameters
        ----------
        """

        super().setGeometry(rect)
        self.maintainLayout(rect, False)

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
        if 0 <= index < len(self.itemList):
            return self.itemList[index]
        else:
            return None

    def takeAt(self, index: int) -> typing.Union[QLayoutItem, None]:
        """

        Parameters
        ----------
        """
        if 0 <= index < len(self.itemList):
            return self.itemList.pop(index)
        else:
            return None

    def minimumSize(self) -> QSize:
        """

        Parameters
        ----------
        """
        size = QSize()
        for item in self.itemList:
            size = size.expandedTo(item.minimumSize())

        margins = self.contentsMargins()
        size += QSize(margins.left() + margins.right(), margins.top() + margins.bottom())
        return size

    '''
    def __del__(self):
        # copied for consistency, not sure this is needed or ever called
        item = self.takeAt(0)
        while item:
            item = self.takeAt(0)
    '''

    def horizontalSpacing(self) -> int:
        if self.m_hSpace >= 0:
            return self.m_hSpace
        else:
            return self.smartSpacing(QStyle.PM_LayoutHorizontalSpacing)

    def verticalSpacing(self) -> int:
        if self.m_vSpace >= 0:
            return self.m_vSpace
        else:
            return self.smartSpacing(QStyle.PM_LayoutVerticalSpacing)

    def count(self) -> int:
        return len(self.itemList)

    def heightForWidth(self, width: int) -> int:
        height = self.maintainLayout(QRect(0, 0, width, 0), True)
        return height

    def smartSpacing(self, pm: QStyle.PixelMetric) -> int:
        parent = self.parent()
        if not parent:
            return -1
        elif parent.isWidgetType():
            return parent.style().pixelMetric(pm, None, parent)
        else:
            return parent.spacing()

    @staticmethod
    def expandinDirections() -> Qt.Orientations:
        return Qt.Orientations(Qt.Orientation(0))

    @staticmethod
    def hasHeightForWidth() -> bool:
        return True

    def maintainLayout(self, rect: QRect, test_only: bool) -> int:

        print("HCKAYAY!")
        left, top, right, bottom = self.getContentsMargins()
        effective_rect = rect.adjusted(+left, +top, -right, -bottom)
        x = effective_rect.x()
        y = effective_rect.y()
        line_height = 0

        for item in self.itemList:
            # set position of object
            wid = item.widget()
            space_x = self.horizontalSpacing()
            if space_x == -1:
                space_x = wid.style().layoutSpacing(QSizePolicy.PushButton, QSizePolicy.PushButton, Qt.Horizontal)
            space_y = self.verticalSpacing()
            if space_y == -1:
                space_y = wid.style().layoutSpacing(QSizePolicy.PushButton, QSizePolicy.PushButton, Qt.Vertical)

            next_x = x + item.sizeHint().width() + space_x
            if next_x - space_x > effective_rect.right() and line_height > 0:
                x = effective_rect.x()
                y = y + line_height + space_y
                next_x = x + item.sizeHint().width() + space_x
                line_height = 0

            if not test_only:
                item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))

            x = next_x
            line_height = max(line_height, item.sizeHint().height())

        return y + line_height - rect.y() + bottom
