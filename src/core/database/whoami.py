# src/core/database/whoami.py
"""
Registro de identidade de NPCs (whoami → nome).

Fonte única de verdade para EWhoAmI — antes em src/core/enums.py.
Resolve:
    whoami_id (int) → nome legível do NPC
"""
from __future__ import annotations

# ---------------------------------------------------------------------------
# Mapeamento whoami_id → nome do NPC
# Extraído da DLL do jogo (Origin Systems / Looking Glass Studios).
# ---------------------------------------------------------------------------

_WHOAMI_NAMES: dict[int, str] = {
    0:   "Generic",
    1:   "Corby",
    2:   "Shak",
    3:   "Goldthirst",
    4:   "Shanklick",
    5:   "Eyesnack",
    6:   "Marrowsuck",
    7:   "Ketchaval",
    8:   "Retichall",
    9:   "Vernix",
    10:  "Lanugo",
    11:  "Thorlson",
    12:  "Dorna Ironfist",
    13:  "Morlock",
    14:  "Dr. Owl",
    15:  "Sseetharee",
    16:  "Ishtass",
    17:  "Sethar Strongarm",
    18:  "Lakshi Longtooth",
    19:  "Hagbard",
    20:  "Gulik",
    21:  "Steeltoe",
    22:  "Golem",
    23:  "Judy",
    24:  "Prisoner",
    25:  "Door",
    26:  "Celaven",
    27:  "Garamon",
    28:  "Zak",
    64:  "Jaacar",
    65:  "Eb",
    66:  "Drog",
    67:  "Bragit",
    88:  "Brawnclan",
    89:  "Hewstone",
    90:  "Ironwit",
    91:  "Janus",
    110: "Gazer",
    112: "Bandit",
    113: "Head Bandit",
    114: "Issleek",
    136: "Oradinar",
    137: "Linnet",
    138: "Derek",
    139: "Trisch",
    140: "Ree",
    141: "Feznor",
    142: "Rodrick",
    143: "Biden",
    144: "Rawstag",
    146: "Doris",
    147: "Kyle",
    148: "Cecil",
    149: "Meredith",
    161: "Anjor",
    162: "Kneenibble",
    184: "Delanrey",
    185: "Nilpont",
    186: "Folina",
    187: "Illomo",
    188: "Gralwart",
    189: "Shenilor",
    190: "Bronus",
    191: "Ranthru",
    192: "Fyrgen",
    193: "Louvnon",
    194: "Dominus",
    207: "Warren",
    208: "Cardon",
    209: "Guard",
    210: "Naruto",
    211: "Dantes",
    212: "Kallistan",
    213: "Fintor",
    214: "Bolinard",
    215: "Smonden",
    216: "Jailor",
    217: "Gurstang",
    218: "Griffle",
    219: "Guard",
    220: "Guard",
    221: "Imp",
    222: "Guard",
    231: "Tyball",
    232: "Carasso",
    233: "Count",
    988: "Endicott",
    989: "Xoruw",
    990: "Troll Watchingseer",
    991: "Alfred",
    992: "Tom",
    993: "Ossikka",
    994: "Sir Nolant",
    995: "Sir Korianous",
    996: "Corwin",
    997: "Sir Cabirus",
    998: "Almiric",
    999: "Arial",
}

# ---------------------------------------------------------------------------
# API pública
# ---------------------------------------------------------------------------

def npc_name(whoami_id: int) -> str:
    """int → nome do NPC; 'NPC#N' se não mapeado."""
    return _WHOAMI_NAMES.get(whoami_id, f"NPC#{whoami_id}")


def all_npcs() -> list[tuple[int, str]]:
    """Lista de todos os NPCs mapeados como (id, nome), ordenada por id."""
    return sorted(_WHOAMI_NAMES.items())


def find_by_name(name: str) -> int | None:
    """Busca um NPC pelo nome (case-insensitive). Retorna o id ou None."""
    norm = name.strip().lower()
    for wid, wname in _WHOAMI_NAMES.items():
        if wname.lower() == norm:
            return wid
    return None
