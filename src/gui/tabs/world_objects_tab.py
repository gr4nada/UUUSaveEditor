# src/gui/tabs/world_objects_tab.py

import tkinter as tk
from tkinter import ttk


class WorldObjectsTab(ttk.Frame):
    """
    'World Objects' Tab Component — Read-only placeholder layout.

    Displays data entity structures and size counts for worldObjects, 
    worldObjectsByLevel, and mapData clusters. Full edit support arrives in Sprint 5.
    """

    def __init__(self, parent: ttk.Notebook) -> None:
        super().__init__(parent, padding=20)
        self._labels: dict[str, ttk.Label] = {}
        self._build()

    def load(self, save_game) -> None:
        wo  = save_game.world_objects
        md  = save_game.map_data
        inv = save_game.inventory_data
        wo_by_level = save_game.raw.get("worldObjectsByLevel", {})

        self._labels["wo_count"].config(
            text=f"{len(wo):,} objects", foreground="#fff")
        self._labels["map_keys"].config(
            text=f"{len(md)} keys", foreground="#fff")
        self._labels["level"].config(
            text=str(save_game.current_level), foreground="#fff")
        self._labels["wo_by_level"].config(
            text=f"{len(wo_by_level)} level(s) cached", foreground="#fff")

        main_inv = inv.get("mainInventory", [])
        self._labels["main_inv"].config(
            text=f"{len(main_inv)} item(s)", foreground="#fff")

    def _build(self) -> None:
        notice = ttk.Label(
            self,
            text="✦  World Objects editing coming in Sprint 5.  This tab is currently informational.",
            foreground="#888", font=("Arial", 9, "italic"))
        notice.pack(pady=(5, 20))

        card = ttk.LabelFrame(self, text=" Save World State ", padding=20)
        card.pack(anchor="n", padx=40, pady=10, fill="x")

        rows = [
            ("wo_count",    "World Objects:"),
            ("wo_by_level", "Objects by Level:"),
            ("map_keys",    "Map Data:"),
            ("main_inv",    "Main Inventory:"),
            ("level",       "Current Level:"),
        ]
        for row_idx, (key, label) in enumerate(rows):
            ttk.Label(card, text=label, width=22, anchor="e").grid(
                row=row_idx, column=0, sticky="e", pady=6, padx=(0, 10))
            lbl = ttk.Label(card, text="—", foreground="#888")
            lbl.grid(row=row_idx, column=1, sticky="w", pady=6)
            self._labels[key] = lbl