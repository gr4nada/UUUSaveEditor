# src/core/database/objects.py
"""
Enciclopédia de objetos do jogo (itens, armaduras, armas, containers, etc.).

Fonte única de verdade para:
  - nome legível       → object_name(id)
  - ícone unicode      → object_icon(id)
  - categoria          → object_category(id)
  - propriedades físicas (massa, valor) → object_props(id)
  - dados de equipamento por slot       → EQUIPMENT_BY_SLOT
  - filtros para o explorer             → ITEM_TYPE_GROUPS, ITEM_TYPES_SKIP

Anteriormente espalhado entre:
  - src/core/enums.py         (EObjectType, PROP_ITENS, ITEM_TYPE_GROUPS, ITEM_TYPES_SKIP)
  - src/core/object_dictionary.py (_OBJECT_DB, lookup, resolve_name, resolve_icon)
  - src/core/inventory.py     (WIKI_ITEM_DATABASE)
"""
from __future__ import annotations

# ---------------------------------------------------------------------------
# Banco de dados principal — objectType (int) → metadados completos
# ---------------------------------------------------------------------------

_DB: dict[int, dict] = {
    # ── Weapons ──────────────────────────────────────────────────────────────
    0:  {"name": "Hand Axe",         "category": "Weapon",    "icon": "⚔", "mass": 2.4, "value": 20},
    1:  {"name": "Battle Axe",       "category": "Weapon",    "icon": "⚔", "mass": 4.0, "value": 60},
    2:  {"name": "Axe",              "category": "Weapon",    "icon": "⚔", "mass": 3.2, "value": 100},
    3:  {"name": "Dagger",           "category": "Weapon",    "icon": "⚔", "mass": 0.8, "value": 20},
    4:  {"name": "Shortsword",       "category": "Weapon",    "icon": "⚔", "mass": 1.6, "value": 50},
    5:  {"name": "Longsword",        "category": "Weapon",    "icon": "⚔", "mass": 2.4, "value": 80},
    6:  {"name": "Broadsword",       "category": "Weapon",    "icon": "⚔", "mass": 3.2, "value": 100},
    7:  {"name": "Cudgel",           "category": "Weapon",    "icon": "⚔", "mass": 1.6, "value": 15},
    8:  {"name": "Light Mace",       "category": "Weapon",    "icon": "⚔", "mass": 2.4, "value": 55},
    9:  {"name": "Mace",             "category": "Weapon",    "icon": "⚔", "mass": 3.2, "value": 90},
    10: {"name": "A Shiny Sword",    "category": "Weapon",    "icon": "⚔", "mass": 3.4, "value": 0},
    11: {"name": "Jeweled Axe",      "category": "Weapon",    "icon": "⚔", "mass": 3.2, "value": 250},
    12: {"name": "Black Sword",      "category": "Weapon",    "icon": "⚔", "mass": 3.6, "value": 200},
    13: {"name": "Jeweled Sword",    "category": "Weapon",    "icon": "⚔", "mass": 2.8, "value": 250},
    14: {"name": "Jeweled Mace",     "category": "Weapon",    "icon": "⚔", "mass": 2.8, "value": 250},
    15: {"name": "Fist",             "category": "Weapon",    "icon": "⚔", "mass": 0.0, "value": 0},
    24: {"name": "Sling",            "category": "Weapon",    "icon": "⚔", "mass": 0.4, "value": 10},
    25: {"name": "Bow",              "category": "Weapon",    "icon": "⚔", "mass": 1.2, "value": 50},
    26: {"name": "Crossbow",         "category": "Weapon",    "icon": "⚔", "mass": 2.4, "value": 70},
    27: {"name": "Knife",            "category": "Weapon",    "icon": "⚔", "mass": 0.0, "value": 0},
    31: {"name": "Jeweled Bow",      "category": "Weapon",    "icon": "⚔", "mass": 1.6, "value": 150},

    # Ammo & projectiles
    16: {"name": "Sling Stone",      "category": "Ammo",      "icon": "·",  "mass": 0.1, "value": 1},
    17: {"name": "Crossbow Bolt",    "category": "Ammo",      "icon": "·",  "mass": 0.2, "value": 4},
    18: {"name": "Arrow",            "category": "Ammo",      "icon": "·",  "mass": 0.1, "value": 2},
    19: {"name": "Stone",            "category": "Ammo",      "icon": "·",  "mass": 0.4, "value": 0},

    # ── Armour ───────────────────────────────────────────────────────────────
    32: {"name": "Leather Vest",     "category": "Armour",    "icon": "🛡", "mass": 2.0, "value": 20,
         "slot": "Chest",    "protection": 2},
    33: {"name": "Mail Shirt",       "category": "Armour",    "icon": "🛡", "mass": 4.0, "value": 45,
         "slot": "Chest",    "protection": 5},
    34: {"name": "Breastplate",      "category": "Armour",    "icon": "🛡", "mass": 8.0, "value": 70,
         "slot": "Chest",    "protection": 8},
    35: {"name": "Leather Leggings", "category": "Armour",    "icon": "🛡", "mass": 1.6, "value": 15,
         "slot": "Legs",     "protection": 2},
    36: {"name": "Mail Leggings",    "category": "Armour",    "icon": "🛡", "mass": 3.2, "value": 35,
         "slot": "Legs",     "protection": 4},
    37: {"name": "Plate Leggings",   "category": "Armour",    "icon": "🛡", "mass": 6.4, "value": 60,
         "slot": "Legs",     "protection": 6},
    38: {"name": "Leather Gloves",   "category": "Armour",    "icon": "🛡", "mass": 0.8, "value": 10,
         "slot": "Hands",    "protection": 1},
    39: {"name": "Chain Gauntlets",  "category": "Armour",    "icon": "🛡", "mass": 1.2, "value": 20,
         "slot": "Hands",    "protection": 2},
    40: {"name": "Plate Gauntlets",  "category": "Armour",    "icon": "🛡", "mass": 1.6, "value": 30,
         "slot": "Hands",    "protection": 3},
    41: {"name": "Leather Boots",    "category": "Armour",    "icon": "🛡", "mass": 1.2, "value": 12,
         "slot": "Feet",     "protection": 1},
    42: {"name": "Chain Boots",      "category": "Armour",    "icon": "🛡", "mass": 1.6, "value": 25,
         "slot": "Feet",     "protection": 2},
    43: {"name": "Plate Boots",      "category": "Armour",    "icon": "🛡", "mass": 2.0, "value": 40,
         "slot": "Feet",     "protection": 3},
    44: {"name": "Leather Cap",      "category": "Armour",    "icon": "🛡", "mass": 0.8, "value": 15,
         "slot": "Head",     "protection": 1},
    45: {"name": "Chain Cowl",       "category": "Armour",    "icon": "🛡", "mass": 1.2, "value": 30,
         "slot": "Head",     "protection": 3},
    46: {"name": "Helmet",           "category": "Armour",    "icon": "🛡", "mass": 1.6, "value": 50,
         "slot": "Head",     "protection": 5},
    47: {"name": "Dragonskin Boots", "category": "Armour",    "icon": "🛡", "mass": 3.2, "value": 150,
         "slot": "Feet",     "protection": 5},
    48: {"name": "Crown A",          "category": "Armour",    "icon": "🛡", "mass": 0.4, "value": 140,
         "slot": "Head",     "protection": 2},
    49: {"name": "Crown B",          "category": "Armour",    "icon": "🛡", "mass": 0.4, "value": 120,
         "slot": "Head",     "protection": 2},
    50: {"name": "Crown C",          "category": "Armour",    "icon": "🛡", "mass": 0.4, "value": 90,
         "slot": "Head",     "protection": 2},

    # ── Shields ──────────────────────────────────────────────────────────────
    55: {"name": "Shiny Shield",     "category": "Armour",    "icon": "🛡", "mass": 3.0, "value": 100,
         "slot": "Left Hand", "protection": 4},
    59: {"name": "Tower Shield",     "category": "Armour",    "icon": "🛡", "mass": 4.0, "value": 65,
         "slot": "Left Hand", "protection": 6},
    60: {"name": "Wooden Shield",    "category": "Armour",    "icon": "🛡", "mass": 3.0, "value": 30,
         "slot": "Left Hand", "protection": 3},
    61: {"name": "Small Shield",     "category": "Armour",    "icon": "🛡", "mass": 2.0, "value": 20,
         "slot": "Left Hand", "protection": 2},
    62: {"name": "Buckler",          "category": "Armour",    "icon": "🛡", "mass": 1.0, "value": 10,
         "slot": "Left Hand", "protection": 1},
    63: {"name": "Jeweled Shield",   "category": "Armour",    "icon": "🛡", "mass": 2.5, "value": 200,
         "slot": "Left Hand", "protection": 5},

    # ── Jewellery ─────────────────────────────────────────────────────────────
    21: {"name": "Amulet",           "category": "Jewellery", "icon": "◉",  "mass": 0.2, "value": 90,
         "slot": "Neck"},
    54: {"name": "Iron Ring",        "category": "Jewellery", "icon": "◉",  "mass": 0.1, "value": 40,
         "slot": "Ring"},
    56: {"name": "Gold Ring",        "category": "Jewellery", "icon": "◉",  "mass": 0.1, "value": 100,
         "slot": "Ring"},
    57: {"name": "Silver Ring",      "category": "Jewellery", "icon": "◉",  "mass": 0.1, "value": 70,
         "slot": "Ring"},
    58: {"name": "Red Ring",         "category": "Jewellery", "icon": "◉",  "mass": 0.1, "value": 150,
         "slot": "Ring"},

    # ── Containers ───────────────────────────────────────────────────────────
    128: {"name": "Sack",            "category": "Container", "icon": "📦", "mass": 0.2, "value": 5},
    129: {"name": "Open Sack",       "category": "Container", "icon": "📦", "mass": 0.2, "value": 5},
    130: {"name": "Pack",            "category": "Container", "icon": "📦", "mass": 0.4, "value": 15},
    131: {"name": "Open Pack",       "category": "Container", "icon": "📦", "mass": 0.4, "value": 15},
    132: {"name": "Box",             "category": "Container", "icon": "📦", "mass": 1.0, "value": 10},
    133: {"name": "Open Box",        "category": "Container", "icon": "📦", "mass": 1.0, "value": 10},
    134: {"name": "Pouch",           "category": "Container", "icon": "📦", "mass": 0.1, "value": 3},
    135: {"name": "Open Pouch",      "category": "Container", "icon": "📦", "mass": 0.1, "value": 3},
    136: {"name": "Map Case",        "category": "Container", "icon": "📦", "mass": 0.2, "value": 8},
    137: {"name": "Open Map Case",   "category": "Container", "icon": "📦", "mass": 0.2, "value": 8},
    138: {"name": "Gold Coffer",     "category": "Container", "icon": "📦", "mass": 2.0, "value": 40},
    139: {"name": "Open Gold Coffer","category": "Container", "icon": "📦", "mass": 2.0, "value": 40},
    140: {"name": "Urn",             "category": "Container", "icon": "📦", "mass": 0.4, "value": 4},
    141: {"name": "Quiver",          "category": "Container", "icon": "📦", "mass": 0.4, "value": 12},
    142: {"name": "Bowl",            "category": "Container", "icon": "📦", "mass": 0.2, "value": 2},
    143: {"name": "Rune Bag",        "category": "Container", "icon": "📦", "mass": 0.2, "value": 25},

    # ── Light Sources ─────────────────────────────────────────────────────────
    144: {"name": "Lantern",         "category": "Light",     "icon": "🔦", "mass": 1.0, "value": 20},
    145: {"name": "Lantern",         "category": "Light",     "icon": "🔦", "mass": 1.0, "value": 20},
    146: {"name": "Torch",           "category": "Light",     "icon": "🔦", "mass": 0.4, "value": 2},
    147: {"name": "Candle",          "category": "Light",     "icon": "🔦", "mass": 0.1, "value": 4},
    148: {"name": "Taper",           "category": "Light",     "icon": "🔦", "mass": 0.1, "value": 1},
    149: {"name": "Lit Lantern",     "category": "Light",     "icon": "🔦", "mass": 1.0, "value": 20},
    150: {"name": "Lit Torch",       "category": "Light",     "icon": "🔦", "mass": 0.4, "value": 2},
    151: {"name": "Lit Candle",      "category": "Light",     "icon": "🔦", "mass": 0.1, "value": 4},
    152: {"name": "Lit Taper",       "category": "Light",     "icon": "🔦", "mass": 0.1, "value": 1},

    # ── Wands ────────────────────────────────────────────────────────────────
    153: {"name": "Wand A",          "category": "Wand",      "icon": "🪄", "mass": 0.4, "value": 80},
    154: {"name": "Wand B",          "category": "Wand",      "icon": "🪄", "mass": 0.4, "value": 100},
    155: {"name": "Wand C",          "category": "Wand",      "icon": "🪄", "mass": 0.4, "value": 150},
    156: {"name": "Wand D",          "category": "Wand",      "icon": "🪄", "mass": 0.4, "value": 200},
    157: {"name": "Broken Wand A",   "category": "Wand",      "icon": "🪄", "mass": 0.2, "value": 10},
    158: {"name": "Broken Wand B",   "category": "Wand",      "icon": "🪄", "mass": 0.2, "value": 10},
    159: {"name": "Broken Wand C",   "category": "Wand",      "icon": "🪄", "mass": 0.2, "value": 15},
    160: {"name": "Broken Wand D",   "category": "Wand",      "icon": "🪄", "mass": 0.2, "value": 20},

    # ── Treasures & Gems ──────────────────────────────────────────────────────
    161: {"name": "Coin",            "category": "Coin",      "icon": "🪙", "mass": 0.0, "value": 1},
    162: {"name": "Gold Coins",      "category": "Coin",      "icon": "🪙", "mass": 0.1, "value": 10},
    163: {"name": "Ruby",            "category": "Gem",       "icon": "◉",  "mass": 0.1, "value": 40},
    164: {"name": "Red Gem",         "category": "Gem",       "icon": "◉",  "mass": 0.1, "value": 25},
    165: {"name": "Small Blue Gem",  "category": "Gem",       "icon": "◉",  "mass": 0.1, "value": 15},
    166: {"name": "Large Blue Gem",  "category": "Gem",       "icon": "◉",  "mass": 0.2, "value": 60},
    167: {"name": "Sapphire",        "category": "Gem",       "icon": "◉",  "mass": 0.1, "value": 50},
    168: {"name": "Emerald",         "category": "Gem",       "icon": "◉",  "mass": 0.1, "value": 45},
    169: {"name": "Amulet",          "category": "Jewellery", "icon": "◉",  "mass": 0.2, "value": 90},
    170: {"name": "Goblet",          "category": "Treasure",  "icon": "·",  "mass": 0.4, "value": 45},
    171: {"name": "Sceptre",         "category": "Treasure",  "icon": "·",  "mass": 0.8, "value": 120},
    172: {"name": "Gold Chain",      "category": "Treasure",  "icon": "·",  "mass": 0.2, "value": 75},
    173: {"name": "Gold Plate",      "category": "Treasure",  "icon": "·",  "mass": 0.6, "value": 85},
    174: {"name": "Ankh Pendant",    "category": "Treasure",  "icon": "·",  "mass": 0.1, "value": 100},
    175: {"name": "Shiny Cup",       "category": "Treasure",  "icon": "·",  "mass": 0.4, "value": 30},
    176: {"name": "Large Gold Nugget","category": "Treasure",  "icon": "·",  "mass": 1.5, "value": 150},

    # ── Food & Drink ──────────────────────────────────────────────────────────
    177: {"name": "Piece of Meat",   "category": "Food",      "icon": "🍖", "mass": 0.4, "value": 4},
    178: {"name": "Loaf of Bread",   "category": "Food",      "icon": "🍖", "mass": 0.4, "value": 2},
    179: {"name": "Piece of Cheese", "category": "Food",      "icon": "🍖", "mass": 0.2, "value": 3},
    180: {"name": "Apple",           "category": "Food",      "icon": "🍖", "mass": 0.1, "value": 1},
    181: {"name": "Ear of Corn",     "category": "Food",      "icon": "🍖", "mass": 0.2, "value": 1},
    182: {"name": "Loaf of Bread B", "category": "Food",      "icon": "🍖", "mass": 0.4, "value": 2},
    183: {"name": "Fish",            "category": "Food",      "icon": "🍖", "mass": 0.3, "value": 2},
    184: {"name": "Popcorn",         "category": "Food",      "icon": "🍖", "mass": 0.1, "value": 1},
    185: {"name": "Mushroom",        "category": "Food",      "icon": "🍖", "mass": 0.1, "value": 1},
    186: {"name": "Toadstool",       "category": "Food",      "icon": "🍖", "mass": 0.1, "value": 0},
    187: {"name": "Bottle of Ale",   "category": "Food",      "icon": "🍖", "mass": 0.6, "value": 3},
    188: {"name": "Red Potion",      "category": "Potion",    "icon": "⚗",  "mass": 0.4, "value": 25},
    189: {"name": "Green Potion",    "category": "Potion",    "icon": "⚗",  "mass": 0.4, "value": 25},
    190: {"name": "Bottle of Water", "category": "Food",      "icon": "🍖", "mass": 0.5, "value": 1},
    191: {"name": "Flask of Port",   "category": "Food",      "icon": "🍖", "mass": 0.6, "value": 12},
    192: {"name": "Bottle of Wine",  "category": "Food",      "icon": "🍖", "mass": 0.6, "value": 8},

    # ── Keys ─────────────────────────────────────────────────────────────────
    226: {"name": "Key of Truth",    "category": "Key",       "icon": "🔑", "mass": 0.1, "value": 0},
    227: {"name": "Key of Love",     "category": "Key",       "icon": "🔑", "mass": 0.1, "value": 0},
    228: {"name": "Two-Part Key (Top-Left)", "category": "Key","icon": "🔑", "mass": 0.1, "value": 0},
    229: {"name": "Two-Part Key",    "category": "Key",       "icon": "🔑", "mass": 0.1, "value": 0},
    230: {"name": "Two-Part Key B",  "category": "Key",       "icon": "🔑", "mass": 0.1, "value": 0},
    231: {"name": "Key of Infinity", "category": "Key",       "icon": "🔑", "mass": 0.1, "value": 0},

    # ── Runestones ────────────────────────────────────────────────────────────
    233: {"name": "Runestone: An",   "category": "RuneStone", "icon": "◈",  "mass": 0.1, "value": 10},
    234: {"name": "Runestone: Bet",  "category": "RuneStone", "icon": "◈",  "mass": 0.1, "value": 10},
    235: {"name": "Runestone: Corp", "category": "RuneStone", "icon": "◈",  "mass": 0.1, "value": 10},
    236: {"name": "Runestone: Des",  "category": "RuneStone", "icon": "◈",  "mass": 0.1, "value": 10},
    237: {"name": "Runestone: Ex",   "category": "RuneStone", "icon": "◈",  "mass": 0.1, "value": 10},
    238: {"name": "Runestone: Flam", "category": "RuneStone", "icon": "◈",  "mass": 0.1, "value": 10},
    239: {"name": "Runestone: Grav", "category": "RuneStone", "icon": "◈",  "mass": 0.1, "value": 10},
    240: {"name": "Runestone: Hur",  "category": "RuneStone", "icon": "◈",  "mass": 0.1, "value": 10},
    241: {"name": "Runestone: In",   "category": "RuneStone", "icon": "◈",  "mass": 0.1, "value": 10},
    242: {"name": "Runestone: Jux",  "category": "RuneStone", "icon": "◈",  "mass": 0.1, "value": 10},
    243: {"name": "Runestone: Kal",  "category": "RuneStone", "icon": "◈",  "mass": 0.1, "value": 10},
    244: {"name": "Runestone: Lor",  "category": "RuneStone", "icon": "◈",  "mass": 0.1, "value": 10},
    245: {"name": "Runestone: Mani", "category": "RuneStone", "icon": "◈",  "mass": 0.1, "value": 10},
    246: {"name": "Runestone: Nox",  "category": "RuneStone", "icon": "◈",  "mass": 0.1, "value": 10},
    247: {"name": "Runestone: Ort",  "category": "RuneStone", "icon": "◈",  "mass": 0.1, "value": 10},
    248: {"name": "Runestone: Por",  "category": "RuneStone", "icon": "◈",  "mass": 0.1, "value": 10},
    249: {"name": "Runestone: Quas", "category": "RuneStone", "icon": "◈",  "mass": 0.1, "value": 10},
    250: {"name": "Runestone: Rel",  "category": "RuneStone", "icon": "◈",  "mass": 0.1, "value": 10},
    251: {"name": "Runestone: Sanct","category": "RuneStone", "icon": "◈",  "mass": 0.1, "value": 10},
    252: {"name": "Runestone: Tym",  "category": "RuneStone", "icon": "◈",  "mass": 0.1, "value": 10},
    253: {"name": "Runestone: Uus",  "category": "RuneStone", "icon": "◈",  "mass": 0.1, "value": 10},
    254: {"name": "Runestone: Vas",  "category": "RuneStone", "icon": "◈",  "mass": 0.1, "value": 10},
    255: {"name": "Runestone: Wis",  "category": "RuneStone", "icon": "◈",  "mass": 0.1, "value": 10},
    256: {"name": "Runestone: Xen",  "category": "RuneStone", "icon": "◈",  "mass": 0.1, "value": 10},
    257: {"name": "Runestone: Ylem", "category": "RuneStone", "icon": "◈",  "mass": 0.1, "value": 10},
    258: {"name": "Runestone: Zu",   "category": "RuneStone", "icon": "◈",  "mass": 0.1, "value": 10},
}

# Ícone por categoria (fallback quando o tipo exato não está no DB)
CATEGORY_ICONS: dict[str, str] = {
    "Weapon":    "⚔",
    "Ammo":      "·",
    "Armour":    "🛡",
    "Jewellery": "◉",
    "Light":     "🔦",
    "Food":      "🍖",
    "Potion":    "⚗",
    "Key":       "🔑",
    "Container": "📦",
    "RuneStone": "◈",
    "Coin":      "🪙",
    "Gem":       "◉",
    "Treasure":  "·",
    "Wand":      "🪄",
}

# ---------------------------------------------------------------------------
# Filtros para o World Objects Explorer
# ---------------------------------------------------------------------------

ITEM_TYPE_GROUPS: dict[str, set | None] = {
    "All":        None,
    "Weapons":    {"Weapon", "WeaponBase"},
    "Armour":     {"Armour"},
    "Wands":      {"Wand"},
    "Food":       {"Food"},
    "Keys":       {"Key"},
    "Books":      {"Book", "Scroll"},
    "RuneStones": {"RuneStone"},
    "Containers": {"Container"},
    "Potions":    {"Potion"},
    "Other":      {"Portable", "Ring", "Amulet", "Coin"},
}

ITEM_TYPES_SKIP: frozenset[str] = frozenset({
    "BloodStain", "Decal", "Trigger", "UnderCursorHidden",
    "Bones", "Trap", "Door", "UUObject",
})

# ---------------------------------------------------------------------------
# Dados de equipamento por slot — usado pela dialog de equipamentos
# (substitui WIKI_ITEM_DATABASE de inventory.py)
# ---------------------------------------------------------------------------

EQUIPMENT_BY_SLOT: dict[str, list[dict]] = {
    "Head": [
        {"id": 44, "name": "Leather Cap",  "weight": "0.8",  "protection": "1", "details": "Basic leather head protection"},
        {"id": 45, "name": "Chain Cowl",   "weight": "1.2",  "protection": "3", "details": "Interlinked iron mesh cowl"},
        {"id": 46, "name": "Helmet",       "weight": "1.6",  "protection": "5", "details": "Full iron plate helm"},
        {"id": 48, "name": "Crown A",      "weight": "0.4",  "protection": "2", "details": "Regal decorative crown"},
        {"id": 49, "name": "Crown B",      "weight": "0.4",  "protection": "2", "details": "Regal decorative crown variation"},
        {"id": 50, "name": "Crown C",      "weight": "0.4",  "protection": "2", "details": "Regal decorative crown variation"},
    ],
    "Neck": [
        {"id": 21, "name": "Amulet",       "weight": "0.2",  "details": "Decorative or magical neck amulet"},
    ],
    "Chest": [
        {"id": 32, "name": "Leather Vest",  "weight": "2.0",  "protection": "2", "details": "Light cured leather torso armour"},
        {"id": 33, "name": "Mail Shirt",    "weight": "4.0",  "protection": "5", "details": "Medium chainlink torso protection"},
        {"id": 34, "name": "Breastplate",   "weight": "8.0",  "protection": "8", "details": "Heavy steel plate torso protection"},
    ],
    "Hands": [
        {"id": 38, "name": "Leather Gloves",  "weight": "0.8", "protection": "1", "details": "Light leather hand protection"},
        {"id": 39, "name": "Chain Gauntlets", "weight": "1.2", "protection": "2", "details": "Interlinked chain gauntlets"},
        {"id": 40, "name": "Plate Gauntlets", "weight": "1.6", "protection": "3", "details": "Heavy steel plate gauntlets"},
    ],
    "Legs": [
        {"id": 35, "name": "Leather Leggings","weight": "1.6", "protection": "2", "details": "Light leather leg protection"},
        {"id": 36, "name": "Mail Leggings",   "weight": "3.2", "protection": "4", "details": "Chainmail leg protection"},
        {"id": 37, "name": "Plate Leggings",  "weight": "6.4", "protection": "6", "details": "Full steel plate leggings"},
    ],
    "Feet": [
        {"id": 41, "name": "Leather Boots",   "weight": "1.2", "protection": "1", "details": "Standard leather boots"},
        {"id": 42, "name": "Chain Boots",     "weight": "1.6", "protection": "2", "details": "Chainmail foot protection"},
        {"id": 43, "name": "Plate Boots",     "weight": "2.0", "protection": "3", "details": "Heavy steel plate boots"},
        {"id": 47, "name": "Dragonskin Boots","weight": "3.2", "protection": "5", "details": "Rare magical dragonscale boots"},
    ],
    "Right Hand": [
        {"id": 3,  "name": "Dagger",        "weight": "0.8",  "damage": "1-4",  "details": "Slashing / Thrusting weapon"},
        {"id": 4,  "name": "Shortsword",    "weight": "1.6",  "damage": "2-7",  "details": "Slashing / Thrusting weapon"},
        {"id": 5,  "name": "Longsword",     "weight": "2.4",  "damage": "3-12", "details": "Balanced Slashing / Thrusting weapon"},
        {"id": 6,  "name": "Broadsword",    "weight": "3.2",  "damage": "3-11", "details": "Heavy slashing weapon"},
        {"id": 10, "name": "A Shiny Sword", "weight": "3.4",  "damage": "4-15", "details": "High-quality magical blade"},
        {"id": 12, "name": "Black Sword",   "weight": "3.6",  "damage": "5-20", "details": "Rare cursed or enchanted blade"},
        {"id": 13, "name": "Jeweled Sword", "weight": "2.8",  "damage": "3-14", "details": "Ornate gem-encrusted blade"},
        {"id": 0,  "name": "Hand Axe",      "weight": "2.4",  "damage": "2-6",  "details": "Light chopping weapon"},
        {"id": 1,  "name": "Battle Axe",    "weight": "4.0",  "damage": "4-16", "details": "Heavy two-handed executioner axe"},
        {"id": 2,  "name": "Axe",           "weight": "3.2",  "damage": "3-10", "details": "Standard woodcutter axe"},
        {"id": 11, "name": "Jeweled Axe",   "weight": "3.2",  "damage": "4-14", "details": "Ornate ceremonial axe"},
        {"id": 7,  "name": "Cudgel",        "weight": "1.6",  "damage": "1-6",  "details": "Basic wooden bludgeon"},
        {"id": 8,  "name": "Light Mace",    "weight": "2.4",  "damage": "2-7",  "details": "Flanged iron light mace"},
        {"id": 9,  "name": "Mace",          "weight": "3.2",  "damage": "3-10", "details": "Heavy iron crushing mace"},
        {"id": 14, "name": "Jeweled Mace",  "weight": "2.8",  "damage": "3-12", "details": "Ornate ceremonial crushing mace"},
        {"id": 24, "name": "Sling",         "weight": "0.4",  "details": "Simple leather ranged projectile launcher"},
        {"id": 25, "name": "Bow",           "weight": "1.2",  "details": "Standard wooden shortbow"},
        {"id": 26, "name": "Crossbow",      "weight": "2.4",  "details": "Mechanical heavy ranged weapon"},
        {"id": 31, "name": "Jeweled Bow",   "weight": "1.6",  "details": "Enchanted masterwork bow"},
    ],
    "Left Hand": [
        {"id": 62, "name": "Buckler",        "weight": "1.0",  "protection": "1", "details": "Small fast parrying shield"},
        {"id": 61, "name": "Small Shield",   "weight": "2.0",  "protection": "2", "details": "Standard light round shield"},
        {"id": 60, "name": "Wooden Shield",  "weight": "3.0",  "protection": "3", "details": "Medium reinforced wooden shield"},
        {"id": 55, "name": "Shiny Shield",   "weight": "3.0",  "protection": "4", "details": "Polished magical shield"},
        {"id": 59, "name": "Tower Shield",   "weight": "4.0",  "protection": "6", "details": "Massive rectangular plate shield"},
        {"id": 63, "name": "Jeweled Shield", "weight": "2.5",  "protection": "5", "details": "Ornate gem-gilded shield"},
    ],
    "Light Source": [
        {"id": 145, "name": "Lantern",     "weight": "1.0", "details": "Standard portable light source"},
        {"id": 146, "name": "Torch",       "weight": "0.4", "details": "Consumable wooden torch"},
        {"id": 147, "name": "Candle",      "weight": "0.1", "details": "Small wax candle"},
        {"id": 148, "name": "Taper",       "weight": "0.1", "details": "Thin wax taper light"},
        {"id": 149, "name": "Lit Lantern", "weight": "1.0", "details": "Active lantern source"},
        {"id": 150, "name": "Lit Torch",   "weight": "0.4", "details": "Active burning torch"},
        {"id": 151, "name": "Lit Candle",  "weight": "0.1", "details": "Active burning candle"},
    ],
    "Ring": [
        {"id": 54, "name": "Iron Ring",   "weight": "0.1", "details": "Plain iron ring"},
        {"id": 56, "name": "Gold Ring",   "weight": "0.1", "details": "Valuable gold ring"},
        {"id": 57, "name": "Silver Ring", "weight": "0.1", "details": "Silver ring"},
        {"id": 58, "name": "Red Ring",    "weight": "0.1", "details": "Gemmed ring"},
    ],
}

# ---------------------------------------------------------------------------
# API pública
# ---------------------------------------------------------------------------

def object_name(object_type: int, object_name_raw: str = "", type_name: str = "") -> str:
    """
    Retorna o melhor nome disponível para um objeto.

    Prioridade:
      1. objectName do save (se não vazio)
      2. Dicionário interno
      3. objectTypeName do save (se não vazio)
      4. "Object#N"
    """
    if object_name_raw and object_name_raw.strip():
        return object_name_raw.strip()
    entry = _DB.get(object_type)
    if entry:
        return entry["name"]
    if type_name and type_name.strip():
        return type_name.strip()
    return f"Object#{object_type}"


def object_icon(object_type: int, type_name: str = "") -> str:
    """Retorna o ícone unicode para um objectType."""
    entry = _DB.get(object_type)
    if entry:
        return entry["icon"]
    return CATEGORY_ICONS.get(type_name, "·")


def object_category(object_type: int) -> str:
    """Retorna a categoria do objeto, ou 'Unknown'."""
    entry = _DB.get(object_type)
    return entry["category"] if entry else "Unknown"


def object_props(object_type: int) -> dict:
    """
    Retorna propriedades físicas: {"mass": float, "value": int}.
    Retorna zeros se o tipo não estiver no banco.
    """
    entry = _DB.get(object_type, {})
    return {"mass": entry.get("mass", 0.0), "value": entry.get("value", 0)}


def lookup(object_type: int) -> dict:
    """
    Retorna o registro completo do objectType, ou fallback genérico.
    Compatibilidade retroativa com object_dictionary.lookup().
    """
    return _DB.get(object_type, {
        "name":     f"Object#{object_type}",
        "category": "Unknown",
        "icon":     "·",
    })


def all_categories() -> list[str]:
    """Lista de categorias únicas no banco."""
    return sorted({v["category"] for v in _DB.values()})
