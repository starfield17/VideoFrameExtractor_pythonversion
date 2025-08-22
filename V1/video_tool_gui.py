# video_tool_gui.py
from __future__ import annotations
import sys
from pathlib import Path
from PyQt6 import QtWidgets, QtCore
from video_tool_core import extract_frames, convert_to_mp4, merge_videos_recursively

class Worker(QtCore.QThread):
    line = QtCore.pyqtSignal(str)
    done = QtCore.pyqtSignal(bool)

    def __init__(self, fn, arg):
        super().__init__()
        self.fn = fn
        self.arg = arg

    def run(self):
        def logger(msg: str):
            self.line.emit(msg)
        ok = self.fn(self.arg, log=logger)
        self.done.emit(ok)

class ToolTab(QtWidgets.QWidget):
    def __init__(self, label: str, picker_kind: str, action_label: str, action_fn):
        super().__init__()
        self.action_fn = action_fn
        self.picker_kind = picker_kind

        self.path_edit = QtWidgets.QLineEdit()
        browse_btn = QtWidgets.QPushButton("Browse…")
        browse_btn.clicked.connect(self.browse)

        top = QtWidgets.QHBoxLayout()
        top.addWidget(QtWidgets.QLabel(label))
        top.addWidget(self.path_edit)
        top.addWidget(browse_btn)

        self.run_btn = QtWidgets.QPushButton(action_label)
        self.run_btn.clicked.connect(self.start)
        self.log = QtWidgets.QTextEdit()
        self.log.setReadOnly(True)

        v = QtWidgets.QVBoxLayout(self)
        v.addLayout(top)
        v.addWidget(self.run_btn)
        v.addWidget(self.log)

        self.worker: Worker | None = None

    def browse(self):
        if self.picker_kind == "file":
            p, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select video file")
            if p:
                self.path_edit.setText(p)
        else:
            d = QtWidgets.QFileDialog.getExistingDirectory(self, "Select directory")
            if d:
                self.path_edit.setText(d)

    def start(self):
        path = self.path_edit.text().strip()
        if not path:
            QtWidgets.QMessageBox.warning(self, "Missing path", "Please choose a file or folder.")
            return
        if not Path(path).exists():
            QtWidgets.QMessageBox.critical(self, "Invalid path", f"'{path}' does not exist.")
            return
        self.run_btn.setEnabled(False)
        self.log.clear()
        self.worker = Worker(self.action_fn, path)
        self.worker.line.connect(lambda s: self.log.append(s))
        self.worker.done.connect(self.finish)
        self.worker.start()

    def finish(self, ok: bool):
        self.log.append("\n✅ Done." if ok else "\n❌ Finished with errors.")
        self.run_btn.setEnabled(True)
        self.worker = None

class Main(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Video Processing Tool (OpenCV)")
        tabs = QtWidgets.QTabWidget()

        tabs.addTab(ToolTab("Input (file or folder):", "file_or_dir", "Extract Frames",
                            lambda p, log=print: extract_frames(p, log=log)), "Extract Frames")

        tabs.addTab(ToolTab("Input (file or folder):", "file_or_dir", "Convert to MP4 (video only)",
                            lambda p, log=print: convert_to_mp4(p, log=log)), "Convert to MP4")

        tabs.addTab(ToolTab("Input (folder):", "dir", "Merge Videos per Directory",
                            lambda p, log=print: merge_videos_recursively(p, log=log)), "Merge Videos")

        self.setCentralWidget(tabs)
        self.resize(800, 600)

def main():
    app = QtWidgets.QApplication(sys.argv)
    w = Main()
    w.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

