from keywords import extract_keywords
from items import Items
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QScrollArea
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineProfile
from PyQt6.QtCore import QUrl, QThreadPool, Qt, QTimer

from feeds import updateFeeds, tasks

# Only needed for access to command line arguments
import sys

# You need one (and only one) QApplication instance per application.
# Pass in sys.argv to allow command line arguments for your app.
# If you know you won't use command line arguments QApplication([]) works too.
app = QApplication(sys.argv)

# Create a Qt widget, which will be our window.
window = QWidget()
window.setObjectName('window')
style = '\n'.join(open('style.css').readlines())
window.setStyleSheet(style)
window.setWindowTitle('Feed')
layout = QHBoxLayout()

view = QWebEngineView()
view.setObjectName('web-engine-view')
scroll = QScrollArea()
scroll.setWidget(items)
scroll.setObjectName('scroll-area')
scroll.setWidgetResizable(True)
scroll.setMinimumWidth(500)
layout.addWidget(scroll)


view.load(QUrl("https://duckduckgo.com"))
window.resize(1224, 750)
# Disable cookies
layout.addWidget(view,stretch=1)
layout.addStretch()
window.setLayout(layout)
window.show()  # IMPORTANT!!!!! Windows are hidden by default.

view.loadFinished.connect(lambda load, view=view,
                          items=items: extract_keywords(view, 1, items))
view.loadStarted.connect(
    lambda view=view, items=items: extract_keywords(view, 0, items))
# Start the event loop.
updateFeeds(items.initialize, app.aboutToQuit)
# fetch = FetchFeed()
# fetch.fetched.connect(lambda: items.initialize(fetch.d))
# fetch.getFeeds()
app.exec()


# Your application won't reach here until you exit and the event
# loop has stopped.
