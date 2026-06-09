# src/gui/constants.py
import logging

logger = logging.getLogger("gui.constants")

UNDERWORLD_CLASSES = ["Fighter", "Mage", "Bard", "Tinker", "Druid", "Paladin", "Ranger", "Shepherd"]

QUEST_FLAGS = [
    {"id": 0,  "flag": "MurgoFreed",           "floor": "Lvl 2", "desc": "Freed the merchant Murgo from the Dwarf prison cells"},
    {"id": 1,  "flag": "TalkedToHagbard",      "floor": "Lvl 3", "desc": "Spoke with Hagbard, leader of the human refugees"},
    {"id": 2,  "flag": "MetDrOwl",             "floor": "Lvl 1", "desc": "Found Dr. Owl to investigate the Talismans location"},
    {"id": 3,  "flag": "CanSpeakToKetcheval",  "floor": "Lvl 2", "desc": "Gained clearance to speak with Ketcheval the Miner"},
    {"id": 4,  "flag": "GazerKilled",          "floor": "Lvl 2", "desc": "Defeated the terrifying Gazer blocking the southern mines"},
    {"id": 5,  "flag": "ShouldFindTalismans",  "floor": "Global", "desc": "Triggered the Grand Quest to recover the 8 Talismans"},
    {"id": 6,  "flag": "BefriendedLizardmen",  "floor": "Lvl 3", "desc": "Learned the dialect and made peace with the Lizardmen tribe"},
    {"id": 7,  "flag": "ConvoWithMurgo",       "floor": "Lvl 2", "desc": "Concluded essential secret dialogue options with Murgo"},
    {"id": 8,  "flag": "BronusBookGoBoom",     "floor": "Lvl 3", "desc": "Resolved the sabotage/book delivery quest for Bronus"},
    {"id": 9,  "flag": "FindGurstang",         "floor": "Lvl 2", "desc": "Activated the search tracker for the dwarf Gurstang"},
    {"id": 10, "flag": "WhereIsZak",           "floor": "Lvl 2", "desc": "Located the exact whereabouts of the blind merchant Zak"},
    {"id": 11, "flag": "RodrickKilled",        "floor": "Lvl 3", "desc": "Slayed Rodrick, the corrup Chaos Knight of the fortress"},
    {"id": 32, "flag": "KnightOfCrux",         "floor": "Lvl 5", "desc": "Became a Knight of the Order of the Crux Gamata"},
    {"id": 36, "flag": "TalismansLeft",        "floor": "Global", "desc": "System tracker for remaining Talismans in the Abyss"},
    {"id": 37, "flag": "Dreams",               "floor": "Global", "desc": "Experienced prophetic dream visions from the Ghost"}
]

SPELL_DATABASE = [
    {"name": "Create Food", "rune": "IMY"}, {"name": "Leap", "rune": "UP"},
    {"name": "Light", "rune": "IL"}, {"name": "Magic Arrow", "rune": "OJ"},
    {"name": "Resist Blows", "rune": "BIS"}, {"name": "Stealth", "rune": "SH"},
    {"name": "Create Fear", "rune": "QC"}, {"name": "Curse", "rune": "AS"},
    {"name": "Detect Monster", "rune": "WM"}, {"name": "Lesser Heal", "rune": "IBM"},
    {"name": "Rune of Warding", "rune": "IJ"}, {"name": "Slow Fall", "rune": "RDP"},
    {"name": "Conceal", "rune": "BSL"}, {"name": "Lightning", "rune": "OG"},
    {"name": "Night Vision", "rune": "QL"}, {"name": "Speed", "rune": "RTP"},
    {"name": "Strengthen Door", "rune": "SJ"}, {"name": "Thick Skin", "rune": "IS"},
    {"name": "Flameproof", "rune": "SF"}, {"name": "Heal", "rune": "IM"},
    {"name": "Poison", "rune": "NM"}, {"name": "Remove Trap", "rune": "AJ"},
    {"name": "Water Walk", "rune": "YP"}, {"name": "Cure Poison", "rune": "AN"},
    {"name": "Fireball", "rune": "PF"}, {"name": "Levitate", "rune": "HP"},
    {"name": "Missile Protection", "rune": "GSP"}, {"name": "Name Enchantment", "rune": "OWY"},
    {"name": "Open", "rune": "EY"}, {"name": "Smite Undead", "rune": "ACM"},
    {"name": "Daylight", "rune": "VIL"}, {"name": "Gate Travel", "rune": "VRP"},
    {"name": "Greater Heal", "rune": "VIM"}, {"name": "Paralyze", "rune": "AEP"},
    {"name": "Sheet Lightning", "rune": "VOG"}, {"name": "Telekinesis", "rune": "OPY"},
    {"name": "Ally", "rune": "IMR"}, {"name": "Fly", "rune": "VHP"},
    {"name": "Invisibility", "rune": "VSL"}, {"name": "Confusion", "rune": "VAW"},
    {"name": "Reveal", "rune": "OAQ"}, {"name": "Summon Monster", "rune": "KM"},
    {"name": "Armageddon", "rune": "VKC"}, {"name": "Flame Wind", "rune": "FH"},
    {"name": "Freeze Time", "rune": "AT"}, {"name": "Iron Flesh", "rune": "IVS"},
    {"name": "Roaming Sight", "rune": "OPW"}, {"name": "Tremor", "rune": "VPY"},
    {"name": "Cursed", "rune": ""}, {"name": "Mana Regeneration", "rune": ""},
    {"name": "Regeneration", "rune": ""}, {"name": "Poison Resistance", "rune": ""},
    {"name": "Acid", "rune": "ZZZ"}
]