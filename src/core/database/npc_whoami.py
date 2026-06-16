# src/core/database/npc_whoami.py
"""
Mapping of critter_id -> monster sprite type.

Complements whoami.py (whoami_id -> unique NPC name).
This module resolves the other side: which sprite/animation
is associated with each critter slot in the game engine.

Source: OBJECTS_CRITTER table from UWXtract (GOG version) and
        animations at https://wiki.ultimacodex.com/wiki/Category:Ultima_Underworld_Animations

ID relationships
----------------
  object_slot  = critter_id + 64    (slots 64..127 in OBJECTS.DAT)
  critter_id   = object_slot - 64   (0..63, animation index)
  npc_whoami   = per-instance save field (0..255, determines name/portrait/conversation)

For generic monsters (npc_whoami == 0) the portrait uses the critter_id:
    assets/npc_whoami/{critter_id}.gif   <- Uw1.critter{critter_id}.idlespin.gif from the wiki

For unique NPCs (npc_whoami > 0) the portrait uses the whoami_id:
    assets/WhoAmI/{whoami_id}.png        <- extracted from genhead.gr / whoami.py

How to get missing portraits
-----------------------------
  Download from:  https://wiki.ultimacodex.com/wiki/File:Uw1.critter{N}.idlespin.gif
  Save as:        assets/npc_whoami/{N}.gif
  (icon_loader._find_whoami_path already tries .png then .gif)
"""
from __future__ import annotations
import os

# ---------------------------------------------------------------------------
# critter_id (0..63) -> monster type name
# Source: OBJECTS_CRITTER.csv / wiki technical table.
# object_slot = critter_id + 64  (e.g. critter 0 = slot 64 = Rotworm)
# ---------------------------------------------------------------------------

_CRITTER_NAMES: dict[int, str] = {
    0:  "Rotworm",
    1:  "Flesh Slug",
    2:  "Cave Bat",
    3:  "Giant Rat",
    4:  "Giant Spider",
    5:  "Acid Slug",
    6:  "Goblin",           # green, variant A
    7:  "Goblin",           # green, variant B
    8:  "Giant Rat",        # stronger variant
    9:  "Vampire Bat",
    10: "Skeleton",
    11: "Imp",
    12: "Goblin",           # gray, variant A
    13: "Goblin",           # gray, variant B
    14: "Goblin",           # gray, variant C
    15: "Ethereal Void Creature",
    16: "Goblin",           # gray, variant D
    17: "Mongbat",
    18: "Bloodworm",
    19: "Wolf Spider",
    20: "Mountainman",
    21: "Green Lizardman",
    22: "Mountainman",      # stronger variant
    23: "Lurker",
    24: "Red Lizardman",
    25: "Gray Lizardman",
    26: "Outcast",
    27: "Headless",
    28: "Dread Spider",
    29: "Fighter",          # knight variant A
    30: "Fighter",          # knight variant B
    31: "Fighter",          # knight variant C
    32: "Troll",
    33: "Ghost",
    34: "Fighter",          # knight variant D
    35: "Ghoul",
    36: "Ghost",            # stronger variant
    37: "Ghost",            # ethereal variant
    38: "Gazer",
    39: "Mage",             # variant A
    40: "Fighter",          # knight variant E
    41: "Dark Ghoul",
    42: "Mage",             # variant B
    43: "Mage",             # variant C
    44: "Mage",             # variant D
    45: "Mage",             # variant E
    46: "Ghoul",            # stronger variant
    47: "Feral Troll",
    48: "Great Troll",
    49: "Dire Ghost",
    50: "Earth Golem",
    51: "Mage",             # high-level
    52: "Deep Lurker",
    53: "Shadow Beast",
    54: "Reaper",
    55: "Stone Golem",
    56: "Fire Elemental",
    57: "Metal Golem",
    58: "Wisp",
    59: "Tyball",           # boss (sprite slot)
    60: "Slasher of Veils", # final boss
    61: "Ethereal Void Creature",
    62: "Ethereal Void Creature",
    63: "Adventurer",       # player character slot
}

# Directory for monster portraits (critter_id -> generic sprite)
_NPC_WHOAMI_DIR = os.path.join("assets", "npc_whoami")

# ---------------------------------------------------------------------------
# Which critter_ids already have a local portrait in assets/npc_whoami/
# (0..28 collected manually; 29..63 still to be downloaded from the wiki)
# ---------------------------------------------------------------------------

_CRITTERS_WITH_LOCAL_PORTRAIT: frozenset[int] = frozenset(range(0, 29))

# Base URL to download missing GIFs:
# https://wiki.ultimacodex.com/wiki/File:Uw1.critter{N}.idlespin.gif
# Save as: assets/npc_whoami/{N}.gif

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def critter_name(critter_id: int) -> str:
    """critter_id (0-63) -> monster type name; 'Critter#N' if unmapped."""
    return _CRITTER_NAMES.get(critter_id, f"Critter#{critter_id}")


def object_slot_to_critter_id(object_slot: int) -> int:
    """Convert object_slot (64-127) to critter_id (0-63)."""
    if not (64 <= object_slot <= 127):
        raise ValueError(f"object_slot out of critter range: {object_slot}")
    return object_slot - 64


def critter_id_to_object_slot(critter_id: int) -> int:
    """Convert critter_id (0-63) to object_slot (64-127)."""
    if not (0 <= critter_id <= 63):
        raise ValueError(f"critter_id out of range: {critter_id}")
    return critter_id + 64


def has_local_portrait(critter_id: int) -> bool:
    """True if assets/npc_whoami/{critter_id}.png/gif exists locally."""
    return critter_id in _CRITTERS_WITH_LOCAL_PORTRAIT


def portrait_path(critter_id: int) -> str:
    """
    Expected relative path for this critter_id's portrait.
    Does not check whether the file exists — use icon_loader for that.
    No extension; loader tries .png then .gif.
    """
    return os.path.join(_NPC_WHOAMI_DIR, str(critter_id))


def wiki_gif_url(critter_id: int) -> str:
    """
    Wiki page URL for the animation GIF of this critter_id.
    Save the downloaded file as: assets/npc_whoami/{critter_id}.gif
    """
    return (
        f"https://wiki.ultimacodex.com/wiki/"
        f"File:Uw1.critter{critter_id}.idlespin.gif"
    )


def missing_portraits() -> list[tuple[int, str]]:
    """
    List of (critter_id, name) whose local portrait does not yet exist.
    Sorted by critter_id.
    """
    return [
        (cid, name)
        for cid, name in sorted(_CRITTER_NAMES.items())
        if not has_local_portrait(cid)
    ]


def all_critters() -> list[tuple[int, str]]:
    """All mapped critters as (critter_id, name), sorted by id."""
    return sorted(_CRITTER_NAMES.items())
