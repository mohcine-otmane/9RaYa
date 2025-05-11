from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLineEdit, QListWidget, QLabel, QPushButton, QFileDialog,
                             QMessageBox, QProgressBar)
from PyQt6.QtCore import Qt, QSize, QThread, pyqtSignal
from .pdf_card import PDFCard
from utils.pdf_utils import generate_thumbnail
from utils.file_utils import get_pdf_files
import os
import sys
import traceback

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
        
        self.current_path = None
        self.workers = []
        self.setup_ui()
        self.load_styles()
        self.select_folder()

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

        self.files_list = QListWidget()
        self.files_list.setViewMode(QListWidget.ViewMode.IconMode)
        self.files_list.setIconSize(QSize(150, 200))
        self.files_list.setSpacing(10)
        self.files_list.setResizeMode(QListWidget.ResizeMode.Adjust)
        layout.addWidget(self.files_list)

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
            self.load_files()

    def load_files(self):
        if not self.current_path:
            return
            
        self.files_list.clear()
        try:
            pdf_files = get_pdf_files(self.current_path)
            if not pdf_files:
                QMessageBox.information(self, "No PDFs Found", 
                    "No PDF files found in the selected folder.")
                return

            # Cancel any existing workers
            for worker in self.workers:
                worker.quit()
                worker.wait()
            self.workers.clear()

            # Setup progress bar
            self.progress_bar.setMaximum(len(pdf_files))
            self.progress_bar.setValue(0)
            self.progress_bar.setVisible(True)

            # Create placeholder items
            for pdf_file in pdf_files:
                card = PDFCard(pdf_file, None)
                self.files_list.addItem(card)

            # Start thumbnail generation in background
            for i, pdf_file in enumerate(pdf_files):
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
        for i in range(self.files_list.count()):
            item = self.files_list.item(i)
            if item.filename == filename:
                item.set_thumbnail(thumbnail_path)
                break
        self.progress_bar.setValue(self.progress_bar.value() + 1)
        if self.progress_bar.value() >= self.progress_bar.maximum():
            self.progress_bar.setVisible(False)

    def on_thumbnail_error(self, filename, error):
        print(f"Error generating thumbnail for {filename}: {error}")
        self.progress_bar.setValue(self.progress_bar.value() + 1)
        if self.progress_bar.value() >= self.progress_bar.maximum():
            self.progress_bar.setVisible(False)

    def filter_files(self):
        search_text = self.search_input.text().lower()
        for i in range(self.files_list.count()):
            item = self.files_list.item(i)
            item.setHidden(search_text not in item.text().lower()) 