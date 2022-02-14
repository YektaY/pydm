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
        self.testRect = None
        self.position_dict = {}

    '''
    def addWidget(self, item: QWidget):
        """
        
        Parameters
        ----------
        """
        self.itemList.append(item)
    '''

    def addItem(self, item: QLayoutItem):
        """

        Parameters
        ----------
        """
        self.itemList.append(item)

    def setGeometry(self, rect: QRect) -> None:
        """

        Parameters
        ----------
        """

        super().setGeometry(rect)
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

    '''
    def sizeHint(self) -> QSize:
    '''

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
        height = self.maintainLayout(QRect(0, 0, width, 0))
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

    def maintainLayout(self, rect: QRect) -> int:
        """
        layouts the logic for scaling the window as the screen changes size.
        This layout designed for relative scaling.

        Parameters
        ----------

        """

        #print(rect.width(), rect.height())
        height = 0
        effective_rect = self.contentsRect()
        screen_ratio = effective_rect.width()/effective_rect.height()

        for item in self.itemList:
            child_widget = item.widget()
            #print(child_widget.width(), child_widget.height(), child_widget)
            child_ratio = child_widget.width()/child_widget.height()
            if screen_ratio > child_ratio:
                width = child_widget.width()*effective_rect.height()/child_widget.height()
                height = effective_rect.height()
            else:
                width = effective_rect.width()
                height = child_widget.height()*effective_rect.width()/child_widget.width()

            width = round(width)
            height = round(height)
            x = round(child_widget.x()*width/child_widget.width())
            y = round(child_widget.y()*height/child_widget.height())

            scaled_item = QRect(0, 0, width, height)
            item.setGeometry(scaled_item)

            if hasattr(child_widget, 'text'):
                pass

        return height



    '''
    def maintainLayout(self, rect: QRect) -> int:
        """
        layouts the logic for scaling the window as the screen changes size.


        Parameters
        ----------


        """


        if self.testRect is None:
            self.testRect = rect

        left, top, right, bottom = self.getContentsMargins()
        effective_rect = rect.adjusted(+left, +top, -right, -bottom)
        x = effective_rect.x()
        y = effective_rect.y()

        ratio_origin = self.testRect.width()/self.testRect.height()
        ratio_changed = effective_rect.width()/effective_rect.height()


        if ratio_origin > ratio_changed:
            width_screen = effective_rect.width()
            height_screen = width_screen/ratio_origin
            x = 0
            y = (effective_rect.height() - height_screen)/2
        else:
            height_screen = effective_rect.height()
            width_screen = height_screen*ratio_origin
            y = 0
            x = (effective_rect.width() - width_screen)/2
    
        min = self.minimumSize()
        h_ratio = effective_rect.height()/self.testRect.height()
        w_ratio = effective_rect.width()/self.testRect.width()
        print(rect.width(), self.testRect.width(), "ratio", w_ratio, h_ratio)

        if h_ratio < 1:
            h_ratio = 1

        if w_ratio < 1:
            w_ratio = 1

        line_height = 0
        
        for index, item in enumerate(self.itemList):
            child_widget = item.widget()

            if index not in self.position_dict:
                self.position_dict[index] = (child_widget.width(), child_widget.height())

            space_x = self.horizontalSpacing()
            space_y = self.verticalSpacing()

            # determine new scale of main widget's child objects
            width = child_widget.width() + effective_rect.width() - self.testRect.width()
            height = child_widget.height() + effective_rect.height() - self.testRect.height()
            #width = effective_rect.width()
            #height = effective_rect.height()
            print(width, child_widget.width(), effective_rect.width(), self.testRect.width())
            position = QSize(width, height)

            original_child_size = self.position_dict[index]
            #print(original_child_size[0], original_child_size[1], child_widget)
            x = child_widget.x()
            y = y + height + space_y

            # set new scale and position of child object
            item.setGeometry(QRect(QPoint(int(x), int(y)), position))

            height = item.sizeHint().height() * height_screen
            width = item.sizeHint().width() * width_screen
            height = int(height)
            width = int(width)
            pos = QSize(width, height)
            
            space_x = self.horizontalSpacing()
            if space_x == -1:
                space_x = child_widget.style().layoutSpacing(QSizePolicy.PushButton, QSizePolicy.PushButton, Qt.Horizontal)

            space_y = self.verticalSpacing()
            if space_y == -1:
                space_y = child_widget.style().layoutSpacing(QSizePolicy.PushButton, QSizePolicy.PushButton, Qt.Vertical)

            next_x = x + pos.width() + space_x
            
            x = next_x
            line_height = max(line_height, pos.height())

            if next_x - space_x > effective_rect.right() and line_height > 0:
                x = effective_rect.x()
                y = y + pos.height() + space_y
                next_x = x + pos.width() + space_x
                line_height = 0


            #item.widget().size().scale(width, height, Qt.KeepAspectRatio)


            #child_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            space_x = self.horizontalSpacing()
            if space_x == -1:
                space_x = child_widget.style().layoutSpacing(QSizePolicy.PushButton, QSizePolicy.PushButton, Qt.Horizontal)
            space_y = self.verticalSpacing()
            if space_y == -1:
                space_y = child_widget.style().layoutSpacing(QSizePolicy.PushButton, QSizePolicy.PushButton, Qt.Vertical)

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
          

       #return y + line_height - rect.y() + bottom
        return 0
    
    '''

