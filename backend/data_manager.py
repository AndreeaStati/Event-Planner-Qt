import json
import os
from backend.event import Event

DATA_FILE = "events_data.json"

def save_data(events_list):
    try:
        data_to_save = [event.to_dict() for event in events_list]
        
        with open(DATA_FILE, "w") as f:
            json.dump(data_to_save, f, indent=4)
        print("Date salvate cu succes!")
    except Exception as e:
        print(f"Eroare la salvare: {e}")

def load_data():
    if not os.path.exists(DATA_FILE):
        return [] 

    try:
        with open(DATA_FILE, "r") as f:
            data_loaded = json.load(f)
            
        events_list = [Event.from_dict(event_data) for event_data in data_loaded]
        return events_list
    except Exception as e:
        print(f"Eroare la incarcare: {e}")
        return []