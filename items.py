import requests 
from PyQt6.QtWidgets import QWidget,QVBoxLayout,QHBoxLayout,QLabel,QTextEdit,QFrame
from PyQt6.QtGui import QTextDocument, QPixmap
from PyQt6.QtCore import QUrl, Qt
from card import Card


class Items(QWidget):

    def __init__(self,view,window, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.layout.addWidget(QLabel('Items'))
        self.window = window
        self.view = view

    def add_items(self, data):
        doc = QTextDocument()
        for entry in data.entries:
            item = Card(entry,doc,parent=self)
            self.layout.addWidget(item)
            item.c.clicked.connect(lambda entry=entry: self.clickItem(entry))

    def initialize(self, data):
        # self.layout = QVBoxLayout()
        self.add_items(data)

        # self.setLayout(self.layout)
        self.updateGeometry()

    def clickItem(self,entry):
        self.view.load(QUrl(entry.link))