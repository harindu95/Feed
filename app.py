from PyQt6.QtWidgets import QApplication, QWidget,QVBoxLayout,QHBoxLayout, QScrollArea
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineProfile
from PyQt6.QtCore import QUrl, QThreadPool, Qt 

from feeds import updateFeeds

# Only needed for access to command line arguments
import sys

# You need one (and only one) QApplication instance per application.
# Pass in sys.argv to allow command line arguments for your app.
# If you know you won't use command line arguments QApplication([]) works too.
app = QApplication(sys.argv)

# Create a Qt widget, which will be our window.
window = QWidget()
window.setWindowTitle('Feed')
layout = QHBoxLayout()

from items import Items
view = QWebEngineView()
items = Items(view,window)
scroll = QScrollArea()
scroll.setWidget(items)
scroll.setWidgetResizable(True)
scroll.setMinimumWidth(500)
layout.addWidget(scroll)



view.load(QUrl("https://duckduckgo.com"))
window.resize(1224, 750)
# Disable cookies
view.page().profile().setPersistentCookiesPolicy(QWebEngineProfile.PersistentCookiesPolicy.NoPersistentCookies)
layout.addWidget(view)
layout.addStretch()
window.setLayout(layout)
window.show()  # IMPORTANT!!!!! Windows are hidden by default.


# Start the event loop.
updateFeeds(items.initialize)
# fetch = FetchFeed()
# fetch.fetched.connect(lambda: items.initialize(fetch.d))
# fetch.getFeeds()
app.exec()



# Your application won't reach here until you exit and the event
# loop has stopped.
