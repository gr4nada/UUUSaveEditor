# src/core/world_parser.py
"""
Pure parser for worldObjectsByLevel → typed lists for the GUI.
Stateless, no Tkinter, 100% testable.
"""
from __future__ import annotations
import json
import logging
from src.core.database.critters import (
    state_label  as critter_state_label,
    goal_label   as critter_goal_label,
    attitude_label as critter_attitude_label,
    movement_label as movement_type_label,
)
from src.core.database.whoami   import npc_name as whoami_name
from src.core.database.objects  import ITEM_TYPE_GROUPS, ITEM_TYPES_SKIP

logger = logging.getLogger("core.world_parser")

_TYPE_ICONS: dict[str, str] = {
    "Weapon": "⚔", "WeaponBase": "⚔", "Armour": "🛡", "Wand": "🪄",
    "Food": "🍖", "Key": "🔑", "Book": "📖", "Scroll": "📜",
    "RuneStone": "◈", "Container": "📦", "Potion": "⚗", "Coin": "🪙",
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


def _parse_loot(loot_list: list) -> list[dict]:
    """Extracts minimal information from each item in the critter's loot list."""
    result = []
    for raw in loot_list:
        inner = _jd(raw) if isinstance(raw, dict) else {}
        otype = raw.get("objectType", inner.get("objectType", 0)) if isinstance(raw, dict) else 0
        
        # Skip empty loot slots
        if otype == 0:
            continue

        name  = (raw.get("objectName") or inner.get("objectName") or "").strip()
        tname = raw.get("objectTypeName", "")
        qty   = inner.get("quantity", 1)
        ench  = inner.get("enchantmentName", "")
        if not name:
            name = f"[{tname}]" if tname else "Unknown"
        result.append({
            "object_type": otype,
            "name":        name,
            "type_name":   tname,
            "icon":        _TYPE_ICONS.get(tname, "·"),
            "quantity":    qty,
            "enchantment": ench,
        })
    return result


def parse_world(raw_save: dict) -> tuple[list[dict], list[dict]]:
    """
    Returns (critters, items) from worldObjectsByLevel.

    critter keys:
        level, object_type, type_name, whoami_id, name,
        hp, max_hp, attitude, attitude_label, state,
        dead, player_ally, critter_level, talked_to,
        goal, gtarg, movement_type, loot, loot_count,
        object_index, tile_x, tile_y

    item keys:
        level, object_type, type_name, object_name, icon,
        quantity, enchantment, quality, quality_class,
        is_enchanted, object_index, active, tile_x, tile_y
    """
    wobl = raw_save.get("worldObjectsByLevel", [])
    critters: list[dict] = []
    items:    list[dict] = []

    for lvl_idx, lvl_data in enumerate(wobl):
        dlvl    = lvl_idx + 1
        all_obj = lvl_data.get("objects", []) + lvl_data.get("inactiveObjects", [])

        for obj in all_obj:
            d = _jd(obj)
            
            # Fetch object type prioritizing the main wrapper object structure
            otype = obj.get("objectType", d.get("objectType", 0))
            if otype == 0:
                continue

            if _is_critter(d):
                hp    = d.get("hp", 0)
                att   = d.get("attitude", 0)
                wid   = d.get("whoami", 0)
                loot  = _parse_loot(d.get("loot", []))

                critters.append({
                    "level":          dlvl,
                    "object_type":    otype,
                    "type_name":      obj.get("objectTypeName", ""),
                    "whoami_id":      wid,
                    "name":           whoami_name(wid),
                    "hp":             hp,
                    "max_hp":         d.get("originalHp", hp),
                    "attitude":       att,
                    "attitude_label": critter_attitude_label(att),
                    "state":          d.get("state", 0),
                    "dead":           d.get("deathProcessed", False) or hp <= 0,
                    "player_ally":    d.get("playerAlly", False),
                    "critter_level":  d.get("critterLevel", 0),
                    "talked_to":      d.get("talkedTo", 0),
                    "goal":               d.get("goal", 0),
                    "goal_label":         critter_goal_label(d.get("goal", 0)),
                    "gtarg":              d.get("gtarg", 0),
                    "movement_type":      d.get("movementType", 0),
                    "movement_label":     movement_type_label(d.get("movementType", 0)),
                    "state_label":        critter_state_label(d.get("state", 0)),
                    "loot":           loot,
                    "loot_count":     len(loot),
                    "object_index":   obj.get("objectIndex", d.get("objectIndex", 0)),
                    "tile_x":         d.get("initialTileX", 0),
                    "tile_y":         d.get("initialTileY", 0),
                    "_node":          obj,
                })

            else:
                tname = obj.get("objectTypeName", "")
                if tname in ITEM_TYPES_SKIP:
                    continue
                name  = (obj.get("objectName") or d.get("objectName") or "").strip()
                ench  = d.get("enchantmentName", "")
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
                    "tile_x":         d.get("initialTileX", 0),
                    "tile_y":         d.get("initialTileY", 0),
                    "_node":          obj,
                })

    return critters, items


def filter_items(items: list[dict], group: str = "All", search: str = "") -> list[dict]:
    allowed = ITEM_TYPE_GROUPS.get(group)
    result  = items if allowed is None else [i for i in items if i["type_name"] in allowed]
    if search:
        q = search.lower()
        result = [i for i in result
                  if q in i["object_name"].lower()
                  or q in i["enchantment"].lower()
                  or q in i["type_name"].lower()]
    return result


def filter_critters(critters: list[dict],
                    show_dead: bool = True, level: int = 0) -> list[dict]:
    result = critters
    if not show_dead:
        result = [c for c in result if not c["dead"]]
    if level > 0:
        # Match against map dungeon index 'level' to fulfill unit test constraints
        result = [c for c in result if c["level"] == level]
    return result


# ---------------------------------------------------------------------------
# Write API — edicao de world objects e critters no raw_save
#
# Todas as funcoes localizam o no pelo (level, object_index), atualizam
# jsonData via _patch_jsondata(), e retornam True em sucesso.
# ---------------------------------------------------------------------------

def _find_node(raw_save: dict, level: int, object_index: int) -> dict | None:
    """
    Localiza o no raw de um world object pelo nivel (1-based) e objectIndex.
    Busca em objects e inactiveObjects do nivel correto.
    Retorna None se nao encontrado.
    """
    wobl = raw_save.get("worldObjectsByLevel", [])
    lvl_idx = level - 1
    if not (0 <= lvl_idx < len(wobl)):
        logger.warning("_find_node: level %d fora do range (%d niveis)", level, len(wobl))
        return None
    lvl_data = wobl[lvl_idx]
    for bucket in ("objects", "inactiveObjects"):
        for obj in lvl_data.get(bucket, []):
            idx = obj.get("objectIndex", _jd(obj).get("objectIndex", -1))
            if idx == object_index:
                return obj
    logger.warning("_find_node: objectIndex %d nao encontrado no level %d", object_index, level)
    return None


def _patch_jsondata(node: dict, patches: dict) -> bool:
    """
    Aplica `patches` ao jsonData de `node` e re-serializa.
    Retorna True em sucesso.
    """
    raw = node.get("jsonData", "")
    try:
        d = json.loads(raw) if raw else {}
    except Exception:
        logger.error("_patch_jsondata: jsonData invalido no no %r", node.get("objectIndex"))
        return False
    d.update(patches)
    node["jsonData"] = json.dumps(d)
    return True


# --- Itens ---

def set_item_quantity(raw_save: dict, level: int, object_index: int,
                      quantity: int) -> bool:
    """Define a quantidade de um item no mundo."""
    quantity = max(1, int(quantity))
    node = _find_node(raw_save, level, object_index)
    if node is None:
        return False
    return _patch_jsondata(node, {"quantity": quantity})


def set_item_enchantment(raw_save: dict, level: int, object_index: int,
                         enchantment: str) -> bool:
    """Define o nome de encantamento de um item (string vazia = sem encanto)."""
    node = _find_node(raw_save, level, object_index)
    if node is None:
        return False
    is_enchanted = bool(enchantment.strip())
    return _patch_jsondata(node, {
        "enchantmentName": enchantment.strip(),
        "isEnchanted":     is_enchanted,
    })


def set_item_active(raw_save: dict, level: int, object_index: int,
                    active: bool) -> bool:
    """Ativa ou desativa um item no mundo (activeInLevel)."""
    node = _find_node(raw_save, level, object_index)
    if node is None:
        return False
    return _patch_jsondata(node, {"activeInLevel": bool(active)})


# --- Critters ---

def set_critter_hp(raw_save: dict, level: int, object_index: int,
                   hp: int, original_hp: int | None = None) -> bool:
    """
    Define o HP atual de um critter.
    Se original_hp for fornecido, atualiza tambem originalHp (HP maximo).
    hp = 0 marca o critter como morto (deathProcessed = True).
    """
    hp = max(0, int(hp))
    patches: dict = {"hp": hp, "deathProcessed": hp <= 0}
    if original_hp is not None:
        patches["originalHp"] = max(1, int(original_hp))
    node = _find_node(raw_save, level, object_index)
    if node is None:
        return False
    return _patch_jsondata(node, patches)


def set_critter_attitude(raw_save: dict, level: int, object_index: int,
                         attitude: int) -> bool:
    """Define a atitude de um critter (0=Hostile,1=Upset,2=Mellow,3=Friendly)."""
    attitude = max(0, min(3, int(attitude)))
    node = _find_node(raw_save, level, object_index)
    if node is None:
        return False
    return _patch_jsondata(node, {"attitude": attitude})


def set_critter_ally(raw_save: dict, level: int, object_index: int,
                     ally: bool) -> bool:
    """Define se o critter e aliado do jogador."""
    node = _find_node(raw_save, level, object_index)
    if node is None:
        return False
    return _patch_jsondata(node, {"playerAlly": bool(ally)})


def set_critter_goal(raw_save: dict, level: int, object_index: int,
                     goal: int) -> bool:
    """Define o objetivo (ECritterGoal) de um critter (0-14)."""
    goal = max(0, min(14, int(goal)))
    node = _find_node(raw_save, level, object_index)
    if node is None:
        return False
    return _patch_jsondata(node, {"goal": goal})
