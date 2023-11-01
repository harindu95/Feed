from PyQt6.QtCore import pyqtSignal,QObject

class Connection(QObject):
    done = pyqtSignal()

def plain_text(html):
    from bs4 import BeautifulSoup

    plain = ' '.join(BeautifulSoup(html, "html.parser").findAll(text=True))  
    return plain