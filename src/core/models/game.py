# src/core/models/game.py
"""SaveGame — single entry point for save access."""
from __future__ import annotations
import logging

from src.core.models.primitives import FIELD_LIMITS, _clamp
from src.core.models.player     import PlayerModel
from src.core.models.objects    import GameObject

logger = logging.getLogger("core.models.game")

class SaveGame:
    """
    Single entry point for save access.

    Usage:
        sg = SaveGame(raw_dict)
        sg.player.hp = 999
        sg.player.name        → "Avatar"
        sg.slot_name          → "Slot 0"
        sg.raw                → original dict (for save_manager)
    """

    def __init__(self, raw: dict) -> None:
        self._raw = raw
        self.player = PlayerModel(raw.get("playerData", {}))

    # — Save metadata —
    @property
    def raw(self) -> dict:           return self._raw
    @property
    def version(self) -> str:        return str(self._raw.get("version", ""))
    @property
    def slot_name(self) -> str:      return str(self._raw.get("slotName", ""))
    @property
    def display_name(self) -> str:   return str(self._raw.get("displayName", ""))
    @property
    def saved_at(self) -> str:       return str(self._raw.get("savedAtIso", ""))
    @property
    def current_level(self) -> int:  return int(self._raw.get("currentLevel", 0))
    @current_level.setter
    def current_level(self, v: int) -> None:
        """
        Sets the player's current dungeon level (teleport between levels).
        Clamped to FIELD_LIMITS["dungeon_level"] = (0, 9) — the 10 existing
        levels in worldObjectsByLevel.
        """
        lo, hi = FIELD_LIMITS["dungeon_level"]
        # Also limit to actual number of levels present in save, in case
        # worldObjectsByLevel has fewer than 10 entries.
        max_level = min(hi, len(self._raw.get("worldObjectsByLevel", [])) - 1)
        if max_level < lo:
            max_level = hi
        self._raw["currentLevel"] = _clamp(int(v), lo, max_level)

    # — Non-editable blocks for now —
    @property
    def inventory_data(self) -> dict:    return self._raw.get("inventoryData", {})
    @property
    def world_objects(self) -> list:     return self._raw.get("worldObjects", [])
    @property
    def world_objects_by_level(self) -> list: return self._raw.get("worldObjectsByLevel", [])
    @property
    def map_data(self) -> dict:          return self._raw.get("mapData", {})

    # — Map Annotations (Sprint 10) —
    #
    # mapData = {"pages": [{"mappedRLE": "...", "notes": [...]}]}
    #
    # Each "note" is a free-form dict (typically {"x", "y", "text"}).
    # The API below treats `notes` only as a list of dicts — does not enforce
    # a strict schema, preserving any unknown keys in existing notes
    # (mappedRLE is never touched).

    def get_map_notes(self, page: int = 0) -> list[dict]:
        """Returns list of annotations for page `page` (shallow copy)."""
        pages = self._raw.get("mapData", {}).get("pages", [])
        if not (0 <= page < len(pages)):
            return []
        return list(pages[page].get("notes", []))

    def add_map_note(self, page: int, note: dict) -> bool:
        """
        Adiciona uma anotação à página `page`. `note` é armazenado como veio
        (ex: {"x": 10, "y": 20, "text": "Tesouro aqui"}). Retorna False se a
        página não existir.
        """
        pages = self._raw.get("mapData", {}).get("pages", [])
        if not (0 <= page < len(pages)):
            logger.warning("add_map_note: página %d fora do range (%d páginas)", page, len(pages))
            return False
        pages[page].setdefault("notes", []).append(dict(note))
        return True

    def update_map_note(self, page: int, index: int, note: dict) -> bool:
        """
        Substitui a anotação `index` da página `page` por `note`.
        Retorna False se página ou índice forem inválidos.
        """
        pages = self._raw.get("mapData", {}).get("pages", [])
        if not (0 <= page < len(pages)):
            return False
        notes = pages[page].setdefault("notes", [])
        if not (0 <= index < len(notes)):
            logger.warning("update_map_note: índice %d fora do range (%d notas)", index, len(notes))
            return False
        notes[index] = dict(note)
        return True

    def delete_map_note(self, page: int, index: int) -> bool:
        """Remove a anotação `index` da página `page`. Retorna False se inválido."""
        pages = self._raw.get("mapData", {}).get("pages", [])
        if not (0 <= page < len(pages)):
            return False
        notes = pages[page].setdefault("notes", [])
        if not (0 <= index < len(notes)):
            logger.warning("delete_map_note: índice %d fora do range (%d notas)", index, len(notes))
            return False
        notes.pop(index)
        return True

    @property
    def map_page_count(self) -> int:
        return len(self._raw.get("mapData", {}).get("pages", []))

    @property
    def dungeon_level(self) -> int:
        """Nível de masmorra atual do jogador (currentLevel)."""
        return int(self._raw.get("currentLevel", 0))

    # — Main Inventory —
    @property
    def main_inventory(self) -> list[GameObject]:
        items = self._raw.get("inventoryData", {}).get("mainInventory", [])
        return [GameObject(it) for it in items]

    def delete_main_inventory_item(self, index: int) -> None:
        items = self._raw.get("inventoryData", {}).get("mainInventory", [])
        if not (0 <= index < len(items)):
            logger.error("Main inventory index out of range: %d", index)
            return
        removed = items.pop(index)
        logger.info("Main inventory item #%d removed: %r", index, removed.get("objectName"))

    # — Equipped Items —
    @property
    def equipped_items(self) -> list[GameObject]:
        items = self._raw.get("inventoryData", {}).get("equippedItems", [])
        return [GameObject(it) for it in items]

    # — World Objects (parsed) —
    def parse_world(self) -> tuple[list[dict], list[dict]]:
        """Retorna (critters, items) via world_parser.parse_world."""
        from src.core.world_parser import parse_world as _parse_world
        return _parse_world(self._raw)
