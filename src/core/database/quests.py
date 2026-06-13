# src/core/database/quests.py
"""
Enciclopédia de quests, feitiços e runas do jogo.

Fonte única de verdade para:
  - QUEST_FLAGS     — flags de quest conhecidas pelo editor
  - SPELL_TABLE     — tabela completa de feitiços (círculo, runas)
  - SPELL_DATABASE  — lista simplificada para buscas/filtros
  - RUNES_LIST      — lista das 24 runas do jogo

Anteriormente em:
  - src/gui/constants.py (QUEST_FLAGS, SPELL_DATABASE, SPELL_TABLE, RUNES_LIST)
  - src/core/save_controller.py (importava QUEST_FLAGS de gui.constants)
"""
from __future__ import annotations

# ---------------------------------------------------------------------------
# Quest Flags
# ---------------------------------------------------------------------------

QUEST_FLAGS: list[dict] = [
    {"id":  0, "flag": "MurgoFreed",          "floor": "Lvl 2",  "desc": "Freed the merchant Murgo from the Dwarf prison cells"},
    {"id":  1, "flag": "TalkedToHagbard",     "floor": "Lvl 3",  "desc": "Spoke with Hagbard, leader of the human refugees"},
    {"id":  2, "flag": "MetDrOwl",            "floor": "Lvl 1",  "desc": "Found Dr. Owl to investigate the Talismans location"},
    {"id":  3, "flag": "CanSpeakToKetcheval", "floor": "Lvl 2",  "desc": "Gained clearance to speak with Ketcheval the Miner"},
    {"id":  4, "flag": "GazerKilled",         "floor": "Lvl 2",  "desc": "Defeated the terrifying Gazer blocking the southern mines"},
    {"id":  5, "flag": "ShouldFindTalismans", "floor": "Global", "desc": "Triggered the Grand Quest to recover the 8 Talismans"},
    {"id":  6, "flag": "BefriendedLizardmen", "floor": "Lvl 3",  "desc": "Learned the dialect and made peace with the Lizardmen tribe"},
    {"id":  7, "flag": "ConvoWithMurgo",      "floor": "Lvl 2",  "desc": "Concluded essential secret dialogue options with Murgo"},
    {"id":  8, "flag": "BronusBookGoBoom",    "floor": "Lvl 3",  "desc": "Resolved the sabotage/book delivery quest for Bronus"},
    {"id":  9, "flag": "FindGurstang",        "floor": "Lvl 2",  "desc": "Activated the search tracker for the dwarf Gurstang"},
    {"id": 10, "flag": "WhereIsZak",          "floor": "Lvl 2",  "desc": "Located the exact whereabouts of the blind merchant Zak"},
    {"id": 11, "flag": "RodrickKilled",       "floor": "Lvl 3",  "desc": "Slayed Rodrick, the corrupt Chaos Knight of the fortress"},
    {"id": 32, "flag": "KnightOfCrux",        "floor": "Lvl 5",  "desc": "Became a Knight of the Order of the Crux Gamata"},
    {"id": 36, "flag": "TalismansLeft",       "floor": "Global", "desc": "System tracker for remaining Talismans in the Abyss"},
    {"id": 37, "flag": "Dreams",              "floor": "Global", "desc": "Experienced prophetic dream visions from the Ghost"},
]

# Índice por flag name para lookup O(1)
_QUEST_BY_FLAG: dict[str, dict] = {q["flag"]: q for q in QUEST_FLAGS}
# ID máximo de flag — usado em save/load para dimensionar a lista
QUEST_MAX_ID: int = max(q["id"] for q in QUEST_FLAGS)


def quest_by_flag(flag_name: str) -> dict | None:
    """Retorna o registro de uma flag pelo nome, ou None."""
    return _QUEST_BY_FLAG.get(flag_name)


# ---------------------------------------------------------------------------
# Runas
# ---------------------------------------------------------------------------

RUNES_LIST: list[str] = [
    "An", "Bet", "Corp", "Des", "Ex", "Flam", "Grav", "Hur",
    "In", "Jux", "Kal", "Lor", "Mani", "Nox", "Ort", "Por",
    "Quas", "Rel", "Sanct", "Tym", "Uus", "Vas", "Wis", "Ylem",
]


# ---------------------------------------------------------------------------
# Tabela completa de feitiços (círculo + runas)
# ---------------------------------------------------------------------------

SPELL_TABLE: dict[int, dict] = {
    1:  {"circle": 1, "name": "Light",             "runes": ["In", "Lor"]},
    2:  {"circle": 1, "name": "Resist Blows",      "runes": ["Bet", "In", "Sanct"]},
    3:  {"circle": 1, "name": "Magic Arrow",        "runes": ["Ort", "Jux"],          "type": "Combat"},
    4:  {"circle": 1, "name": "Create Food",        "runes": ["In", "Mani", "Ylem"]},
    5:  {"circle": 1, "name": "Stealth",            "runes": ["Sanct", "Hur"]},
    6:  {"circle": 2, "name": "Leap",               "runes": ["Uus", "Por"]},
    7:  {"circle": 2, "name": "Curse",              "runes": ["An", "Sanct"]},
    8:  {"circle": 2, "name": "Slow Fall",          "runes": ["Rel", "Des", "Por"]},
    9:  {"circle": 2, "name": "Lesser Heal",        "runes": ["In", "Bet", "Mani"]},
    10: {"circle": 2, "name": "Detect Monster",     "runes": ["Wis", "Mani"]},
    11: {"circle": 2, "name": "Cause Fear",         "runes": ["Quas", "Corp"]},
    12: {"circle": 3, "name": "Rune of Warding",    "runes": ["In", "Jux"]},
    13: {"circle": 3, "name": "Speed",              "runes": ["Rel", "Tym", "Por"]},
    14: {"circle": 3, "name": "Conceal",            "runes": ["Bet", "Sanct", "Lor"]},
    15: {"circle": 3, "name": "Night Vision",       "runes": ["Quas", "Lor"]},
    16: {"circle": 3, "name": "Electrical Bolt",    "runes": ["Ort", "Grav"],         "type": "Combat"},
    17: {"circle": 3, "name": "Strengthen Door",    "runes": ["Sanct", "Jux"]},
    18: {"circle": 4, "name": "Thick Skin",         "runes": ["In", "Sanct"]},
    19: {"circle": 4, "name": "Water Walk",         "runes": ["Ylem", "Por"]},
    20: {"circle": 4, "name": "Heal",               "runes": ["In", "Mani"]},
    21: {"circle": 4, "name": "Levitate",           "runes": ["Hur", "Por"]},
    22: {"circle": 4, "name": "Poison",             "runes": ["Nox", "Mani"]},
    23: {"circle": 4, "name": "Flameproof",         "runes": ["Sanct", "Flam"]},
    24: {"circle": 5, "name": "Remove Trap",        "runes": ["An", "Jux"]},
    25: {"circle": 5, "name": "Fireball",           "runes": ["Por", "Flam"],         "type": "Combat"},
    26: {"circle": 5, "name": "Smite Undead",       "runes": ["An", "Corp", "Mani"]},
    27: {"circle": 5, "name": "Name Enchantment",   "runes": ["Ort", "Wis", "Ylem"]},
    28: {"circle": 5, "name": "Missile Protection", "runes": ["Grav", "Sanct", "Por"]},
    29: {"circle": 5, "name": "Open",               "runes": ["Ex", "Ylem"]},
    30: {"circle": 6, "name": "Cure Poison",        "runes": ["An", "Nox"]},
    31: {"circle": 6, "name": "Greater Heal",       "runes": ["Vas", "In", "Mani"]},
    32: {"circle": 6, "name": "Sheet Lightning",    "runes": ["Vas", "Ort", "Grav"]},
    33: {"circle": 6, "name": "Gate Travel",        "runes": ["Vas", "Rel", "Por"]},
    34: {"circle": 6, "name": "Paralyze",           "runes": ["An", "Ex", "Por"]},
    35: {"circle": 6, "name": "Daylight",           "runes": ["Vas", "In", "Lor"]},
    36: {"circle": 7, "name": "Telekinesis",        "runes": ["Ort", "Por", "Ylem"]},
    37: {"circle": 7, "name": "Fly",                "runes": ["Vas", "Hur", "Por"]},
    38: {"circle": 7, "name": "Ally",               "runes": ["In", "Mani", "Rel"]},
    39: {"circle": 7, "name": "Summon Monster",     "runes": ["Kal", "Mani"]},
    40: {"circle": 7, "name": "Invisibility",       "runes": ["Vas", "Sanct", "Lor"]},
    41: {"circle": 7, "name": "Confusion",          "runes": ["Vas", "An", "Wis"]},
    42: {"circle": 8, "name": "Reveal",             "runes": ["Ort", "An", "Quas"]},
    43: {"circle": 8, "name": "Iron Flesh",         "runes": ["In", "Vas", "Sanct"]},
    44: {"circle": 8, "name": "Tremor",             "runes": ["Vas", "Por", "Ylem"]},
    45: {"circle": 8, "name": "Roaming Sight",      "runes": ["Ort", "Por", "Wis"]},
    46: {"circle": 8, "name": "Flame Wind",         "runes": ["Flam", "Hur"]},
    47: {"circle": 8, "name": "Freeze Time",        "runes": ["An", "Tym"]},
    48: {"circle": 8, "name": "Armageddon",         "runes": ["Vas", "Kal", "Corp"]},
    49: {"circle": 0, "name": "Mass Paralyze",      "runes": []},
    50: {"circle": 0, "name": "Acid",               "runes": []},
    51: {"circle": 0, "name": "Local Teleport",     "runes": []},
    52: {"circle": 0, "name": "Mana Boost",         "runes": []},
}

# Lista simplificada para uso em Listbox e filtros de busca
SPELL_DATABASE: list[dict] = [
    {"name": s["name"], "rune": "".join(r[0] for r in s["runes"])}
    for s in SPELL_TABLE.values()
]


def spell_name(spell_id: int) -> str:
    """int → nome do feitiço, ou 'Spell#N'."""
    entry = SPELL_TABLE.get(spell_id)
    return entry["name"] if entry else f"Spell#{spell_id}"


def spells_by_circle(circle: int) -> list[dict]:
    """Retorna todos os feitiços de um círculo específico."""
    return [{"id": sid, **s} for sid, s in SPELL_TABLE.items() if s["circle"] == circle]
