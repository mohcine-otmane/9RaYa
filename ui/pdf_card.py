from PyQt6.QtWidgets import QListWidgetItem
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtCore import Qt
import os

class PDFCard(QListWidgetItem):
    def __init__(self, filename, thumbnail_path=None):
        super().__init__()
        self.filename = filename
        self.setText(filename)
        self.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        
        if thumbnail_path:
            self.set_thumbnail(thumbnail_path)
            
    def set_thumbnail(self, thumbnail_path):
        if os.path.exists(thumbnail_path):
            pixmap = QPixmap(thumbnail_path)
            if not pixmap.isNull():
                self.setIcon(QIcon(pixmap))
            else:
                print(f"Failed to load thumbnail for {self.filename} - Invalid image file")
        else:
            print(f"Failed to load thumbnail for {self.filename} - File not found: {thumbnail_path}") 