"""
Portrait Panel Component

Displays the portrait image of the selected critter (WhoAmI for named NPCs
or sprite for generic creatures).
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional

from src.gui.widgets.icon_loader import IconLoader
from src.gui.constants import THEME

_PORTRAIT_W, _PORTRAIT_H = 80, 80


class PortraitPanel(ttk.LabelFrame):
    """
    Panel showing the portrait of the currently selected critter.
    """

    def __init__(self, parent):
        super().__init__(parent, text=" Portrait ", padding=4)
        self._loader = IconLoader.get_instance()
        self._portrait_ref = None

        self._build()

    def _build(self) -> None:
        self._canvas = tk.Canvas(
            self, width=_PORTRAIT_W, height=_PORTRAIT_H,
            bg=THEME["bg_deep"], highlightthickness=1,
            highlightbackground=THEME["border_deep"])
        self._canvas.pack()

        self._name_lbl = ttk.Label(
            self, text="—", foreground=THEME["fg_faint"],
            font=("Arial", 7), wraplength=_PORTRAIT_W, anchor="center")
        self._name_lbl.pack(pady=(2, 0))

        self._draw_placeholder()

    def _draw_placeholder(self) -> None:
        """Draw placeholder when no portrait is available."""
        self._canvas.delete("all")
        w, h = _PORTRAIT_W, _PORTRAIT_H
        self._canvas.create_rectangle(
            2, 2, w-2, h-2,
            outline=THEME["border_placeholder"], fill=THEME["bg_panel"])
        self._canvas.create_text(
            w//2, h//2, text="?", fill=THEME["fg_placeholder"],
            font=("Arial", 28, "bold"))

    def update_portrait(self, critter: dict) -> None:
        """Update portrait based on critter data."""
        self._canvas.delete("all")
        self._portrait_ref = None

        whoami_id = critter.get("whoami_id", 0)
        critter_id = critter.get("critter_id")

        photo = None
        size = (_PORTRAIT_W, _PORTRAIT_H)

        if whoami_id > 0:
            photo = self._loader.get_whoami_portrait(whoami_id, size=size)
        elif critter_id is not None:
            photo = self._loader.get_critter_portrait(critter_id, size=size)

        if photo:
            self._portrait_ref = photo
            cx, cy = _PORTRAIT_W // 2, _PORTRAIT_H // 2
            self._canvas.create_image(cx, cy, image=photo, anchor="center")
        else:
            self._draw_placeholder()

        name = critter.get("name") if whoami_id > 0 else critter.get("type_name", "—")
        self._name_lbl.config(text=name)