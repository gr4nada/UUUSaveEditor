"""
.tabs/critters/components/__init__.py
Components Package for Critters Tab

Exporta todos os painéis reutilizáveis.
"""
from .critter_model import Critter

from .components.portrait_panel import PortraitPanel
from .components.detail_panel import DetailPanel
from .components.loot_panel import LootPanel
from .components.editor_panel import EditorPanel
from .components.inspector_panel import InspectorPanel   
__all__ = [
    "Critter",
    "PortraitPanel",
    "DetailPanel",
    "LootPanel",
    "EditorPanel",
    "InspectorPanel",
]