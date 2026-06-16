"""
Components Package

Contains all reusable UI panels for the Critters tab.
"""

from .portrait_panel import PortraitPanel
from .detail_panel import DetailPanel
from .loot_panel import LootPanel
from .editor_panel import EditorPanel
from .inspector_panel import InspectorPanel

__all__ = [
    "PortraitPanel",
    "DetailPanel",
    "LootPanel",
    "EditorPanel",
    "InspectorPanel",
]