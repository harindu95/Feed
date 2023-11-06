from PyQt6.QtCore import pyqtSignal, QObject, QCoreApplication, QEventLoop, QTimer, Qt

from typing import List
import asyncio


class Connection(QObject):
    done = pyqtSignal()


def plain_text(html):
    from bs4 import BeautifulSoup

    plain = ' '.join(BeautifulSoup(html, "html.parser").findAll(text=True))
    return plain


class GenericWorker(QObject):

    start = pyqtSignal()
    finished = pyqtSignal([object])

    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.start.connect(self.run)

    def run(self):
        self.result = self.func(*self.args, **self.kwargs)
        self.finished.emit(self.result)


class AsyncGeneratorWorker(QObject):

    start = pyqtSignal()
    data = pyqtSignal([object])
    finished = pyqtSignal()

    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs
        # self.start.connect(self.run)
        self.start.connect(self.run, Qt.ConnectionType.DirectConnection)


    # def async_loop(self):
    #     async def task():
    #         async for result in self.func(*self.args,**self.kwargs):
    #             self.data.emit(result)
    #             # self.loop.processEvents()
    #             # await asyncio.sleep(1)  

    #     # self.generator = self.func(*self.args, **self.kwargs)
       
         # None - default executor
    def task(self):
        self.loop = QEventLoop()
        timer = QTimer.singleShot(0, self.loop_call)
        self.finished.connect(self.loop.exit)
        self.loop.exec()
        
    def loop_call(self):
        asyncio.run(self.default())        

    #    self.async_loop.run_until_complete(self.async_func())
    
    # async def async_func(self):
       
    #         generator = self.func(*self.args, **self.kwargs)
            
    #         await asyncio.sleep(10)
    #         await self.get_result(generator)
       
    # async def get_result(self, generator):
    #     try:   
    #         result = await generator.__anext__()
    #         if result is not None:
    #             self.data.emit(result)
    #         await asyncio.sleep(4)            
    #         await self.get_result(generator)
    #     except StopAsyncIteration:
    #         pass

    async def default(self):
        async for result in self.func(*self.args,**self.kwargs):
            self.data.emit(result)
            await asyncio.sleep(0.2)

    def run(self):
        self.async_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.async_loop)
        # self.loop_call()
        self.async_loop.run_until_complete(self.default())
        # self.task()

class AsyncFetch(QObject):

    start = pyqtSignal()
    data = pyqtSignal([object])
    finished = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super().__init__()
        # self.func = func
        self.args = args
        self.kwargs = kwargs
        self.start.connect(self.run)
        # self.start.connect(self.run, Qt.ConnectionType.QueuedConnection)

    def run(self):
        from feeds import get_feeds
        # self.func(*self.args,**self.kwargs)
        get_feeds(self.kwargs['urls'], self.data)
        self.finished.emit()