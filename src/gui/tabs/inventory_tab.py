# src/gui/tabs/inventory_tab.py
"""Inventory Tab — Handles player equipment layout and main container inventory."""
import os
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import logging

from src.core.inventory import get_equipment_summary

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
        self._icon_cache:   dict[int, ImageTk.PhotoImage] = {}
        self._on_slot_clicked = None
        self._build()

    def set_on_slot_clicked(self, fn) -> None:
        self._on_slot_clicked = fn

    def refresh(self, raw_save_data: dict) -> None:
        self._icon_cache.clear()
        equip_summary = get_equipment_summary(raw_save_data)
        for item in equip_summary:
            idx = item["slot_index"]
            lbl = self._slot_labels[idx]
            obj_type = item["objectType"]

            if item["is_empty"] or obj_type == 0:
                lbl.config(image="", text="Empty", bg="#222", fg="#555")
                lbl.image = None
                lbl.unbind("<Enter>"); lbl.unbind("<Leave>")
            else:
                photo = self._load_icon(obj_type)
                lbl.config(image=photo, text="", bg="#1a1a1a")
                lbl.image = photo

                enchant = f" | ✦ {item['enchantment']}" if item.get("enchantment") else ""
                name = item["objectName"]
                lbl.bind("<Enter>", lambda e, n=name, s=enchant:
                         lbl.winfo_toplevel().title(f"Item: {n}{s}"))
                lbl.bind("<Leave>", lambda e:
                         lbl.winfo_toplevel().title("Ultima Underworld Unity - Save Editor"))

    def _build(self) -> None:
        # Sub-notebook for separating Equipped Items from Main Inventory views
        sub_nb = ttk.Notebook(self)
        sub_nb.pack(fill="both", expand=True)

        # — Equipped Items Tab —
        equip_frame = ttk.Frame(sub_nb, padding=5)
        sub_nb.add(equip_frame, text="  Equipped Items  ")
        self._build_equipment_grid(equip_frame)

        # — Main Inventory Tab (Placeholder) —
        main_frame = ttk.Frame(sub_nb, padding=20)
        sub_nb.add(main_frame, text="  Main Inventory  ")
        ttk.Label(main_frame,
                  text="Main inventory editing coming in a future sprint.",
                  foreground="#888", font=("Arial", 10, "italic")).pack(pady=40)

    def _build_equipment_grid(self, parent: ttk.Frame) -> None:
        canvas = tk.Canvas(parent, width=550, height=420,
                           bg="#2b2b2b", highlightthickness=1, highlightbackground="#444")
        canvas.pack(pady=10)

        canvas.create_rectangle(210, 50, 340, 370, fill="#1f1f1f", outline="#555")
        canvas.create_text(275, 210, text="AVATAR", fill="#333",
                           font=("Arial", 16, "bold"))

        for idx, (x, y) in enumerate(_SLOT_POSITIONS):
            canvas.create_window(
                x + 32, y + 32,
                window=tk.Label(canvas, bg="#111", width=9, height=4,
                                bd=2, relief="groove"))
            lbl = tk.Label(canvas, bg="#222", text="Empty", fg="#555",
                           font=("Arial", 7))
            canvas.create_window(x + 32, y + 32, window=lbl)
            canvas.create_text(x + 32, y - 10, text=_SLOT_NAMES[idx],
                               fill="#aaa", font=("Arial", 7, "bold"))
            lbl.bind("<Button-1>", lambda e, slot=idx: self._handle_click(slot))
            self._slot_labels.append(lbl)

    def _handle_click(self, slot_index: int) -> None:
        if self._on_slot_clicked:
            self._on_slot_clicked(slot_index)

    def _load_icon(self, object_type: int) -> ImageTk.PhotoImage:
        if object_type in self._icon_cache:
            return self._icon_cache[object_type]
        path = os.path.join("assets", "icons", f"{object_type}.png")
        size = (44, 44)
        if object_type != 0 and os.path.exists(path):
            try:
                img = Image.open(path).convert("RGBA")
                
                # Sanitize backgrounds: Convert white/near-white pixel layouts into alpha transparent channels
                cleaned = [
                    (0, 0, 0, 0) if p[0] >= 245 and p[1] >= 245 and p[2] >= 245 else p
                    for p in img.getdata()
                ]
                img.putdata(cleaned)
                img.thumbnail(size, Image.Resampling.NEAREST)
                
                # Center-paste sanitized assets onto a transparent canvas square bounding frame
                canvas = Image.new("RGBA", size, (0, 0, 0, 0))
                canvas.paste(img, ((size[0]-img.width)//2, (size[1]-img.height)//2), img)
                photo = ImageTk.PhotoImage(canvas)
                self._icon_cache[object_type] = photo
                return photo
            except Exception as e:
                logger.error("Icon load error %d: %s", object_type, e)
                
        # Generate dark fallback placeholder tile if asset structures fail or map keys are missing
        fallback = ImageTk.PhotoImage(Image.new("RGBA", size, (34, 34, 34, 255)))
        self._icon_cache[object_type] = fallback
        return fallback