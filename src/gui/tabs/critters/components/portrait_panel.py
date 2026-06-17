"""
Portrait Panel Component

Displays the portrait of the selected critter/NPC.
Uses WhoAmI portrait for named NPCs and critter sprite for generic creatures.
"""

import tkinter as tk
from tkinter import ttk
import logging
from typing import Optional

from src.gui.widgets.icon_loader import IconLoader
from src.gui.constants import THEME

logger = logging.getLogger("gui.tabs.critters.portrait")

_PORTRAIT_SIZE = 92


class PortraitPanel(ttk.LabelFrame):
    """
    Painel que exibe o retrato do critter/NPC selecionado.
    Prioriza portrait de WhoAmI para NPCs nomeados.
    """

    def __init__(self, parent):
        super().__init__(parent, text=" Portrait ", padding=8)
        self._loader = IconLoader.get_instance()
        self._portrait_ref = None  # manter referência para evitar GC

        self._build_ui()

    def _build_ui(self) -> None:
        """Constrói a interface do painel de retrato."""
        # Canvas para a imagem
        self._canvas = tk.Canvas(
            self,
            width=_PORTRAIT_SIZE,
            height=_PORTRAIT_SIZE,
            bg=THEME.get("bg_deep", "#1e1e1e"),
            highlightthickness=1,
            highlightbackground=THEME.get("border_deep", "#444444")
        )
        self._canvas.pack(pady=4)

        # Nome abaixo do retrato
        self._name_lbl = ttk.Label(
            self,
            text="—",
            foreground=THEME.get("fg_faint", "#888888"),
            font=("Arial", 8),
            wraplength=_PORTRAIT_SIZE,
            anchor="center"
        )
        self._name_lbl.pack(pady=(4, 0))

        self._draw_placeholder()

    def _draw_placeholder(self) -> None:
        """Desenha placeholder quando não há retrato disponível."""
        self._canvas.delete("all")
        self._canvas.create_rectangle(
            4, 4, _PORTRAIT_SIZE-4, _PORTRAIT_SIZE-4,
            outline=THEME.get("border_placeholder", "#555555"),
            fill=THEME.get("bg_panel", "#2d2d2d")
        )
        self._canvas.create_text(
            _PORTRAIT_SIZE//2,
            _PORTRAIT_SIZE//2,
            text="?",
            fill=THEME.get("fg_placeholder", "#666666"),
            font=("Arial", 36, "bold")
        )

    def update(self, critter: dict) -> None:
        """Atualiza o retrato com base nos dados do critter."""
        self._canvas.delete("all")
        self._portrait_ref = None

        if not critter:
            self._draw_placeholder()
            self._name_lbl.config(text="—")
            return

        whoami_id = critter.get("whoami_id", 0)
        critter_id = critter.get("critter_id") or critter.get("object_type")

        photo = None

        # Prioridade: WhoAmI para NPCs nomeados
        if whoami_id > 0:
            photo = self._loader.get_whoami_portrait(whoami_id, size=(_PORTRAIT_SIZE, _PORTRAIT_SIZE))
        # Fallback: sprite do critter
        elif critter_id is not None:
            photo = self._loader.get_critter_portrait(critter_id, size=(_PORTRAIT_SIZE, _PORTRAIT_SIZE))

        if photo:
            self._portrait_ref = photo
            self._canvas.create_image(
                _PORTRAIT_SIZE // 2,
                _PORTRAIT_SIZE // 2,
                image=photo,
                anchor="center"
            )
        else:
            self._draw_placeholder()

        # Nome exibido
        if whoami_id > 0:
            display_name = critter.get("name", "Unknown NPC")
        else:
            display_name = critter.get("type_name", "Creature")

        self._name_lbl.config(text=display_name)

    def clear(self) -> None:
        """Limpa o painel."""
        self._draw_placeholder()
        self._name_lbl.config(text="—")
        self._portrait_ref = None