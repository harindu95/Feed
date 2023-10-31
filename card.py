from PyQt6.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QFrame
from PyQt6.QtGui import QTextDocument, QPixmap
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtCore import pyqtSignal, QObject
import sys
import requests


def process_description(doc, text):
    doc.setHtml(text)
    plain = doc.toPlainText()
    return plain.strip()


def get_image(path):
    try:
        # url_data = urllib.request.urlopen(path).read()
        request = requests.get(path)
        return request.content
    except:
        print("Can't access url:", path, file=sys.stderr)
        return None


def trim_description(desc):
    return desc[:200]


class Connection(QObject):
    clicked = pyqtSignal()


class Card(QFrame):

    def __init__(self, entry, doc: QTextDocument, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.entry = entry
        self.c = Connection()

        icon = QLabel()
        description = QWidget()
        layout = QHBoxLayout()
        self.setLayout(layout)
        
        if self.entry.image_url != '':
            image = get_image(self.entry.image_url)
            self.pixmap = QPixmap()
            self.pixmap.loadFromData(image)
            self.pixmap = self.pixmap.scaled(160, 160, Qt.AspectRatioMode.KeepAspectRatio)
            icon.setPixmap(self.pixmap)
            icon.setFixedWidth(160)
            layout.addWidget(icon)

        else:
            print("No URL found!")
            print(self.entry.title, self.entry.image_url)

        layout.addWidget(description)
        title_layout = QVBoxLayout()

        self.setObjectName("Card")
        # self.setStyleSheet("border: 1px solid red;")
        self.setStyleSheet("QFrame#Card{ border-top:1px solid black; }")

        title = QLabel()
        title.setText(entry.title)
        title_font = title.font()
        title_font.setPointSize(12)
        title.setFont(title_font)
        title.setWordWrap(True)
        title_layout.addWidget(title)
        description.setLayout(title_layout)

        self.content = process_description(doc, entry.summary)
        self.hidden = True
        subtitle = QLabel()
        subtitle.setText(trim_description(self.content))
        subtitle.setWordWrap(True)
        title_layout.addWidget(subtitle)

        self.mousePressEvent = lambda event: self.c.clicked.emit()
