import typing
from PyQt6 import QtCore, QtGui
import requests
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QListView, QLineEdit, QStackedWidget, QLabel
from PyQt6.QtCore import QModelIndex,  QUrl, Qt, QAbstractListModel, QVariant, pyqtSignal
from PyQt6.QtGui import QStandardItemModel
from card.delegate import CardDelegate
from common import GenericWorker, AsyncGeneratorWorker
from itemsModel import ItemsModel

class Items(QWidget):

    def __init__(self, view, application, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.application = application
        # self.items = []
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.view = view
        self.search = QLineEdit()
        self.search.setObjectName("search-box")
        self.search.setPlaceholderText("Search")
        self.search.returnPressed.connect(self.search_items)
        self.layout.addWidget(self.search)
        self.background_thread = application.createThread()
        self.background_thread.start()
        self.organize_running = False
        self.stacked = QStackedWidget()
        self.layout.addWidget(self.stacked)   
        self.list_view = QListView()
        self.stacked.addWidget(self.list_view)
        self.list_view.setObjectName("list-view")
        self.list_message = QLabel()
        self.list_message.setObjectName("list-message")
        self.stacked.addWidget(self.list_message)
        self.list_model = ItemsModel()
        self.list_view.setModel(self.list_model)
        self.list_view.clicked.connect(self.clickItem)
        self.list_view.verticalScrollBar().valueChanged.connect(self.scroll_changed)
        from card import CardDelegate
        delegate = CardDelegate()
        # delegate = ItemDelegate()
        self.list_view.setItemDelegate(delegate)
        self.list_view.setLayoutMode(QListView.LayoutMode.Batched)
        self.list_view.setBatchSize(20)
        self.setObjectName('items')

        self.list_model.layoutAboutToBeChanged.connect(lambda:self.show_message("Loading...") )
        self.list_model.layoutChanged.connect(self.show_list_view)
        self.list_model.searchEmpty.connect(lambda: self.show_message("No search results found!."))
        # QTimer.singleShot(0,self.fetch_feeds)
        self.fetch_feeds()

    def show_list_view(self):
        self.stacked.setCurrentIndex(0)

    def show_message(self,msg):
        self.list_message.setText(msg)
        self.stacked.setCurrentIndex(1)

    def search_items(self):
        txt = self.search.text().strip()
        self.list_model.search(txt)

    def scroll_changed(self, val):
        max = self.list_view.verticalScrollBar().maximum()
        dy = max - val
        if dy < 5 :
            self.list_model.scroll.emit(val)

    def clickItem(self, index):
        item = index.data()
        self.view.page().load(QUrl(item.link))

    def remove_bottom_item(self):
        try:
            item = self.view_items.pop()
            self.remove_item(item)
        except Exception:
            return
        
    def add_items(self, data:list):
        if data is None:
            return
        for feed in data:
            # print(feed.entries)
            self.list_model.addItems(feed.entries)


    def fetch_feeds(self):

        from feeds import updateFeeds
        updateFeeds(self.application, self.add_items)

    def remove_all_items(self):
        for i in range(self.layout.count()):
            item = self.layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)

    def sort_items(self,items):
        self.list_model.setList(items)
        self.list_view.scrollToTop()


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
        items = self.list_model.view_items[:]
        corpus = self.application.corpus
        sortWorker = GenericWorker(Items.organize_items, items, corpus)
        sortWorker.moveToThread(self.background_thread)
        sortWorker.finished.connect(
            self.handleOrganize, Qt.ConnectionType.QueuedConnection)
        sortWorker.start.emit()
