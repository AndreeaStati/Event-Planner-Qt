from datetime import datetime
import traceback
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QListWidget, QDialog,
    QMessageBox, QFrame,
    QScrollArea, QSplitter, QGroupBox, QComboBox
)
from PySide6.QtCore import Qt

from ui.seat_widget import SeatWidget
from ui.event_dialog import EventDialog
from ui.guest_dialog import GuestDialog


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.events = []
        self.current_event = None
        self.guest_map = {} 

        self.setWindowTitle("Event Planner")
        self.setGeometry(100, 100, 1400, 800)

        self.init_ui()

        try:
            with open("ui/resources.qss", "r") as f:
                self.setStyleSheet(f.read())
        except FileNotFoundError:
            print("resources.qss not found, default style will be used")

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout()

        # Left panel - list of events and actions
        left_panel = self.create_left_panel()

        # Right panel - event details and seating map
        right_panel = self.create_right_panel()

        # Splitter for resizing
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)

        main_layout.addWidget(splitter)
        central_widget.setLayout(main_layout)


    def create_left_panel(self):
        panel = QWidget()
        layout = QVBoxLayout()

        # Title
        title = QLabel("Events")
        title.setStyleSheet("font-size: 18px; font-weight: bold; padding: 10px;")
        layout.addWidget(title)

        # Events list
        self.events_list = QListWidget()
        self.events_list.itemClicked.connect(self.select_event)
        layout.addWidget(self.events_list)

        # Event action buttons
        btn_new_event = QPushButton("New Event")
        btn_new_event.clicked.connect(self.add_event)
        layout.addWidget(btn_new_event)

        btn_delete_event = QPushButton("Delete Event")
        btn_delete_event.setStyleSheet("background-color: #F44336;")
        btn_delete_event.clicked.connect(self.delete_event)
        layout.addWidget(btn_delete_event)

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separator)

        # Unassigned guests
        guest_group = QGroupBox("Unassigned Guests")
        guest_layout = QVBoxLayout()

        self.guests_list = QListWidget()
        self.guests_list.setDragEnabled(True)
        self.guests_list.setDefaultDropAction(Qt.MoveAction)
        guest_layout.addWidget(self.guests_list)

        btn_add_guest = QPushButton("Add Guest")
        btn_add_guest.clicked.connect(self.add_guest)
        guest_layout.addWidget(btn_add_guest)

        btn_remove_guest = QPushButton("Remove Guest")
        btn_remove_guest.setStyleSheet("background-color: #FF9800;")
        btn_remove_guest.clicked.connect(self.remove_guest)
        guest_layout.addWidget(btn_remove_guest)

        guest_group.setLayout(guest_layout)
        layout.addWidget(guest_group)

        panel.setLayout(layout)
        return panel

    def create_right_panel(self):
        """Create the right panel with event details and seating map"""
        panel = QWidget()
        layout = QVBoxLayout()

        # Event information
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

        # Seating map container
        self.seats_scroll = QScrollArea()
        self.seats_scroll.setWidgetResizable(True)
        self.seats_widget = QWidget()
        self.seats_layout = QVBoxLayout()
        self.seats_widget.setLayout(self.seats_layout)
        self.seats_scroll.setWidget(self.seats_widget)
        layout.addWidget(self.seats_scroll)

        # Legend
        legend = self.create_legend()
        layout.addWidget(legend)

        panel.setLayout(layout)
        return panel

    def create_legend(self):
        """Create legend for seat states"""
        legend_group = QGroupBox("Legend")
        layout = QHBoxLayout()

        label_available = QLabel("  Available")
        label_available.setStyleSheet("background-color: #E0E0E0; padding: 5px; border-radius: 3px;")
        layout.addWidget(label_available)

        label_occupied = QLabel("  Occupied")
        label_occupied.setStyleSheet("background-color: #4CAF50; color: white; padding: 5px; border-radius: 3px;")
        layout.addWidget(label_occupied)

        label_reserved = QLabel("  Reserved")
        label_reserved.setStyleSheet("background-color: #FFC107; padding: 5px; border-radius: 3px;")
        layout.addWidget(label_reserved)

        layout.addStretch()
        legend_group.setLayout(layout)
        return legend_group

    def update_events_list(self):
        self.events_list.clear()
        for event in self.events:
            date_str = event.date_time.strftime("%d.%m.%Y %H:%M") if isinstance(event.date_time, datetime) else str(event.date_time)
            self.events_list.addItem(f"{event.name} - {date_str}")

    def update_unassigned_guests_list(self):
        self.guests_list.clear()
        if self.current_event:
            for guest in self.current_event.unassigned_guests:
                self.guests_list.addItem(guest.get_full_name())

    def update_seating_map(self):
        while self.seats_layout.count():
            item = self.seats_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not self.current_event:
            label = QLabel("No event selected")
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("font-size: 14px; color: #757575; padding: 50px;")
            self.seats_layout.addWidget(label)
            return

        self.guest_map.clear()
        for seat in self.current_event.seats:
            if seat.guest:
                self.guest_map[str(id(seat.guest))] = seat.guest

        stage_label = QLabel("Stage / Podium")
        stage_label.setAlignment(Qt.AlignCenter)
        stage_label.setStyleSheet("""
            background-color: #212121;
            color: white;
            font-size: 14px;
            font-weight: bold;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        """)
        self.seats_layout.addWidget(stage_label)

        # Organize seats by row
        rows_dict = {}
        for seat in self.current_event.seats:
            if seat.row not in rows_dict:
                rows_dict[seat.row] = []
            rows_dict[seat.row].append(seat)

        for row in sorted(rows_dict.keys()):
            row_container = QWidget()
            row_layout = QHBoxLayout()
            row_layout.setSpacing(5)

            # Row label
            row_label = QLabel(f"R{row}")
            row_label.setFixedWidth(40)
            row_label.setAlignment(Qt.AlignCenter)
            row_label.setStyleSheet("font-weight: bold; color: #424242;")
            row_layout.addWidget(row_label)

            # Seats in the row
            for seat in sorted(rows_dict[row], key=lambda s: s.number):
                seat_widget = SeatWidget(seat)
                seat_widget.seat_clicked.connect(self.seat_clicked)
                row_layout.addWidget(seat_widget)

            row_layout.addStretch()
            row_container.setLayout(row_layout)
            self.seats_layout.addWidget(row_container)

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
        <p><b>Capacity:</b> {len(e.seats)} seats ({e.num_rows} rows x {e.num_seats_per_row} seats)</p>
        <p><b>Occupied:</b> {e.get_occupied_seats_count()} | <b>Available:</b> {e.get_available_seats_count()}</p>
        <p><b>Unassigned Guests:</b> {len(e.unassigned_guests)}</p>
        """
        self.event_info_label.setText(info_text)

    def add_event(self):
        try:
            print("Opening EventDialog...")  # Debug
            dialog = EventDialog(self)
            print("EventDialog created successfully")  # Debug
            
            result = dialog.exec()
            print(f"Dialog result: {result}")  # Debug
            
            if result == QDialog.Accepted:
                event = dialog.get_event()
                print(f"Event received: {event}")  # Debug
                
                if event:
                    self.events.append(event)
                    self.update_events_list()
                    QMessageBox.information(self, "Success", f"Event '{event.name}' was created successfully!")
                else:
                    QMessageBox.warning(self, "Error", "All required fields must be filled!")
        except Exception as e:
            print(f"ERROR in add_event: {e}")
            traceback.print_exc()
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
        if not self.current_event:
            return

        if seat.guest:
            # Seat is occupied - offer options
            reply = QMessageBox.question(
                self,
                "Seat Management",
                f"Seat {seat.get_identifier()} is occupied by {seat.guest.get_full_name()}.\n\nDo you want to free this seat?",
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
            # Seat is free - manual allocation
            if not self.current_event.unassigned_guests:
                QMessageBox.information(self, "Info", "There are no unassigned guests!")
                return

            # Dialog to select a guest
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

    def move_guest_to_seat(self, guest_id, target_seat):
        if not self.current_event:
            return

        # Find guest
        guest = self.guest_map.get(guest_id)
        if not guest:
            return

        # Find source seat
        source_seat = None
        for seat in self.current_event.seats:
            if seat.guest == guest:
                source_seat = seat
                break

        if source_seat and target_seat.is_available():
            # Move guest
            source_seat.release()
            target_seat.assign_guest(guest)
            self.update_seating_map()
            self.update_event_info()
