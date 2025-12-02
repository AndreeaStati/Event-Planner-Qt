from PySide6.QtWidgets import QDialog, QFormLayout, QLineEdit, QSpinBox, QDateTimeEdit, QHBoxLayout, QPushButton
from PySide6.QtCore import QDateTime
from datetime import datetime

print("Importing Event class...")
from backend.event import Event
print("Event class imported successfully")

class EventDialog(QDialog):

    def __init__(self, parent=None, event=None):
        print(f"EventDialog.__init__ called with parent={parent}, event={event}")
        try:
            if parent is None:
                from PySide6.QtWidgets import QApplication
                parent = QApplication.activeWindow()

            super().__init__(parent)
            print("super().__init__ successful")
            
            self.event_data = event
            self.setModal(True)
            self.setMinimumWidth(400)
            print("Basic properties set")

            layout = QFormLayout()
            print("QFormLayout created")

            self.input_name = QLineEdit()
            self.input_name.setPlaceholderText("Ex: Technology Conference")
            print("input_name created")

            print("STEP 1 OK")
            self.input_date_time = QDateTimeEdit()
            print("STEP 2 OK")
            self.input_date_time.setDateTime(QDateTime.currentDateTime())
            print("STEP 3 OK")
            #self.input_date_time.setCalendarPopup(True)
            print("STEP 4 OK")
            print("input_date_time created")

            self.input_location = QLineEdit()
            self.input_location.setPlaceholderText("Ex: Senate Hall")
            print("input_location created")

            self.input_rows = QSpinBox()
            self.input_rows.setRange(1, 50)
            self.input_rows.setValue(10)
            print("input_rows created")

            self.input_seats_per_row = QSpinBox()
            self.input_seats_per_row.setRange(1, 50)
            self.input_seats_per_row.setValue(10)
            print("input_seats_per_row created")

            if self.event_data:
                self.input_name.setText(self.event_data.name)
                self.input_location.setText(self.event_data.location)
                self.input_rows.setValue(self.event_data.num_rows)
                self.input_seats_per_row.setValue(self.event_data.num_seats_per_row)

                if isinstance(self.event_data.date_time, datetime):
                    qdt = QDateTime(self.event_data.date_time)
                    self.input_date_time.setDateTime(qdt)

            layout.addRow("Name:", self.input_name)
            layout.addRow("Date & Time:", self.input_date_time)
            layout.addRow("Location:", self.input_location)
            layout.addRow("Number of Rows:", self.input_rows)
            layout.addRow("Seats per Row:", self.input_seats_per_row)
            print("All rows added to layout")

            btn_layout = QHBoxLayout()
            self.btn_save = QPushButton("Save")
            self.btn_cancel = QPushButton("Cancel")

            self.btn_save.clicked.connect(self.accept)
            self.btn_cancel.clicked.connect(self.reject)

            btn_layout.addWidget(self.btn_save)
            btn_layout.addWidget(self.btn_cancel)

            layout.addRow(btn_layout)
            self.setLayout(layout)
            self.setWindowTitle("Add New Event" if not event else "Edit Event")
            print("EventDialog.__init__ completed successfully")
            
        except Exception as e:
            print(f"ERROR in EventDialog.__init__: {e}")
            import traceback
            traceback.print_exc()
            raise

    def get_event(self):
        name = self.input_name.text().strip()
        location = self.input_location.text().strip()

        qt_dt = self.input_date_time.dateTime()
        date = qt_dt.date().toPython()
        time = qt_dt.time().toPython()
        date_time = datetime.combine(date, time)

        num_rows = self.input_rows.value()
        num_seats = self.input_seats_per_row.value()

        if not name or not location:
            return None

        return Event(name, date_time, location, num_rows, num_seats)