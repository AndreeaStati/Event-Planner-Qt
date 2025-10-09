from PySide6.QtWidgets import QMainWindow, QLabel, QVBoxLayout, QWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Event Planner")

        central = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Salut! Aplicația funcționează 🎉"))
        central.setLayout(layout)
        self.setCentralWidget(central)
