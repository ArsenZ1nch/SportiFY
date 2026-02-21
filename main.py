import os
import shutil # zugriff auf Dateien für PDF/Excel import
import sys

from PySide6.QtWidgets import QApplication, QFileDialog, QMainWindow
from PySide6.QtCore import QObject, Slot, Signal, QTimer, QUrl
from PySide6.QtWebEngineWidgets import QWebEngineView

from gui import MainWindow

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(PROJECT_ROOT, "temp_uploads") # Ordner für hochgeladene PDF's/Excel


# "Backend" hier definieren
class Backend(QObject):
    notify = Signal(str, str)
    windowStateChanged = Signal(str, bool)

    def __init__(self):
        super().__init__()
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        self._window = None
        # track external windows (itslearning, webuntis)
        self._external_windows = {}
        # emit initial state (both closed)
        QTimer.singleShot(0, lambda: self._emit_initial_window_states())

    def set_window(self, window):
        self._window = window
    # Demo PYthon / JS communication
    @Slot()
    def startAssignmentDemo(self):
        print("Zuteilen: Demo gestartet digga")
        QTimer.singleShot(5000, self._assignment_done)

    def _assignment_done(self):
        self.notify.emit("Digga, die Zuteilung ist abgeschlossen. ", "modal")
    
    # window controls begin

    @Slot()
    def windowMinimize(self):
        if self._window:
            self._window.showMinimized()

    @Slot()
    def windowToggleMaximize(self):
        if not self._window:
            return
        if self._window.isMaximized():
            self._window.showNormal()
        else:
            self._window.showMaximized()

    @Slot()
    def windowClose(self):
        if self._window:
            self._window.close()

    @Slot()
    def windowStartDrag(self):
        if not self._window:
            return
        handle = self._window.windowHandle()
        if handle:
            handle.startSystemMove()

    # window controls end
    # file import
    @Slot()
    def importFile(self):
        file_path, _ = QFileDialog.getOpenFileName(
            None,
            "Datei importieren",
            PROJECT_ROOT,
            "Excel/PDF (*.xlsx *.xls *.pdf)"
        )
        if not file_path:
            self.notify.emit("Import abgebrochen.", "warning")
            return
        # wenn user irgendwas dummes hochladen
        ext = os.path.splitext(file_path)[1].lower()
        if ext not in {".xlsx", ".xls", ".pdf"}:
            self.notify.emit("Ungültiger Dateityp. Bitte Excel oder PDF wählen.", "error")
            return

        base_name = os.path.basename(file_path)
        name_root, name_ext = os.path.splitext(base_name)
        target_path = os.path.join(UPLOAD_DIR, base_name)
        counter = 1
        # wenn idiot selbe datei hochlädt umbenennen:
        while os.path.exists(target_path):
            target_path = os.path.join(UPLOAD_DIR, f"{name_root}_{counter}{name_ext}")
            counter += 1

        try:
            shutil.copy2(file_path, target_path)
            self.notify.emit(f"Upload erfolgreich: {os.path.basename(target_path)}", "success")
        except Exception as exc:
            self.notify.emit(f"Upload fehlgeschlagen: {exc}", "error")

    def _emit_initial_window_states(self):
        self.windowStateChanged.emit("itslearning", False)
        self.windowStateChanged.emit("webuntis", False)

    # External browser windows (not frameless)
    @Slot(str)
    def openWindow(self, key: str):
        """Open an external window for the given key. Valid keys: itslearning, webuntis."""
        mapping = {
            "itslearning": ("https://mpg.itslearning.com", "MPG Sportify/itsLearning"),
            "webuntis": ("https://mpg-berlin.webuntis.com/WebUntis/#/basic/login", "MPG Sportify/WebUntis"),
        }
        if key not in mapping:
            self.notify.emit(f"Unbekannter externen Fenster-Key: {key}", "warning")
            return

        # if already open, raise/focus
        if key in self._external_windows and self._external_windows[key]:
            w = self._external_windows[key]
            try:
                w.show()
                w.raise_()
                w.activateWindow()
            except Exception:
                pass
            return

        url, title = mapping[key]

        class BrowserWindow(QMainWindow):
            def __init__(self, url, title):
                super().__init__()
                self.setWindowTitle(title)
                self.resize(1000, 700)
                view = QWebEngineView()
                view.load(QUrl(url))
                self.setCentralWidget(view)

            def closeEvent(self, event):
                try:
                    # emit a QObject.destroyed will also be delivered, but we want
                    # a direct callback to backend. We'll rely on the stored ref.
                    pass
                finally:
                    super().closeEvent(event)

        win = BrowserWindow(url, title)
        win.show()
        self._external_windows[key] = win
        # connect to destroyed to know when closed
        def _on_destroyed(obj=None, k=key):
            # remove reference and notify frontend
            if k in self._external_windows:
                try:
                    del self._external_windows[k]
                except Exception:
                    self._external_windows[k] = None
            self.windowStateChanged.emit(k, False)

        win.destroyed.connect(_on_destroyed)
        # notify frontend that window opened
        self.windowStateChanged.emit(key, True)

    @Slot(str, result=bool)
    def isWindowOpen(self, key: str) -> bool:
        return key in self._external_windows and self._external_windows[key] is not None


app = QApplication(sys.argv)

backend = Backend()

window = MainWindow(backend)  # Backend übergeben
window.show()

sys.exit(app.exec())
