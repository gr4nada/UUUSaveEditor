# src/gui/tabs/inventory_tab.py
"""Inventory Tab — Handles player equipment layout and main container inventory."""
import os
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import logging

from src.core.inventory              import (
    get_equipment_summary,
    get_main_inventory_summary,
    set_main_inventory_quantity,
    delete_main_inventory_item,
)
from src.gui.widgets.tooltip     import Tooltip
from src.gui.widgets.icon_loader     import IconLoader, ICON_MEDIUM
from src.gui.constants               import THEME

logger = logging.getLogger("gui.tabs.inventory")

_SLOT_POSITIONS = [
    (80,  60), (243, 60),  (400, 60),
    (80,  160), (243, 150), (400, 160),
    (80,  260), (145, 110), (243, 240),
    (335, 110), (243, 320),
]
_SLOT_NAMES = [
    "Light Source", "Head",   "Neck",
    "Right Hand",   "Chest",  "Left Hand",
    "Gloves",       "Ring 1", "Legs",
    "Ring 2",       "Boots",
]


class InventoryTab(ttk.Frame):
    """
    'Inventory' Tab Component.

    Public API:
        refresh(raw_save_data)      → Redraws asset slots with data mapped from the active save.
        set_on_slot_clicked(fn)     → Injects a listener callback function fn(slot_index).
    """

    def __init__(self, parent: ttk.Notebook) -> None:
        super().__init__(parent, padding=5)
        self._slot_labels:  list[tk.Label]         = []
        self._slot_fill_colors: list[str]          = []
        self._selected_slot: int | None            = None
        self._loader = IconLoader.get_instance()
        self._on_slot_clicked = None
        self._raw_save: dict | None = None
        self._build()

    def set_on_slot_clicked(self, fn) -> None:
        self._on_slot_clicked = fn

    def refresh(self, raw_save_data: dict) -> None:
        self._raw_save = raw_save_data

        equip_summary = get_equipment_summary(raw_save_data)
        for item in equip_summary:
            idx = item["slot_index"]
            lbl = self._slot_labels[idx]
            obj_type = item["objectType"]

            if item["is_empty"] or obj_type == 0:
                lbl.config(image="", text="Empty", bg=THEME["bg_slot_empty"], fg=THEME["fg_slot_empty"],
                           width=9, height=4)
                lbl.image = None
                lbl.unbind("<Enter>"); lbl.unbind("<Leave>")
                self._slot_fill_colors[idx] = THEME["bg_slot_empty"]
            else:
                photo = self._loader.get_item_icon(obj_type, ICON_MEDIUM)
                lbl.config(image=photo, text="", bg=THEME["bg_slot_filled"], width=0, height=0)
                self._slot_fill_colors[idx] = THEME["bg_slot_filled"]
                lbl.image = photo

                enchant = f" | ✦ {item['enchantment']}" if item.get("enchantment") else ""
                name = item["objectName"]
                # Tooltip real — mostra nome e encantamento ao hover
                tip_text = f"{name}{enchant}" if enchant else name
                Tooltip(lbl, tip_text, delay=200)

        for idx, lbl in enumerate(self._slot_labels):
            lbl.bind("<Enter>", lambda e, i=idx: self._on_hover_enter(i), add="+")
            lbl.bind("<Leave>", lambda e, i=idx: self._on_hover_leave(i), add="+")

        self._apply_selection_highlight()
        self._refresh_main_inventory()

    def _build(self) -> None:
        # Sub-notebook for separating Equipped Items from Main Inventory views
        sub_nb = ttk.Notebook(self)
        sub_nb.pack(fill="both", expand=True)

        # — Equipped Items Tab —
        equip_frame = ttk.Frame(sub_nb, padding=5)
        sub_nb.add(equip_frame, text="  Equipped Items  ")
        self._build_equipment_grid(equip_frame)

        # — Main Inventory Tab —
        main_frame = ttk.Frame(sub_nb, padding=8)
        sub_nb.add(main_frame, text="  Main Inventory  ")
        self._build_main_inventory(main_frame)

    def _build_equipment_grid(self, parent: ttk.Frame) -> None:
        canvas = tk.Canvas(parent, width=550, height=420,
                           bg=THEME["bg_canvas"], highlightthickness=1,
                           highlightbackground=THEME["border_canvas"])
        canvas.pack(pady=10)

        canvas.create_rectangle(210, 50, 340, 370,
                                 fill=THEME["bg_avatar_body"],
                                 outline=THEME["border_avatar"])
        canvas.create_text(275, 210, text="AVATAR", fill=THEME["fg_avatar_label"],
                           font=("Arial", 16, "bold"))

        for idx, (x, y) in enumerate(_SLOT_POSITIONS):
            lbl = tk.Label(canvas, bg=THEME["bg_slot_empty"],
                           text="Empty", fg=THEME["fg_slot_empty"],
                           font=("Arial", 7), width=9, height=4,
                           bd=2, relief="groove")
            canvas.create_window(x + 32, y + 32, window=lbl)
            canvas.create_text(x + 32, y - 10, text=_SLOT_NAMES[idx],
                               fill=THEME["fg_slot_label"], font=("Arial", 7, "bold"))
            lbl.bind("<Button-1>", lambda e, slot=idx: self._handle_click(slot))
            self._slot_labels.append(lbl)
            self._slot_fill_colors.append(THEME["bg_slot_empty"])

    def _on_hover_enter(self, idx: int) -> None:
        lbl = self._slot_labels[idx]
        if idx != self._selected_slot:
            lbl.config(bg=THEME["list_select"])

    def _on_hover_leave(self, idx: int) -> None:
        lbl = self._slot_labels[idx]
        if idx != self._selected_slot:
            lbl.config(bg=self._slot_fill_colors[idx])

    def _apply_selection_highlight(self) -> None:
        for idx, lbl in enumerate(self._slot_labels):
            if idx == self._selected_slot:
                lbl.config(relief="solid", bd=2,
                           highlightthickness=2,
                           highlightbackground=THEME["tag_enchanted"],
                           highlightcolor=THEME["tag_enchanted"])
            else:
                lbl.config(relief="groove", bd=2, highlightthickness=0)

    def _handle_click(self, slot_index: int) -> None:
        self._selected_slot = slot_index
        self._apply_selection_highlight()
        if self._on_slot_clicked:
            self._on_slot_clicked(slot_index)

    # ------------------------------------------------------------------
    # Main Inventory
    # ------------------------------------------------------------------

    _MI_COLS = ("name", "type", "qty", "enchant", "contents")
    _MI_COL_CFG = {
        "name":     ("Name",        220, "w"),
        "type":     ("Type",        120, "w"),
        "qty":      ("Qty",          50, "center"),
        "enchant":  ("Enchantment", 150, "w"),
        "contents": ("Contains",    100, "center"),
    }

    def _build_main_inventory(self, parent: ttk.Frame) -> None:
        hint = ttk.Label(
            parent,
            text="Double-click Qty to edit. Containers show item count but their "
                 "contents aren't editable yet.",
            foreground=THEME["fg_muted"], font=("Arial", 9, "italic"))
        hint.pack(anchor="w", pady=(0, 6))

        tree_frame = ttk.Frame(parent)
        tree_frame.pack(fill="both", expand=True)

        self._mi_tree = ttk.Treeview(
            tree_frame, columns=self._MI_COLS, show="headings", selectmode="browse")
        for col in self._MI_COLS:
            label, width, anchor = self._MI_COL_CFG[col]
            self._mi_tree.heading(col, text=label)
            self._mi_tree.column(col, width=width, anchor=anchor)

        sb = ttk.Scrollbar(tree_frame, orient="vertical", command=self._mi_tree.yview)
        self._mi_tree.configure(yscrollcommand=sb.set)
        self._mi_tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        self._mi_tree.bind("<Double-1>", self._on_main_inventory_double_click)

        toolbar = ttk.Frame(parent)
        toolbar.pack(fill="x", pady=(8, 0))
        ttk.Button(toolbar, text="🗑  Delete Selected",
                   command=self._on_main_inventory_delete).pack(side="left")

    def _refresh_main_inventory(self) -> None:
        if not hasattr(self, "_mi_tree"):
            return
        self._mi_tree.delete(*self._mi_tree.get_children())
        if not self._raw_save:
            return

        for item in get_main_inventory_summary(self._raw_save):
            contents = f"{item['contents_count']} items" if item["contents_count"] else ""
            self._mi_tree.insert(
                "", "end", iid=str(item["index"]),
                values=(item["objectName"], item["objectTypeName"],
                        item["quantity"], item["enchantment"], contents))

    def _on_main_inventory_double_click(self, event) -> None:
        if not self._raw_save:
            return
        region = self._mi_tree.identify_region(event.x, event.y)
        col = self._mi_tree.identify_column(event.x)
        row = self._mi_tree.identify_row(event.y)
        if region != "cell" or not row or col != "#3":  # "#3" == qty column
            return
        self._edit_main_inventory_quantity(row)

    def _edit_main_inventory_quantity(self, row_iid: str) -> None:
        bbox = self._mi_tree.bbox(row_iid, "#3")
        if not bbox:
            return
        x, y, w, h = bbox
        current = self._mi_tree.set(row_iid, "qty")

        var = tk.StringVar(value=str(current))
        entry = ttk.Entry(self._mi_tree, textvariable=var, justify="center")
        entry.place(x=x, y=y, width=w, height=h)
        entry.focus_set()
        entry.select_range(0, "end")

        def commit(_event=None) -> None:
            value = var.get()
            entry.destroy()
            try:
                qty = int(value)
            except ValueError:
                messagebox.showerror("Invalid Quantity", "Quantity must be a whole number.")
                return
            if qty < 1:
                qty = 1
            set_main_inventory_quantity(self._raw_save, int(row_iid), qty)
            self._mi_tree.set(row_iid, "qty", qty)

        def cancel(_event=None) -> None:
            entry.destroy()

        entry.bind("<Return>", commit)
        entry.bind("<FocusOut>", commit)
        entry.bind("<Escape>", cancel)

    def _on_main_inventory_delete(self) -> None:
        if not self._raw_save:
            return
        sel = self._mi_tree.selection()
        if not sel:
            return
        row_iid = sel[0]
        name = self._mi_tree.set(row_iid, "name")
        if not messagebox.askyesno("Delete Item", f"Remove '{name}' from the inventory?"):
            return
        delete_main_inventory_item(self._raw_save, int(row_iid))
        self._refresh_main_inventory()
