import functools
import pprint
import async_timeout
import asyncio
import aiohttp
import feedparser
from PyQt6.QtCore import QRunnable, QUrl
from PyQt6.QtCore import pyqtSignal, QObject, Qt, QEventLoop, QThreadPool
import PyQt6.QtNetwork as QtNetwork
from queue import Queue
from common import Connection




tasks = []


def updateFeeds(callback, end):
    from config import urls
    # for url in urls:
    #     fetch = FetchFeed(url)
    #     fetch.c.done.connect(lambda fetch=fetch: callback(
    #         fetch.feed), Qt.ConnectionType.QueuedConnection)
    #     QThreadPool.globalInstance().start(fetch)
    for url in urls:
        fetch = AsyncFetchFeeds([url])
        fetch.setAutoDelete(False)
        tasks.append(fetch)
        end.connect(fetch.quit)
        fetch.c.done.connect(lambda fetch=fetch: callback(
            fetch.feeds), Qt.ConnectionType.AutoConnection)
        QThreadPool.globalInstance().start(fetch)

    # def check_feeds(fetch):
    #     # timer.start(100)
    #     while len(fetch.feeds) > 0:
    #         feed = fetch.feeds.pop()
    #         callback(feed)

    # timer.timeout.connect(lambda fetch=fetch: check_feeds)
    # timer.start(10)


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


INTERVAL = 60


async def fetch(session, url):
    with async_timeout.timeout(10):
        async with session.get(url) as response:
            return await response.text()


def run_in_executor(f):
    @functools.wraps(f)
    def inner(*args, **kwargs):
        loop = asyncio.get_running_loop()
        return loop.run_in_executor(None, lambda: f(*args, **kwargs))

    return inner


async def get_image(path):
    async with aiohttp.ClientSession() as session:
        async with session.get(path) as response:
            return await response.read()


@run_in_executor
def parse_image(content):
    import lxml.etree
    source = '<div>{}</div>'.format(content).replace('&hellip;', '')
    # print(source)
    tree = lxml.etree.fromstring(source)
    images = tree.xpath("///img/@src")
    if len(images) > 0:
        return images[0]
    else:
        images = tree.xpath("///video/@poster")
        if len(images) > 0:
            return images[0]
        else:
            return ''


@run_in_executor
def parse_rss(html):
    return feedparser.parse(html)


def keys_exists(element, *keys):
    '''
    Check if *keys (nested) exists in `element` (dict).
    '''
    if not isinstance(element, dict):
        raise AttributeError('keys_exists() expects dict as first argument.')
    if len(keys) == 0:
        raise AttributeError(
            'keys_exists() expects at least two arguments, one given.')

    _element = element
    for key in keys:
        try:
            _element = _element[key]
        except KeyError:
            return False
    return True


class AsyncFetchFeeds(QRunnable):

    def __init__(self, urls, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.urls = urls
        self.exit = False
        self.feeds = {}
        self.record = []
        self.c = Connection()

    def loop_exit(self):
        for task in asyncio.Task.all_tasks():
            if not task.done():
                task.cancel()

        self.loop.stop()

    def quit(self):
        print("AsyncFetchFeeds:exit About to Quit")
        self.exit = True
        self.loop.call_soon_threadsafe(self.loop_exit)
        self.setAutoDelete(True)
        QThreadPool.globalInstance().clear()

    async def process_feed(self, rss):

        for post in rss.entries:
            # print(post.title)
            post.title = post.title if 'title' in post else ''
            if "media_thumbnail" in post:
                post.image_url = post.media_thumbnail[0]['url']
            else:
                post.image_url = await parse_image(post.summary)
                if post.image_url == '':
                    try:
                        post.image_url = rss.feed.logo
                        # post.image_url = rss.feed.icon

                    except Exception:
                        print(rss.feed)
                        pass

            if post.image_url != '':
                post.image_data = await get_image(post.image_url)

        self.feeds = rss
        print("FetchFeeds:handle_request: Signal emit")
        # self.timer.start(0)
        self.c.done.emit()

    async def fetchfeeds(self, loop, feedurls):
        if self.exit:
            return

        # feeds = []
        if self.record == []:
            for url in feedurls:
                self.record.append({'url': url, 'last': ""})

        if self.exit:
            return
        
        headers = {'UserAgent':'Mozilla/5.0 (Linux; Android 13; Pixel 7 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36'}

        for feed in self.record:
            # async with aiohttp.ClientSession(loop=loop,headers=headers) as session:
            #     # await asyncio.sleep(2)
            #     html = await fetch(session, feed['url'])
                rss = await parse_rss(feed['url'])

                if feed['last']:
                    if feed['last']['title'] != rss['entries'][0]['title'] and feed['last']['link'] != rss['entries'][0]['link']:
                        print("new entry")
                        feed['last'] = rss['entries'][0]
                        await self.process_feed(rss)
                        # print("MSG {}".format(feed['last']['title']))
                        # print("MSG {}".format(feed['last']['link']))
                else:
                    try:
                        feed['last'] = rss['entries'][0]
                        print("new entry")
                        await self.process_feed(rss)
                    except IndexError:
                        print(rss)
        if self.exit != True:
            await asyncio.sleep(INTERVAL)

    def run(self):
        if not self.exit:

            # self.qt_loop = QEventLoop()
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            # loop = asyncio.get_event_loop()
            try:
                self.loop.run_until_complete(
                    self.fetchfeeds(self.loop, self.urls))
            except RuntimeError as err:
                if self.exit:
                    # Exit app
                    return
                else:
                    print(err)
            QThreadPool.globalInstance().start(self)
