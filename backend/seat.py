from .guest import Guest

class Seat:
    def __init__(self, row, number):
        self.row = row
        self.number = number
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
        return f"R{self.row}-S{self.number}"

    def to_dict(self):
        return {
            'row': self.row,
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



