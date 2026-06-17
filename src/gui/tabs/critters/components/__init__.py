"""
Components Package for Critters Tab

Exporta todos os painéis reutilizáveis.
"""

from .portrait_panel import PortraitPanel
from .detail_panel import DetailPanel
from .loot_panel import LootPanel
from .editor_panel import EditorPanel
from .inspector_panel import InspectorPanel   # ← nome do arquivo + nome da classe

__all__ = [
    "PortraitPanel",
    "DetailPanel",
    "LootPanel",
    "EditorPanel",
    "InspectorPanel",
]