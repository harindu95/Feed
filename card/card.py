from PyQt6.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QFrame
from PyQt6.QtCore import Qt
from PyQt6.QtCore import pyqtSignal, QObject
from PyQt6.QtGui import QPainter, QPixmap,QRegion, QFont
from PyQt6.QtWidgets import QStyle,QStyleOptionViewItem,QWidget, QVBoxLayout, QPushButton, QStyledItemDelegate, QLabel
from PyQt6.QtCore import QModelIndex, QSize, QRect, QPoint
from .toolbar import CardToolbar

def process_description(text):
    from bs4 import BeautifulSoup

    plain = ' '.join(BeautifulSoup(text, "html.parser").findAll(text=True))
    # doc.setHtml(text)
    # plain = doc.toPlainText()
    return plain.strip()


def trim_description(desc):
    return desc[:150]


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

        self.title.setText(item.title)
        # content = process_description(item.summary)
        content = item.description
        self.subtitle.setText(trim_description(content))

    def clear(self):
        self.icon.setPixmap(QPixmap())
        self.icon.hide()
        self.title.setText("CARD TITLE")
        self.subtitle.setText('')
   

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.icon = QLabel()
        description = QWidget()
        layout = QHBoxLayout()
        # self.setLayout(layout)
        self.icon.setFixedWidth(160)
        
        toolbar = CardToolbar()

        l = QVBoxLayout()
        l.setObjectName('root-layout')
        l.addWidget(toolbar)
        l.setSpacing(0)
        l.setContentsMargins(0,0,0,0)
        self.setLayout(l)

        container = QWidget()
        container.setLayout(layout)
        l.addWidget(container)

        layout.setObjectName('container-layout')
        layout.setSpacing(0)
        layout.setContentsMargins(0,0,0,0)

        layout.addWidget(self.icon)
        layout.addWidget(description)
        description_layout = QVBoxLayout()

        self.setObjectName("card")

        self.title = QLabel()        
        self.title.setObjectName('title')
        self.title.setWordWrap(True)
        
        description_layout.addWidget(self.title)
        description.setLayout(description_layout)

        self.hidden = True
        self.subtitle = QLabel()
        self.subtitle.setObjectName('subtitle')
        self.subtitle.setWordWrap(True)
        description_layout.addWidget(self.subtitle)
        description_layout.setContentsMargins(0,0,0,0)
        # self.mousePressEvent = lambda event: self.c.clicked.emit()
        self.get_stylesheet()

    def get_stylesheet(self,file='card.css'):
        from file import readFile
        readFile(file, self.setStyleSheet)


