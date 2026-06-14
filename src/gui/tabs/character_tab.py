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
from src.gui.constants import UNDERWORLD_CLASSES, THEME
from src.core.save_model import FIELD_LIMITS


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

        # Dungeon & State (Sprint 11)
        self._easy_var = tk.BooleanVar(value=False)
        self._pos_x_var = tk.StringVar(value="0.000")
        self._pos_y_var = tk.StringVar(value="0.000")
        self._pos_z_var = tk.StringVar(value="0.000")

        # Dreams Remaining — 6 spinboxes (Sprint 11)
        self._dream_vars: list[tk.StringVar] = [tk.StringVar(value="0") for _ in range(6)]

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

    def load(self, save_game) -> None:
        player = save_game.player
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
        self._dungeon_lbl.config(text=str(save_game.dungeon_level or "—"))

        # Dungeon & State (Sprint 11)
        self._easy_var.set(player.easy)
        pos = player.position
        self._pos_x_var.set(f"{pos['x']:.3f}")
        self._pos_y_var.set(f"{pos['y']:.3f}")
        self._pos_z_var.set(f"{pos['z']:.3f}")

        # Dreams Remaining (Sprint 11)
        dreams = player.dreams_remaining
        for i, var in enumerate(self._dream_vars):
            var.set(str(dreams[i] if i < len(dreams) else 0))

        # Atributos + status + progressão
        for key, attr in _ATTR_KEY_MAP.items():
            self._widgets[key].config(state="normal")
            self._vars[key].set(str(getattr(player, attr, 0)))

        # Statistics
        for key, _, extractor in _STATISTICS:
            try:
                self._stat_lbls[key].config(text=extractor(player), foreground=THEME["fg_stat_value"])
            except Exception:
                self._stat_lbls[key].config(text="—", foreground=THEME["fg_faint"])

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

    def get_story_overrides(self) -> dict:
        """
        Campos de 'Dungeon & State' (Sprint 11) que são mesclados em
        payload.story antes do save — easy mode e posição do jogador.
        Valores não-numéricos em X/Y/Z caem em 0.0 (mesma tolerância usada
        em story_tab).
        """
        def _f(var: tk.StringVar) -> float:
            try:
                return float(var.get())
            except (ValueError, tk.TclError):
                return 0.0

        def _i(var: tk.StringVar) -> int:
            try:
                return int(var.get())
            except (ValueError, tk.TclError):
                return 0

        return {
            "easy": self._easy_var.get(),
            "position": {
                "x": _f(self._pos_x_var),
                "y": _f(self._pos_y_var),
                "z": _f(self._pos_z_var),
            },
            "dreams_remaining": [_i(v) for v in self._dream_vars],
        }

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
        self._build_dungeon_state(col1)
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
        self._dungeon_lbl = ttk.Label(lf, text="—", foreground=THEME["fg_dungeon"])
        self._dungeon_lbl.grid(row=row, column=1, sticky="w", pady=3)

    def _build_attributes(self, parent) -> None:
        lf = ttk.LabelFrame(parent, text=" Attributes & Vitals ", padding=10)
        lf.pack(fill="x", pady=(0, 8))
        for i, (key, label) in enumerate(_ATTRIBUTES):
            self._int_row(lf, key, label, i)

    def _build_dungeon_state(self, parent) -> None:
        """
        Sprint 11 — Easy Mode + posição do jogador (teleporte).

        'Teleport' aqui significa: editar X/Y/Z e salvar — não há
        movimento em tempo real, apenas a coordenada gravada no save é
        alterada. O nível da masmorra (currentLevel) permanece na aba
        Story, pois afeta qual conjunto de world objects é carregado.
        """
        lf = ttk.LabelFrame(parent, text=" Dungeon & State ", padding=10)
        lf.pack(fill="x", pady=(0, 8))

        ttk.Checkbutton(lf, text="Easy Mode", variable=self._easy_var).grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 6))

        ttk.Label(lf, text="Position (Teleport):", anchor="w",
                  font=("Arial", 8, "bold")).grid(
            row=1, column=0, columnspan=2, sticky="w", pady=(4, 4))

        pos_row = ttk.Frame(lf)
        pos_row.grid(row=2, column=0, columnspan=2, sticky="w")
        for label, var in [("X:", self._pos_x_var), ("Y:", self._pos_y_var), ("Z:", self._pos_z_var)]:
            ttk.Label(pos_row, text=label, anchor="e", width=2).pack(side="left", padx=(0, 2))
            ttk.Entry(pos_row, textvariable=var, width=9).pack(side="left", padx=(0, 8))

        ttk.Label(lf,
                  text="Editar X/Y/Z e salvar move o personagem para essas\ncoordenadas na próxima vez que o save for carregado.",
                  foreground=THEME["fg_dim"], font=("Arial", 8, "italic"),
                  justify="left").grid(row=3, column=0, columnspan=2, sticky="w", pady=(6, 0))

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

        # Dreams Remaining — 6 spinboxes lado a lado (Sprint 11)
        next_row = len(_PROGRESSION)
        ttk.Separator(lf, orient="horizontal").grid(
            row=next_row, column=0, columnspan=2, sticky="ew", pady=8)
        next_row += 1

        ttk.Label(lf, text="Dreams Remaining:", anchor="w",
                  font=("Arial", 8, "bold")).grid(
            row=next_row, column=0, columnspan=2, sticky="w", pady=(0, 4))
        next_row += 1

        dream_row = ttk.Frame(lf)
        dream_row.grid(row=next_row, column=0, columnspan=2, sticky="w")
        _dlo, _dhi = FIELD_LIMITS["dream_count"]
        for var in self._dream_vars:
            ttk.Spinbox(dream_row, from_=_dlo, to=_dhi, textvariable=var,
                        width=4).pack(side="left", padx=(0, 4))
        next_row += 1

        ttk.Label(lf,
                  text="Um valor por talismã/sonho restante (índice = cupDreamIndex aponta para um destes).",
                  foreground=THEME["fg_dim"], font=("Arial", 8, "italic"),
                  wraplength=220, justify="left").grid(
            row=next_row, column=0, columnspan=2, sticky="w", pady=(6, 0))

    # --- Coluna 3 ---

    def _build_statistics(self, parent) -> None:
        lf = ttk.LabelFrame(parent, text=" Statistics ", padding=10)
        lf.pack(fill="x", pady=(0, 8))

        ttk.Label(lf, text="read-only", foreground=THEME["fg_dead"],
                  font=("Arial", 7, "italic")).grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 6))

        for i, (key, label, _) in enumerate(_STATISTICS):
            ttk.Label(lf, text=label + ":", anchor="e",
                      width=_LBL_W).grid(row=i + 1, column=0,
                                         sticky="e", pady=3, padx=(0, 8))
            lbl = ttk.Label(lf, text="—", foreground=THEME["fg_faint"],
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
