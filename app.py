from keywords import extract_text
from items import Items
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QScrollArea
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineProfile
from PyQt6.QtCore import QThreadPool, Qt

from toolbar import Toolbar

# Only needed for access to command line arguments
import sys

# You need one (and only one) QApplication instance per application.
# Pass in sys.argv to allow command line arguments for your app.
# If you know you won't use command line arguments QApplication([]) works too.
app = QApplication(sys.argv)

# Create a Qt widget, which will be our window.
window = QWidget()
window.setObjectName('window')
from file import readFile
readFile('style.css',window.setStyleSheet)
window.setWindowTitle('Feed')
layout = QHBoxLayout()

from application import application

view = QWebEngineView()
view.setObjectName('web-engine-view')
from browser import setupWebEngine
setupWebEngine(view,application)

items = Items(view,application)
# scroll.setWidget(items)
# scroll.setObjectName('scroll-area')
# scroll.setWidgetResizable(True)
# scroll.setMinimumWidth(500)
layout.addWidget(items)

QThreadPool.globalInstance().setMaxThreadCount(8)


window.resize(1224, 750)
# Disable cookies
layout.addWidget(view,stretch=1)
toolbar = Toolbar(items,view,application)
toolbar.callback = view
layout.addWidget(toolbar)
layout.addStretch()
window.setLayout(layout)
window.show()  # IMPORTANT!!!!! Windows are hidden by default.

view.page().loadingChanged.connect(
    lambda loadinfo,view=view: extract_text(view, loadinfo, application))
# Start the event loop.
app.aboutToQuit.connect(application.close_threads)

app.exec()


# Your application won't reach here until you exit and the event
# loop has stopped.
