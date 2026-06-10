# src/gui/tabs/character_tab.py
"""
Aba 'Character' — layout em 3 colunas.

Coluna 1 (esquerda):   Identity  +  Attributes & Vitals
Coluna 2 (centro):     Status Conditions  +  Progression
Coluna 3 (direita):    Statistics (read-only)

Regras de portrait/gender:
  - Gender Combobox: Male / Female
  - Portrait Spinbox filtra automaticamente conforme gender:
      Male   → opções 0–4
      Female → opções 5–9
  - Trocar gender → portrait reseta para o primeiro valor do gênero
  - portrait_id → body no paper doll (mapeamento 1:1)
"""
import tkinter as tk
from tkinter import ttk
from src.gui.constants import UNDERWORLD_CLASSES


def _fmt_time(sec: float) -> str:
    s = int(sec)
    return f"{s // 3600:,}h {(s % 3600) // 60:02d}m"


# Portrait ranges por gênero
_PORTRAIT_MALE   = list(range(5))     # 0-4
_PORTRAIT_FEMALE = list(range(5, 10)) # 5-9

_ATTR_KEY_MAP = {
    "vitality":   "vitality",
    "maxMana":    "max_mana",
    "strength":   "strength",
    "dexterity":  "dexterity",
    "intellect":  "intellect",
    "hp":         "hp",
    "mana":       "mana",
    "poison":     "poison",
    "hunger":     "hunger",
    "fatigue":    "fatigue",
    "drunkenness":"drunkenness",
    "charLevel":  "level",
    "xp":         "xp",
    "skillPoints":"skill_points",
}

_ATTRIBUTES = [
    ("vitality",  "Max HP"),
    ("maxMana",   "Max Mana"),
    ("strength",  "Strength"),
    ("dexterity", "Dexterity"),
    ("intellect", "Intellect"),
]

_STATUS = [
    ("hp",          "Current HP"),
    ("mana",        "Current Mana"),
    ("poison",      "Poison"),
    ("hunger",      "Hunger"),
    ("fatigue",     "Fatigue"),
    ("drunkenness", "Drunkenness"),
]

_PROGRESSION = [
    ("charLevel",   "Character Level"),
    ("xp",          "Experience"),
    ("skillPoints", "Skill Points"),
]

_STATISTICS = [
    ("play_time",        "Play Time",       lambda p: _fmt_time(p.play_time)),
    ("game_time",        "Game Time",       lambda p: _fmt_time(p.game_time)),
    ("books_read",       "Books Read",      lambda p: str(p.books_read)),
    ("books_burned",     "Books Burned",    lambda p: str(p.books_burned)),
    ("num_fish_caught",  "Fish Caught",     lambda p: str(p.num_fish_caught)),
    ("num_repairs",      "Repairs Made",    lambda p: str(p.num_repairs)),
    ("water_walk_steps", "Water Steps",     lambda p: str(p.water_walk_steps)),
    ("lava_walk_steps",  "Lava Steps",      lambda p: str(p.lava_walk_steps)),
]

_LBL_W = 16  # largura dos labels em colunas


class CharacterTab(ttk.Frame):
    """
    Aba consolidada de personagem — 3 colunas.

    API pública:
        load(player)             → preenche todos os campos
        get_values() → dict      → coleta valores editáveis
        on_portrait_change(fn)   → fn(portrait_id: int)
        on_gender_change(fn)     → fn(female: bool)  [unused externamente — portrait já implica gender]
    """

    def __init__(self, parent: ttk.Notebook) -> None:
        super().__init__(parent, padding=10)
        self._vars:       dict[str, tk.StringVar]    = {}
        self._widgets:    dict[str, tk.Widget]        = {}
        self._stat_lbls:  dict[str, ttk.Label]        = {}
        self._on_portrait_change = None
        self._on_gender_change   = None
        self._suppress_traces    = False   # evita loops durante load
        self._build()

    # ------------------------------------------------------------------
    # Callbacks externos
    # ------------------------------------------------------------------

    def on_portrait_change(self, fn) -> None:
        self._on_portrait_change = fn

    def on_gender_change(self, fn) -> None:
        self._on_gender_change = fn

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    def load(self, player) -> None:
        self._suppress_traces = True

        # Identidade — ordem importa: gender antes de portrait
        self._widgets["playerName"].config(state="normal")
        self._vars["playerName"].set(player.name)

        self._widgets["playerClass"].config(state="readonly")
        self._widgets["playerClass"].set(player.player_class_name)

        self._widgets["leftHanded"].config(state="readonly")
        self._widgets["leftHanded"].set(
            "Left-Handed" if player.left_handed else "Right-Handed")

        # Gender
        gender_str = "Female" if player.female else "Male"
        self._widgets["female"].config(state="readonly")
        self._widgets["female"].set(gender_str)
        self._update_portrait_options(player.female)

        # Portrait Spinbox
        portrait_options = _PORTRAIT_FEMALE if player.female else _PORTRAIT_MALE
        pid = player.portrait if player.portrait in portrait_options else portrait_options[0]
        self._vars["portrait"].set(str(pid))
        self._widgets["portrait"].config(state="readonly")

        # Dungeon level — read-only
        self._dungeon_lbl.config(text=str(player._p.get("__dungeon_level__", "—")))

        # Atributos + status + progressão
        for key, attr in _ATTR_KEY_MAP.items():
            self._widgets[key].config(state="normal")
            self._vars[key].set(str(getattr(player, attr, 0)))

        # Statistics
        for key, _, extractor in _STATISTICS:
            try:
                self._stat_lbls[key].config(text=extractor(player), foreground="#ccc")
            except Exception:
                self._stat_lbls[key].config(text="—", foreground="#555")

        self._suppress_traces = False

    def get_values(self) -> dict:
        attrs: dict = {}

        attrs["playerName"]  = self._vars["playerName"].get()
        attrs["playerClass"] = self._vars["playerClass"].get()
        attrs["female"]      = self._vars["female"].get() == "Female"
        attrs["leftHanded"]  = self._vars["leftHanded"].get() == "Left-Handed"
        attrs["portrait"]    = int(self._vars["portrait"].get() or 0)

        for key in _ATTR_KEY_MAP:
            attrs[key] = int(self._vars[key].get() or 0)

        return attrs

    # ------------------------------------------------------------------
    # Construção — 3 colunas
    # ------------------------------------------------------------------

    def _build(self) -> None:
        col1 = ttk.Frame(self)
        col2 = ttk.Frame(self)
        col3 = ttk.Frame(self)
        col1.grid(row=0, column=0, sticky="n", padx=(0, 12))
        col2.grid(row=0, column=1, sticky="n", padx=(0, 12))
        col3.grid(row=0, column=2, sticky="n")

        self._build_identity(col1)
        self._build_attributes(col1)
        self._build_status(col2)
        self._build_progression(col2)
        self._build_statistics(col3)

    # --- Coluna 1 ---

    def _build_identity(self, parent) -> None:
        lf = ttk.LabelFrame(parent, text=" Identity ", padding=10)
        lf.pack(fill="x", pady=(0, 8))

        row = 0

        # Name
        self._lbl_row(lf, "Name:", row)
        var = tk.StringVar()
        self._vars["playerName"] = var
        w = ttk.Entry(lf, textvariable=var, state="disabled", width=16)
        w.grid(row=row, column=1, sticky="w", pady=3)
        self._widgets["playerName"] = w
        row += 1

        # Class
        self._lbl_row(lf, "Class:", row)
        var = tk.StringVar()
        self._vars["playerClass"] = var
        w = ttk.Combobox(lf, textvariable=var, values=UNDERWORLD_CLASSES,
                         state="disabled", width=14)
        w.grid(row=row, column=1, sticky="w", pady=3)
        self._widgets["playerClass"] = w
        row += 1

        # Dominant Hand
        self._lbl_row(lf, "Dominant Hand:", row)
        var = tk.StringVar()
        self._vars["leftHanded"] = var
        w = ttk.Combobox(lf, textvariable=var,
                         values=["Right-Handed", "Left-Handed"],
                         state="disabled", width=14)
        w.grid(row=row, column=1, sticky="w", pady=3)
        self._widgets["leftHanded"] = w
        row += 1

        # Separador
        ttk.Separator(lf, orient="horizontal").grid(
            row=row, column=0, columnspan=2, sticky="ew", pady=8)
        row += 1

        # Gender (radio-style via Combobox)
        self._lbl_row(lf, "Gender:", row)
        var = tk.StringVar()
        self._vars["female"] = var
        w = ttk.Combobox(lf, textvariable=var,
                         values=["Male", "Female"],
                         state="disabled", width=10)
        w.grid(row=row, column=1, sticky="w", pady=3)
        self._widgets["female"] = w
        var.trace_add("write", self._on_gender_changed)
        row += 1

        # Portrait (Spinbox filtrado por gender)
        self._lbl_row(lf, "Portrait:", row)
        var = tk.StringVar()
        self._vars["portrait"] = var
        self._portrait_spin = ttk.Spinbox(
            lf, textvariable=var,
            values=_PORTRAIT_MALE,
            state="disabled", width=5,
            command=self._on_portrait_spun,
        )
        self._portrait_spin.grid(row=row, column=1, sticky="w", pady=3)
        self._widgets["portrait"] = self._portrait_spin
        var.trace_add("write", self._on_portrait_written)
        row += 1

        # Dungeon Level (read-only)
        ttk.Separator(lf, orient="horizontal").grid(
            row=row, column=0, columnspan=2, sticky="ew", pady=8)
        row += 1

        self._lbl_row(lf, "Dungeon Level:", row)
        self._dungeon_lbl = ttk.Label(lf, text="—", foreground="#888")
        self._dungeon_lbl.grid(row=row, column=1, sticky="w", pady=3)

    def _build_attributes(self, parent) -> None:
        lf = ttk.LabelFrame(parent, text=" Attributes & Vitals ", padding=10)
        lf.pack(fill="x", pady=(0, 8))
        for i, (key, label) in enumerate(_ATTRIBUTES):
            self._int_row(lf, key, label, i)

    # --- Coluna 2 ---

    def _build_status(self, parent) -> None:
        lf = ttk.LabelFrame(parent, text=" Status Conditions ", padding=10)
        lf.pack(fill="x", pady=(0, 8))
        for i, (key, label) in enumerate(_STATUS):
            self._int_row(lf, key, label, i)

    def _build_progression(self, parent) -> None:
        lf = ttk.LabelFrame(parent, text=" Progression ", padding=10)
        lf.pack(fill="x", pady=(0, 8))
        for i, (key, label) in enumerate(_PROGRESSION):
            self._int_row(lf, key, label, i)

    # --- Coluna 3 ---

    def _build_statistics(self, parent) -> None:
        lf = ttk.LabelFrame(parent, text=" Statistics ", padding=10)
        lf.pack(fill="x", pady=(0, 8))

        ttk.Label(lf, text="read-only", foreground="#444",
                  font=("Arial", 7, "italic")).grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 6))

        for i, (key, label, _) in enumerate(_STATISTICS):
            ttk.Label(lf, text=label + ":", anchor="e",
                      width=_LBL_W).grid(row=i + 1, column=0,
                                         sticky="e", pady=3, padx=(0, 8))
            lbl = ttk.Label(lf, text="—", foreground="#555",
                            width=12, anchor="w")
            lbl.grid(row=i + 1, column=1, sticky="w", pady=3)
            self._stat_lbls[key] = lbl

    # ------------------------------------------------------------------
    # Helpers de construção
    # ------------------------------------------------------------------

    def _lbl_row(self, parent, text: str, row: int) -> None:
        ttk.Label(parent, text=text, anchor="e",
                  width=_LBL_W).grid(row=row, column=0,
                                     sticky="e", pady=3, padx=(0, 8))

    def _int_row(self, parent, key: str, label: str, row: int) -> None:
        self._lbl_row(parent, label + ":", row)
        var = tk.StringVar()
        entry = ttk.Entry(parent, textvariable=var,
                          state="disabled", width=10)
        entry.grid(row=row, column=1, sticky="w", pady=3)
        self._vars[key] = var
        self._widgets[key] = entry

    # ------------------------------------------------------------------
    # Portrait / Gender — lógica de filtragem
    # ------------------------------------------------------------------

    def _update_portrait_options(self, female: bool) -> None:
        options = _PORTRAIT_FEMALE if female else _PORTRAIT_MALE
        self._portrait_spin.config(values=options)

    def _on_gender_changed(self, *_) -> None:
        if self._suppress_traces:
            return
        female = self._vars["female"].get() == "Female"
        self._update_portrait_options(female)
        # Reset portrait para o primeiro valor do novo gênero
        first = _PORTRAIT_FEMALE[0] if female else _PORTRAIT_MALE[0]
        self._suppress_traces = True
        self._vars["portrait"].set(str(first))
        self._suppress_traces = False
        if self._on_gender_change:
            self._on_gender_change(female)
        self._fire_portrait(first)

    def _on_portrait_spun(self) -> None:
        """Chamado pelos botões ▲▼ do Spinbox."""
        self._fire_portrait_from_var()

    def _on_portrait_written(self, *_) -> None:
        """Chamado quando o StringVar muda (inclusive via load)."""
        if self._suppress_traces:
            return
        self._fire_portrait_from_var()

    def _fire_portrait_from_var(self) -> None:
        try:
            pid = int(self._vars["portrait"].get())
            self._fire_portrait(pid)
        except ValueError:
            pass

    def _fire_portrait(self, pid: int) -> None:
        if self._on_portrait_change:
            self._on_portrait_change(pid)
