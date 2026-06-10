# src/gui/widgets/save_header.py
"""
SaveHeaderFrame — barra de slot + info do save.

Exibe apenas dados do arquivo de save, não do personagem:
  [Slot 0 ▼] [Load]   Loaded: Comeco   Saved: 2026-06-09 22:14
"""
import tkinter as tk
from tkinter import ttk
import logging

logger = logging.getLogger("gui.widgets.save_header")


class SaveHeaderFrame(ttk.Frame):
    """
    Linha superior com slot selector, botão Load e metadados do save.
    Não exibe nenhuma informação do personagem.

    API pública:
        update_from_save(raw_save_data, slot_number)
        clear()
    """

    def __init__(self, parent, on_load=None, **kwargs):
        super().__init__(parent, padding=(8, 6), **kwargs)
        self._on_load = on_load
        self._build()
        self.clear()

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    def update_from_save(self, raw_save_data: dict, slot_number: int) -> None:
        try:
            display = raw_save_data.get("displayName") or raw_save_data.get("slotName", "")
            saved   = raw_save_data.get("savedAtIso", "")
            if isinstance(saved, str) and "T" in saved:
                saved = saved.split("T")[0] + "  " + saved.split("T")[1][:5]

            self._info_lbl.config(
                text=f"Loaded: {display}     Saved: {saved}",
                foreground="#aaa",
            )
        except Exception as e:
            logger.error("Header update error: %s", e)
            self.clear()

    def clear(self) -> None:
        self._info_lbl.config(text="No save loaded", foreground="#555")

    def set_load_command(self, fn) -> None:
        self._load_btn.config(command=fn)

    @property
    def slot_combo(self):
        return self._slot_combo

    # ------------------------------------------------------------------
    # Construção
    # ------------------------------------------------------------------

    def _build(self) -> None:
        ttk.Label(self, text="Save Slot:").pack(side="left", padx=(0, 6))

        self._slot_combo = ttk.Combobox(
            self,
            values=[f"Slot {i}" for i in range(10)],
            state="readonly",
            width=9,
        )
        self._slot_combo.current(0)
        self._slot_combo.pack(side="left")

        self._load_btn = ttk.Button(self, text="Load", width=7)
        self._load_btn.pack(side="left", padx=(6, 20))

        self._info_lbl = ttk.Label(self, text="", font=("Arial", 9))
        self._info_lbl.pack(side="left")

    # ------------------------------------------------------------------
    # Compatibilidade com test_save_header.py
    # ------------------------------------------------------------------

    @staticmethod
    def _get_class_name(class_id: int) -> str:
        from src.gui.constants import UNDERWORLD_CLASSES
        if 0 <= class_id < len(UNDERWORLD_CLASSES):
            return UNDERWORLD_CLASSES[class_id]
        return "Unknown"
