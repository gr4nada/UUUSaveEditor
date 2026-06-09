# src/gui/tabs/stats_tab.py
import logging
import tkinter as tk
from tkinter import ttk
from src.core.enums import NOMES_SKILLS
from src.gui.constants import UNDERWORLD_CLASSES

logger = logging.getLogger("gui.tabs.stats")

# ---------------------------------------------------------------------------
# Definição declarativa dos campos — adicionar/remover campo = uma linha aqui
# ---------------------------------------------------------------------------

_IDENTITY_FIELDS = [
    {"key": "playerName",  "label": "Player Name:",        "type": "entry",  "width": 16},
    {"key": "playerClass", "label": "Player Class:",       "type": "combo",  "options": UNDERWORLD_CLASSES},
    {"key": "female",      "label": "Gender:",             "type": "combo",  "options": ["Male", "Female"]},
    {"key": "leftHanded",  "label": "Dominant Hand:",      "type": "combo",  "options": ["Right-Handed", "Left-Handed"]},
    {"key": "portrait",    "label": "Portrait ID (0-31):", "type": "entry",  "width": 6},
]

_ATTRIBUTE_FIELDS = [
    ("charLevel",   "Level:"),
    ("exp",         "Experience (EXP):"),
    ("strength",    "Strength (STR):"),
    ("intellect",   "Intellect (INT):"),
    ("dexterity",   "Dexterity (DEX):"),
    ("hp",          "Health Points (HP):"),
    ("vitality",    "Max Vitality:"),
    ("mana",        "Current Mana:"),
    ("maxMana",     "Max Mana:"),
    ("skillPoints", "Unspent Skill Points:"),
]

_SURVIVAL_FIELDS = [
    ("poison",      "Poison Level:"),
    ("hunger",      "Hunger Level:"),
    ("fatigue",     "Fatigue Level:"),
    ("drunkenness", "Drunkenness Level:"),
]


class StatsTab(ttk.Frame):
    """
    Aba 'Player Data'.

    API pública:
        set_values(attributes, skills)  — preenche todos os campos
        get_values() -> (dict, dict)    — coleta atributos e skills
        maximize_skills_view(value)     — atalho do cheat
    """

    def __init__(self, parent: ttk.Notebook) -> None:
        super().__init__(parent, padding=10)

        # Internals — não acessar de fora desta classe
        self._vars:     dict[str, tk.StringVar]  = {}   # todos os campos de texto/int
        self._widgets:  dict[str, tk.Widget]      = {}   # combos e entries por key
        self._editable: list[tk.Widget]           = []   # para habilitar/desabilitar em lote

        self._create_layout()

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    def set_values(self, attributes: dict, skills: dict) -> None:
        """Habilita os campos e os preenche com os dados do save."""
        # Identidade
        for field in _IDENTITY_FIELDS:
            key = field["key"]
            raw = attributes.get(key)
            w   = self._widgets[key]

            if field["type"] == "combo":
                w.config(state="readonly")
                w.set(self._resolve_combo(field, raw))
            else:
                w.config(state="normal")
                self._vars[key].set(str(raw) if raw is not None else "")

        # Atributos numéricos + survival
        for key, _ in _ATTRIBUTE_FIELDS + _SURVIVAL_FIELDS:
            self._widgets[key].config(state="normal")
            self._vars[key].set(str(attributes.get(key, 0)))

        # Skills
        for skill_name in NOMES_SKILLS:
            self._widgets[f"skill_{skill_name}"].config(state="normal")
            self._vars[f"skill_{skill_name}"].set(str(skills.get(skill_name, 0)))

    def get_values(self) -> tuple[dict, dict]:
        """
        Retorna (attributes_dict, skills_dict).
        Lança ValueError se algum campo numérico contiver texto inválido.
        """
        attrs: dict = {}

        for field in _IDENTITY_FIELDS:
            key = field["key"]
            raw = self._vars[key].get()
            if field["key"] == "female":
                attrs[key] = (raw == "Female")
            elif field["key"] == "leftHanded":
                attrs[key] = (raw == "Left-Handed")
            elif field["key"] == "portrait":
                attrs[key] = int(raw)
            else:
                attrs[key] = raw

        for key, _ in _ATTRIBUTE_FIELDS + _SURVIVAL_FIELDS:
            attrs[key] = int(self._vars[key].get())

        skills = {
            name: int(self._vars[f"skill_{name}"].get())
            for name in NOMES_SKILLS
        }
        return attrs, skills

    def maximize_skills_view(self, value: int = 30) -> None:
        """Atualiza a view de skills para o valor do cheat."""
        for name in NOMES_SKILLS:
            self._vars[f"skill_{name}"].set(str(value))

    # ------------------------------------------------------------------
    # Construção interna
    # ------------------------------------------------------------------

    def _create_layout(self) -> None:
        left = ttk.LabelFrame(self, text=" Identity & Attributes ", padding=10)
        left.pack(side="left", fill="both", expand=True, padx=5)

        right = ttk.LabelFrame(self, text=" Skills Matrix ", padding=10)
        right.pack(side="right", fill="both", expand=True, padx=5)

        self._build_attributes(left)
        self._build_skills(right)

    def _build_attributes(self, parent: ttk.LabelFrame) -> None:
        canvas = tk.Canvas(parent, borderwidth=0, highlightthickness=0)
        scroll = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        inner  = ttk.Frame(canvas)
        inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=inner, anchor="nw")
        canvas.configure(yscrollcommand=scroll.set)
        canvas.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        row = 0

        # — Identidade —
        ttk.Label(inner, text="Character Identity", font=("Arial", 9, "bold")).grid(
            row=row, column=0, columnspan=2, sticky="w", pady=5)
        row += 1

        for field in _IDENTITY_FIELDS:
            key = field["key"]
            ttk.Label(inner, text=field["label"]).grid(row=row, column=0, sticky="w", pady=3)
            var = tk.StringVar()
            self._vars[key] = var

            if field["type"] == "combo":
                w = ttk.Combobox(inner, textvariable=var, values=field["options"],
                                 state="disabled", width=14)
            else:
                w = ttk.Entry(inner, textvariable=var, state="disabled",
                              width=field.get("width", 12))

            w.grid(row=row, column=1, sticky="w", pady=3)
            self._widgets[key] = w
            self._editable.append(w)
            row += 1

        ttk.Separator(inner, orient="horizontal").grid(
            row=row, column=0, columnspan=2, sticky="ew", pady=10)
        row += 1

        # — Atributos & Vitals —
        ttk.Label(inner, text="Attributes & Vitals", font=("Arial", 9, "bold")).grid(
            row=row, column=0, columnspan=2, sticky="w", pady=5)
        row += 1

        for key, label in _ATTRIBUTE_FIELDS:
            row = self._add_int_row(inner, key, label, row)

        ttk.Separator(inner, orient="horizontal").grid(
            row=row, column=0, columnspan=2, sticky="ew", pady=10)
        row += 1

        # — Survival States —
        ttk.Label(inner, text="Survival States", font=("Arial", 9, "bold")).grid(
            row=row, column=0, columnspan=2, sticky="w", pady=5)
        row += 1

        for key, label in _SURVIVAL_FIELDS:
            row = self._add_int_row(inner, key, label, row)

    def _add_int_row(self, parent: ttk.Frame, key: str, label: str, row: int) -> int:
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", pady=3)
        var = tk.StringVar()
        entry = ttk.Entry(parent, textvariable=var, state="disabled", width=12)
        entry.grid(row=row, column=1, sticky="w", pady=3)
        self._vars[key] = var
        self._widgets[key] = entry
        self._editable.append(entry)
        return row + 1

    def _build_skills(self, parent: ttk.LabelFrame) -> None:
        canvas = tk.Canvas(parent, borderwidth=0, highlightthickness=0)
        scroll = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        inner  = ttk.Frame(canvas)
        inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=inner, anchor="nw")
        canvas.configure(yscrollcommand=scroll.set)
        canvas.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        for idx, name in enumerate(NOMES_SKILLS):
            k = f"skill_{name}"
            ttk.Label(inner, text=f"{name}:").grid(row=idx, column=0, sticky="w", pady=2, padx=5)
            var = tk.StringVar()
            entry = ttk.Entry(inner, textvariable=var, state="disabled", width=6)
            entry.grid(row=idx, column=1, sticky="w", pady=2, padx=5)
            self._vars[k] = var
            self._widgets[k] = entry
            self._editable.append(entry)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _resolve_combo(field: dict, raw) -> str:
        """Converte o valor bruto do save para a string exibida no Combobox."""
        if field["key"] == "female":
            return "Female" if raw else "Male"
        if field["key"] == "leftHanded":
            return "Left-Handed" if raw else "Right-Handed"
        options = field.get("options", [])
        return raw if raw in options else (options[0] if options else "")
