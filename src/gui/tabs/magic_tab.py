# src/gui/tabs/magic_tab.py
"""Magic Tab — Reads and edits magicData.castSpells (known spells)."""
import tkinter as tk
from tkinter import ttk
from src.gui.constants import THEME, SPELL_TABLE

class MagicTab(ttk.Frame):
    """
    'Magic' Tab — Renders global magicData properties and lets the user
    toggle which spells the character knows (magicData.castSpells).

    Public API:
        load(player)   → Refreshes the visual frame hierarchy with updated states.
        get_spells()   → list[bool], the updated castSpells array (index i == SPELL_TABLE[i+1]).
    """

    def __init__(self, parent: ttk.Notebook) -> None:
        super().__init__(parent, padding=20)
        self._spell_rows: list[tuple] = []
        self._spell_vars: dict[int, tk.BooleanVar] = {}  # 0-based castSpells index -> var
        self._cast_spells_len: int = 0
        self._build()

    def load(self, player) -> None:
        magic = player.magic_data
        cast_spells = magic.get("castSpells", [])
        active_spells = magic.get("activeSpells", [])

        self._cast_spells_len = len(cast_spells)

        valid_active_count = sum(1 for s in active_spells if isinstance(s, dict))

        # Spells Known reflects the live checkbox state once loaded
        known_count = sum(1 for v in cast_spells if v)
        self._cast_count_lbl.config(
            text=f"{known_count} spells known",
            foreground=THEME["tag_spell_known"])

        self._active_count_lbl.config(
            text=f"{valid_active_count} active" if valid_active_count else "None active",
            foreground=THEME["tag_spell_active"] if valid_active_count else THEME["tag_spells_none"])

        self._mouse_primed_lbl.config(
            text="YES" if magic.get("hasMousePrimedSpell") else "NO",
            foreground=THEME["tag_mouse_primed"])

        # Populate known-spells checkbox grid from castSpells
        self._spell_vars.clear()
        for widget in self._spell_grid.winfo_children():
            widget.destroy()

        for i, known in enumerate(cast_spells):
            spell_id = i + 1
            spell = SPELL_TABLE.get(spell_id)
            if spell is None:
                continue

            var = tk.BooleanVar(value=bool(known))
            self._spell_vars[i] = var

            row = ttk.Frame(self._spell_grid)
            row.pack(fill="x", anchor="w")

            cb = ttk.Checkbutton(row, variable=var, command=self._refresh_known_count)
            cb.pack(side="left")

            runes = " ".join(spell.get("runes", [])) or "—"
            label = f"{spell['name']:<22} (Circle {spell['circle']:>2})  {runes}"
            ttk.Label(row, text=label, foreground=THEME["tag_spell_known"],
                      font=("Consolas", 9)).pack(side="left", padx=(4, 0))

        # Populate active baseline spell nodes (read-only)
        self._active_listbox.delete(0, tk.END)
        for spell in active_spells:
            if not isinstance(spell, dict):
                continue
            name = spell.get("spellName", spell.get("name", "Unknown"))
            self._active_listbox.insert(tk.END, f"  {name}")

    def get_spells(self) -> list[bool]:
        """Returns the updated castSpells boolean array, preserving original length."""
        result = [False] * self._cast_spells_len
        for i, var in self._spell_vars.items():
            if 0 <= i < self._cast_spells_len:
                result[i] = var.get()
        return result

    def _refresh_known_count(self) -> None:
        known_count = sum(1 for var in self._spell_vars.values() if var.get())
        self._cast_count_lbl.config(
            text=f"{known_count} spells known",
            foreground=THEME["tag_spell_known"])

    def _build(self) -> None:
        notice = ttk.Label(
            self,
            text="✦  Toggle the spells this character knows. Active spell effects are read-only.",
            foreground=THEME["fg_muted"], font=("Arial", 9, "italic"))
        notice.pack(pady=(5, 15))

        top = ttk.Frame(self)
        top.pack(fill="x", padx=20)

        # — Summary cards —
        summary = ttk.LabelFrame(top, text=" Magic Summary ", padding=12)
        summary.pack(side="left", fill="x", expand=True, padx=(0, 10))

        rows = [
            ("Spells Known:",       "_cast_count_lbl"),
            ("Active Spells:",      "_active_count_lbl"),
            ("Mouse-Primed Spell:", "_mouse_primed_lbl"),
        ]
        for row_idx, (label, attr) in enumerate(rows):
            ttk.Label(summary, text=label, width=20, anchor="e").grid(
                row=row_idx, column=0, sticky="e", pady=4, padx=(0, 8))
            lbl = ttk.Label(summary, text="—", foreground=THEME["fg_muted"])
            lbl.grid(row=row_idx, column=1, sticky="w", pady=4)
            setattr(self, attr, lbl)

        # — Spell lists —
        bottom = ttk.Frame(self)
        bottom.pack(fill="both", expand=True, padx=20, pady=(10, 0))

        # Known spells: editable checkbox grid (scrollable)
        known_card = ttk.LabelFrame(bottom, text=" Known Spells (castSpells) ", padding=8)
        known_card.pack(side="left", fill="both", expand=True, padx=(0, 5))

        canvas = tk.Canvas(known_card, background=THEME["list_bg_spells"],
                            highlightthickness=0)
        sb1 = ttk.Scrollbar(known_card, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=sb1.set)
        sb1.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        self._spell_grid = ttk.Frame(canvas)
        grid_id = canvas.create_window((0, 0), window=self._spell_grid, anchor="nw")

        def _on_grid_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        self._spell_grid.bind("<Configure>", _on_grid_configure)

        def _on_canvas_configure(event):
            canvas.itemconfig(grid_id, width=event.width)
        canvas.bind("<Configure>", _on_canvas_configure)

        # Active active temporary spell effects view track
        active_card = ttk.LabelFrame(bottom, text=" Active Spells ", padding=8)
        active_card.pack(side="right", fill="both", expand=True, padx=(5, 0))
        sb2 = ttk.Scrollbar(active_card)
        sb2.pack(side="right", fill="y")
        self._active_listbox = tk.Listbox(
            active_card, font=("Consolas", 9),
            background=THEME["list_bg_active"], foreground=THEME["tag_spell_active"],
            selectbackground=THEME["list_select"], highlightthickness=0,
            yscrollcommand=sb2.set)
        self._active_listbox.pack(fill="both", expand=True)
        sb2.config(command=self._active_listbox.yview)
