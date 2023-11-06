from PyQt6.QtCore import QThread
class Application:

    def __init__(self):
        super().__init__()
        self.word_clouds = []
        self.corpus = []
        self.threads = []

    def createThread(self):
        thread = QThread()
        self.threads.append(thread)
        return thread

    def close_threads(self):
        for t in self.threads:
            t.quit()

application = Application()