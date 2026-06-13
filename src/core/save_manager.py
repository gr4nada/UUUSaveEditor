import os
import gzip
import json
import logging
import shutil
import time

logger = logging.getLogger("core.save_manager")

# Target directory for Unity's Persistent Data Path
SAVES_DIR = os.path.expandvars(r"%USERPROFILE%\AppData\LocalLow\Kweepa\UnityUnderground\Saves")

# Quantos backups manter por slot.
MAX_BACKUPS_PER_SLOT = 10


def _backups_dir() -> str:
    """Calculado a partir de SAVES_DIR no momento da chamada (não no import),
    para que testes possam monkeypatch SAVES_DIR e o backup siga corretamente."""
    return os.path.join(SAVES_DIR, "backups")


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


def backup_save(slot_number: int) -> str | None:
    """
    Copia o arquivo atual do slot para SAVES_DIR/backups/ com timestamp,
    antes de qualquer sobrescrita. Retorna o caminho do backup criado, ou
    None se o arquivo do slot ainda não existe (nada para fazer backup).

    Falhas de backup são logadas mas não impedem o save — perder o backup
    é muito menos grave do que perder a capacidade de salvar de vez.
    """
    file_path = os.path.join(SAVES_DIR, f"slot{slot_number}.json.gz")
    if not os.path.exists(file_path):
        return None

    try:
        backups_dir = _backups_dir()
        os.makedirs(backups_dir, exist_ok=True)
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        micros = f"{time.time() % 1:.6f}".split(".")[1]
        backup_path = os.path.join(backups_dir, f"slot{slot_number}_{timestamp}_{micros}.json.gz")
        shutil.copy2(file_path, backup_path)
        logger.info(f"Backup created for slot {slot_number}: {backup_path}")
        _prune_old_backups(slot_number)
        return backup_path
    except OSError as exc:
        logger.warning(f"Failed to create backup for slot {slot_number}: {exc}")
        return None


def _prune_old_backups(slot_number: int, keep: int | None = None) -> None:
    """Mantém apenas os `keep` (default MAX_BACKUPS_PER_SLOT) backups mais recentes do slot."""
    if keep is None:
        keep = MAX_BACKUPS_PER_SLOT
    backups_dir = _backups_dir()
    try:
        prefix = f"slot{slot_number}_"
        entries = [
            f for f in os.listdir(backups_dir)
            if f.startswith(prefix) and f.endswith(".json.gz")
        ]
        entries.sort(reverse=True)  # timestamps no nome => ordem cronológica reversa
        for old in entries[keep:]:
            try:
                os.remove(os.path.join(backups_dir, old))
                logger.debug(f"Pruned old backup: {old}")
            except OSError as exc:
                logger.warning(f"Failed to prune old backup {old}: {exc}")
    except OSError as exc:
        logger.warning(f"Failed to list backups for slot {slot_number}: {exc}")


def save_game_data(slot_number: int, data: dict):
    """
    Serializes and compresses the modified dictionary back into GZip format.

    Cria automaticamente um backup do arquivo atual (se existir) antes de
    sobrescrever — ver `backup_save`.
    """
    file_path = os.path.join(SAVES_DIR, f"slot{slot_number}.json.gz")
    logger.info(f"Saving data to slot {slot_number}")

    backup_save(slot_number)

    json_text = json.dumps(data, indent=4, ensure_ascii=False)
    with gzip.open(file_path, 'wb') as f:
        f.write(json_text.encode('utf-8'))
    
    logger.info(f"Save slot {slot_number} written successfully")