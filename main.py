import sys
import traceback
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtGui import QPalette, QColor
from PySide6.QtCore import qInstallMessageHandler, QtMsgType
from app.main_window import MainWindow

def qt_message_handler(mode, context, message):
    """Handler pentru mesajele Qt"""
    if mode == QtMsgType.QtCriticalMsg or mode == QtMsgType.QtFatalMsg:
        print(f"Qt Critical/Fatal: {message}")
        print(f"File: {context.file}, Line: {context.line}")
    else:
        print(f"Qt: {message}")

def exception_hook(exctype, value, tb):
    """Handler global pentru exceptii"""
    print("=" * 80)
    print("EXCEPTION CAUGHT:")
    print("=" * 80)
    traceback.print_exception(exctype, value, tb)
    print("=" * 80)
    #QMessageBox.critical(None, "Error", f"{exctype.__name__}: {value}")

def main():
    # Instaleaza handlere pentru exceptii
    sys.excepthook = exception_hook
    qInstallMessageHandler(qt_message_handler)

    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(245, 245, 245))
    palette.setColor(QPalette.WindowText, QColor(33, 33, 33))
    palette.setColor(QPalette.Base, QColor(255, 255, 255))
    palette.setColor(QPalette.AlternateBase, QColor(245, 245, 245))
    palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 255))
    palette.setColor(QPalette.ToolTipText, QColor(33, 33, 33))
    palette.setColor(QPalette.Text, QColor(33, 33, 33))
    palette.setColor(QPalette.Button, QColor(33, 150, 243))
    palette.setColor(QPalette.ButtonText, QColor(255, 255, 255))
    palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
    palette.setColor(QPalette.Highlight, QColor(33, 150, 243))
    palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
    app.setPalette(palette)

    fereastra = MainWindow()
    fereastra.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()