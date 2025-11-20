class Guest:
    def __init__(self, last_name, first_name, email="", phone=""):
        self.last_name = last_name
        self.first_name = first_name  # CORECTAT: era "fist_name"
        self.email = email
        self.phone = phone
        self.assigned_seat = None

    def get_full_name(self):
        return f"{self.last_name} {self.first_name}"

    def to_dict(self):
        return {
            'last_name': self.last_name,
            'first_name': self.first_name,  # CORECTAT: era "fist_name"
            'email': self.email,
            'phone': self.phone
        }

    @staticmethod
    def from_dict(data):
        return Guest(
            data['last_name'],
            data['first_name'],
            data.get('email', ''),
            data.get('phone', '')
        )