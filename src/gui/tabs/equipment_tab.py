# src/gui/tabs/equipment_tab.py
import tkinter as tk
from tkinter import ttk
from src.gui.icon_loader import IconLoader

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

_DEFAULT_WINDOW_TITLE = "Ultima Underworld Unity - Save Editor"


class EquipmentTab(ttk.Frame):
    """
    Aba 'Equipped Items'.

    Recebe on_slot_clicked como callback — não importa dialogs diretamente.

    API pública:
        refresh_equipment_ui(equip_summary)  — redesenha os slots com novos dados
    """

    def __init__(self, parent: ttk.Notebook, icon_loader: IconLoader,
                 on_slot_clicked=None) -> None:
        super().__init__(parent, padding=10)
        self._icon_loader    = icon_loader
        self._on_slot_clicked = on_slot_clicked   # Callable[[int], None] | None
        self._slot_labels: list[tk.Label] = []
        self._create_widgets()

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    def refresh_equipment_ui(self, equip_summary: list[dict]) -> None:
        """Atualiza o grid com a lista vinda de get_equipment_summary()."""
        for item in equip_summary:
            idx = item["slot_index"]
            lbl = self._slot_labels[idx]
            obj_type = item["objectType"]

            if item["is_empty"] or obj_type == 0:
                lbl.config(image="", text="Empty", bg="#222")
                lbl.image = None
                lbl.unbind("<Enter>")
                lbl.unbind("<Leave>")
            else:
                photo = self._icon_loader.load_slot_icon(obj_type)
                lbl.config(image=photo, text="", bg="#1a1a1a")
                lbl.image = photo  # referência forte — não remover

                enchant_suffix = f" | Magic: {item['enchantment']}" if item.get("enchantment") else ""
                item_name = item["objectName"]

                lbl.bind("<Enter>", lambda e, lbl=lbl, n=item_name, s=enchant_suffix:
                         lbl.winfo_toplevel().title(f"Item: {n}{s}"))
                lbl.bind("<Leave>", lambda e, lbl=lbl:
                         lbl.winfo_toplevel().title(_DEFAULT_WINDOW_TITLE))

    # ------------------------------------------------------------------
    # Construção interna
    # ------------------------------------------------------------------

    def _create_widgets(self) -> None:
        canvas = tk.Canvas(self, width=550, height=400, bg="#2b2b2b",
                           highlightthickness=1, highlightbackground="#444")
        canvas.pack(pady=20)

        canvas.create_rectangle(210, 50, 340, 350, fill="#1f1f1f", outline="#555")
        canvas.create_text(275, 200, text="AVATAR", fill="#444", font=("Arial", 16, "bold"))

        for idx, (x, y) in enumerate(_SLOT_POSITIONS):
            canvas.create_window(
                x + 32, y + 32,
                window=tk.Label(canvas, bg="#111", width=9, height=4, bd=2, relief="groove"),
            )
            lbl = tk.Label(canvas, bg="#222", text="Empty", fg="#666")
            canvas.create_window(x + 32, y + 32, window=lbl)
            canvas.create_text(x + 32, y - 10, text=_SLOT_NAMES[idx],
                               fill="#bbb", font=("Arial", 8, "bold"))
            lbl.bind("<Button-1>", lambda e, slot=idx: self._handle_click(slot))
            self._slot_labels.append(lbl)

    def _handle_click(self, slot_index: int) -> None:
        if self._on_slot_clicked:
            self._on_slot_clicked(slot_index)
