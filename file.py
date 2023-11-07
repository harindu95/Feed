from PyQt6.QtCore import pyqtSignal, QObject, QCoreApplication, QEventLoop, QTimer, Qt, QThreadPool


def readFile_signal(filepath: str, signal:pyqtSignal):

    def read_file(file:str = filepath,signal:pyqtSignal = signal):
        f = '\n'.join(open(file,encoding='utf-8').readlines())
        signal.emit(f)

    QThreadPool.globalInstance().start(read_file)


class FileConnection(QObject):
    read = pyqtSignal(str)

def readFile(file:str, callback:callable):

    conn = FileConnection()
    def read_file(file:str = file,conn=conn):
        f = '\n'.join(open(file,encoding='utf-8').readlines())
        conn.read.emit(f)

    conn.read.connect(callback)
    QThreadPool.globalInstance().start(read_file)

class FilesConnection(QObject):
    read = pyqtSignal(list)

def readFiles(files:list, callback:callable):
    conn = FilesConnection()

    def read_files(files:list = files,conn=conn):
        result = []
        for file in files:
            f = '\n'.join(open(file,encoding='utf-8').readlines())
            result.append(f)
        conn.read.emit(result)

    conn.read.connect(callback)
    QThreadPool.globalInstance().start(read_files)