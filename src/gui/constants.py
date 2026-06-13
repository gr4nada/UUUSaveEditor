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

# ---------------------------------------------------------------------------
# Re-exports do database — fonte única de verdade.
# Mantidos aqui para retrocompatibilidade com qualquer import legado de
# src.gui.constants que ainda não foi migrado.
# ---------------------------------------------------------------------------
from src.core.database.quests   import QUEST_FLAGS, SPELL_DATABASE, SPELL_TABLE, RUNES_LIST
from src.core.database.critters import ATTITUDE_COLORS
from src.core.database.skills   import PLAYER_CLASSES as UNDERWORLD_CLASSES

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