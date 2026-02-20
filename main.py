import os
import shutil # zugriff auf Dateien für PDF/Excel import
import sys

from PySide6.QtWidgets import QApplication, QFileDialog
from PySide6.QtCore import QObject, Slot, Signal, QTimer

from gui import MainWindow

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(PROJECT_ROOT, "temp_uploads") # Ordner für hochgeladene PDF's/Excel


# "Backend" hier definieren
class Backend(QObject):
    notify = Signal(str, str)

    def __init__(self):
        super().__init__()
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        self._window = None

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


app = QApplication(sys.argv)

backend = Backend()

window = MainWindow(backend)  # Backend übergeben
window.show()

sys.exit(app.exec())
