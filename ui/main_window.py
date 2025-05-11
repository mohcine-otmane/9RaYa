from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLineEdit, QLabel, QPushButton, QFileDialog,
                             QMessageBox, QProgressBar, QScrollArea, QGridLayout)
from PyQt6.QtCore import Qt, QSize, QThread, pyqtSignal
from .pdf_card import PDFCardWidget
from utils.pdf_utils import generate_thumbnail
from utils.file_utils import get_pdf_files
import os
import sys
import traceback
import json

CONFIG_PATH = os.path.join(os.path.expanduser("~"), ".pdf_viewer_config")

class ThumbnailWorker(QThread):
    finished = pyqtSignal(str, str)
    error = pyqtSignal(str, str)
    
    def __init__(self, pdf_path, filename):
        super().__init__()
        self.pdf_path = pdf_path
        self.filename = filename
        
    def run(self):
        try:
            thumbnail = generate_thumbnail(self.pdf_path)
            self.finished.emit(self.filename, thumbnail)
        except Exception as e:
            self.error.emit(self.filename, str(e))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF Viewer (Read Only)")
        self.setMinimumSize(1000, 600)
        self.current_path = self.load_last_folder()
        self.workers = []
        self.pdf_files = []
        self.thumbnails = {}
        self.setup_ui()
        self.load_styles()
        if not self.current_path:
            self.select_folder()
        else:
            self.load_files()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        top_bar = QHBoxLayout()
        self.folder_btn = QPushButton("Select Folder")
        self.folder_btn.clicked.connect(self.select_folder)
        self.folder_btn.setStyleSheet("""
            QPushButton {
                background-color: #2d2d2d;
                border: 1px solid #3d3d3d;
                padding: 5px 15px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #3d3d3d;
            }
        """)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search PDFs...")
        self.search_input.textChanged.connect(self.filter_files)
        read_only_label = QLabel("Read Only Mode")
        read_only_label.setStyleSheet("color: #ff6b6b; font-weight: bold;")
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #3d3d3d;
                border-radius: 3px;
                text-align: center;
                background-color: #2d2d2d;
            }
            QProgressBar::chunk {
                background-color: #4a90e2;
            }
        """)
        top_bar.addWidget(self.folder_btn)
        top_bar.addWidget(self.search_input)
        top_bar.addWidget(read_only_label)
        top_bar.addWidget(self.progress_bar)
        layout.addLayout(top_bar)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.grid_widget = QWidget()
        self.grid_layout = QGridLayout(self.grid_widget)
        self.grid_layout.setSpacing(16)
        self.scroll_area.setWidget(self.grid_widget)
        layout.addWidget(self.scroll_area)
        self.central_layout = layout

    def load_styles(self):
        with open("styles.qss", "r") as f:
            self.setStyleSheet(f.read())

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select PDF Folder",
            self.current_path if self.current_path else os.path.expanduser("~"),
            QFileDialog.Option.ShowDirsOnly
        )
        if folder:
            self.current_path = folder
            self.save_last_folder(folder)
            self.load_files()

    def load_files(self):
        if not self.current_path:
            return
        self.clear_grid()
        try:
            self.pdf_files = get_pdf_files(self.current_path)
            if not self.pdf_files:
                QMessageBox.information(self, "No PDFs Found", 
                    "No PDF files found in the selected folder.")
                return
            for worker in self.workers:
                worker.quit()
                worker.wait()
            self.workers.clear()
            self.progress_bar.setMaximum(len(self.pdf_files))
            self.progress_bar.setValue(0)
            self.progress_bar.setVisible(True)
            self.thumbnails = {}
            for i, pdf_file in enumerate(self.pdf_files):
                worker = ThumbnailWorker(
                    os.path.join(self.current_path, pdf_file),
                    pdf_file
                )
                worker.finished.connect(self.on_thumbnail_ready)
                worker.error.connect(self.on_thumbnail_error)
                self.workers.append(worker)
                worker.start()
        except Exception as e:
            print("Error loading PDFs:")
            print(traceback.format_exc())
            QMessageBox.critical(self, "Error",
                "An error occurred while loading PDFs. Please check the console for details.")

    def on_thumbnail_ready(self, filename, thumbnail_path):
        self.thumbnails[filename] = thumbnail_path
        self.progress_bar.setValue(self.progress_bar.value() + 1)
        if self.progress_bar.value() >= self.progress_bar.maximum():
            self.progress_bar.setVisible(False)
            self.display_grid()

    def on_thumbnail_error(self, filename, error):
        print(f"Error generating thumbnail for {filename}: {error}")
        self.progress_bar.setValue(self.progress_bar.value() + 1)
        if self.progress_bar.value() >= self.progress_bar.maximum():
            self.progress_bar.setVisible(False)
            self.display_grid()

    def clear_grid(self):
        for i in reversed(range(self.grid_layout.count())):
            widget = self.grid_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

    def display_grid(self):
        self.clear_grid()
        if not self.pdf_files:
            return
        width = self.scroll_area.viewport().width()
        thumb_width = 170
        spacing = self.grid_layout.spacing()
        columns = max(1, width // (thumb_width + spacing))
        row = 0
        col = 0
        for pdf_file in self.pdf_files:
            thumb = self.thumbnails.get(pdf_file)
            card = PDFCardWidget(pdf_file, thumb)
            self.grid_layout.addWidget(card, row, col)
            col += 1
            if col >= columns:
                col = 0
                row += 1
        self.grid_widget.adjustSize()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.display_grid()

    def filter_files(self):
        search_text = self.search_input.text().lower()
        self.pdf_files = [f for f in get_pdf_files(self.current_path) if search_text in f.lower()]
        self.display_grid()

    def save_last_folder(self, folder):
        try:
            with open(CONFIG_PATH, "w") as f:
                json.dump({"last_folder": folder}, f)
        except Exception as e:
            print(f"Failed to save config: {e}")

    def load_last_folder(self):
        try:
            if os.path.exists(CONFIG_PATH):
                with open(CONFIG_PATH, "r") as f:
                    data = json.load(f)
                    return data.get("last_folder")
        except Exception as e:
            print(f"Failed to load config: {e}")
        return None 