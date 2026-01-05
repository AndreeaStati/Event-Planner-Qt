from backend.data_manager import save_data, load_data
import re
from datetime import datetime
import traceback
import math
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QListWidget, QDialog,
    QMessageBox, QFrame,
    QScrollArea, QSplitter, QGroupBox, QComboBox,
    QGridLayout, QListWidgetItem, QFileDialog
)
from PySide6.QtGui import QDrag, QPixmap, QPainter, QColor, QCloseEvent
from PySide6.QtCore import Qt, QMimeData, QPoint
from backend.guest import Guest
from ui.seat_widget import SeatWidget
from ui.event_dialog import EventDialog
from ui.guest_dialog import GuestDialog


class GuestListWidget(QListWidget):
    """
        Lista personalizata care gestioneaza vizual operatiunea de Drag & Drop.
    """
    def mimeData(self, items):
        mime = QMimeData()
        if items:
            guest_id = items[0].data(Qt.UserRole)
            if guest_id:
                mime.setText(guest_id)
        return mime

    def startDrag(self, supportedActions):
        item = self.currentItem()
        if not item:
            return

        mime_data = self.mimeData([item])
        drag = QDrag(self)
        drag.setMimeData(mime_data)

        text = item.text()
        rect_width = len(text) * 8 + 20
        pixmap = QPixmap(rect_width, 30)
        pixmap.fill(Qt.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)

        painter.setBrush(QColor("white"))
        painter.setPen(QColor("#2196F3"))
        painter.drawRoundedRect(0, 0, rect_width - 2, 28, 5, 5)

        painter.setPen(Qt.black)
        painter.drawText(pixmap.rect(), Qt.AlignCenter, text)
        painter.end()

        drag.setPixmap(pixmap)
        drag.setHotSpot(QPoint(rect_width // 2, 15))

        drag.exec(supportedActions)


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.events = load_data()
        self.current_event = None
        self.guest_map = {}

        self.setWindowTitle("Event Planner")
        self.setGeometry(100, 100, 1400, 800)

        self.init_ui()

        try:
            with open("ui/resources.qss", "r") as f:
                self.setStyleSheet(f.read())
        except FileNotFoundError:
            print("resources.qss not found")

        self.update_events_list()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout()

        left_panel = self.create_left_panel()
        right_panel = self.create_right_panel()

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)

        main_layout.addWidget(splitter)
        central_widget.setLayout(main_layout)

    def closeEvent(self, event: QCloseEvent):
        save_data(self.events)
        event.accept()

    def create_left_panel(self):
        panel = QWidget()
        layout = QVBoxLayout()

        title = QLabel("Events")
        title.setStyleSheet("font-size: 18px; font-weight: bold; padding: 10px;")
        layout.addWidget(title)

        self.events_list = QListWidget()
        self.events_list.itemClicked.connect(self.select_event)
        layout.addWidget(self.events_list)

        btn_new_event = QPushButton("New Event")
        btn_new_event.clicked.connect(self.add_event)
        layout.addWidget(btn_new_event)

        btn_delete_event = QPushButton("Delete Event")
        btn_delete_event.setStyleSheet("background-color: #F44336;")
        btn_delete_event.clicked.connect(self.delete_event)
        layout.addWidget(btn_delete_event)

        btn_save = QPushButton("Save Changes")
        btn_save.setStyleSheet("background-color: #4CAF50; color: white;")
        btn_save.clicked.connect(lambda: save_data(self.events))
        layout.addWidget(btn_save)

        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separator)

        guest_group = QGroupBox("Unassigned Guests")
        guest_layout = QVBoxLayout()

        self.guests_list = GuestListWidget()
        self.guests_list.setDragEnabled(True)
        self.guests_list.setDragDropMode(QListWidget.DragOnly)
        guest_layout.addWidget(self.guests_list)

        btn_add_guest = QPushButton("Add Guest")
        btn_add_guest.clicked.connect(self.add_guest)
        guest_layout.addWidget(btn_add_guest)

        btn_import = QPushButton("Import from .txt")
        btn_import.setStyleSheet("background-color: #607D8B; color: white;")
        btn_import.clicked.connect(self.import_guests_from_file)
        guest_layout.addWidget(btn_import)

        btn_remove_guest = QPushButton("Remove Guest")
        btn_remove_guest.setStyleSheet("background-color: #FF9800;")
        btn_remove_guest.clicked.connect(self.remove_guest)
        guest_layout.addWidget(btn_remove_guest)

        guest_group.setLayout(guest_layout)
        layout.addWidget(guest_group)

        panel.setLayout(layout)
        return panel

    def import_guests_from_file(self):
        """
        Parseaza un fisier text si extrage automat nume, email si telefon folosind Regex.
        """
        if not self.current_event:
            QMessageBox.warning(self, "Warning", "Please select an event first!")
            return

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Guest List",
            "",
            "Text Files (*.txt);;All Files (*)"
        )

        if not file_path:
            return

        try:
            count = 0
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            for line in lines:
                line = line.strip()
                if not line:
                    continue

                email = ""
                email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', line)
                if email_match:
                    email = email_match.group(0)
                    line = line.replace(email, "").strip()

                phone = ""
                phone_match = re.search(r'\+?\d{6,}', line)
                if phone_match:
                    phone = phone_match.group(0)
                    line = line.replace(phone, "").strip()

                raw_name = " ".join(line.split())

                if not raw_name:
                    continue

                name_parts = raw_name.split()
                if len(name_parts) >= 2:
                    last_name = name_parts[0]
                    first_name = " ".join(name_parts[1:])
                else:
                    last_name = raw_name
                    first_name = ""

                new_guest = Guest(last_name, first_name, email, phone)
                self.current_event.add_guest(new_guest)
                count += 1

            self.update_unassigned_guests_list()
            self.update_event_info()

            QMessageBox.information(self, "Success", f"Successfully imported {count} guests!")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to import file: {str(e)}")

    def create_right_panel(self):
        panel = QWidget()
        layout = QVBoxLayout()

        self.event_info_label = QLabel("Select an event to view details")
        self.event_info_label.setStyleSheet("""
            font-size: 16px;
            padding: 15px;
            background-color: white;
            border-radius: 5px;
            border: 1px solid #E0E0E0;
        """)
        self.event_info_label.setWordWrap(True)
        layout.addWidget(self.event_info_label)

        self.seats_scroll = QScrollArea()
        self.seats_scroll.setWidgetResizable(True)
        self.seats_widget = QWidget()
        self.seats_layout = QVBoxLayout()
        self.seats_widget.setLayout(self.seats_layout)
        self.seats_scroll.setWidget(self.seats_widget)
        layout.addWidget(self.seats_scroll)

        legend = self.create_legend()
        layout.addWidget(legend)

        panel.setLayout(layout)
        return panel

    def create_legend(self):
        legend_group = QGroupBox("Legend")
        layout = QHBoxLayout()

        label_available = QLabel("  Available")
        label_available.setStyleSheet("background-color: #E0E0E0; padding: 5px; border-radius: 3px;")
        layout.addWidget(label_available)

        label_occupied = QLabel("  Occupied")
        label_occupied.setStyleSheet("background-color: #4CAF50; color: white; padding: 5px; border-radius: 3px;")
        layout.addWidget(label_occupied)

        layout.addStretch()
        legend_group.setLayout(layout)
        return legend_group

    def update_events_list(self):
        self.events_list.clear()
        for event in self.events:
            date_str = event.date_time.strftime("%d.%m.%Y %H:%M") if isinstance(event.date_time, datetime) else str(
                event.date_time)
            self.events_list.addItem(f"{event.name} - {date_str}")

    def update_unassigned_guests_list(self):
        self.guests_list.clear()
        if self.current_event:
            for guest in self.current_event.unassigned_guests:
                item = QListWidgetItem(guest.get_full_name())
                unique_id = f"guest:{id(guest)}"
                item.setData(Qt.UserRole, unique_id)
                self.guests_list.addItem(item)

    def handle_guest_drop(self, guest_id_str, target_seat):
        self.move_guest_to_seat(guest_id_str, target_seat)

    def update_seating_map(self):
        """
        Randeaza vizual sala.
        Calculeaza pozitia meselor in grid si a scaunelor in cerc (trigonometrie).
        """
        while self.seats_layout.count():
            item = self.seats_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not self.current_event:
            label = QLabel("Select an event :)")
            label.setAlignment(Qt.AlignCenter)
            self.seats_layout.addWidget(label)
            return

        self.guest_map.clear()
        for seat in self.current_event.seats:
            if seat.guest:
                self.guest_map[str(id(seat.guest))] = seat.guest

        tables_container = QWidget()
        tables_grid = QGridLayout()

        tables_grid.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        tables_grid.setHorizontalSpacing(40)
        tables_grid.setVerticalSpacing(10)
        tables_grid.setContentsMargins(10, 10, 10, 50)

        tables_container.setLayout(tables_grid)

        tables_dict = {}
        for seat in self.current_event.seats:
            if seat.table_number not in tables_dict:
                tables_dict[seat.table_number] = []
            tables_dict[seat.table_number].append(seat)

        FRAME_SIZE = 200
        CENTER_X = FRAME_SIZE // 2
        CENTER_Y = FRAME_SIZE // 2

        TABLE_RADIUS = 45
        CHAIR_SIZE = 30
        GAP = 10
        PLACEMENT_RADIUS = TABLE_RADIUS + GAP + (CHAIR_SIZE // 2)

        row_idx = 0
        col_idx = 0
        MAX_TABLES_PER_ROW = 4

        for table_num in sorted(tables_dict.keys()):
            table_frame = QFrame()
            table_frame.setFixedSize(FRAME_SIZE, FRAME_SIZE)
            table_frame.setStyleSheet("background-color: transparent; border: none;")

            lbl_table = QLabel(f"Masa\n{table_num}", table_frame)
            lbl_table.setAlignment(Qt.AlignCenter)
            lbl_table.setFixedSize(TABLE_RADIUS * 2, TABLE_RADIUS * 2)
            lbl_table.move(CENTER_X - TABLE_RADIUS, CENTER_Y - TABLE_RADIUS)

            lbl_table.setStyleSheet(f"""
                QLabel {{
                    background-color: #5D4037; 
                    color: white; 
                    border-radius: {TABLE_RADIUS}px; 
                    font-weight: bold;
                    border: 4px solid #3E2723;
                }}
            """)

            seats_at_table = tables_dict[table_num]
            num_seats = len(seats_at_table)

            if num_seats > 0:
                angle_step = (2 * math.pi) / num_seats

                for i, seat in enumerate(seats_at_table):
                    seat_widget = SeatWidget(seat, parent=table_frame)
                    seat_widget.setFixedSize(CHAIR_SIZE, CHAIR_SIZE)
                    seat_widget.setStyleSheet(f"""
                        SeatWidget {{
                            min-width: {CHAIR_SIZE}px;
                            max-width: {CHAIR_SIZE}px;
                            min-height: {CHAIR_SIZE}px;
                            max-height: {CHAIR_SIZE}px;
                        }}
                    """)

                    seat_widget.seat_clicked.connect(self.seat_clicked)
                    seat_widget.guest_dropped_on_seat.connect(self.handle_guest_drop)

                    current_angle = i * angle_step - (math.pi / 2)
                    center_chair_x = CENTER_X + PLACEMENT_RADIUS * math.cos(current_angle)
                    center_chair_y = CENTER_Y + PLACEMENT_RADIUS * math.sin(current_angle)

                    pos_x = int(center_chair_x - (CHAIR_SIZE / 2))
                    pos_y = int(center_chair_y - (CHAIR_SIZE / 2))

                    seat_widget.move(pos_x, pos_y)

                    seat_widget.update_appearance()
                    current_style = seat_widget.styleSheet()
                    size_fix = f"""
                        QFrame {{
                            min-width: {CHAIR_SIZE}px; max-width: {CHAIR_SIZE}px;
                            min-height: {CHAIR_SIZE}px; max-height: {CHAIR_SIZE}px;
                            border-radius: {CHAIR_SIZE // 2}px;
                        }}
                    """
                    seat_widget.setStyleSheet(current_style + size_fix)
                    seat_widget.show()

            tables_grid.addWidget(table_frame, row_idx, col_idx)

            col_idx += 1
            if col_idx >= MAX_TABLES_PER_ROW:
                col_idx = 0
                row_idx += 1

        self.seats_layout.addWidget(tables_container)
        self.seats_layout.addStretch()

    def update_event_info(self):
        if not self.current_event:
            self.event_info_label.setText("Select an event to view details")
            return

        e = self.current_event
        date_str = e.date_time.strftime("%d.%m.%Y %H:%M") if isinstance(e.date_time, datetime) else str(e.date_time)

        info_text = f"""
        <h2>{e.name}</h2>
        <p><b>Date & Time:</b> {date_str}</p>
        <p><b>Location:</b> {e.location}</p>
        <p><b>Capacity:</b> {len(e.seats)} seats ({e.num_rows} tables x {e.num_seats_per_row} seats)</p>
        <p><b>Occupied:</b> {e.get_occupied_seats_count()} | <b>Available:</b> {e.get_available_seats_count()}</p>
        <p><b>Unassigned Guests:</b> {len(e.unassigned_guests)}</p>
        """
        self.event_info_label.setText(info_text)

    def add_event(self):
        try:
            dialog = EventDialog(self)
            result = dialog.exec()

            if result == QDialog.Accepted:
                event = dialog.get_event()
                if event:
                    self.events.append(event)
                    self.update_events_list()
                    QMessageBox.information(self, "Success", f"Event '{event.name}' was created successfully!")
                else:
                    QMessageBox.warning(self, "Error", "All required fields must be filled!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create event: {str(e)}")

    def delete_event(self):
        index = self.events_list.currentRow()
        if index >= 0:
            event = self.events[index]
            reply = QMessageBox.question(
                self,
                "Confirmation",
                f"Are you sure you want to delete the event '{event.name}'?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.events.pop(index)
                if self.current_event == event:
                    self.current_event = None
                self.update_events_list()
                self.update_event_info()
                self.update_seating_map()
                self.update_unassigned_guests_list()
        else:
            QMessageBox.warning(self, "Warning", "Please select an event to delete!")

    def select_event(self, item):
        index = self.events_list.row(item)
        self.current_event = self.events[index]
        self.update_event_info()
        self.update_seating_map()
        self.update_unassigned_guests_list()

    def add_guest(self):
        if not self.current_event:
            QMessageBox.warning(self, "Warning", "Please select an event first!")
            return

        dialog = GuestDialog(self)
        if dialog.exec() == QDialog.Accepted:
            guest = dialog.get_guest()
            if guest:
                self.current_event.add_guest(guest)
                self.update_unassigned_guests_list()
                self.update_event_info()
                QMessageBox.information(self, "Success", f"Guest '{guest.get_full_name()}' was added!")
            else:
                QMessageBox.warning(self, "Error", "First name and last name are required!")

    def remove_guest(self):
        if not self.current_event:
            QMessageBox.warning(self, "Warning", "Please select an event first!")
            return

        index = self.guests_list.currentRow()
        if index >= 0:
            guest = self.current_event.unassigned_guests[index]
            reply = QMessageBox.question(
                self,
                "Confirmation",
                f"Are you sure you want to remove guest '{guest.get_full_name()}'?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.current_event.unassigned_guests.pop(index)
                self.update_unassigned_guests_list()
                self.update_event_info()
        else:
            QMessageBox.warning(self, "Warning", "Please select a guest to remove!")

    def seat_clicked(self, seat):
        """
        Gestioneaza click-ul pe scaun:
        - Daca e ocupat: ofera eliberarea locului.
        - Daca e liber: permite alocarea manuala a unui invitat.
        """
        if not self.current_event:
            return

        if seat.guest:
            reply = QMessageBox.question(
                self,
                "Seat Management",
                f" {seat.get_identifier()} is occupied by {seat.guest.get_full_name()}.\n\nDo you want to free this seat?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                guest = seat.guest
                seat.release()
                self.current_event.unassigned_guests.append(guest)
                self.update_seating_map()
                self.update_unassigned_guests_list()
                self.update_event_info()
        else:
            if not self.current_event.unassigned_guests:
                QMessageBox.information(self, "Info", "There are no unassigned guests!")
                return

            dialog = QDialog(self)
            dialog.setWindowTitle("Assign Guest")
            layout = QVBoxLayout()

            label = QLabel(f"Select a guest for seat {seat.get_identifier()}:")
            layout.addWidget(label)

            combo = QComboBox()
            for g in self.current_event.unassigned_guests:
                combo.addItem(g.get_full_name())
            layout.addWidget(combo)

            btn_layout = QHBoxLayout()
            btn_ok = QPushButton("OK")
            btn_cancel = QPushButton("Cancel")
            btn_ok.clicked.connect(dialog.accept)
            btn_cancel.clicked.connect(dialog.reject)
            btn_layout.addWidget(btn_ok)
            btn_layout.addWidget(btn_cancel)
            layout.addLayout(btn_layout)

            dialog.setLayout(layout)

            if dialog.exec() == QDialog.Accepted:
                index = combo.currentIndex()
                if index >= 0:
                    guest = self.current_event.unassigned_guests.pop(index)
                    seat.assign_guest(guest)
                    self.update_seating_map()
                    self.update_unassigned_guests_list()
                    self.update_event_info()

    def move_guest_to_seat(self, guest_id_str, target_seat):
        """
        Logica centrala de mutare:
        Gaseste invitatul (din lista sau alt scaun) si il asigneaza locului tinta.
        """
        if not self.current_event:
            return

        found_guest = None

        if guest_id_str in self.guest_map:
            found_guest = self.guest_map[guest_id_str]

        if not found_guest:
            for g in self.current_event.unassigned_guests:
                if str(id(g)) == str(guest_id_str):
                    found_guest = g
                    break

        if not found_guest:
            return

        if not target_seat.is_available():
            QMessageBox.warning(self, "Ocupat", "Locul este deja ocupat.")
            return

        if found_guest.assigned_seat:
            found_guest.assigned_seat.release()

        if found_guest in self.current_event.unassigned_guests:
            self.current_event.unassigned_guests.remove(found_guest)

        target_seat.assign_guest(found_guest)

        self.update_seating_map()
        self.update_unassigned_guests_list()
        self.update_event_info()