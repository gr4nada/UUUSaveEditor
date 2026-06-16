"""
Loot Panel Component

Displays the loot/inventory of the selected critter with icons.
"""

import tkinter as tk
from tkinter import ttk
from src.gui.widgets.icon_loader import IconLoader, ICON_SMALL
from src.gui.constants import THEME


class LootPanel(ttk.LabelFrame):
    """
    Shows loot items of the selected critter.
    """

    def __init__(self, parent):
        super().__init__(parent, text=" Loot ", padding=4)
        self._loader = IconLoader.get_instance()
        self._icons = []
        self._build()

    def _build(self) -> None:
        vsb = ttk.Scrollbar(self, orient="vertical")
        vsb.pack(side="right", fill="y")

        self._tree = ttk.Treeview(
            self, columns=("name", "qty", "enchant"),
            show="tree headings", height=5,
            yscrollcommand=vsb.set)
        vsb.config(command=self._tree.yview)
        self._tree.pack(fill="both", expand=True)

        self._tree.heading("#0", text="")
        self._tree.column("#0", width=28, stretch=False)

        for col, text, width in [
            ("name", "Item", 160),
            ("qty", "Qty", 40),
            ("enchant", "Enchant", 120)
        ]:
            self._tree.heading(col, text=text)
            self._tree.column(col, width=width, anchor="w" if col == "name" else "center")

        self._tree.tag_configure("ench", foreground=THEME["tag_enchanted"])

    def update(self, critter: dict) -> None:
        """Update loot display."""
        self._tree.delete(*self._tree.get_children())
        self._icons.clear()

        loot = critter.get("loot", [])
        if not loot:
            self._tree.insert("", "end", values=("— empty —", "", ""))
            return

        for item in loot:
            photo = self._loader.get_item_icon(
                item.get("object_type", 0), size=ICON_SMALL)
            self._icons.append(photo)

            tags = ("ench",) if item.get("enchantment") else ()
            self._tree.insert("", "end", image=photo or "", values=(
                item.get("name", "Unknown"),
                item.get("quantity", 0),
                item.get("enchantment", "")
            ), tags=tags)