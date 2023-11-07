from PyQt6.QtGui import QPainter,QRegion
from PyQt6.QtWidgets import QStyle,QStyleOptionViewItem,QStyledItemDelegate
from PyQt6.QtCore import QModelIndex, QSize, QRect, QPoint

from . import Card

class CardDelegate(QStyledItemDelegate):

    def __init__(self ) -> None:
        super().__init__()
        self.card = Card()

    def sizeHint(self, option: QStyleOptionViewItem, index: QModelIndex) -> QSize:
        item = index.data()
        self.card.setItem(item)
        rect = QRect(0,0,450,200)
        self.card.setGeometry(rect)
        if item.image_url == '':
            rect.setHeight(150)
            self.card.setGeometry(rect)
        width = 450
        # self.card.setFixedWidth(width)
        height = self.card.size().height()
        
        size = QSize()
        size.setHeight(height)
        size.setWidth(width)
        return size

    def paint(self, painter: QPainter , option: QStyleOptionViewItem, index: QModelIndex) -> None:
        painter.save()
        item = index.data()
        self.card.setItem(item)
        painter.translate(option.rect.x(),option.rect.y())
        self.card.setGeometry(option.rect)
        region = QRegion(0,0, option.rect.width(),option.rect.height())
        p = QPoint()
        p.setX(0)
        p.setY(0)
        self.card.render(painter,targetOffset=p,sourceRegion=region)
        painter.restore()
