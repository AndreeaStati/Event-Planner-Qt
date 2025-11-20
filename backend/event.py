from datetime import datetime
from .seat import Seat
from .guest import Guest

class Event:
    """Class representing an event"""

    def __init__(self, name, date_time, location, num_rows=10, num_seats_per_row=10):
        self.name = name
        self.date_time = date_time
        self.location = location
        self.num_rows = num_rows
        self.num_seats_per_row = num_seats_per_row
        self.seats = []
        self.unassigned_guests = []
        self._initialize_seats()

    def _initialize_seats(self):
        """Create all seats for the event"""
        self.seats = []
        for row in range(1, self.num_rows + 1):
            for number in range(1, self.num_seats_per_row + 1):
                self.seats.append(Seat(row, number))

    def add_guest(self, guest: Guest):
        """Add a guest to the list of unassigned guests"""
        self.unassigned_guests.append(guest)

    def get_seat(self, row, number):
        """Return the seat at the specified position"""
        for seat in self.seats:
            if seat.row == row and seat.number == number:
                return seat
        return None

    def get_occupied_seats_count(self):
        """Return the number of occupied seats"""
        return sum(1 for seat in self.seats if not seat.is_available())

    def get_available_seats_count(self):
        """Return the number of available seats"""
        return len(self.seats) - self.get_occupied_seats_count()

    def to_dict(self):
        return {
            'name': self.name,
            'date_time': self.date_time.isoformat() if isinstance(self.date_time, datetime) else str(self.date_time),
            'location': self.location,
            'num_rows': self.num_rows,
            'num_seats_per_row': self.num_seats_per_row,
            'seats': [seat.to_dict() for seat in self.seats],
            'unassigned_guests': [g.to_dict() for g in self.unassigned_guests]
        }

    @staticmethod
    def from_dict(data):
        date_time = datetime.fromisoformat(data['date_time']) if isinstance(data['date_time'], str) else data['date_time']
        event = Event(
            data['name'],
            date_time,
            data['location'],
            data['num_rows'],
            data['num_seats_per_row']
        )
        event.seats = [Seat.from_dict(s) for s in data['seats']]
        event.unassigned_guests = [Guest.from_dict(g) for g in data['unassigned_guests']]
        return event
