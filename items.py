import requests
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QFrame
from PyQt6.QtGui import QTextDocument, QPixmap
from PyQt6.QtCore import QUrl, Qt
from card import Card
from queue import Queue, Empty


class Items(QWidget):

    def __init__(self, view, window, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.window = window
        self.items = []
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.view = view
        self.updateUi()

    def add_item(self, item):
        self.items.append(item)
        card = Card(item)
        card.c.clicked.connect(lambda item=item: self.clickItem(item))
        self.layout.addWidget(card)
        self.updateGeometry()

    def add_items(self, data):
        for entry in data.entries:
            self.add_item(entry)

    def remove_all_items(self):
        for i in range(self.layout.count()):
            item = self.layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)

    def updateUi(self):
        self.remove_all_items()
        # self.items.reverse()
        for item in self.items:
            card = Card(item)
            card.c.clicked.connect(lambda item=item: self.clickItem(item))
            self.layout.addWidget(card)
        self.updateGeometry()

    def initialize(self, feeds):
        self.add_items(feeds)

    def clickItem(self, entry):
        self.view.load(QUrl(entry.link))
