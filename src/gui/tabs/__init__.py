"""
Critters Tab Package

Modular implementation of the Critters explorer tab for the Ultima Underworld Save Editor.
├── __init__.py
├── character_tab.py
├── critters_tab.py
├── inventory_tab.py
├── magic_tab.py
├── skills_quests_tab.py         
├── story_tab.py
├── world_objects_tab.py
└── characters/
|   ├── __init__.py
|   ├── critter_model.py
|   ├── filters.py
|   └── components/
|       ├── __init__.py
|       ├── attributes_panel.py
|       ├── dungeon_state_panel.py
|       ├── identity_panel.py
|       ├── progression_panel.py
|       ├── statistics_panel.py
|       └── status_panel.py
└── critters/
|   ├── __init__.py
|   ├── critter_model.py
|   ├── filters.py
|   └── components/
|       ├── __init__.py
|       ├── detail_panel.py
|       ├── editor_panel.py
|       ├── inspector_panel.py
|       ├── loot_panel.py
|       └── portrait_panel.py
├── common/
│   ├── __init__.py
│   └── base_tab.py   
└── critters/
|   ├── __init__.py
|   ├── critter_model.py
|   ├── filters.py
|   └── components/
|       ├── __init__.py
|       ├── detail_panel.py
|       ├── editor_panel.py
|       ├── inspector_panel.py
|       ├── loot_panel.py
|       └── portrait_panel.py
└── magics/
|   ├── __init__.py
|   ├── magic_model.py
|   └── components/
|       ├── __init__.py
|       ├── Runes_panel.py
|       └── Spell_panel.py
└── stories/
    ├── __init__.py
    ├── story_model.py
    ├── filters.py
    └── components/
        ├── __init__.py
        ├── game_state_panel.py
        ├── plot_flags_panel.py
        └── map_notes_panel.py
"""

from .critters_tab import CrittersTab

__all__ = ["CrittersTab"]
