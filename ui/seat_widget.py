from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel
from PySide6.QtGui import QDrag
from PySide6.QtCore import Qt, QMimeData, Signal
from PySide6.QtGui import QPixmap

class SeatWidget(QFrame):

    seat_clicked = Signal(object)

    def __init__(self, seat, parent=None):
        super().__init__(parent)
        self.seat = seat
        self.setAcceptDrops(True)
        self.setFixedSize(60, 60)
        self.setFrameStyle(QFrame.Box | QFrame.Raised)
        self.setLineWidth(2)

        layout = QVBoxLayout()
        layout.setContentsMargins(2, 2, 2, 2)

        self.label_position = QLabel(seat.get_identifier())
        self.label_position.setAlignment(Qt.AlignCenter)
        self.label_position.setStyleSheet("font-size: 9px; font-weight: bold;")

        self.label_guest = QLabel("")
        self.label_guest.setAlignment(Qt.AlignCenter)
        self.label_guest.setWordWrap(True)
        self.label_guest.setStyleSheet("font-size: 8px;")

        layout.addWidget(self.label_position)
        layout.addWidget(self.label_guest)
        self.setLayout(layout)

        self.update_appearance()

    def update_appearance(self):
        if self.seat.guest:
            self.setStyleSheet("""
                QFrame {
                    background-color: #4CAF50;
                    border: 2px solid #2E7D32;
                    border-radius: 5px;
                }
                QLabel {
                    color: white;
                }
            """)
            short_name = self.seat.guest.get_full_name()
            if len(short_name) > 15:
                short_name = short_name[:12] + "..."
            self.label_guest.setText(short_name)
        elif self.seat.reserved:
            self.setStyleSheet("""
                QFrame {
                    background-color: #FFC107;
                    border: 2px solid #F57C00;
                    border-radius: 5px;
                }
                QLabel {
                    color: #333;
                }
            """)
            self.label_guest.setText("Reserved")
        else:
            self.setStyleSheet("""
                QFrame {
                    background-color: #E0E0E0;
                    border: 2px solid #9E9E9E;
                    border-radius: 5px;
                }
                QLabel {
                    color: #333;
                }
            """)
            self.label_guest.setText("Available")

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.seat_clicked.emit(self.seat)

            if self.seat.guest:
                drag = QDrag(self)
                mime_data = QMimeData()
                mime_data.setText(f"guest:{id(self.seat.guest)}")
                drag.setMimeData(mime_data)

                pixmap = QPixmap(self.size())
                self.render(pixmap)
                drag.setPixmap(pixmap)
                drag.setHotSpot(event.pos())

                drag.exec(Qt.MoveAction)

    def dragEnterEvent(self, event):
        if event.mimeData().hasText() and event.mimeData().text().startswith("guest:"):
            if self.seat.is_available():
                event.acceptProposedAction()
                self.setStyleSheet("""
                    QFrame {
                        background-color: #81C784;
                        border: 2px solid #4CAF50;
                        border-radius: 5px;
                    }
                """)

    def dragLeaveEvent(self, event):
        self.update_appearance()

    def dropEvent(self, event):
        if event.mimeData().hasText() and event.mimeData().text().startswith("guest:"):
            guest_id = event.mimeData().text().split(":")[1]
            event.acceptProposedAction()
            self.parent().parent().parent().move_guest_to_seat(guest_id, self.seat)
        self.update_appearance()
