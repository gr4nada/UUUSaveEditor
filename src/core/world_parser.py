# src/core/world_parser.py
"""
Parser puro de worldObjectsByLevel → listas tipadas para a GUI.

Não tem estado, não tem Tkinter.
Separa critters de items, resolve nomes via enums.
"""
from __future__ import annotations
import json
import logging
from src.core.enums import whoami_name, attitude_label, ITEM_TYPES_SKIP, ITEM_TYPE_GROUPS

logger = logging.getLogger("core.world_parser")

_TYPE_ICONS: dict[str, str] = {
    "Weapon":    "⚔",
    "WeaponBase":"⚔",
    "Armour":    "🛡",
    "Wand":      "🪄",
    "Food":      "🍖",
    "Key":       "🔑",
    "Book":      "📖",
    "Scroll":    "📜",
    "RuneStone": "◈",
    "Container": "📦",
    "Potion":    "⚗",
}


def _jd(obj: dict) -> dict:
    raw = obj.get("jsonData", "")
    if not raw:
        return {}
    try:
        return json.loads(raw)
    except Exception:
        return {}


def _is_critter(d: dict) -> bool:
    return "whoami" in d and "hp" in d


def parse_world(raw_save: dict) -> tuple[list[dict], list[dict]]:
    """
    Retorna (critters, items) de worldObjectsByLevel.

    critter keys:
        level, object_type, type_name, whoami_id, name,
        hp, max_hp, attitude, attitude_label, state,
        dead, player_ally, critter_level, talked_to,
        loot_count, object_index

    item keys:
        level, object_type, type_name, object_name, icon,
        quantity, enchantment, quality, quality_class,
        is_enchanted, object_index, active, tile_x, tile_y
    """
    wobl = raw_save.get("worldObjectsByLevel", [])
    critters: list[dict] = []
    items:    list[dict] = []

    for lvl_idx, lvl_data in enumerate(wobl):
        dlvl = lvl_idx + 1
        all_objs = lvl_data.get("objects", []) + lvl_data.get("inactiveObjects", [])

        for obj in all_objs:
            d = _jd(obj)
            otype = obj.get("objectType", d.get("objectType", 0))
            if otype == 0:
                continue

            if _is_critter(d):
                hp     = d.get("hp", 0)
                max_hp = d.get("originalHp", hp)
                att    = d.get("attitude", 0)
                wid    = d.get("whoami", 0)
                dead   = d.get("deathProcessed", False) or hp <= 0

                critters.append({
                    "level":         dlvl,
                    "object_type":   otype,
                    "type_name":     obj.get("objectTypeName", ""),
                    "whoami_id":     wid,
                    "name":          whoami_name(wid),
                    "hp":            hp,
                    "max_hp":        max_hp,
                    "attitude":      att,
                    "attitude_label":attitude_label(att),
                    "state":         d.get("state", 0),
                    "dead":          dead,
                    "player_ally":   d.get("playerAlly", False),
                    "critter_level": d.get("critterLevel", 0),
                    "talked_to":     d.get("talkedTo", 0),
                    "loot_count":    len(d.get("loot", [])),
                    "object_index":  obj.get("objectIndex", d.get("objectIndex", 0)),
                })

            else:
                tname = obj.get("objectTypeName", "")
                if tname in ITEM_TYPES_SKIP:
                    continue

                name = (obj.get("objectName") or d.get("objectName") or "").strip()
                ench = d.get("enchantmentName", "")

                items.append({
                    "level":         dlvl,
                    "object_type":   otype,
                    "type_name":     tname,
                    "object_name":   name,
                    "icon":          _TYPE_ICONS.get(tname, "·"),
                    "quantity":      d.get("quantity", 1),
                    "enchantment":   ench,
                    "quality":       d.get("quality", 0),
                    "quality_class": d.get("qualityClass", 0),
                    "is_enchanted":  bool(ench),
                    "object_index":  obj.get("objectIndex", d.get("objectIndex", 0)),
                    "active":        d.get("activeInLevel", True),
                    "tile_x":        d.get("initialTileX", 0),
                    "tile_y":        d.get("initialTileY", 0),
                })

    return critters, items


def filter_items(items: list[dict], group: str = "All",
                 search: str = "") -> list[dict]:
    allowed = ITEM_TYPE_GROUPS.get(group)
    result = items if allowed is None else [i for i in items if i["type_name"] in allowed]
    if search:
        q = search.lower()
        result = [i for i in result
                  if q in i["object_name"].lower()
                  or q in i["enchantment"].lower()
                  or q in i["type_name"].lower()]
    return result


def filter_critters(critters: list[dict],
                    show_dead: bool = True,
                    level: int = 0) -> list[dict]:
    result = critters
    if not show_dead:
        result = [c for c in result if not c["dead"]]
    if level > 0:
        result = [c for c in result if c["level"] == level]
    return result
