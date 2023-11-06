import typing
from PyQt6 import QtCore, QtGui
import requests
from PyQt6.QtWidgets import QStyle,QStyleOptionViewItem,QWidget, QVBoxLayout, QListView, QStyledItemDelegate, QLabel
from PyQt6.QtCore import QModelIndex, QObject, QUrl, Qt, QTimer, QThread, QAbstractListModel, QVariant, QRect, QSize, QPoint
from card import Card
from common import GenericWorker, AsyncGeneratorWorker


class ItemsModel(QAbstractListModel):

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.list = []

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self.list)

    def data(self, index: QModelIndex, extra):
        if index.row() < len(self.list):
            return self.list[index.row()]
        else:
            return QVariant()

    def setData(self, index: QModelIndex, value) -> bool:
        i = index.row()
        if i < len(self.list):
            self.list[i] = value
        elif i == len(self.list):
            self.list.insert(i,value)
        else:
            return False
        
        self.dataChanged.emit(index, index)
        return True
        
    def addItem(self, item):
        index = self.createIndex(len(self.list), 1,item)
        self.setData(index, item)


class Items(QWidget):

    def __init__(self, view, scroll, application, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scroll = scroll
        self.application = application
        # self.items = []
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.view = view
        self.background_thread = application.createThread()
        self.background_thread.start()
        self.organize_running = False
        self.list_view = QListView()
        self.layout.addWidget(self.list_view)
        self.list_model = ItemsModel()
        self.list_view.setModel(self.list_model)
        self.list_view.clicked.connect(self.clickItem)
        from card import CardDelegate
        delegate = CardDelegate()
        # delegate = ItemDelegate()
        self.list_view.setItemDelegate(delegate)
        self.list_view.setLayoutMode(QListView.LayoutMode.Batched)
        self.setObjectName('items')
        # QTimer.singleShot(0,self.fetch_feeds)
        self.fetch_feeds()

    def clickItem(self, index):
        item = index.data()
        self.view.page().load(QUrl(item.link))

    def remove_bottom_item(self):
        try:
            item = self.view_items.pop()
            self.remove_item(item)
        except Exception:
            return
        
    def add_item(self, item):
        card = Card(item)
        self.view_items.append(item)
        item.cardIndex = len(self.cards)
        item.index = len(self.cards)
        self.cards.append(card)
        # item.widget = card
        item.rank = 0

        card.c.clicked.connect(lambda card=card: self.clickItem(card))
        self.layout.addWidget(card)

    def add_items(self, data):
        if data is None:
            return
        for feed in data:
            for item in feed.entries:
                self.list_model.addItem(item)


    def fetch_feeds(self):

        from feeds import updateFeeds
        updateFeeds(self.application, self.add_items)

    def remove_all_items(self):
        for i in range(self.layout.count()):
            item = self.layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)

    def sort_items(self, items):
        if items == self.items:
            return
        else:
            self.items = items
        for i, item in enumerate(self.items):
            if 'cardIndex' in item and item.cardIndex >= 0:
                card = self.cards[item.cardIndex]
                self.layout.removeWidget(card)
                # print(i,item.title,item.rank)
                self.layout.insertWidget(i, card)
                item.cardIndex = i
                # item.index = i

        self.scroll.verticalScrollBar().setValue(0)


    def initialize(self, feeds):
        self.add_items(feeds)


    def set_wordclouds(self, wordclouds):
        print('wordclouds', len(wordclouds))
        self.application.word_clouds = wordclouds

    from typing import List

    def organize_items(items: List[dict], corpus):
        from keywords import get_centroids, rank_items, generateWordClouds
        centroids = get_centroids(corpus)
        word_clouds = generateWordClouds(centroids)
        items = rank_items(items, centroids)
        items.sort(reverse=True, key=lambda x: x.rank)
        return (items, word_clouds)

    def handleOrganize(self, result):
        self.organize_running = False
        items, word_clouds = result
        self.set_wordclouds(word_clouds)
        self.sort_items(items)

    def organize(self):
        # from keywords import corpus
        if self.organize_running:
            print("Organize already running!")
            return
        self.organize_running = True
        items = self.items[:]
        corpus = self.application.corpus
        sortWorker = GenericWorker(Items.organize_items, items, corpus)
        sortWorker.moveToThread(self.background_thread)
        sortWorker.finished.connect(
            self.handleOrganize, Qt.ConnectionType.QueuedConnection)
        sortWorker.start.emit()
