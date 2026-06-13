# src/gui/constants.py
import logging

logger = logging.getLogger("gui.constants")

# ---------------------------------------------------------------------------
# THEME — fonte única de verdade para todas as cores da interface.
#
# Agrupamentos semânticos:
#   bg_*      → fundos de superfície
#   border_*  → bordas e highlights de canvas
#   fg_*      → texto e ícones
#   list_*    → backgrounds de Listbox / Treeview
#   tag_*     → foreground de tags semânticas (status, raridade, atitude)
#   canvas_*  → elementos desenhados em tk.Canvas
# ---------------------------------------------------------------------------
THEME: dict[str, str] = {
    # --- Superfícies ---
    "bg_app":         "#252525",   # fundo principal da janela / TFrame / TLabelframe
    "bg_deep":        "#0d0d0d",   # canvases de portrait e paper doll
    "bg_panel":       "#111111",   # painéis de texto rico (Summary, Detail)
    "bg_canvas":      "#2b2b2b",   # canvas de equipamentos
    "bg_avatar_body": "#1f1f1f",   # retângulo central do avatar no canvas
    "bg_slot_empty":  "#222222",   # slot vazio de equipamento
    "bg_slot_filled": "#1a1a1a",   # slot preenchido de equipamento
    "bg_slot_shadow": "#111111",   # placeholder de fundo atrás do slot

    # --- Listbox / Treeview ---
    "list_bg":         "#1e1e1e",  # fundo padrão de Listbox
    "list_bg_spells":  "#1a1a2e",  # listbox de feitiços conhecidos (tom azulado)
    "list_bg_active":  "#1a2e1a",  # listbox de feitiços ativos (tom esverdeado)
    "list_row_even":   "#1a1a1a",  # linhas pares do Treeview
    "list_row_odd":    "#141414",  # linhas ímpares do Treeview
    "list_select":     "#264f78",  # seleção de Listbox / Treeview

    # --- Bordas e highlights ---
    "border_canvas":   "#444444",  # borda do canvas de equipamentos
    "border_subtle":   "#2a2a2a",  # highlight de canvases de portrait
    "border_deep":     "#222222",  # highlight de canvases escuros (critters portrait)
    "border_avatar":   "#555555",  # outline do retângulo do avatar
    "border_placeholder": "#1e1e1e",  # outline do placeholder de portrait

    # --- Texto primário / interface ---
    "fg_primary":      "#ffffff",  # texto em destaque (nome do personagem)
    "fg_secondary":    "#aaaaaa",  # texto informativo (save header, info labels)
    "fg_muted":        "#888888",  # texto secundário / hints
    "fg_dim":          "#666666",  # texto desabilitado / itálico explicativo
    "fg_faint":        "#555555",  # texto quase invisível (count labels, empty slots)
    "fg_dead":         "#444444",  # texto de critters mortos / read-only hints
    "fg_placeholder":  "#2a2a2a",  # texto de placeholder em canvases escuros

    # --- Cores de UI temática ---
    "fg_avatar_label": "#333333",  # texto "AVATAR" no canvas
    "fg_slot_label":   "#aaaaaa",  # nome do slot no canvas de equipamentos
    "fg_slot_empty":   "#555555",  # texto "Empty" nos slots
    "fg_labelframe":   "#777777",  # label dos LabelFrames (TLabelframe.Label)
    "fg_stat_value":   "#cccccc",  # valores de estatísticas carregados
    "fg_dungeon":      "#888888",  # dungeon level (read-only)
    "fg_class":        "#aaaaff",  # classe do personagem (preview lateral)
    "fg_level":        "#888888",  # level/dungeon no preview lateral

    # --- Cores semânticas de jogo ---
    "tag_enchanted":   "#d4af37",  # itens encantados (dourado)
    "tag_quest_on":    "#4ec9b0",  # quest flag ativa (verde-azulado)
    "tag_quest_off":   "#888888",  # quest flag inativa
    "tag_spell_known": "#aaaaff",  # feitiço conhecido (azul claro)
    "tag_spell_active":"#88ff88",  # feitiço ativo (verde claro)
    "tag_summary_hdr": "#ffffff",  # cabeçalho de seção no Summary
    "tag_summary_val": "#4ec9b0",  # valor no Summary
    "tag_summary_sep": "#666666",  # separador no Summary
    "tag_detail_key":  "#555555",  # chave no Detail panel dos critters
    "tag_detail_val":  "#dddddd",  # valor no Detail panel dos critters
    "tag_move":        "#4d96ff",  # tipo de movimento (azul)
    "tag_goal":        "#c586c0",  # goal dos critters (roxo)
    "tag_state":       "#9cdcfe",  # state dos critters (azul claro)
    "tag_mouse_primed":"#ffffff",  # mouse-primed spell (branco)
    "tag_spells_none": "#666666",  # "none active" na magic tab

    # --- Atitudes dos critters ---
    "attitude_hostile":  "#ff6b6b",  # Hostile  — vermelho
    "attitude_upset":    "#ff9944",  # Upset    — laranja
    "attitude_mellow":   "#ffd93d",  # Mellow   — amarelo
    "attitude_friendly": "#6bcb77",  # Friendly — verde

    # --- Dialogs ---
    "dialog_spell_fg": "#107c10",  # texto de feitiços na dialog de equipamentos
}

# Mapa de atitude → chave de tema (usado em critters_tab e enums)
ATTITUDE_COLORS: dict[int, str] = {
    0: THEME["attitude_hostile"],
    1: THEME["attitude_upset"],
    2: THEME["attitude_mellow"],
    3: THEME["attitude_friendly"],
}

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

# src/core/constants_magic.py

SPELL_TABLE = {
    1: {"circle": 1, "name": "Light", "runes": ["In", "Lor"]},
    2: {"circle": 1, "name": "Resist Blows", "runes": ["Bet", "In", "Sanct"]},
    3: {"circle": 1, "name": "Magic Arrow", "runes": ["Ort", "Jux"], "type": "Combat"},
    4: {"circle": 1, "name": "Create Food", "runes": ["In", "Mani", "Ylem"]},
    5: {"circle": 1, "name": "Stealth", "runes": ["Sanct", "Hur"]},
    6: {"circle": 2, "name": "Leap", "runes": ["Uus", "Por"]},
    7: {"circle": 2, "name": "Curse", "runes": ["An", "Sanct"]},
    8: {"circle": 2, "name": "Slow Fall", "runes": ["Rel", "Des", "Por"]},
    9: {"circle": 2, "name": "Lesser Heal", "runes": ["In", "Bet", "Mani"]},
    10: {"circle": 2, "name": "Detect Monster", "runes": ["Wis", "Mani"]},
    11: {"circle": 2, "name": "Cause Fear", "runes": ["Quas", "Corp"]},
    12: {"circle": 3, "name": "Rune of Warding", "runes": ["In", "Jux"]},
    13: {"circle": 3, "name": "Speed", "runes": ["Rel", "Tym", "Por"]},
    14: {"circle": 3, "name": "Conceal", "runes": ["Bet", "Sanct", "Lor"]},
    15: {"circle": 3, "name": "Night Vision", "runes": ["Quas", "Lor"]},
    16: {"circle": 3, "name": "Electrical Bolt", "runes": ["Ort", "Grav"], "type": "Combat"},
    17: {"circle": 3, "name": "Strengthen Door", "runes": ["Sanct", "Jux"]},
    18: {"circle": 4, "name": "Thick Skin", "runes": ["In", "Sanct"]},
    19: {"circle": 4, "name": "Water Walk", "runes": ["Ylem", "Por"]},
    20: {"circle": 4, "name": "Heal", "runes": ["In", "Mani"]},
    21: {"circle": 4, "name": "Levitate", "runes": ["Hur", "Por"]},
    22: {"circle": 4, "name": "Poison", "runes": ["Nox", "Mani"]},
    23: {"circle": 4, "name": "Flameproof", "runes": ["Sanct", "Flam"]},
    24: {"circle": 5, "name": "Remove Trap", "runes": ["An", "Jux"]},
    25: {"circle": 5, "name": "Fireball", "runes": ["Por", "Flam"], "type": "Combat"},
    26: {"circle": 5, "name": "Smite Undead", "runes": ["An", "Corp", "Mani"]},
    27: {"circle": 5, "name": "Name Enchantment", "runes": ["Ort", "Wis", "Ylem"]},
    28: {"circle": 5, "name": "Missile Protection", "runes": ["Grav", "Sanct", "Por"]},
    29: {"circle": 5, "name": "Open", "runes": ["Ex", "Ylem"]},
    30: {"circle": 6, "name": "Cure Poison", "runes": ["An", "Nox"]},
    31: {"circle": 6, "name": "Greater Heal", "runes": ["Vas", "In", "Mani"]},
    32: {"circle": 6, "name": "Sheet Lightning", "runes": ["Vas", "Ort", "Grav"]},
    33: {"circle": 6, "name": "Gate Travel", "runes": ["Vas", "Rel", "Por"]},
    34: {"circle": 6, "name": "Paralyze", "runes": ["An", "Ex", "Por"]},
    35: {"circle": 6, "name": "Daylight", "runes": ["Vas", "In", "Lor"]},
    36: {"circle": 7, "name": "Telekinesis", "runes": ["Ort", "Por", "Ylem"]},
    37: {"circle": 7, "name": "Fly", "runes": ["Vas", "Hur", "Por"]},
    38: {"circle": 7, "name": "Ally", "runes": ["In", "Mani", "Rel"]},
    39: {"circle": 7, "name": "Summon Monster", "runes": ["Kal", "Mani"]},
    40: {"circle": 7, "name": "Invisibility", "runes": ["Vas", "Sanct", "Lor"]},
    41: {"circle": 7, "name": "Confusion", "runes": ["Vas", "An", "Wis"]},
    42: {"circle": 8, "name": "Reveal", "runes": ["Ort", "An", "Quas"]},
    43: {"circle": 8, "name": "Iron Flesh", "runes": ["In", "Vas", "Sanct"]},
    44: {"circle": 8, "name": "Tremor", "runes": ["Vas", "Por", "Ylem"]},
    45: {"circle": 8, "name": "Roaming Sight", "runes": ["Ort", "Por", "Wis"]},
    46: {"circle": 8, "name": "Flame Wind", "runes": ["Flam", "Hur"]},
    47: {"circle": 8, "name": "Freeze Time", "runes": ["An", "Tym"]},
    48: {"circle": 8, "name": "Armageddon", "runes": ["Vas", "Kal", "Corp"]},
    49: {"circle": 0, "name": "Mass Paralyze", "runes": []},
    50: {"circle": 0, "name": "Acid", "runes": []},
    51: {"circle": 0, "name": "Local Teleport", "runes": []},
    52: {"circle": 0, "name": "Mana Boost", "runes": []},
}

# Lista única de todas as 24 Runas do jogo para renderizar caixas de seleção (Checkboxes)
RUNES_LIST = [
    "An", "Bet", "Corp", "Des", "Ex", "Flam", "Grav", "Hur",
    "In", "Jux", "Kal", "Lor", "Mani", "Nox", "Ort", "Por",
    "Quas", "Rel", "Sanct", "Tym", "Uus", "Vas", "Wis", "Ylem"
]

ITEM_ID_TO_SPRITE_BASE = {
    32: 0,   # Leather Vest -> Começa no 000
    33: 1,   # Mail Shirt   -> Começa no 001
    34: 2,   # Breastplate  -> Começa no 002
    35: 3,   # Leather Leggings -> 003
    36: 4,   # Mail Leggings    -> 004
    37: 5,   # Plate Leggings   -> 005
    38: 6,   # Leather Gloves   -> 006
    39: 7,   # Chain Gauntlets  -> 007
    40: 8,   # Plate Gauntlets  -> 008
    41: 9,   # Leather Boots    -> 009
    42: 10,  # Chain Boots      -> 010
    43: 11,  # Plate Boots      -> 011
    44: 12,  # Leather Cap      -> 012
    45: 13,  # Chain Cowl       -> 013
    46: 14,  # Helmet           -> 014
    # Itens Especiais (Ignoram o multiplicador de qualidade)
    47: 61,  # Crown            -> Sprite 061
}

OFFSETS_MALE = {
    "head":    (44, 3),   
    "chest":   (27, 53),  
    "legs":    (49,62),  
    "hands":   (22, 120),  
    "feet":    (40,210), 
}

OFFSETS_FEMALE = {
    "head":    (44, 4),   
    "chest":   (27, 53),  
    "legs":    (49,62),  
    "hands":   (22, 121),  
    "feet":    (40, 209), 
}

ITEM_ID_TO_PART_TYPE = {
    32: "chest", 33: "chest", 34: "chest",
    35: "legs",  36: "legs",  37: "legs",
    38: "hands", 39: "hands", 40: "hands",
    41: "feet",  42: "feet",  43: "feet",
    44: "head",  45: "head",  46: "head", 47: "feet", 48:"head",49:"head",
}