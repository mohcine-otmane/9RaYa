import sys
from PyQt6.QtWidgets import QApplication, QSplashScreen
from PyQt6.QtGui import QIcon, QPixmap
from ui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("icon.ico"))
    splash = QSplashScreen(QPixmap("splash.png"))
    splash.show()
    app.processEvents()
    window = MainWindow()
    window.show()
    splash.finish(window)
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 