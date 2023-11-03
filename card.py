from PyQt6.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QFrame
from PyQt6.QtGui import QTextDocument, QPixmap
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtCore import pyqtSignal, QObject
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

    def __init__(self, entry, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.entry = entry
        self.c = Connection()

        icon = QLabel()
        description = QWidget()
        layout = QHBoxLayout()
        self.setLayout(layout)

        if self.entry.image_url != '':
            image = self.entry.image_data
            self.pixmap = QPixmap()
            self.pixmap.loadFromData(image)
            self.pixmap = self.pixmap.scaled(
                200, 160, Qt.AspectRatioMode.KeepAspectRatio,transformMode = Qt.TransformationMode.SmoothTransformation)
            icon.setPixmap(self.pixmap)
            icon.setFixedWidth(160)
            layout.addWidget(icon)

        else:
            print("No Image URL found!")

        layout.addWidget(description)
        title_layout = QVBoxLayout()

        self.setObjectName("card")
        # self.setStyleSheet("border: 1px solid red;")
        # self.setStyleSheet(
        #     "QFrame#Card{ border-top:3px solid gray; background:white; }")

        title = QLabel()
        title.setText(process_description(entry.title))
        title.setObjectName('title')
        # title_font = title.font()
        # title_font.setPointSize(12)
        # title.setFont(title_font)
        title.setWordWrap(True)
        title_layout.addWidget(title)
        description.setLayout(title_layout)

        self.content = process_description(entry.summary)
        self.hidden = True
        subtitle = QLabel()
        subtitle.setText(trim_description(self.content))
        subtitle.setObjectName('subtitle')
        subtitle.setWordWrap(True)
        title_layout.addWidget(subtitle)

        self.mousePressEvent = lambda event: self.c.clicked.emit()
