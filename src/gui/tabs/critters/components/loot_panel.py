"""
Loot Panel Component

Displays the loot/inventory of the selected critter with icons and enchantment info.
"""

import tkinter as tk
from tkinter import ttk
import logging
from typing import List

from src.gui.widgets.icon_loader import IconLoader, ICON_SMALL
from src.gui.constants import THEME

logger = logging.getLogger("gui.tabs.critters.loot")


class LootPanel(ttk.LabelFrame):
    """
    Painel que exibe o loot/inventário do critter selecionado,
    com ícones e informações de encantamento.
    """

    def __init__(self, parent):
        super().__init__(parent, text=" Loot / Inventory ", padding=6)
        self._loader = IconLoader.get_instance()
        self._icons: List[tk.PhotoImage] = []  # keep references to prevent GC
        self._build_ui()

    def _build_ui(self) -> None:
        """Constrói a interface do painel de loot."""
        # Scrollbar
        vsb = ttk.Scrollbar(self, orient="vertical")
        vsb.pack(side="right", fill="y")

        # Treeview
        self._tree = ttk.Treeview(
            self,
            columns=("name", "qty", "enchant"),
            show="tree headings",
            height=6,
            yscrollcommand=vsb.set,
            selectmode="none"  # Apenas visualização por enquanto
        )
        vsb.config(command=self._tree.yview)
        self._tree.pack(fill="both", expand=True)

        # Configurar colunas
        self._tree.heading("#0", text="")
        self._tree.column("#0", width=32, stretch=False)   # espaço para ícone

        self._tree.heading("name", text="Item")
        self._tree.heading("qty", text="Qty")
        self._tree.heading("enchant", text="Enchantment")

        self._tree.column("name", width=170, anchor="w")
        self._tree.column("qty", width=50, anchor="center")
        self._tree.column("enchant", width=130, anchor="w")

        # Tag para itens encantados
        self._tree.tag_configure("enchanted", foreground=THEME.get("tag_enchanted", "#ffd700"))

    def update(self, critter: dict) -> None:
        """Atualiza o painel com o loot do critter selecionado."""
        # Limpa itens anteriores
        self._tree.delete(*self._tree.get_children())
        self._icons.clear()

        loot_list: list = critter.get("loot", [])

        if not loot_list:
            self._tree.insert("", "end", values=("", "— empty —", ""))
            return

        for item in loot_list:
            obj_type = item.get("object_type", 0)
            name = item.get("name", "Unknown Item")
            quantity = item.get("quantity", 1)
            enchantment = item.get("enchantment", "")

            # Carrega ícone
            photo = self._loader.get_item_icon(obj_type, size=ICON_SMALL)
            self._icons.append(photo)  # manter referência

            tags = ("enchanted",) if enchantment else ()

            self._tree.insert(
                "", 
                "end", 
                image=photo or "", 
                values=(name, quantity, enchantment),
                tags=tags
            )

    def clear(self) -> None:
        """Limpa o painel."""
        self._tree.delete(*self._tree.get_children())
        self._icons.clear()
        self._tree.insert("", "end", values=("", "— no loot —", ""))