from PyQt6.QtCore import QTimer
from common import GenericWorker
from PyQt6.QtCore import QThread
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


def updateFeeds(application,callback):
    from config import urls

    for url in urls:
        fetch = AsyncFetchFeeds([url])
        fetch.setAutoDelete(False)
        tasks.append(fetch)
        application.threads.append(fetch)
        fetch.c.done.connect(lambda fetch=fetch: callback(
            fetch.feeds), Qt.ConnectionType.AutoConnection)
        QThreadPool.globalInstance().start(fetch, 0)


# def check_feeds(fetch):
#     # timer.start(100)
#     while len(fetch.feeds) > 0:
#         feed = fetch.feeds.pop()
#         callback(feed)

# timer.timeout.connect(lambda fetch=fetch: check_feeds)
# timer.start(10)


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
def parse_image(post, rss):
    import lxml.html
    import lxml.html.clean
    import lxml.etree
    content = post.content[0].value
    html = lxml.html.fromstring(content)
    cleaner = lxml.html.clean.Cleaner(style=True)
    doc = cleaner.clean_html(html)
    # return
    # source = '<div>{}</div>'.format(doc)
    # print(source)
    # tree = lxml.etree.fromstring(source)
    # images = tree.xpath("img/@src")
    images = doc.xpath("//img/@src")

    if len(images) > 0:
        return images[0]
    else:
        images = doc.xpath("video/@poster")
        if len(images) > 0:
            return images[0]
        else:
            try:
                if 'image' in rss.feed:
                    return rss.feed.image.href
                elif 'logo' in rss.feed:
                    return rss.feed.logo
            except Exception as e:
                print("no image found", post.title)

            return ''


@run_in_executor
def parse_rss(html):
    return feedparser.parse(html)


# @run_in_executor
# async def process_feed(feed):
#     for i, post in enumerate(feed.entries):
#         if not 'summary' in post:
#             feed.entries[i] = {}
#             feed.entries[i].summary = post
#             post = feed.entries[i]
#             post.title = ''
#         # print(post.title)
#         if "media_thumbnail" in post:
#             post.image_url = post.media_thumbnail[0]['url']
#         # elif "media_content" in post and len(post.media_content) > 0 and 'url' in post.media_content[0]:
#         elif "media_content" in post:

#             post.image_url = post.media_content[0]['url']
#         else:
#             post.image_url = await parse_image(post)

#     return feed

@run_in_executor
def process_description(text):
    from bs4 import BeautifulSoup

    plain = ' '.join(BeautifulSoup(text, "html.parser").findAll(text=True))
    # doc.setHtml(text)
    # plain = doc.toPlainText()
    return plain.strip()


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


async def process_feed(rss):
    for i, post in enumerate(rss.entries):
        # print(post.title)
        if not 'content' in post:
            if 'summary' in post:
                from collections import UserDict
                post.content = [UserDict()]
                post.content[0].value = post.summary
            else:
                p = feedparser.FeedParserDict()
                p.summary = post
                from collections import UserDict
                p.content = [UserDict()]
                p.content[0].value = post
                rss.entries[i] = p
                post = p
        if not 'title' in post:
            p.title = ''

        # post.title = post.title if 'title' in post else ''
        if "media_thumbnail" in post:
            post.image_url = post.media_thumbnail[0]['url']
        elif "media_content" in post:
            post.image_url = post.media_content[0]['url']
        else:
            post.image_url = await parse_image(post, rss)
            if len(post.image_url) == 0:
                try:
                    if 'image' in rss.feed:
                        post.image_url = rss.feed.image.href
                    elif 'logo' in rss.feed:
                        post.image_url = rss.feed.logo
                    # post.image_url = rss.feed.icon

                except Exception:
                    # print(rss.feed)
                    pass

        if post.image_url != '':
            post.image_data = await get_image(post.image_url)

        post.title = await process_description(post.title)
        post.description = await process_description(post.summary)

# def get_feeds(urls, signal):
#     record = []

#     async def task():
#         async for f in fetchfeeds(urls):
#             await process_feed(f)
#             signal.emit(f)

#     asyncio.run(task())


class AsyncFetchFeeds(QRunnable):

    def __init__(self, urls, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.urls = urls
        self.exit = False
        self.feeds = []
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
        # if self.loop.is_running():
            # self.loop.call_soon_threadsafe(self.loop_exit)
        self.setAutoDelete(True)
        QThreadPool.globalInstance().clear()

    async def fetchfeeds(self, feedurls):

        if self.record == []:
            for url in feedurls:
                self.record.append({'url': url, 'last': ""})

        ACCEPT_HEADER: str = (
            "application/atom+xml"
            ",application/rdf+xml"
            ",application/rss+xml"
            ",application/x-netcdf"
            ",application/xml"
            ";q=0.9,text/xml"
            ";q=0.2,*/*"
            ";q=0.1"
        )

        headers = {'User-Agent': 'Mozilla/5.0 (Linux; Android 13; Pixel 7 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36',
                   'Accept': ACCEPT_HEADER
                   }

        for feed in self.record:
            conn = aiohttp.TCPConnector(limit_per_host=5)
            async with aiohttp.ClientSession(headers=headers, connector=conn) as session:
                # await asyncio.sleep(2)
                html = await fetch(session, feed['url'])
                rss = await parse_rss(html)

                if feed['last']:
                    if len(rss.entries) < 1:
                        continue
                    if feed['last']['title'] != rss['entries'][0]['title'] and feed['last']['link'] != rss['entries'][0]['link']:
                        feed['last'] = {}
                        feed['last'].title = rss['entries'][0].title
                        feed['last'].link = rss['entries'][0].link
                        print("RSS Feed updated: ", feed.url)
                        print("MSG {}".format(feed['last']['title']))
                        print("MSG {}".format(feed['last']['link']))
                        await process_feed(rss)
                        self.feeds.append(rss)
                else:
                    try:
                        feed['last'] = rss['entries'][0]
                        print("RSS Feed updated: ", feed['url'])
                        if not 'summary' in rss['entries'][0]:
                            print('No entry summary', rss)
                        await process_feed(rss)
                        self.feeds.append(rss)
                    except IndexError:
                        print("No entry:", rss)
                
        print("FetchFeeds:handle_request: Signal emit")
        # self.timer.start(0)
        self.c.done.emit()

    def run(self):
        if not self.exit:

            # self.qt_loop = QEventLoop()
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            # self.loop.set_debug(True)
            # loop = asyncio.get_event_loop()
            try:
                self.loop.run_until_complete(
                    self.fetchfeeds(self.urls))
            except RuntimeError as err:
                if self.exit:
                    # Exit app
                    return
                else:
                    print(err)
                    pass
            finally:
                pass
                # self.loop.close()
            # QThreadPool.globalInstance().start(self)
            QTimer.singleShot(INTERVAL * 1000, self.run)
