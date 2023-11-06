import typing
from PyQt6 import QtCore
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineProfile
from PyQt6.QtCore import QUrl, QObject, QThreadPool, QThread, QRunnable, pyqtSignal, Qt,pyqtSlot
from PyQt6.QtWebEngineCore import QWebEngineUrlRequestInterceptor, QWebEngineUrlRequestInfo, QWebEngineScript
from adblockparser import AdblockRules
import adblock
# import aiofiles

# rules = AdblockRules(raw_rules,use_re2=True, max_mem=512*1024*1024)

type = QWebEngineUrlRequestInfo.ResourceType
resources = {
    type.ResourceTypeFontResource: 'font',
    type.ResourceTypeImage: 'image',
    type.ResourceTypeMainFrame: 'main_frame',
    type.ResourceTypeMedia: 'media',
    type.ResourceTypeObject: 'object',
    type.ResourceTypeScript: 'script',
    type.ResourceTypePing: 'ping',
    type.ResourceTypePluginResource: 'object_subrequest',
    type.ResourceTypeStylesheet: 'stylesheet',
    type.ResourceTypeSubFrame: 'sub_frame',
    type.ResourceTypeXhr: "xmlhttprequest",
    type.ResourceTypeUnknown: 'other',
    type.ResourceTypeWebSocket: "websocket",
    type.ResourceTypeSubResource: "other"
}


def getResourceType(type):
    if type in resources:
        return resources[type]
    else:
        return 'other'


def read_filterset():
    import glob
    files = glob.glob("./filters/*.txt")
    rules = []
    for path in files:
        with open(path, encoding='utf-8') as f:
            raw_rules = '\n'.join(f.readlines())
            rules.append(raw_rules)
            # self.filterset.add_filter_list(raw_rules,format="standard")
    return rules


class WebEngineUrlRequestInterceptor(QWebEngineUrlRequestInterceptor):

    def __init__(self, view: QWebEngineView, application,*args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.view = view
        self.settings = application
        self.read_thread = application.createThread()
        # settings.threads.append(self.read_thread)
        # self.read_thread.start()
                
        from common import GenericWorker
        #  FuncThread(self.read_filterset)

        read_worker = GenericWorker(read_filterset)
        read_worker.moveToThread(self.read_thread)
        n = QThreadPool.globalInstance().activeThreadCount()
        read_worker.finished.connect(self.initialize, Qt.ConnectionType.QueuedConnection)
        read_worker.start.emit()
        
        # self.rules = []
        # self.inject_thread = QThread()
        # self.inject_thread.start()
        self.scripts = {}

        self.initialize = False
        self.view.page().loadStarted.connect(self.inject)

    def show_readable(self, article):
        doc = '''
        <html>
        <body>
        <h1>{title}</h1>
        <div>{content}</div>
        <body>
        </html>
        '''.format(title=article['title'], content=article['content'])

        self.view.page().setHtml(doc, QUrl('about:readable'))

    def dark_mode(self):
        url = self.view.page().url().toString()
        if url.startswith('about:'):
            return
        script = '\n'.join(open('Readability.js').readlines())
        # init_script = '\n'.join(open('show_readable.js').readlines())
        init_script = '''
        var documentClone = document.cloneNode(true);
        var article = new Readability(documentClone).parse();
        article;
        '''
        script += init_script
        # css = 'div *:not(img),p{background-color:white;filter:saturate(10%) invert(100%);} img{filter:invert(100%) saturate(1000%);}'
        # css_script = '''
        # window.onload = function(){{
        #     let styles = `{}`
        #     var styleSheet = document.createElement("style")
        #     styleSheet.innerText = styles
        #     document.head.appendChild(styleSheet)
        # }};
        # '''.format(css)

        # s = QWebEngineScript()
        # s.setInjectionPoint(QWebEngineScript.InjectionPoint.DocumentReady)
        # s.setSourceCode(script)
        # self.view.page().scripts().insert(s)
        self.view.page().runJavaScript(script, self.show_readable)
        # self.inject_thread.fireChanged.emit()

    # from types import List,str
    from typing import List
    def initialize(self, rules:List[str]):
        print("Adblock initialized")
        print("rules: {}", len(rules) )
        self.filterset = adblock.FilterSet()
        for rule in rules:
            self.filterset.add_filter_list(rule, format='standard')
        self.adblock = adblock.Engine(self.filterset, optimize=True)
        self.initialize = True

    def injectScript(self, url:str, cosmetic: adblock.UrlSpecificResources):
        css_hide = '{} {{ display: none !important }}'
        css = css_hide.format(','.join(cosmetic.hide_selectors))
        css_script = '''
        function adblock(){{
            let styles = `{}`
            var styleSheet = document.createElement("style")
            styleSheet.innerText = styles
            document.head.appendChild(styleSheet)
        }}
        if (document.readyState !== 'loading') 
            adblock();
        else 
            document.addEventListener('DOMContentLoaded', adblock );
        
        '''.format(css)
        # print("Injecting script ....", cosmetic.hide_selectors)
        # self.view.page().runJavaScript(css_script)
        if url in self.scripts:
            self.scripts[url].append(css_script)
        else:
            self.scripts[url] = [css_script]

    def inject(self):
        url = self.view.page().url().toString()
        if not url in self.scripts:
            return
        scripts = self.scripts[url]
        for script in scripts:
            # self.view.page().runJavaScript(script)
            engine_script = QWebEngineScript()
            engine_script.setSourceCode(script)
            engine_script.setInjectionPoint(
                QWebEngineScript.InjectionPoint.DocumentCreation)
            self.view.page().scripts().insert(engine_script)

    def interceptRequest(self, info :QWebEngineUrlRequestInfo):
        if not self.initialize:
            return
        url = info.requestUrl().toString()
        sourceUrl = info.initiator().toString()
        request_type = getResourceType(info.resourceType())
        result = self.adblock.check_network_urls(url, sourceUrl, request_type)

        if result.matched:
            # print("block::::::::::::::::::::::", url)
            info.block(True)
        else:
            cosmetic = self.adblock.url_cosmetic_resources(url)
            self.injectScript(url, cosmetic)
            # QThreadPool.globalInstance().start(lambda cosmetic=cosmetic:self.injectScript(cosmetic))
            # print(result)


def setupWebEngine(view, settings):
    # view = QWebEngineView()
    view.setObjectName('web-engine-view')
    view.load(QUrl("https://duckduckgo.com"))
    view.page().profile().setPersistentCookiesPolicy(
        QWebEngineProfile.PersistentCookiesPolicy.NoPersistentCookies)
    interceptor = WebEngineUrlRequestInterceptor(view, settings,parent=view)
    view.page().profile().setUrlRequestInterceptor(interceptor)
