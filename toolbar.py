from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton
from PyQt6.QtCore import pyqtSignal, QObject, Qt, QEventLoop, QThreadPool, QUrl, QThread

class Toolbar(QWidget):

    def __init__(self, items, view,application, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.items = items
        self.settings = application
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        organize_btn = QPushButton()
        show_btn = QPushButton()
        organize_btn.setText("Organize")
        show_btn.setText("Show")
        self.layout.addWidget(organize_btn)
        self.layout.addWidget(show_btn)
        self.layout.addStretch()
        organize_btn.clicked.connect(self.items.organize)
        show_btn.clicked.connect(self.show)
        self.view = view
        self.setObjectName('toolbar')

    def onClick(self):
        self.items.organize()

    def show(self):
        try:
            show_clusters(self.settings.word_clouds, self.view)
        except AttributeError:
            pass


    

def show_clusters(images, view):
    html = "<html><body>{}</body></html>"
    body = ""
    x = 0
    for img in images:
        svg = img.to_svg()
        # section = "<div>{}<p>Cluster {}</p></div>".format(svg, x)
        section = "<div style='margin:10px'>{}</div>"
        body += section.format(svg)
        x += 1

    html = html.format(body)
    view.page().setHtml(html, QUrl("about:wordcloud"))
