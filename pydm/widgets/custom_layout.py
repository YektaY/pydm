from qtpy.QtWidgets import QWidget, QLayout, QLayoutItem, QSizePolicy
from qtpy.QtCore import Qt, QRect, QSize, QPoint
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
        self.setContentsMargins(margin, margin, margin, margin)
        self.testRect = None
        self.position_dict = {}
        self.org = [640, 480]

    def addItem(self, item: QLayoutItem):
        """

        Parameters
        ----------
        """
        self._item_list.append(item)

    def setGeometry(self, rect: QRect) -> None:
        """

        Parameters
        ----------
        """

        super(PYDMLayout, self).setGeometry(rect)
        print(self._item_list[0].geometry().size())
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
            size = item.widget().geometry().size()

            margins = self.contentsMargins()
        #size += QSize(margins.left() + margins.right(), margins.top() + margins.bottom())

        return size

    def count(self) -> int:
        return len(self._item_list)

    '''
    def heightForWidth(self, width: int) -> int:
        height = self.maintainLayout()
        return height
    '''

    @staticmethod
    def expandingDirections() -> Qt.Orientations:
        return Qt.Orientations(Qt.Orientation(0))

    @staticmethod
    def hasHeightForWidth() -> bool:
        return True

    def maintainLayout(self, rect) -> int:
        """
        layouts the logic for scaling the window as the screen changes size.
        This layout designed for relative scaling.
        """

        height = 0
        effective_rect = rect

        if effective_rect.height() - self.org[1] == 0:
            return height

        screen_ratio = effective_rect.width() / effective_rect.height()

        for item in self._item_list:
            child_widget = item.widget()

            if child_widget.width() == 0 or child_widget.height() == 0:
                continue

            child_ratio = child_widget.width() / child_widget.height()


            a = effective_rect.width()/self.org[0]
            b = effective_rect.height()/self.org[1]

            if a > b:
                scale = a
            else:
                scale = b

            print(scale)

            width = child_widget.width() * scale
            height = child_widget.height() * scale
            x = round(child_widget.x() * width / child_widget.width())
            y = round(child_widget.y() * height / child_widget.height())

            scaled_item = QRect(x, y, width, height)
            item.setGeometry(scaled_item)

        self.org[0] = effective_rect.width()
        self.org[1] = effective_rect.height()

        return height
