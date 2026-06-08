import os
import gzip
import json

# Target directory for Unity's Persistent Data Path
SAVES_DIR = os.path.expandvars(r"%USERPROFILE%\AppData\LocalLow\Kweepa\UnityUnderground\Saves")

def load_save(slot_number: int) -> dict:
    """Decompresses and loads a specific save slot (0 to 9) into a Python dictionary."""
    file_path = os.path.join(SAVES_DIR, f"slot{slot_number}.json.gz")
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Save slot file {slot_number} does not exist at {SAVES_DIR}")
    
    with gzip.open(file_path, 'rb') as f:
        return json.loads(f.read().decode('utf-8'))

def save_game_data(slot_number: int, data: dict):
    """Serializes and compresses the modified dictionary back into GZip format."""
    file_path = os.path.join(SAVES_DIR, f"slot{slot_number}.json.gz")
    json_text = json.dumps(data, indent=4)
    with gzip.open(file_path, 'wb') as f:
        f.write(json_text.encode('utf-8'))