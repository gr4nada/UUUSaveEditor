"""
Magic Tab — Visual spell and rune editing.
"""

import tkinter as tk
from tkinter import ttk
from collections import defaultdict

from .common.base_tab import BaseTab
from src.gui.constants import THEME, SPELL_TABLE, RUNES_LIST
from src.gui.widgets.icon_loader import IconLoader, ICON_MEDIUM


_RUNE_ICON_BASE = 232
_RUNE_GRID_COLS = 6
_RUNE_ICON_SIZE = (32, 32)

_SPELL_ID_TO_IDX: dict[int, int] = {sid: sid - 1 for sid in SPELL_TABLE}

_RUNE_TO_SPELLS: dict[str, list[int]] = defaultdict(list)
for _sid, _sp in SPELL_TABLE.items():
    for _r in _sp.get("runes", []):
        _RUNE_TO_SPELLS[_r].append(_sid)

_BY_CIRCLE: dict[int, list] = defaultdict(list)
for _sid, _sp in SPELL_TABLE.items():
    _BY_CIRCLE[_sp["circle"]].append((_sid, _sp))


class MagicTab(BaseTab):
    """
    Magic tab — visual editing of known spells and rune management.
    """

    def __init__(self, parent: ttk.Notebook) -> None:
        self._loader = IconLoader.get_instance()
        self._spell_vars: dict[int, tk.BooleanVar] = {}
        self._rune_labels: dict[str, tk.Label] = {}
        self._rune_icons: dict[str, object] = {}
        self._cast_spells_len: int = 0

        # UI references
        self._cast_count_lbl = None
        self._active_count_lbl = None
        self._mouse_primed_lbl = None
        self._active_listbox = None
        self._spell_frame = None
        self._tooltip_window = None

        super().__init__(parent, title="Magic")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def load(self, save_game) -> None:
        """Load magic data from save_game."""
        super().load(save_game)
        player = save_game.player
        magic = player.magic_data
        cast_spells = player.cast_spells
        active_spells = magic.get("activeSpells", [])

        self._cast_spells_len = len(cast_spells)

        # Summary
        known_count = sum(1 for v in cast_spells if v)
        valid_active_count = sum(1 for s in active_spells if isinstance(s, dict))

        if self._cast_count_lbl:
            self._cast_count_lbl.config(
                text=f"{known_count} / {len(cast_spells)} spells known",
                foreground=THEME["tag_spell_known"])
        if self._active_count_lbl:
            self._active_count_lbl.config(
                text=f"{valid_active_count} active" if valid_active_count else "None active",
                foreground=THEME["tag_spell_active"] if valid_active_count else THEME["tag_spells_none"])
        if self._mouse_primed_lbl:
            self._mouse_primed_lbl.config(
                text="YES" if magic.get("hasMousePrimedSpell") else "NO",
                foreground=THEME["tag_mouse_primed"])

        # Load spell checkboxes
        for cast_idx, known in enumerate(cast_spells):
            if cast_idx in self._spell_vars:
                self._spell_vars[cast_idx].set(bool(known))

        self._refresh_rune_panel()
        self._refresh_known_count()

        # Active spells
        if self._active_listbox:
            self._active_listbox.delete(0, tk.END)
            for spell in active_spells:
                if not isinstance(spell, dict):
                    continue
                name = spell.get("spellName", spell.get("name", "Unknown"))
                self._active_listbox.insert(tk.END, f"  {name}")

        self.clear_changes()

    def get_spells(self) -> list[bool]:
        """Return current castSpells state."""
        result = [False] * self._cast_spells_len
        for i, var in self._spell_vars.items():
            if 0 <= i < self._cast_spells_len:
                result[i] = var.get()
        return result

    # ------------------------------------------------------------------
    # UI Construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        self._build_summary_bar()

        body = ttk.Frame(self)
        body.pack(fill="both", expand=True, padx=4, pady=(6, 0))

        # Left: Rune Panel
        self._build_rune_panel(body)

        # Right: Spells + Active
        right = ttk.Frame(body)
        right.pack(side="left", fill="both", expand=True, padx=(6, 0))
        self._build_spell_list(right)
        self._build_active_panel(right)

    def _build_summary_bar(self) -> None:
        bar = ttk.Frame(self)
        bar.pack(fill="x", padx=4, pady=(0, 4))

        info = ttk.Frame(bar)
        info.pack(side="left", fill="x", expand=True)

        for label, attr, col in [
            ("Spells Known:", "_cast_count_lbl", 0),
            ("Active Spells:", "_active_count_lbl", 1),
            ("Mouse-Primed Spell:", "_mouse_primed_lbl", 2),
        ]:
            ttk.Label(info, text=label, foreground=THEME["fg_muted"], font=("Arial", 9)).grid(
                row=0, column=col*2, sticky="e", padx=(12, 4))
            lbl = ttk.Label(info, text="—", font=("Arial", 9, "bold"))
            lbl.grid(row=0, column=col*2 + 1, sticky="w")
            setattr(self, attr, lbl)

        btns = ttk.Frame(bar)
        btns.pack(side="right")
        ttk.Button(btns, text="✦ Know All", command=self._know_all).pack(side="left", padx=(0, 4))
        ttk.Button(btns, text="✧ Forget All", command=self._forget_all).pack(side="left")

    def _build_rune_panel(self, parent: ttk.Frame) -> None:
        lf = ttk.LabelFrame(parent, text=" Runes ", padding=6)
        lf.pack(side="left", fill="y", padx=(0, 6))

        hint = ttk.Label(lf, text="Highlighted = possessed\n(derived from known spells)",
                         foreground=THEME["fg_muted"], font=("Arial", 8, "italic"), justify="center")
        hint.grid(row=0, column=0, columnspan=_RUNE_GRID_COLS, pady=(0, 6))

        for i, rune in enumerate(RUNES_LIST):
            row = 1 + i // _RUNE_GRID_COLS
            col = i % _RUNE_GRID_COLS

            cell = ttk.Frame(lf)
            cell.grid(row=row, column=col, padx=3, pady=3)

            icon_id = _RUNE_ICON_BASE + i
            photo = self._loader.get_item_icon(icon_id, size=_RUNE_ICON_SIZE)
            self._rune_icons[rune] = photo

            lbl = tk.Label(
                cell, image=photo, text=rune, compound="top",
                font=("Arial", 7), bg=THEME["list_bg_spells"],
                fg=THEME["fg_secondary"], relief="flat", padx=3, pady=2, cursor="hand2"
            )
            lbl.pack()
            self._rune_labels[rune] = lbl

            # Tooltip
            spells = [SPELL_TABLE[sid]["name"] for sid in _RUNE_TO_SPELLS[rune]]
            tip = "  ·  ".join(spells) if spells else "(unused)"
            lbl.bind("<Enter>", lambda e, t=tip, r=rune: self._show_tooltip(e, f"{r}: {t}"))
            lbl.bind("<Leave>", lambda e: self._hide_tooltip())

    def _build_spell_list(self, parent: ttk.Frame) -> None:
        lf = ttk.LabelFrame(parent, text=" Spells by Circle ", padding=4)
        lf.pack(fill="both", expand=True)

        canvas = tk.Canvas(lf, background=THEME["list_bg_spells"], highlightthickness=0)
        sb = ttk.Scrollbar(lf, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        self._spell_frame = ttk.Frame(canvas)
        win_id = canvas.create_window((0, 0), window=self._spell_frame, anchor="nw")

        self._spell_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(win_id, width=e.width))

        circles = sorted(_BY_CIRCLE.keys())
        for circle in circles:
            self._build_circle_section(self._spell_frame, circle)

    def _build_circle_section(self, parent: ttk.Frame, circle: int) -> None:
        circle_label = f"Circle {circle}" if circle > 0 else "Special (Circle 0)"

        header = ttk.Frame(parent)
        header.pack(fill="x", pady=(8, 2))

        ttk.Label(header, text=circle_label, font=("Arial", 9, "bold"),
                  foreground=THEME["tag_spell_known"]).pack(side="left", padx=(4, 8))

        ttk.Button(header, text="Know All",
                   command=lambda c=circle: self._know_circle(c)).pack(side="left", padx=(0, 2))
        ttk.Button(header, text="Forget All",
                   command=lambda c=circle: self._forget_circle(c)).pack(side="left")

        ttk.Separator(parent, orient="horizontal").pack(fill="x", padx=4, pady=(0, 4))

        for spell_id, spell in _BY_CIRCLE[circle]:
            cast_idx = _SPELL_ID_TO_IDX.get(spell_id)
            if cast_idx is None:
                continue

            var = tk.BooleanVar(value=False)
            self._spell_vars[cast_idx] = var

            row = ttk.Frame(parent)
            row.pack(fill="x", padx=4, pady=1)

            cb = ttk.Checkbutton(row, variable=var, command=self._on_spell_toggled)
            cb.pack(side="left")

            runes = " · ".join(spell.get("runes", [])) if spell.get("runes") else "no runes"
            ttk.Label(row, text=f"{spell['name']:<24}", font=("Consolas", 9),
                      foreground=THEME["fg_primary"]).pack(side="left", padx=(4, 0))
            ttk.Label(row, text=runes, font=("Consolas", 8),
                      foreground=THEME["tag_enchanted"]).pack(side="left", padx=(6, 0))

    def _build_active_panel(self, parent: ttk.Frame) -> None:
        lf = ttk.LabelFrame(parent, text=" Active Spells (read-only) ", padding=4)
        lf.pack(fill="x", pady=(4, 0))

        sb = ttk.Scrollbar(lf)
        sb.pack(side="right", fill="y")
        self._active_listbox = tk.Listbox(
            lf, font=("Consolas", 9), height=5,
            background=THEME["list_bg_active"], foreground=THEME["tag_spell_active"],
            selectbackground=THEME["list_select"], highlightthickness=0,
            yscrollcommand=sb.set)
        self._active_listbox.pack(fill="x")
        sb.config(command=self._active_listbox.yview)

    # ------------------------------------------------------------------
    # Logic
    # ------------------------------------------------------------------

    def _on_spell_toggled(self) -> None:
        self._refresh_known_count()
        self._refresh_rune_panel()

    def _refresh_known_count(self) -> None:
        known = sum(1 for v in self._spell_vars.values() if v.get())
        if self._cast_count_lbl:
            self._cast_count_lbl.config(
                text=f"{known} / {self._cast_spells_len} spells known",
                foreground=THEME["tag_spell_known"])

    def _refresh_rune_panel(self) -> None:
        known_spell_ids = {cast_idx + 1 for cast_idx, var in self._spell_vars.items() if var.get()}
        for rune in RUNES_LIST:
            lbl = self._rune_labels.get(rune)
            if not lbl:
                continue
            possessed = any(sid in known_spell_ids for sid in _RUNE_TO_SPELLS[rune])
            if possessed:
                lbl.config(bg="#16213e", fg=THEME["tag_spell_known"], relief="solid")
            else:
                lbl.config(bg=THEME["list_bg_spells"], fg=THEME["fg_muted"], relief="flat")

    def _know_circle(self, circle: int) -> None:
        for spell_id, _ in _BY_CIRCLE[circle]:
            idx = _SPELL_ID_TO_IDX.get(spell_id)
            if idx is not None and idx in self._spell_vars:
                self._spell_vars[idx].set(True)
        self._on_spell_toggled()

    def _forget_circle(self, circle: int) -> None:
        for spell_id, _ in _BY_CIRCLE[circle]:
            idx = _SPELL_ID_TO_IDX.get(spell_id)
            if idx is not None and idx in self._spell_vars:
                self._spell_vars[idx].set(False)
        self._on_spell_toggled()

    def _know_all(self) -> None:
        for var in self._spell_vars.values():
            var.set(True)
        self._on_spell_toggled()

    def _forget_all(self) -> None:
        for var in self._spell_vars.values():
            var.set(False)
        self._on_spell_toggled()

    # ------------------------------------------------------------------
    # Tooltip
    # ------------------------------------------------------------------

    def _show_tooltip(self, event: tk.Event, text: str) -> None:
        self._hide_tooltip()
        x = event.widget.winfo_rootx() + 20
        y = event.widget.winfo_rooty() + 36
        tw = tk.Toplevel(self)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        tk.Label(tw, text=text, justify="left", background="#ffffc0",
                 relief="solid", borderwidth=1, font=("Arial", 8), padx=4, pady=2).pack()
        self._tooltip_window = tw

    def _hide_tooltip(self) -> None:
        if self._tooltip_window:
            try:
                self._tooltip_window.destroy()
            except Exception:
                pass
            self._tooltip_window = None