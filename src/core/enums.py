# src/core/enums.py
import logging
from enum import Enum

logger = logging.getLogger("core.enums")


class EPlayerClass(Enum):
    FIGHTER  = 0
    MAGE     = 1
    BARD     = 2
    TINKER   = 3
    DRUID    = 4
    PALADIN  = 5
    RANGER   = 6
    SHEPHERD = 7


class EAttitude(Enum):
    """
    Atitudes dos critters — confirmadas pelos dados do save.
    0=107 critters (Hostile), 1=39 (Neutral), 2=85 (Friendly), 3=38 (Ally)
    """
    HOSTILE  = 0
    NEUTRAL  = 1
    FRIENDLY = 2
    ALLY     = 3


class EWhoAmI(Enum):
    """
    Mapeamento whoami int → nome do NPC.
    Extraído da DLL do jogo (EWhoAmI C# enum).
    whoami=0 é genérico (critter sem identidade nomeada).
    """
    Generic        = 0
    Corby          = 1
    Shak           = 2
    Goldthirst     = 3
    Shanklick      = 4
    Eyesnack       = 5
    Marrowsuck     = 6
    Ketchaval      = 7
    Retichall      = 8
    Vernix         = 9
    Lanugo         = 10
    Thorlson       = 11
    DornaIronfist  = 12
    Morlock        = 13
    DrOwl          = 14
    Sseetharee     = 15
    Ishtass        = 16
    SetharStrongarm = 17
    LakshiLongtooth = 18
    Hagbard        = 19
    Gulik          = 20
    Steeltoe       = 21
    Golem          = 22
    Judy           = 23
    Prisoner       = 24
    Door           = 25
    Celaven        = 26
    Garamon        = 27
    Zak            = 28
    Jaacar         = 64
    Eb             = 65
    Drog           = 66
    Bragit         = 67
    Brawnclan      = 88
    Hewstone       = 89
    Ironwit        = 90
    Janus          = 91
    Gazer          = 110
    Bandit         = 112
    HeadBandit     = 113
    Issleek        = 114
    Oradinar       = 136
    Linnet         = 137
    Derek          = 138
    Trisch         = 139
    Ree            = 140
    Feznor         = 141
    Rodrick        = 142
    Biden          = 143
    Rawstag        = 144
    Doris          = 146
    Kyle           = 147
    Cecil          = 148
    Meredith       = 149
    Anjor          = 161
    Kneenibble     = 162
    Delanrey       = 184
    Nilpont        = 185
    Folina         = 186
    Illomo         = 187
    Gralwart       = 188
    Shenilor       = 189
    Bronus         = 190
    Ranthru        = 191
    Fyrgen         = 192
    Louvnon        = 193
    Dominus        = 194
    Warren         = 207
    Cardon         = 208
    Guard209       = 209
    Naruto         = 210
    Dantes         = 211
    Kallistan      = 212
    Fintor         = 213
    Bolinard       = 214
    Smonden        = 215
    Jailor         = 216
    Gurstang       = 217
    Griffle        = 218
    Guard219       = 219
    Guard220       = 220
    Imp            = 221
    Guard222       = 222
    Tyball         = 231
    Carasso        = 232
    Count          = 233
    Endicott       = 988
    Xoruw          = 989
    TrollWhatchingseer = 990
    Alfred         = 991
    Tom            = 992
    Ossikka        = 993
    Sir_Nolant     = 994
    Sir_Korianous  = 995
    Corwin         = 996
    Sir_Cabirus    = 997
    Almiric        = 998
    Arial          = 999


def whoami_name(whoami_id: int) -> str:
    """int → nome do NPC; 'NPC#N' se não mapeado."""
    try:
        return EWhoAmI(whoami_id).name
    except ValueError:
        return f"NPC#{whoami_id}"


def attitude_label(attitude_id: int) -> str:
    try:
        return EAttitude(attitude_id).name.capitalize()
    except ValueError:
        return f"Att{attitude_id}"


NOMES_SKILLS = [
    "Attack", "Defense", "Unarmed", "Sword", "Axe", "Mace", "Missile",
    "Mana", "Lore", "Casting", "Traps", "Search", "Track", "Sneak",
    "Repair", "Charm", "Pickpocket", "Acrobat", "Appraise", "Swimming",
]

# Grupos de tipos de objetos para o explorer World Objects
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
    "Other":      {"Portable", "Ring", "Amulet"},
}

# Tipos excluídos do explorer (decoração, física, etc.)
ITEM_TYPES_SKIP = frozenset({
    "BloodStain", "Decal", "Trigger", "UnderCursorHidden",
    "Bones", "Trap", "Door", "UUObject",
})
