import logging
from enum import Enum

logger = logging.getLogger("core.enums")

class EPlayerClass(Enum):
    FIGHTER = 0
    MAGE = 1
    BARD = 2
    TINKER = 3
    DRUID = 4
    PALADIN = 5
    RANGER = 6
    SHEPHERD = 7

class EAttitude(Enum):
    HOSTILE = 0
    NEUTRAL = 1
    FRIENDLY = 2

class EObjectType(Enum):
    NPC_HUMAN = 64
    NPC_GOBLIN_GREEN = 65
    NPC_GOBLIN_GRAY = 66
    NPC_DWARF = 67
    NPC_LIZARDMAN = 68
    NPC_GHOST = 69
    NPC_GHOUL = 70
    NPC_MOUNTAIN_MEN = 71
    NPC_KNIGHTS = 72
    NPC_WIZARDS = 73

class EWhoAmI(Enum):
    None_NPC = 0
    Corby = 1
    Shak = 2
    Goldthirst = 3
    Shanklick = 4
    Eyesnack = 5
    Marrowsuck = 6
    Ketchaval = 7
    Retichall = 8
    Vernix = 9
    Thorlson = 11
    DornaIronfist = 12
    Garamon = 27
    Tyball = 231

NOMES_SKILLS = [
    "Attack", "Defense", "Unarmed", "Sword", "Axe", "Mace", "Missile", 
    "Mana", "Lore", "Casting", "Traps","Search", "Track","Sneak", "Repair", "Charm", 
    "Pickpocket", "Acrobat", "Appraise", "Swimming", 
]