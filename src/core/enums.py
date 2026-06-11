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

class EObjectType(Enum):
    """
    Mapeamento EObjectType int → nome do objeto/item.
    Extraído diretamente do enum C# da DLL do jogo (Unity Port).
    """
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
    KeyOfCourage    = 228
    KeyOfInfinity   = 232
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