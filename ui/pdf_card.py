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
    def __init__(self, filename, thumbnail_path=None, full_path=None, is_favorite_mode=False, favorites=None):
        super().__init__()
        self.setObjectName("PDFCardWidget")
        self.full_path = full_path
        self.filename = filename
        self.is_favorite_mode = is_favorite_mode
        self.add_to_favorite = None
        self.remove_from_favorite = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(6)

        thumb_container = QWidget()
        thumb_container.setFixedSize(150, 200)
        thumb_container.setStyleSheet("background: transparent;")
        thumb_layout = QVBoxLayout(thumb_container)
        thumb_layout.setContentsMargins(0, 0, 0, 0)
        thumb_layout.setSpacing(0)

        self.thumb_label = QLabel()
        self.thumb_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.thumb_label.setFixedSize(150, 200)
        if thumbnail_path and os.path.exists(thumbnail_path):
            pixmap = QPixmap(thumbnail_path)
            if not pixmap.isNull():
                self.thumb_label.setPixmap(
                    pixmap.scaled(150, 200, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                )
        thumb_layout.addWidget(self.thumb_label)

        self.star_label = QLabel(thumb_container)
        self.star_label.setObjectName("star_label")
        self.star_label.setText("★")
        self.star_label.setStyleSheet(
            "color: gold; font-size: 24px; background: transparent;"
        )
        self.star_label.setFixedSize(28, 28)
        self.star_label.move(120, 0)
        self.star_label.setVisible((not is_favorite_mode) and favorites and full_path in favorites)

        layout.addWidget(thumb_container)

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
        # Do not open on left click anymore
        super().mousePressEvent(event)

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        open_action = QAction("Open", self)
        if self.is_favorite_mode:
            fav_action = QAction("Remove from favorite", self)
            fav_action.triggered.connect(self.remove_from_favorite or (lambda: None))
        else:
            fav_action = QAction("Add to favorite...", self)
            fav_action.triggered.connect(self.add_to_favorite or (lambda: None))
        menu.addAction(open_action)
        menu.addAction(fav_action)
        open_action.triggered.connect(self.open_pdf)
        menu.exec(event.globalPos())

    def open_pdf(self):
        if self.full_path and os.path.exists(self.full_path):
            QDesktopServices.openUrl(QUrl.fromLocalFile(self.full_path))

    def add_to_favorite(self):
        # Placeholder: implement your favorite logic here
        print(f"Added to favorite: {self.filename}") 