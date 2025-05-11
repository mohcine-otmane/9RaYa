from PyQt6.QtWidgets import QListWidgetItem, QWidget, QVBoxLayout, QLabel, QMenu
from PyQt6.QtGui import QPixmap, QIcon, QFontMetrics, QDesktopServices, QAction
from PyQt6.QtCore import Qt, QUrl
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

class PDFCardWidget(QWidget):
    def __init__(self, filename, thumbnail_path=None, full_path=None):
        super().__init__()
        self.full_path = full_path
        self.filename = filename
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(6)
        self.thumb_label = QLabel()
        self.thumb_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.thumb_label.setFixedSize(150, 200)
        if thumbnail_path and os.path.exists(thumbnail_path):
            pixmap = QPixmap(thumbnail_path)
            if not pixmap.isNull():
                self.thumb_label.setPixmap(
                    pixmap.scaled(150, 200, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                )
        layout.addWidget(self.thumb_label)
        self.text_label = QLabel()
        self.text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.text_label.setWordWrap(False)
        self.text_label.setFixedWidth(150)
        self.text_label.setStyleSheet("font-size: 12px;")
        metrics = QFontMetrics(self.text_label.font())
        elided = metrics.elidedText(filename, Qt.TextElideMode.ElideRight, 150)
        self.text_label.setText(elided)
        layout.addWidget(self.text_label)
        self.setLayout(layout)

    def set_thumbnail(self, thumbnail_path):
        if os.path.exists(thumbnail_path):
            pixmap = QPixmap(thumbnail_path)
            if not pixmap.isNull():
                self.thumb_label.setPixmap(
                    pixmap.scaled(150, 200, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                )
            else:
                print(f"Failed to load thumbnail for {self.filename} - Invalid image file")
        else:
            print(f"Failed to load thumbnail for {self.filename} - File not found: {thumbnail_path}")

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if self.full_path and os.path.exists(self.full_path):
                QDesktopServices.openUrl(QUrl.fromLocalFile(self.full_path))
        super().mousePressEvent(event)

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        open_action = QAction("Open", self)
        favorite_action = QAction("Add to favorite...", self)
        menu.addAction(open_action)
        menu.addAction(favorite_action)
        open_action.triggered.connect(self.open_pdf)
        favorite_action.triggered.connect(self.add_to_favorite)
        menu.exec(event.globalPos())

    def open_pdf(self):
        if self.full_path and os.path.exists(self.full_path):
            QDesktopServices.openUrl(QUrl.fromLocalFile(self.full_path))

    def add_to_favorite(self):
        # Placeholder: implement your favorite logic here
        print(f"Added to favorite: {self.filename}") 