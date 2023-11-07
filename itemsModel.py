
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QListView, QLineEdit
from PyQt6.QtCore import QModelIndex,  QUrl, Qt, QAbstractListModel, QVariant, pyqtSignal, QThreadPool
from PyQt6.QtGui import QStandardItemModel

class ItemsModel(QAbstractListModel):
    scroll = pyqtSignal(int)
    searchDone = pyqtSignal(object)
    searchEmpty = pyqtSignal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.view_items = []
        self.list = []
        self.min = 0
        self.max = 0    
        self.scroll.connect(self.scrollFetch)
        self.search_mode = False    

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self.view_items)

    def data(self, index: QModelIndex, extra):
        if index.row() >= 0 and index.row() < len(self.view_items):
            return self.view_items[index.row()]
        else:
            print("Invalid index:", index.row())
            return QVariant()
        
    def index(self, row: int, column: int = 0, parent: QModelIndex = QModelIndex()) -> QModelIndex:
        if row < len(self.view_items):
            return self.createIndex(row,column,self.view_items[row])
        else:
            return QModelIndex()

    def setData(self, index: QModelIndex, value) -> bool:
        i = index.row()
        if i < len(self.view_items):
            self.view_items[i] = value
        else:
            return False
        
        self.dataChanged.emit(index, index)
        return True
        
    # def addItem(self, item):
    #     index = self.createIndex(len(self.list), 1,item)
    #     self.setData(index, item)

    def setList(self, list):
        # for i in range(0,len(self.list)):
            # self.list[i].rank = list[i].rank
        self.layoutAboutToBeChanged.emit()
        self.view_items = list
        self.layoutChanged.emit()

    def sortByOrder(self):
        oldIndexes = [self.index(i, 0) for i in range(len(self.view_items))]
        newIndexes = sorted(
            oldIndexes, 
            key=lambda i: i.data().rank, 
            reverse=True
        )
        self.changePersistentIndexList(oldIndexes, newIndexes)
        self.layoutChanged.emit()

    def insertRows(self, row:int, count:int, parent:QModelIndex):
        model = parent.model()
        self.beginInsertRows(QModelIndex(), row, row+count - 1)
        for i in range(count):
            child = model.index(i,0,parent)
            item = child.data()
            self.view_items.insert(row+i,item)

        self.endInsertRows()

    def appendItems(self,items:list):
        count = len(items)
        row = len(self.view_items)
        self.beginInsertRows(QModelIndex(), row, row+count - 1)
        self.view_items.extend(items)
        self.endInsertRows()

    def addItems(self, items:list):
        self.list.extend(items)
        if self.canFetchMore():
            self.fetchMore(QModelIndex(), batch_size=2)

    def canFetchMore(self, parent: QModelIndex = QModelIndex()) -> bool:
        if self.search_mode:
            return False
        return len(self.list) > len(self.view_items)
        # if len(self.view_items) > 1 :
            # return False
        # else:
            # return len(self.list) > len(self.view_items)
    
    def fetchMore(self, parent: QModelIndex = QModelIndex(),batch_size=5) -> None:
        # batch_size = 20
        row = len(self.view_items)
        count = min(batch_size, len(self.list) - row)
        prev = self.max
        self.max += count
        if count > 0:
            self.appendItems(self.list[prev:self.max])

    def scrollFetch(self,val):
        max = self.rowCount()
        dy = max - val
        if dy < 5 and self.canFetchMore():
            self.fetchMore()

    def searchTask(self,txt):
        import re
        result = []
        keywords = set(txt.split())
        r = '|'.join(keywords)
        p = re.compile(r,flags=re.MULTILINE |re.IGNORECASE)
        for item in self.list:
        # if True:
            # item = self.list[0]
            content = item.title + '' + item.description +'' + item.link
            words = set(p.findall(content.lower()))
            if len(words) == len(keywords):
                result.append(item)
        
        self.searchDone.connect(self.show_search_results)
        signal = {
            'result':result,
            'keyword':txt
        }
        self.searchDone.emit(signal)

        if len(result) == 0:
            self.searchEmpty.emit()

    def search(self, txt:str):
        if len(txt) == 0 :
            if self.search_mode != False:
                self.setList([])
                self.fetchMore()
            self.search_mode = False
            return
        else:
            print("search::", txt)
            txt = txt.lower().strip()
            self.keyword = txt
            self.search_mode = True
            QThreadPool.globalInstance().start(lambda txt=txt: self.searchTask(txt))


    def show_search_results(self, result:dict):
        if self.keyword == result['keyword']:
            self.setList(result['result'])