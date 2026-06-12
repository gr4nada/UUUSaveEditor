# src/core/enums.py
import logging
from enum import Enum, IntEnum


logger = logging.getLogger("core.enums")


class EPlayerClass(Enum):
    FIGHTER  = 0;  MAGE     = 1;  BARD     = 2;  TINKER   = 3
    DRUID    = 4;  PALADIN  = 5;  RANGER   = 6;  SHEPHERD = 7


class EAttitude(Enum):
    """Confirmado pelo fixture: 0=107, 1=39, 2=85, 3=38 critters."""
    HOSTILE  = 0;  NEUTRAL  = 1;  FRIENDLY = 2;  ALLY = 3


class EWhoAmI(Enum):
    """EWhoAmI completo extraído da DLL do jogo."""
    Generic = 0; Corby = 1; Shak = 2; Goldthirst = 3; Shanklick = 4
    Eyesnack = 5; Marrowsuck = 6; Ketchaval = 7; Retichall = 8; Vernix = 9
    Lanugo = 10; Thorlson = 11; DornaIronfist = 12; Morlock = 13; DrOwl = 14
    Sseetharee = 15; Ishtass = 16; SetharStrongarm = 17; LakshiLongtooth = 18
    Hagbard = 19; Gulik = 20; Steeltoe = 21; Golem = 22; Judy = 23
    Prisoner = 24; Door = 25; Celaven = 26; Garamon = 27; Zak = 28
    Jaacar = 64; Eb = 65; Drog = 66; Bragit = 67
    Brawnclan = 88; Hewstone = 89; Ironwit = 90; Janus = 91
    Gazer = 110
    Bandit = 112; HeadBandit = 113; Issleek = 114
    Oradinar = 136; Linnet = 137; Derek = 138; Trisch = 139; Ree = 140
    Feznor = 141; Rodrick = 142; Biden = 143; Rawstag = 144
    Doris = 146; Kyle = 147; Cecil = 148; Meredith = 149
    Anjor = 161; Kneenibble = 162
    Delanrey = 184; Nilpont = 185; Folina = 186; Illomo = 187; Gralwart = 188
    Shenilor = 189; Bronus = 190; Ranthru = 191; Fyrgen = 192; Louvnon = 193
    Dominus = 194
    Warren = 207; Cardon = 208; Guard209 = 209; Naruto = 210; Dantes = 211
    Kallistan = 212; Fintor = 213; Bolinard = 214; Smonden = 215; Jailor = 216
    Gurstang = 217; Griffle = 218; Guard219 = 219; Guard220 = 220; Imp = 221
    Guard222 = 222
    Tyball = 231; Carasso = 232; Count = 233;
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

class EObjectType(Enum):
    # ==================== WEAPONS ====================
    HandAxe         = 0
    BattleAxe       = 1
    Axe             = 2
    Dagger          = 3
    Shortsword      = 4
    Longsword       = 5
    Broadsword      = 6
    Cudgel          = 7
    LightMace       = 8
    Mace            = 9
    ShinySword      = 10
    JeweledAxe      = 11
    BlackSword      = 12
    JeweledSword    = 13
    JeweledMace     = 14
    Fist            = 15

    # Projectiles
    SlingStone      = 16
    CrossbowBolt    = 17
    Arrow           = 18
    Stone           = 19

    # Magic Projectiles
    Fireball        = 20
    LightningBolt   = 21
    Acid            = 22
    MagicMissile    = 23

    # Ranged Weapons
    Sling           = 24
    Bow             = 25
    Crossbow        = 26
    Knife           = 27
    JeweledBow      = 31

    # ==================== ARMOR ====================
    LeatherVest     = 32
    MailShirt       = 33
    Breastplate     = 34
    LeatherLeggings = 35
    MailLeggings    = 36
    PlateLeggings   = 37
    LeatherGloves   = 38
    ChainGauntlets  = 39
    PlateGauntlets  = 40
    LeatherBoots    = 41
    ChainBoots      = 42
    PlateBoots      = 43
    LeatherCap      = 44
    ChainCowl       = 45
    Helmet          = 46
    DragonskinBoots = 47

    # Crowns
    CrownA          = 48
    CrownB          = 49
    CrownC          = 50

    # Rings & Shields
    IronRing        = 54
    ShinyShield     = 55
    GoldRing        = 56
    SilverRing      = 57
    RedRing         = 58
    TowerShield     = 59
    WoodenShield    = 60
    SmallShield     = 61
    Buckler         = 62
    JeweledShield   = 63

    # ==================== MONSTERS / CRITTERS ====================
    Rotworm         = 64
    FleshSlug       = 65
    CaveBat         = 66
    GiantRatBrown   = 67
    GiantSpider     = 68
    AcidSlug        = 69
    GoblinA         = 70
    GoblinB         = 71
    GiantRatGrey    = 72
    VampireBat      = 73
    Skeleton        = 74
    Imp             = 75
    GoblinC         = 76
    GoblinD         = 77
    GoblinE         = 78
    GoblinF         = 80
    Mongbat         = 81
    Bloodworm       = 82
    WolfSpider      = 83
    MountainmanA    = 84
    GreenLizardman  = 85
    MountainmanB    = 86
    Lurker          = 87
    RedLizardman    = 88
    GreyLizardman   = 89
    Outcast         = 90
    Headless        = 91
    DreadSpider     = 92
    FighterA        = 93
    FighterB        = 94
    FighterC        = 95
    Troll           = 96
    GhostA          = 97
    FighterD        = 98
    GhoulA          = 99
    GhostB          = 100
    GhostC          = 101
    Gazer           = 102
    MageA           = 103
    FighterE        = 104
    DarkGhoul       = 105
    MageB           = 106
    Sorceress       = 107
    MageD           = 108
    MageE           = 109
    GhoulB          = 110
    FeralTroll      = 111
    GreatTroll      = 112
    DireGhost       = 113
    EarthGolem      = 114
    MageF           = 115
    DeepLurker      = 116
    ShadowBeast     = 117
    Reaper          = 118
    StoneGolem      = 119
    FireElemental   = 120
    MetalGolem      = 121
    Wisp            = 122
    Tyball          = 123
    SlasherOfVeils  = 124
    Avatar          = 127

    # ==================== CONTAINERS ====================
    Sack            = 128
    OpenSack        = 129
    Pack            = 130
    OpenPack        = 131
    Box             = 132
    OpenBox         = 133
    Pouch           = 134
    OpenPouch       = 135
    MapCase         = 136
    OpenMapCase     = 137
    GoldCoffer      = 138
    OpenGoldCoffer  = 139
    Urn             = 140
    Quiver          = 141
    Bowl            = 142
    RuneBag         = 143

    # ==================== LIGHT SOURCES ====================
    Lantern         = 145
    Torch           = 146
    Candle          = 147
    Taper           = 148
    LitLantern      = 149
    LitTorch        = 150
    LitCandle       = 151
    LitTaper        = 152

    # ==================== WANDS ====================
    WandA           = 153
    WandB           = 154
    WandC           = 155
    WandD           = 156
    BrokenWandA     = 157
    BrokenWandB     = 158
    BrokenWandC     = 159
    BrokenWandD     = 160

    # ==================== TREASURES & GEMS ====================
    Coin            = 161
    GoldCoin        = 162
    Ruby            = 163
    RedGem          = 164
    SmallBlueGem    = 165
    LargeBlueGem    = 166
    Sapphire        = 167
    Emerald         = 168
    Amulet          = 169
    Goblet          = 170
    Sceptre         = 171
    GoldChain       = 172
    GoldPlate       = 173
    AnkhPendant     = 174
    ShinyCup        = 175
    LargeGoldNugget = 176

    # ==================== FOOD ====================
    PieceOfMeat     = 177
    LoafOfBreadA    = 178
    PieceOfCheese   = 179
    Apple           = 180
    EarOfCorn       = 181
    LoafOfBreadB    = 182
    Fish            = 183
    Popcorn         = 184
    Mushroom        = 185
    Toadstool       = 186
    BottleOfAle     = 187
    RedPotion       = 188
    GreenPotion     = 189
    BottleOfWater   = 190
    FlaskOfPort     = 191
    BottleOfWine    = 192

    # ==================== KEYS & RUNESTONES ====================
    KeyOfTruth      = 226
    KeyOfLove       = 227
    KeyOfCourage    = 227
    KeyOfInfinity   = 231
    TwoPartKeyTL    = 228
    TwoPartKey      = 229 
    TwoPartKeyB      = 230 
    # Runestones (An, Bet, Corp, ...)
    RunestoneAn     = 233
    RunestoneBet    = 234
    RunestoneCorp   = 235
    # ... (adicione mais conforme necessário)

    # ==================== MISC / UNKNOWN ====================
    Unk28           = 28
    Unk29           = 29
    Unk30           = 30
    Unk51           = 51
    Unk52           = 52
    Unk53           = 53

PROP_ITENS = {
    # === MELEE WEAPONS ===
    0  : {"mass": 2.4, "value": 20},    # Hand Axe
    1  : {"mass": 4.0, "value": 60},    # Battle Axe
    2  : {"mass": 3.2, "value": 100},   # Axe
    3  : {"mass": 0.8, "value": 20},    # Dagger
    4  : {"mass": 1.6, "value": 50},    # Short Sword
    5  : {"mass": 2.4, "value": 80},    # Long Sword
    6  : {"mass": 3.2, "value": 100},   # Broad Sword
    7  : {"mass": 1.6, "value": 15},    # Cudgel
    8  : {"mass": 2.4, "value": 55},    # Light Mace
    9  : {"mass": 3.2, "value": 90},    # Mace
    10 : {"mass": 3.4, "value": 0},     # Shiny Sword (Caliburn)
    11 : {"mass": 3.2, "value": 250},   # Jeweled Axe
    12 : {"mass": 3.6, "value": 200},   # Black Sword
    13 : {"mass": 2.8, "value": 250},   # Jeweled Sword
    14 : {"mass": 2.8, "value": 250},   # Jeweled Mace
    15 : {"mass": 0.0, "value": 0},     # Fist (Mão Nua)

    # === AMMO & PROJECTILES ===
    16 : {"mass": 0.1, "value": 1},     # Sling Stone
    17 : {"mass": 0.2, "value": 4},     # Crossbow Bolt
    18 : {"mass": 0.1, "value": 2},     # Arrow
    19 : {"mass": 0.4, "value": 0},     # Stone
    20 : {"mass": 0.0, "value": 0},     # Fireball spell missile
    21 : {"mass": 0.0, "value": 0},     # Lightning spell missile
    22 : {"mass": 0.0, "value": 0},     # Acid trap projectile
    23 : {"mass": 0.0, "value": 0},     # Magic Missile spell projectile

    # === RANGED WEAPONS ===
    24 : {"mass": 0.4, "value": 10},    # Sling
    25 : {"mass": 1.2, "value": 50},    # Bow
    26 : {"mass": 2.4, "value": 70},    # Crossbow
    27 : {"mass": 0.0, "value": 0},     # Control Slot (Interno)
    28 : {"mass": 0.0, "value": 0},     # Control Slot (Interno)
    29 : {"mass": 0.0, "value": 0},     # Control Slot (Interno)
    30 : {"mass": 0.0, "value": 0},     # Control Slot (Interno)
    31 : {"mass": 1.6, "value": 150},   # Jeweled Bow

    # === ARMOR & WEARABLES ===
    32 : {"mass": 2.0, "value": 20},    # Leather Vest
    33 : {"mass": 4.0, "value": 45},    # Mail Shirt
    34 : {"mass": 8.0, "value": 70},    # Breastplate
    35 : {"mass": 1.6, "value": 15},    # Leather Leggings
    36 : {"mass": 3.2, "value": 35},    # Mail Leggings
    37 : {"mass": 6.4, "value": 60},    # Plate Leggings
    38 : {"mass": 0.8, "value": 10},    # Leather Gloves
    39 : {"mass": 1.2, "value": 20},    # Chain Gauntlets
    40 : {"mass": 1.6, "value": 30},    # Plate Gauntlets
    41 : {"mass": 1.2, "value": 12},    # Leather Boots
    42 : {"mass": 1.6, "value": 25},    # Chain Boots
    43 : {"mass": 2.0, "value": 40},    # Plate Boots
    44 : {"mass": 0.8, "value": 15},    # Leather Cap
    45 : {"mass": 1.2, "value": 30},    # Chain Cowl
    46 : {"mass": 1.6, "value": 50},    # Helmet
    47 : {"mass": 3.2, "value": 150},   # Dragonskin Boots
    48 : {"mass": 0.4, "value": 140},   # Crown (Gold)
    49 : {"mass": 0.4, "value": 120},   # Crown (Silver)
    50 : {"mass": 0.4, "value": 90},    # Crown (Bronze)
    51 : {"mass": 0.0, "value": 0},     # Garment/Amulet Slot Interno
    52 : {"mass": 0.0, "value": 0},     # Garment/Amulet Slot Interno
    53 : {"mass": 0.0, "value": 0},     # Garment/Amulet Slot Interno

    # === SHIELDS & RINGS ===
    54 : {"mass": 0.1, "value": 40},    # Iron Ring
    55 : {"mass": 3.0, "value": 100},   # Shiny Shield
    56 : {"mass": 0.1, "value": 100},   # Gold Ring
    57 : {"mass": 0.1, "value": 70},    # Silver Ring
    58 : {"mass": 0.1, "value": 150},   # Red Ring (Gemmed)
    59 : {"mass": 4.0, "value": 65},    # Tower Shield
    60 : {"mass": 3.0, "value": 30},    # Wooden Shield
    61 : {"mass": 2.0, "value": 20},    # Small Shield
    62 : {"mass": 1.0, "value": 10},    # Buckler
    63 : {"mass": 2.5, "value": 200},   # Jeweled Shield

    # === CONTAINERS ===
    128: {"mass": 0.2, "value": 5},     # Sack (Fechada)
    129: {"mass": 0.2, "value": 5},     # Open Sack
    130: {"mass": 0.4, "value": 15},    # Pack (Mochila)
    131: {"mass": 0.4, "value": 15},    # Open Pack
    132: {"mass": 1.0, "value": 10},    # Box (Baú pequeno)
    133: {"mass": 1.0, "value": 10},    # Open Box
    134: {"mass": 0.1, "value": 3},     # Pouch (Bolsa)
    135: {"mass": 0.1, "value": 3},     # Open Pouch
    136: {"mass": 0.2, "value": 8},     # Map Case
    137: {"mass": 0.2, "value": 8},     # Open Map Case
    138: {"mass": 2.0, "value": 40},    # Gold Coffer (Cofre)
    139: {"mass": 2.0, "value": 40},    # Open Gold Coffer
    140: {"mass": 0.4, "value": 4},     # Urn
    141: {"mass": 0.4, "value": 12},    # Quiver (Aljava)
    142: {"mass": 0.2, "value": 2},     # Bowl
    143: {"mass": 0.2, "value": 25},    # Rune Bag

    # === LIGHT SOURCES ===
    144: {"mass": 1.0, "value": 20},    # Lantern (Unlit)
    145: {"mass": 1.0, "value": 20},    # Lantern (Duplicado)
    146: {"mass": 0.4, "value": 2},     # Torch (Unlit)
    147: {"mass": 0.1, "value": 4},     # Candle (Unlit)
    148: {"mass": 0.1, "value": 1},     # Taper (Vela fina)
    149: {"mass": 1.0, "value": 20},    # Lit Lantern
    150: {"mass": 0.4, "value": 2},     # Lit Torch
    151: {"mass": 0.1, "value": 4},     # Lit Candle
    152: {"mass": 0.1, "value": 1},     # Lit Taper

    # === WANDS ===
    153: {"mass": 0.4, "value": 80},    # Wand A
    154: {"mass": 0.4, "value": 100},   # Wand B
    155: {"mass": 0.4, "value": 150},   # Wand C
    156: {"mass": 0.4, "value": 200},   # Wand D
    157: {"mass": 0.2, "value": 10},    # Broken Wand A
    158: {"mass": 0.2, "value": 10},    # Broken Wand B
    159: {"mass": 0.2, "value": 15},    # Broken Wand C
    160: {"mass": 0.2, "value": 20},    # Broken Wand D

    # === TREASURES & GEMS ===
    161: {"mass": 0.0, "value": 1},     # Coin (Moeda individual)
    162: {"mass": 0.1, "value": 10},    # Gold Nugget/Stack (Moedas)
    163: {"mass": 0.1, "value": 40},    # Ruby
    164: {"mass": 0.1, "value": 25},    # Red Gem
    165: {"mass": 0.1, "value": 15},    # Small Blue Gem
    166: {"mass": 0.2, "value": 60},    # Large Blue Gem
    167: {"mass": 0.1, "value": 50},    # Sapphire
    168: {"mass": 0.1, "value": 45},    # Emerald
    169: {"mass": 0.2, "value": 90},    # Amulet
    170: {"mass": 0.4, "value": 45},    # Goblet (Taça de ouro)
    171: {"mass": 0.8, "value": 120},   # Sceptre
    172: {"mass": 0.2, "value": 75},    # Gold Chain
    173: {"mass": 0.6, "value": 85},    # Gold Plate
    174: {"mass": 0.1, "value": 100},   # Ankh Pendant
    175: {"mass": 0.4, "value": 30},    # Shiny Cup
    176: {"mass": 1.5, "value": 150},   # Large Gold Nugget

    # === FOOD & DRINK ===
    177: {"mass": 0.4, "value": 4},     # Piece of Meat
    178: {"mass": 0.4, "value": 2},     # Loaf of Bread
    179: {"mass": 0.2, "value": 3},     # Piece of Cheese
    180: {"mass": 0.1, "value": 1},     # Apple
    181: {"mass": 0.2, "value": 1},     # Ear of Corn (Milho)
    182: {"mass": 0.4, "value": 2},     # Loaf of Bread B
    183: {"mass": 0.3, "value": 2},     # Fish
    184: {"mass": 0.1, "value": 1},     # Popcorn
    185: {"mass": 0.1, "value": 1},     # Mushroom
    186: {"mass": 0.1, "value": 0},     # Toadstool (Venenoso)
    187: {"mass": 0.6, "value": 3},     # Bottle of Ale
    188: {"mass": 0.4, "value": 25},    # Red Potion
    189: {"mass": 0.4, "value": 25},    # Green Potion
    190: {"mass": 0.5, "value": 1},     # Bottle of Water
    191: {"mass": 0.6, "value": 12},    # Flask of Port
    192: {"mass": 0.6, "value": 8},     # Bottle of Wine

    # === QUEST KEYS & RUNES ===
    226: {"mass": 0.1, "value": 0},     # Key of Truth
    227: {"mass": 0.1, "value": 0},     # Key of Love
    228: {"mass": 0.1, "value": 0},     # Key of Courage
    232: {"mass": 0.1, "value": 0},     # Key of Infinity
    233: {"mass": 0.1, "value": 10},    # Rune: An
    234: {"mass": 0.1, "value": 10},    # Rune: Bet
    235: {"mass": 0.1, "value": 10}     # Rune: Corp
}


class ECritterState(IntEnum):
    """
    Represents the active behavioral execution state of a Critter/NPC AI.
    Mapped from the native 90s Origin Systems AI engine.
    """
    INITIALIZE = 0
    ENABLE = 1
    CROUCH = 2
    IDLE = 3
    FIDGET = 4
    TURN_TO_WANDER = 5
    WANDER = 6
    CONVERSE = 7
    TURN_TO_APPROACH = 8
    APPROACH = 9
    COMBAT_IDLE = 10
    COMBAT_TURN = 11
    ATTACK = 12
    PROJECTILE_IDLE = 13
    PROJECTILE_ATTACK = 14
    TURN_TO_FLEE = 15
    FLEE = 16
    FLINCH = 17
    DIE = 18
    DEAD = 19
    CLEANUP = 20

    @property
    def label(self) -> str:
        """Returns a clean, user-friendly UI string for the state."""
        translations = {
            ECritterState.INITIALIZE: "Initializing",
            ECritterState.ENABLE: "Enabled / Active",
            ECritterState.CROUCH: "Crouching",
            ECritterState.IDLE: "Idling",
            ECritterState.FIDGET: "Fidgeting",
            ECritterState.TURN_TO_WANDER: "Turning to Wander",
            ECritterState.WANDER: "Wandering",
            ECritterState.CONVERSE: "Conversing / Talking",
            ECritterState.TURN_TO_APPROACH: "Turning to Approach",
            ECritterState.APPROACH: "Approaching Target",
            ECritterState.COMBAT_IDLE: "Combat Idle",
            ECritterState.COMBAT_TURN: "Turning in Combat",
            ECritterState.ATTACK: "Attacking (Melee)",
            ECritterState.PROJECTILE_IDLE: "Ranged Combat Idle",
            ECritterState.PROJECTILE_ATTACK: "Attacking (Ranged)",
            ECritterState.TURN_TO_FLEE: "Turning to Flee",
            ECritterState.FLEE: "Fleeing",
            ECritterState.FLINCH: "Flinching / Reeling",
            ECritterState.DIE: "Dying Animation",
            ECritterState.DEAD: "Dead / Corpse State",
            ECritterState.CLEANUP: "Cleaning Up Instance"
        }
        return translations.get(self, f"Unknown State ({self.value})")


class ECritterGoal(IntEnum):
    """
    Represents the high-level objective or agenda assigned to a Critter.
    Cleans up the raw decompiled decompiler suffixes into readable targets.
    """
    STAND_0 = 0
    GO_TO = 1
    WANDER_2 = 2
    FOLLOW_TARGET = 3
    WANDER_4 = 4
    ATTACK_TARGET_5 = 5
    FLEE_TARGET = 6
    STAND_7 = 7
    WANDER_8 = 8
    ATTACK_TARGET_9 = 9
    AWAIT_CONVERSATION = 10
    STAND_11 = 11
    STAND_12  = 12
    STAND_13  = 13
    STAND_14  = 14

    @property
    def label(self) -> str:
        """Maps decompiled identifier tokens into descriptive UI names."""
        translations = {
            ECritterGoal.STAND_0: "Standing Still (Static)",
            ECritterGoal.GO_TO: "Moving to Coordinate",
            ECritterGoal.WANDER_2: "Wandering Area (Type 2)",
            ECritterGoal.FOLLOW_TARGET: "Following / Guarding Target",
            ECritterGoal.WANDER_4: "Patrolling Perimeter (Type 4)",
            ECritterGoal.ATTACK_TARGET_5: "Engaging Target in Combat",
            ECritterGoal.FLEE_TARGET: "Fleeing from Threat",
            ECritterGoal.STAND_7: "Alert Standing (Guard Duty)",
            ECritterGoal.WANDER_8: "Searching Area (Type 8)",
            ECritterGoal.ATTACK_TARGET_9: "Hunting Down Target",
            ECritterGoal.AWAIT_CONVERSATION: "Waiting for Player Chat",
            ECritterGoal.STAND_11: "Passive Standing (Civilian)",
            ECritterGoal.STAND_12: "Sleeping / Inert",
            ECritterGoal.STAND_13: "Standing (Variant 13)",
            ECritterGoal.STAND_14: "Standing (Variant 14)",
        }
        return translations.get(self, f"Unknown Goal ({self.value})")

    @classmethod
    def from_label(cls, ui_text: str):
        """Performs reverse look-up from UI string back to Enum integer value."""
        for item in cls:
            if item.label == ui_text:
                return item
        raise ValueError(f"Invalid UI Label text supplied: {ui_text}")


class ECritterAttitude(IntEnum):
    """Represents the moral disposition of the NPC toward the Avatar."""
    HOSTILE = 0
    UPSET = 1
    MELLOW = 2
    FRIENDLY = 3

    @property
    def label(self) -> str:
        """Returns a professional disposition text for the UI view."""
        translations = {
            ECritterAttitude.HOSTILE: "Hostile (Attack on Sight)",
            ECritterAttitude.UPSET: "Upset / Suspicious",
            ECritterAttitude.MELLOW: "Mellow / Neutral",
            ECritterAttitude.FRIENDLY: "Friendly / Ally"
        }
        return translations.get(self, f"Unknown Attitude ({self.value})")


class EMovementType(IntEnum):
    """Defines the physics locomotion restrictions of the creature archetype."""
    TWILIGHT_ZONE = 0
    WALKING = 1
    FLYING = 2
    SWIMMING = 3
    CREEPING = 4
    CRAWLING = 5


class ETradeResult(IntEnum):
    """Represents the internal state resolution during NPC barter mechanics."""
    UNDEF = 0
    WHAT = 1
    TIRED = 2
    BAD = 3
    NO = 4
    YES = 5


def critter_state_label(state_id: int) -> str:
    """int → label legível de ECritterState."""
    try:
        return ECritterState(state_id).label
    except ValueError:
        return f"State {state_id}"


def critter_goal_label(goal_id: int) -> str:
    """int → label legível de ECritterGoal."""
    try:
        return ECritterGoal(goal_id).label
    except ValueError:
        return f"Goal {goal_id}"


def critter_attitude_label(attitude_id: int) -> str:
    """int → label legível de ECritterAttitude (da DLL)."""
    try:
        return ECritterAttitude(attitude_id).label
    except ValueError:
        return f"Attitude {attitude_id}"


def movement_type_label(movement_id: int) -> str:
    """int → label legível de EMovementType."""
    try:
        return EMovementType(movement_id).name.capitalize()
    except ValueError:
        return f"Move {movement_id}"


def get_object_name(object_id: int) -> str:
    """Retorna o nome do objeto ou 'Unknown#ID' se não mapeado."""
    try:
        return EObjectType(object_id).name
    except ValueError:
        return f"Unknown#{object_id}"


def get_object_type_by_name(name: str) -> int | None:
    """Busca o ID pelo nome (case insensitive)."""
    norm = name.lower().replace(" ", "").replace("_", "")
    for member in EObjectType:
        if norm in member.name.lower() or member.name.lower() in norm:
            return member.value
    return None

def whoami_name(whoami_id: int) -> str:
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

ITEM_TYPE_GROUPS: dict[str, set | None] = {
    "All": None,
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

ITEM_TYPES_SKIP = frozenset({
    "BloodStain", "Decal", "Trigger", "UnderCursorHidden",
    "Bones", "Trap", "Door", "UUObject",
})
