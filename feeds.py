import feedparser
from PyQt6.QtCore import QRunnable, QUrl
from PyQt6.QtCore import pyqtSignal, QObject, Qt, QEventLoop, QThreadPool
import PyQt6.QtNetwork as QtNetwork


def parse_image(content):
    import lxml.etree
    source = '<div>{}</div>'.format(content).replace('&hellip;', '')
    # print(source)
    tree = lxml.etree.fromstring(source)
    images = tree.xpath("///img/@src")
    if len(images) > 0:
        return images[0]
    else:
        return ''


class Connection(QObject):
    done = pyqtSignal()


def updateFeeds(callback):
    urls = ['https://www.theverge.com/rss/frontpage',
            'http://www.reddit.com/r/Buddhism/.rss',
            'https://www.youtube.com/feeds/videos.xml?playlist_id=PLrEnWoR732-BHrPp_Pm8_VleD68f9s14-']
    for url in urls:
        fetch = FetchFeed(url)
        fetch.c.done.connect(lambda fetch=fetch: callback(
            fetch.feed), Qt.ConnectionType.QueuedConnection)
        QThreadPool.globalInstance().start(fetch)


class FetchFeed(QRunnable):

    def __init__(self, url, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.url = url
        self.c = Connection()

    def run(self):
        print("FetchFeeds Running in worker thread")
        event_loop = QEventLoop()
        self.c.done.connect(event_loop.exit)
        self.getFeed(self.url)
        event_loop.exec()

    def getFeed(self, url):
        print(url)
        self.nam = QtNetwork.QNetworkAccessManager()
        req = QtNetwork.QNetworkRequest(QUrl(url))
        self.nam.finished.connect(self.handle_request)
        self.nam.get(req)

    def handle_request(self, reply: QtNetwork.QNetworkReply):
        er = reply.error()
        if er == QtNetwork.QNetworkReply.NetworkError.NoError:
            qbyte = reply.readAll()
            self.feed = feedparser.parse(str(qbyte, 'utf-8'))

            for post in self.feed.entries:
                # print(post.title)
                if "media_thumbnail" in post:
                    post.image_url = post.media_thumbnail[0]['url']
                else:
                    post.image_url = parse_image(post.summary)

            print("FetchFeeds:handle_request: Signal emit")
            self.c.done.emit()
        else:
            print("Error")
            print(reply.errorString())


# class Fetch:

#     def __init__(self, x, nam, urls):
#         self.x = x
#         self.urls = urls
#         self.nam = nam

#     def call(self):
#         # self.nam.finished.disconnect(self.call)
#         self.x += 1
#         x = self.x
#         if x < len(self.urls):
#             # next = Fetch(x,self.nam,self.urls)
#             # self.nam.finished.connect(next.call)
#             print('x : ', x)
#             self.getFeed(self.urls[x])
#         else:
#             print(' x: ', x)
#             if x > 6:
#                 self.nam.finished.disconnect()

#     def getFeed(self, url):
#         req = QtNetwork.QNetworkRequest(QUrl(url))
#         self.nam.get(req)


# class FetchFeed(QObject):

    # fetched = pyqtSignal(name='fetched')

    # def getFeeds(self):
    #     self.nam = QtNetwork.QNetworkAccessManager()
    #     urls = ['https://www.theverge.com/rss/frontpage',
    #             'http://www.reddit.com/r/Buddhism/.rss',
    #             'https://www.youtube.com/feeds/videos.xml?playlist_id=PLrEnWoR732-BHrPp_Pm8_VleD68f9s14-']

    #     x = 0
    #     self.fetch = Fetch(x, self.nam, urls)
    #     self.nam.finished.connect(self.fetch.call)
    #     self.getFeed(urls[0])

    # def getFeed(self, url):
    #     req = QtNetwork.QNetworkRequest(QUrl(url))

    #     self.nam.finished.connect(self.handle_request)
    #     self.nam.get(req)

    # def handle_request(self, reply: QtNetwork.QNetworkReply):
    #     er = reply.error()
    #     if er == QtNetwork.QNetworkReply.NetworkError.NoError:
    #         qbyte = reply.readAll()
    #         self.d = feedparser.parse(str(qbyte, 'utf-8'))

    #         for post in self.d.entries:
    #             # print(post.title)
    #             if "media_thumbnail" in post:
    #                 post.image_url = post.media_thumbnail[0]['url']
    #             else:
    #                 post.image_url = parse_image(post.summary)

    #         self.fetched.emit()

    #     else:
    #         print("Error")
    #         print(reply.errorString())

    # f = open("sample.rss", "r")
    # lines = f.readlines()
    # from io import BytesIO

    # # with open('sample.rss', "rb") as fh:
    # #     buf = BytesIO(fh.read())
    # #     d = feedparser.parse(buf)
    # d = feedparser.parse('http://blogs.law.harvard.edu/tech/rss')
    # d = feedparser.parse('http://www.reddit.com/r/Buddhism/.rss')
    # url = 'https://www.theverge.com/rss/frontpage'
    # # url = 'https://www.youtube.com/feeds/videos.xml?channel_id=UCnCikd0s4i9KoDtaHPlK-JA'
    # # url = 'http://www.reddit.com/r/Buddhism/.rss'
    # d = feedparser.parse(url)
