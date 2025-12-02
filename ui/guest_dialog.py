from PySide6.QtWidgets import QDialog, QFormLayout, QLineEdit, QHBoxLayout, QPushButton
from backend.guest import Guest

class GuestDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Guest")
        self.setModal(True)
        self.setMinimumWidth(350)

        layout = QFormLayout()

        self.input_last_name = QLineEdit()
        self.input_last_name.setPlaceholderText("Ex: Smith")

        self.input_first_name = QLineEdit()
        self.input_first_name.setPlaceholderText("Ex: John")

        self.input_email = QLineEdit()
        self.input_email.setPlaceholderText("Ex: john.smith@email.com")

        self.input_phone = QLineEdit()
        self.input_phone.setPlaceholderText("Ex: 0712345678")

        layout.addRow("Last Name*:", self.input_last_name)
        layout.addRow("First Name*:", self.input_first_name)
        layout.addRow("Email:", self.input_email)
        layout.addRow("Phone:", self.input_phone)

        # Buttons
        btn_layout = QHBoxLayout()
        self.btn_add = QPushButton("Add")
        self.btn_cancel = QPushButton("Cancel")

        self.btn_add.clicked.connect(self.accept)
        self.btn_cancel.clicked.connect(self.reject)

        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_cancel)

        layout.addRow(btn_layout)
        self.setLayout(layout)

    def get_guest(self):
        last_name = self.input_last_name.text().strip()
        first_name = self.input_first_name.text().strip()
        email = self.input_email.text().strip()
        phone = self.input_phone.text().strip()

        if not last_name or not first_name:
            return None

        return Guest(last_name, first_name, email, phone)
