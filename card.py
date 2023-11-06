from PyQt6.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QFrame
from PyQt6.QtCore import Qt
from PyQt6.QtCore import pyqtSignal, QObject
from PyQt6.QtGui import QPainter, QPixmap,QRegion
from PyQt6.QtWidgets import QStyle,QStyleOptionViewItem,QWidget, QVBoxLayout, QListView, QStyledItemDelegate, QLabel
from PyQt6.QtCore import QModelIndex, QSize, QRect, QPoint

import sys
import requests


def process_description(text):
    from bs4 import BeautifulSoup

    plain = ' '.join(BeautifulSoup(text, "html.parser").findAll(text=True))
    # doc.setHtml(text)
    # plain = doc.toPlainText()
    return plain.strip()


def trim_description(desc):
    return desc[:200]


class Connection(QObject):
    clicked = pyqtSignal()


class Card(QFrame):

    def setItem(self, item):
        self.clear()
        self.item = item
        if self.item.image_url != '':
            image = self.item.image_data
            pixmap = QPixmap()
            pixmap.loadFromData(image)
            self.icon.show()
            pixmap = pixmap.scaled(
                200, 160, Qt.AspectRatioMode.KeepAspectRatio,transformMode = Qt.TransformationMode.SmoothTransformation)
            self.icon.setPixmap(pixmap)
        else:
            print("No Image URL found!")

        self.title.setText(process_description(item.title))
        content = process_description(item.summary)
        self.subtitle.setText(trim_description(content))

    def clear(self):
        self.icon.setPixmap(QPixmap())
        self.icon.hide()
        self.title.setText('')
        self.subtitle.setText('')
   

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.icon = QLabel()
        description = QWidget()
        layout = QHBoxLayout()
        self.setLayout(layout)
        self.icon.setFixedWidth(160)
        layout.addWidget(self.icon)        

        layout.addWidget(description)
        title_layout = QVBoxLayout()

        self.setObjectName("card")

        self.title = QLabel()        
        self.title.setObjectName('title')
        self.title.setWordWrap(True)
        font = self.title.font()
        font.setPointSize(14)
        self.title.setFont(font)
        title_layout.addWidget(self.title)
        description.setLayout(title_layout)

        self.hidden = True
        self.subtitle = QLabel()
        self.subtitle.setObjectName('subtitle')
        self.subtitle.setWordWrap(True)
        title_layout.addWidget(self.subtitle)
        # self.mousePressEvent = lambda event: self.c.clicked.emit()
        self.get_stylesheet()

    def get_stylesheet(self,file='card.css'):
        css = '\n'.join(open(file).readlines())
        self.setStyleSheet(css)


class CardDelegate(QStyledItemDelegate):

    def __init__(self ) -> None:
        super().__init__()
        self.card = Card()

    def sizeHint(self, option: QStyleOptionViewItem, index: QModelIndex) -> QSize:
        item = index.data()
        self.card.setItem(item)
        rect = QRect(0,0,450,200)
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
