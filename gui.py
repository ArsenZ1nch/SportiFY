import json
import os
from PySide6.QtWidgets import QMainWindow
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebChannel import QWebChannel
from PySide6.QtCore import QUrl, Slot, Qt
from PySide6.QtGui import QColor


class MainWindow(QMainWindow):

    def __init__(self, backend):
        super().__init__()

        self.setWindowTitle("MPG susSportify") # eigentlich egal weil wir benutzen unseren eigenen Rahmen, nicht von Windows
        self.resize(1000, 600) # wenn kleiner dann scheiße weil notifications unten und es sieht goofy ahh aus
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint) # wichtig frameless sonst ricvhtig arsch
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        # self.setStyleSheet("background: transparent;")

        self.backend = backend
        if hasattr(self.backend, "set_window"):
            self.backend.set_window(self)

        self.view = QWebEngineView()
        # self.view.setAttribute(Qt.WA_TranslucentBackground, True)
        self.view.page().setBackgroundColor(QColor(0, 0, 0, 0))
        self.setCentralWidget(self.view)
        

        # Keep a strong reference to the channel; otherwise it can be GC'd ## war im stackoverflow code drinne
        # and the JS side never gets the backend object.
        self.channel = QWebChannel(self.view.page())
        self.channel.registerObject("backend", self.backend)
        self.view.page().setWebChannel(self.channel)

        path = os.path.abspath("gui/index.html") # ich weiß nicht wie windows file system also kann sein nur unix, bitte testen und mir sagen - Andreas
        self.view.load(QUrl.fromLocalFile(path))

        self.page_ready = False
        self.pending_notifications = []
        self.view.loadFinished.connect(self._on_load_finished)
        self.backend.notify.connect(self._handle_notify)

    def _on_load_finished(self, ok):
        self.page_ready = ok
        if not ok: # traurig :(
            return
        if self.pending_notifications:
            for message, level in self.pending_notifications:
                self._emit_notification_js(message, level)
            self.pending_notifications = []

    @Slot(str, str)
    def _handle_notify(self, message, level):
        if not self.page_ready:
            self.pending_notifications.append((message, level))
            return
        self._emit_notification_js(message, level)

    def _emit_notification_js(self, message, level):
        payload = json.dumps(message)
        level_payload = json.dumps(level)
        script = f"window.__notifyFromPython({payload}, {level_payload});"
        self.view.page().runJavaScript(script)

if __name__ == "__main__":
    print ( "Skibidi Toilet: nicht ausführen goofy " )
else:
    pass