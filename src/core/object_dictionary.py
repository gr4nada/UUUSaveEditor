# src/core/object_dictionary.py
"""
Dicionário de object_type → informação semântica.

Resolve números mágicos em nomes legíveis para a GUI.
Fonte: Ultima Codex, CritterSaveData DLL, observação do save.

Estrutura de cada entrada:
    {
        "name":     str,   — nome exibido na UI
        "category": str,   — agrupamento para filtros
        "icon":     str,   — emoji para a treeview
    }
"""
from __future__ import annotations

# ---------------------------------------------------------------------------
# Mapeamento objectType (int) → metadados
# ---------------------------------------------------------------------------

_OBJECT_DB: dict[int, dict] = {
    # ── Weapons ──
    0:  {"name": "Hand Axe",         "category": "Weapon", "icon": "⚔"},
    1:  {"name": "Battle Axe",       "category": "Weapon", "icon": "⚔"},
    2:  {"name": "Axe",              "category": "Weapon", "icon": "⚔"},
    3:  {"name": "Dagger",           "category": "Weapon", "icon": "⚔"},
    4:  {"name": "Shortsword",       "category": "Weapon", "icon": "⚔"},
    5:  {"name": "Longsword",        "category": "Weapon", "icon": "⚔"},
    6:  {"name": "Broadsword",       "category": "Weapon", "icon": "⚔"},
    7:  {"name": "Cudgel",           "category": "Weapon", "icon": "⚔"},
    8:  {"name": "Light Mace",       "category": "Weapon", "icon": "⚔"},
    9:  {"name": "Mace",             "category": "Weapon", "icon": "⚔"},
    10: {"name": "A Shiny Sword",    "category": "Weapon", "icon": "⚔"},
    11: {"name": "Jeweled Axe",      "category": "Weapon", "icon": "⚔"},
    12: {"name": "Black Sword",      "category": "Weapon", "icon": "⚔"},
    13: {"name": "Jeweled Sword",    "category": "Weapon", "icon": "⚔"},
    14: {"name": "Jeweled Mace",     "category": "Weapon", "icon": "⚔"},
    24: {"name": "Sling",            "category": "Weapon", "icon": "⚔"},
    25: {"name": "Bow",              "category": "Weapon", "icon": "⚔"},
    26: {"name": "Crossbow",         "category": "Weapon", "icon": "⚔"},
    31: {"name": "Jeweled Bow",      "category": "Weapon", "icon": "⚔"},

    # ── Armour ──
    32: {"name": "Leather Vest",     "category": "Armour", "icon": "🛡"},
    33: {"name": "Mail Shirt",       "category": "Armour", "icon": "🛡"},
    34: {"name": "Breastplate",      "category": "Armour", "icon": "🛡"},
    35: {"name": "Leather Leggings", "category": "Armour", "icon": "🛡"},
    36: {"name": "Mail Leggings",    "category": "Armour", "icon": "🛡"},
    37: {"name": "Plate Leggings",   "category": "Armour", "icon": "🛡"},
    38: {"name": "Leather Gloves",   "category": "Armour", "icon": "🛡"},
    39: {"name": "Chain Gauntlets",  "category": "Armour", "icon": "🛡"},
    40: {"name": "Plate Gauntlets",  "category": "Armour", "icon": "🛡"},
    41: {"name": "Leather Boots",    "category": "Armour", "icon": "🛡"},
    42: {"name": "Chain Boots",      "category": "Armour", "icon": "🛡"},
    43: {"name": "Plate Boots",      "category": "Armour", "icon": "🛡"},
    44: {"name": "Leather Cap",      "category": "Armour", "icon": "🛡"},
    45: {"name": "Chain Cowl",       "category": "Armour", "icon": "🛡"},
    46: {"name": "Helmet",           "category": "Armour", "icon": "🛡"},
    47: {"name": "Dragonskin Boots", "category": "Armour", "icon": "🛡"},
    48: {"name": "Crown A",          "category": "Armour", "icon": "🛡"},
    49: {"name": "Crown B",          "category": "Armour", "icon": "🛡"},
    50: {"name": "Crown C",          "category": "Armour", "icon": "🛡"},
    55: {"name": "Shiny Shield",     "category": "Armour", "icon": "🛡"},
    59: {"name": "Tower Shield",     "category": "Armour", "icon": "🛡"},
    60: {"name": "Wooden Shield",    "category": "Armour", "icon": "🛡"},
    61: {"name": "Small Shield",     "category": "Armour", "icon": "🛡"},
    62: {"name": "Buckler",          "category": "Armour", "icon": "🛡"},
    63: {"name": "Jeweled Shield",   "category": "Armour", "icon": "🛡"},

    # ── Jewellery ──
    21: {"name": "Amulet",           "category": "Jewellery", "icon": "◉"},
    54: {"name": "Iron Ring",        "category": "Jewellery", "icon": "◉"},
    56: {"name": "Gold Ring",        "category": "Jewellery", "icon": "◉"},
    57: {"name": "Silver Ring",      "category": "Jewellery", "icon": "◉"},
    58: {"name": "Red Ring",         "category": "Jewellery", "icon": "◉"},

    # ── Light Sources ──
    145: {"name": "Lantern",         "category": "Light",   "icon": "🔦"},
    146: {"name": "Torch",           "category": "Light",   "icon": "🔦"},
    147: {"name": "Candle",          "category": "Light",   "icon": "🔦"},
    148: {"name": "Taper",           "category": "Light",   "icon": "🔦"},
    149: {"name": "Lit Lantern",     "category": "Light",   "icon": "🔦"},
    150: {"name": "Lit Torch",       "category": "Light",   "icon": "🔦"},
    151: {"name": "Lit Candle",      "category": "Light",   "icon": "🔦"},

    # ── Food ──
    64:  {"name": "Ham",             "category": "Food",    "icon": "🍖"},
    65:  {"name": "Chicken Leg",     "category": "Food",    "icon": "🍖"},
    66:  {"name": "Corn",            "category": "Food",    "icon": "🍖"},
    67:  {"name": "Fish",            "category": "Food",    "icon": "🍖"},
    68:  {"name": "Bread",           "category": "Food",    "icon": "🍖"},

    # ── Keys ──
    172: {"name": "Key",             "category": "Key",     "icon": "🔑"},
    173: {"name": "Iron Key",        "category": "Key",     "icon": "🔑"},
    174: {"name": "Magic Key",       "category": "Key",     "icon": "🔑"},
    175: {"name": "Bronze Key",      "category": "Key",     "icon": "🔑"},

    # ── Containers ──
    136: {"name": "Chest",           "category": "Container","icon": "📦"},
    137: {"name": "Backpack",        "category": "Container","icon": "📦"},
    138: {"name": "Gold Coffer",     "category": "Container","icon": "📦"},
    139: {"name": "Sack",            "category": "Container","icon": "📦"},

    # ── Critters (resolução quando objectName é vazio) ──
    80:  {"name": "Goblin",          "category": "Critter", "icon": "👾"},
    81:  {"name": "Mountainman",     "category": "Critter", "icon": "👾"},
    82:  {"name": "Ghost",           "category": "Critter", "icon": "👾"},
    83:  {"name": "Outcast",         "category": "Critter", "icon": "👾"},
    84:  {"name": "Lurker",          "category": "Critter", "icon": "👾"},
    85:  {"name": "Flyer",           "category": "Critter", "icon": "👾"},
    86:  {"name": "Fighter",         "category": "Critter", "icon": "👾"},
    87:  {"name": "Troll",           "category": "Critter", "icon": "👾"},
    88:  {"name": "Skeleton",        "category": "Critter", "icon": "👾"},
    89:  {"name": "Shadow Beast",    "category": "Critter", "icon": "👾"},
    90:  {"name": "Ghoul",           "category": "Critter", "icon": "👾"},
    91:  {"name": "Fire Elemental",  "category": "Critter", "icon": "👾"},
    92:  {"name": "Reaper",          "category": "Critter", "icon": "👾"},
    93:  {"name": "Mage",            "category": "Critter", "icon": "👾"},
    94:  {"name": "Golem",           "category": "Critter", "icon": "👾"},
    95:  {"name": "Imp",             "category": "Critter", "icon": "👾"},
    96:  {"name": "Gazer",           "category": "Critter", "icon": "👾"},
    97:  {"name": "Wisp",            "category": "Critter", "icon": "👾"},
    98:  {"name": "Sorceress",       "category": "Critter", "icon": "👾"},
}

# Prefixos de categoria para busca rápida
_CATEGORY_ICONS = {
    "Weapon":    "⚔",
    "Armour":    "🛡",
    "Jewellery": "◉",
    "Light":     "🔦",
    "Food":      "🍖",
    "Key":       "🔑",
    "Container": "📦",
    "Critter":   "👾",
}


def lookup(object_type: int) -> dict:
    """
    Retorna metadados do objectType, ou um fallback genérico.

    Retorno: {"name": str, "category": str, "icon": str}
    """
    return _OBJECT_DB.get(object_type, {
        "name":     f"Object#{object_type}",
        "category": "Unknown",
        "icon":     "·",
    })


def resolve_name(object_type: int, object_name: str, type_name: str = "") -> str:
    """
    Retorna o melhor nome disponível para um objeto.

    Prioridade:
      1. objectName do save (se não vazio)
      2. Dicionário interno (object_dictionary)
      3. objectTypeName do save (se não vazio)
      4. "Object#N"
    """
    if object_name and object_name.strip():
        return object_name.strip()
    entry = _OBJECT_DB.get(object_type)
    if entry:
        return entry["name"]
    if type_name and type_name.strip():
        return type_name.strip()
    return f"Object#{object_type}"


def resolve_icon(object_type: int, type_name: str = "") -> str:
    """Retorna o ícone unicode para o objectType."""
    entry = _OBJECT_DB.get(object_type)
    if entry:
        return entry["icon"]
    return _CATEGORY_ICONS.get(type_name, "·")


def all_categories() -> list[str]:
    """Lista de categorias únicas no dicionário."""
    return sorted({v["category"] for v in _OBJECT_DB.values()})
