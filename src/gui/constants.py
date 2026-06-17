# src/gui/constants.py
import logging

logger = logging.getLogger("gui.constants")

# ---------------------------------------------------------------------------
# THEME — single source of truth for all interface colors.
#
# Semantic groupings:
#   bg_*      → surface backgrounds
#   border_*  → canvas borders and highlights
#   fg_*      → text and icons
#   list_*    → Listbox / Treeview backgrounds
#   tag_*     → semantic tag foreground (status, rarity, attitude)
#   canvas_*  → elements drawn on tk.Canvas
# ---------------------------------------------------------------------------
THEME: dict[str, str] = {
    # --- Surfaces ---
    "bg_app":         "#252525",   # main window / TFrame / TLabelframe background
    "bg_deep":        "#0d0d0d",   # portrait and paper doll canvases
    "bg_panel":       "#111111",   # rich text panels (Summary, Detail)
    "bg_canvas":      "#2b2b2b",   # equipment canvas
    "bg_avatar_body": "#1f1f1f",   # central avatar rectangle on canvas
    "bg_slot_empty":  "#222222",   # empty equipment slot
    "bg_slot_filled": "#1a1a1a",   # filled equipment slot
    "bg_slot_shadow": "#111111",   # background placeholder behind slot

    # --- Listbox / Treeview ---
    "list_bg":         "#1e1e1e",  # default Listbox background
    "list_bg_spells":  "#1a1a2e",  # known spells listbox (bluish tone)
    "list_bg_active":  "#1a2e1a",  # active spells listbox (greenish tone)
    "list_row_even":   "#1a1a1a",  # even Treeview rows
    "list_row_odd":    "#141414",  # odd Treeview rows
    "list_select":     "#264f78",  # Listbox / Treeview selection

    # --- Borders and highlights ---
    "border_canvas":   "#444444",  # equipment canvas border
    "border_subtle":   "#2a2a2a",  # portrait canvas highlight
    "border_deep":     "#222222",  # dark canvas highlight (critter portrait)
    "border_avatar":   "#555555",  # avatar rectangle outline
    "border_placeholder": "#1e1e1e",  # portrait placeholder outline

    # --- Primary text / interface ---
    "fg_primary":      "#ffffff",  # highlighted text (character name)
    "fg_secondary":    "#aaaaaa",  # informational text (save header, info labels)
    "fg_muted":        "#888888",  # secondary text / hints
    "fg_dim":          "#666666",  # disabled text / italic explanatory
    "fg_faint":        "#555555",  # almost invisible text (count labels, empty slots)
    "fg_dead":         "#444444",  # dead critter text / read-only hints
    "fg_placeholder":  "#2a2a2a",  # placeholder text on dark canvases

    # --- Thematic UI colors ---
    "fg_avatar_label": "#333333",  # "AVATAR" text on canvas
    "fg_slot_label":   "#aaaaaa",  # slot name on equipment canvas
    "fg_slot_empty":   "#555555",  # "Empty" text on slots
    "fg_labelframe":   "#777777",  # LabelFrame label (TLabelframe.Label)
    "fg_stat_value":   "#cccccc",  # loaded statistics values
    "fg_dungeon":      "#888888",  # dungeon level (read-only)
    "fg_class":        "#aaaaff",  # character class (side preview)
    "fg_level":        "#888888",  # level/dungeon on side preview

    # --- Game semantic colors ---
    "tag_enchanted":   "#d4af37",  # enchanted items (gold)
    "tag_quest_on":    "#4ec9b0",  # active quest flag (teal-green)
    "tag_quest_off":   "#888888",  # inactive quest flag
    "tag_spell_known": "#aaaaff",  # known spell (light blue)
    "tag_spell_active":"#88ff88",  # active spell (light green)
    "tag_summary_hdr": "#ffffff",  # section header in Summary
    "tag_summary_val": "#4ec9b0",  # value in Summary
    "tag_summary_sep": "#666666",  # separator in Summary
    "tag_detail_key":  "#555555",  # key in critter Detail panel
    "tag_detail_val":  "#dddddd",  # value in critter Detail panel
    "tag_move":        "#4d96ff",  # movement type (blue)
    "tag_goal":        "#c586c0",  # critter goal (purple)
    "tag_state":       "#9cdcfe",  # critter state (light blue)
    "tag_mouse_primed":"#ffffff",  # mouse-primed spell (white)
    "tag_spells_none": "#666666",  # "none active" in magic tab

    # --- Critter attitudes ---
    "attitude_hostile":  "#ff6b6b",  # Hostile  — red
    "attitude_upset":    "#ff9944",  # Upset    — orange
    "attitude_mellow":   "#ffd93d",  # Mellow   — yellow
    "attitude_friendly": "#6bcb77",  # Friendly — green

    # --- Dialogs ---
    "dialog_spell_fg": "#107c10",  # spell text in equipment dialog
}

# ---------------------------------------------------------------------------
# Re-exports from database — single source of truth.
# Kept here for backward compatibility with any legacy imports from
# src.gui.constants that have not yet been migrated.
# ---------------------------------------------------------------------------
from src.core.database.quests   import QUEST_FLAGS, SPELL_DATABASE, SPELL_TABLE, RUNES_LIST
from src.core.database.critters import ATTITUDE_COLORS
from src.core.database.skills   import PLAYER_CLASSES as UNDERWORLD_CLASSES

ITEM_ID_TO_SPRITE_BASE = {
    32: 0,   # Leather Vest -> Starts at 000
    33: 1,   # Mail Shirt   -> Starts at 001
    34: 2,   # Breastplate  -> Starts at 002
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
    # Special Items (Ignore quality multiplier)
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