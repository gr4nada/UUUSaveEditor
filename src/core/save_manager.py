import os
import gzip
import json
import logging

logger = logging.getLogger("core.save_manager")

# Target directory for Unity's Persistent Data Path
SAVES_DIR = os.path.expandvars(r"%USERPROFILE%\AppData\LocalLow\Kweepa\UnityUnderground\Saves")

def load_save(slot_number: int) -> dict:
    """Decompresses and loads a specific save slot (0 to 9) into a Python dictionary."""
    file_path = os.path.join(SAVES_DIR, f"slot{slot_number}.json.gz")
    logger.debug(f"Attempting to load save slot {slot_number} from {file_path}")
    
    if not os.path.exists(file_path):
        logger.error(f"Save slot file {slot_number} does not exist at {SAVES_DIR}")
        raise FileNotFoundError(f"Save slot file {slot_number} does not exist at {SAVES_DIR}")
    
    with gzip.open(file_path, 'rb') as f:
        try:
            data = json.loads(f.read().decode('utf-8'))
            logger.info(f"Save slot {slot_number} loaded successfully")
            return data
        except json.JSONDecodeError as exc:
            logger.error(f"Invalid save JSON in slot {slot_number}: {exc}")
            raise ValueError(f"Invalid save JSON: {exc}") from exc

def save_game_data(slot_number: int, data: dict):
    """Serializes and compresses the modified dictionary back into GZip format."""
    file_path = os.path.join(SAVES_DIR, f"slot{slot_number}.json.gz")
    logger.info(f"Saving data to slot {slot_number}")
    
    json_text = json.dumps(data, indent=4, ensure_ascii=False)
    with gzip.open(file_path, 'wb') as f:
        f.write(json_text.encode('utf-8'))
    
    logger.info(f"Save slot {slot_number} written successfully")