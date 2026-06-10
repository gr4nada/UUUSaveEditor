# src/gui/tabs/magic_tab.py
"""Magic Tab — Reads and parses magicData structures (read-only for this stage)."""
import tkinter as tk
from tkinter import ttk

class MagicTab(ttk.Frame):
    """
    'Magic' Tab — Renders global magicData properties from the active save block.
    Read-only layout variant; mutation sequences are deferred to Sprint 5.

    Public API:
        load(player) → Refreshes the visual frame hierarchy with updated states.
    """

    def __init__(self, parent: ttk.Notebook) -> None:
        super().__init__(parent, padding=20)
        self._spell_rows: list[tuple] = []
        self._build()

    def load(self, player) -> None:
        magic = player.magic_data
        cast_spells = magic.get("castSpells", [])
        active_spells = magic.get("activeSpells", [])

        # Filter the lists to accurately quantify only legitimate active spell entities (dict objects)
        valid_cast_count = sum(1 for s in cast_spells if isinstance(s, dict))
        valid_active_count = sum(1 for s in active_spells if isinstance(s, dict))

        self._cast_count_lbl.config(
            text=f"{valid_cast_count} spells known",
            foreground="#aaaaff")

        self._active_count_lbl.config(
            text=f"{valid_active_count} active" if valid_active_count else "None active",
            foreground="#88ff88" if valid_active_count else "#666")

        self._mouse_primed_lbl.config(
            text="YES" if magic.get("hasMousePrimedSpell") else "NO",
            foreground="#fff")

        # Populate tracked known spell data collections
        self._spell_listbox.delete(0, tk.END)
        for spell in cast_spells:
            # TYPE GUARD DEFENSE: If slot isn't a dict (e.g., Unity's primitive fallback boolean), show empty
            if not isinstance(spell, dict):
                self._spell_listbox.insert(tk.END, "  [Empty Slot]")
                continue

            name = spell.get("spellName", spell.get("name", "Unknown"))
            rune = spell.get("runeSequence", spell.get("rune", ""))
            self._spell_listbox.insert(tk.END, f"  {name:<28} {rune}")

        # Populate active baseline spell nodes
        self._active_listbox.delete(0, tk.END)
        for spell in active_spells:
            # TYPE GUARD DEFENSE: Skip inactive raw booleans inside buff trackers to avoid rendering junk
            if not isinstance(spell, dict):
                # Optional: Uncomment the line below if you wish to visually display inactive slots
                # self._active_listbox.insert(tk.END, "  [Inactive Slot]")
                continue

            name = spell.get("spellName", spell.get("name", "Unknown"))
            self._active_listbox.insert(tk.END, f"  {name}")

    def _build(self) -> None:
        notice = ttk.Label(
            self,
            text="✦  Magic tab is read-only in this version.  Editing support coming in a future sprint.",
            foreground="#888", font=("Arial", 9, "italic"))
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
            lbl = ttk.Label(summary, text="—", foreground="#888")
            lbl.grid(row=row_idx, column=1, sticky="w", pady=4)
            setattr(self, attr, lbl)

        # — Spells list allocations —
        bottom = ttk.Frame(self)
        bottom.pack(fill="both", expand=True, padx=20, pady=(10, 0))

        # Known spells view track
        known_card = ttk.LabelFrame(bottom, text=" Known Spells (castSpells) ", padding=8)
        known_card.pack(side="left", fill="both", expand=True, padx=(0, 5))
        sb1 = ttk.Scrollbar(known_card)
        sb1.pack(side="right", fill="y")
        self._spell_listbox = tk.Listbox(
            known_card, font=("Consolas", 9),
            background="#1a1a2e", foreground="#aaaaff",
            selectbackground="#264f78", highlightthickness=0,
            yscrollcommand=sb1.set)
        self._spell_listbox.pack(fill="both", expand=True)
        sb1.config(command=self._spell_listbox.yview)

        # Active active temporary spell effects view track
        active_card = ttk.LabelFrame(bottom, text=" Active Spells ", padding=8)
        active_card.pack(side="right", fill="both", expand=True, padx=(5, 0))
        sb2 = ttk.Scrollbar(active_card)
        sb2.pack(side="right", fill="y")
        self._active_listbox = tk.Listbox(
            active_card, font=("Consolas", 9),
            background="#1a2e1a", foreground="#88ff88",
            selectbackground="#264f78", highlightthickness=0,
            yscrollcommand=sb2.set)
        self._active_listbox.pack(fill="both", expand=True)
        sb2.config(command=self._active_listbox.yview)