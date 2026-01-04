from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel
from PySide6.QtGui import QDrag, QPixmap
from PySide6.QtCore import Qt, QMimeData, Signal

class SeatWidget(QFrame):

    seat_clicked = Signal(object)

    guest_dropped_on_seat = Signal(str, object)

    def __init__(self, seat, parent=None):
        super().__init__(parent)
        self.seat = seat
        self.setAcceptDrops(True)
       
        self.setFixedSize(30, 30) 
        
        self.setFrameStyle(QFrame.Box | QFrame.Raised)
        self.setLineWidth(2)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignCenter)

        self.label_info = QLabel(str(seat.number))
        self.label_info.setAlignment(Qt.AlignCenter)
        # Font putin mai mic
        self.label_info.setStyleSheet("font-size: 9px; font-weight: bold; color: #333;")

        layout.addWidget(self.label_info)
        self.setLayout(layout)

        self.update_appearance()

    def update_appearance(self):
        # Definim marimea fixa si raza pentru a suprascrie ORICE din resources.qss
        base_style = """
            SeatWidget {
                min-width: 30px;
                max-width: 30px;
                min-height: 30px;
                max-height: 30px;
                border-radius: 15px; 
                border: 2px solid #555;
            }
        """

        if self.seat.guest:
            # OCUPAT - Verde
            self.setStyleSheet(base_style + """
                SeatWidget {
                    background-color: #4CAF50;
                    border-color: #2E7D32;
                }
            """)
            initials = f"{self.seat.guest.first_name[:1]}.{self.seat.guest.last_name[:1]}."
            self.label_info.setText(initials)
            self.label_info.setToolTip(f"{self.seat.guest.get_full_name()}")
            self.label_info.setStyleSheet("color: white; font-weight: bold; font-size: 8px; border: none;")
            
        elif self.seat.reserved:
            # REZERVAT - Galben
            self.setStyleSheet(base_style + """
                SeatWidget {
                    background-color: #FFC107;
                    border-color: #F57C00;
                }
            """)
            self.label_info.setText("R")
            self.label_info.setStyleSheet("color: #333; font-size: 9px; border: none;")
            
        else:
            # LIBER - Gri
            self.setStyleSheet(base_style + """
                SeatWidget {
                    background-color: #EEEEEE;
                    border-color: #9E9E9E;
                }
            """)
            self.label_info.setText(str(self.seat.number))
            self.label_info.setStyleSheet("color: #333; font-size: 9px; border: none;")

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.seat_clicked.emit(self.seat)

            if self.seat.guest:
                # Start drag operation
                drag = QDrag(self)
                mime_data = QMimeData()
                mime_data.setText(f"guest:{id(self.seat.guest)}")
                drag.setMimeData(mime_data)

                # Create a pixmap for drag
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
        guest_id = None
        
        # 1. Extragem ID-ul din MimeData
        if event.mimeData().hasText():
            text = event.mimeData().text()
            if text.startswith("guest:"):
                guest_id = text.split(":")[1]
        
        # 2. Backup: sursa directa
        if not guest_id and event.source():
            if hasattr(event.source(), 'selectedItems'):
                items = event.source().selectedItems()
                if items:
                    data = items[0].data(Qt.UserRole)
                    if data and data.startswith("guest:"):
                        guest_id = data.split(":")[1]

        if guest_id:
            event.accept()
            print(f"DEBUG: Drop detectat pe scaunul {self.seat.number}, ID Guest: {guest_id}")
            
            # EMITEM SEMNALUL - Nu mai cautam parent() sau window()
            # "Hei, cineva a aruncat invitatul X pe mine!"
            self.guest_dropped_on_seat.emit(guest_id, self.seat)
            
        self.update_appearance()
