from .guest import Guest

class Seat:
    def __init__(self, table_number, seat_number):
        self.table_number = table_number  
        self.number = seat_number
        self.guest = None
        self.reserved = False
    
    def is_available(self):
        return self.guest is None and not self.reserved

    def assign_guest(self, guest: Guest):
        if self.is_available():
            self.guest = guest
            guest.assigned_seat = self
            return True
        return False

    def release(self):
        if self.guest:
            self.guest.assigned_seat = None
            self.guest = None

    def get_identifier(self):
        return f"Masa {self.table_number} - Loc {self.number}"

    def to_dict(self):
        return {
            'row': self.table_number,
            'number': self.number,
            'guest': self.guest.to_dict() if self.guest else None,
            'reserved': self.reserved
        }

    @staticmethod
    def from_dict(data):
        seat = Seat(data['row'], data['number'])
        seat.reserved = data.get('reserved', False)
        if data.get('guest'):
            seat.guest = Guest.from_dict(data['guest'])
        return seat