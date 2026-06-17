# src/gui/tabs/characters/character_model.py
"""
CharacterViewModel — adaptador entre PlayerModel (core) e os painéis da GUI.

Responsabilidades:
  - Definir os campos editáveis e seus metadados (label, key, atributo no model)
  - Expor helpers de conversão (formatter de tempo, ranges válidos)
  - Manter as constantes de UI que antes estavam no topo de character_tab.py

Não importa tkinter — é puro Python, testável sem display.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Any


# ---------------------------------------------------------------------------
# Helpers de formatação
# ---------------------------------------------------------------------------

def fmt_time(sec: float) -> str:
    """Formata segundos em horas e minutos."""
    s = int(sec)
    return f"{s // 3600:,}h {(s % 3600) // 60:02d}m"


# ---------------------------------------------------------------------------
# Constantes de campos
# ---------------------------------------------------------------------------

# Mapeamento: chave do payload (raw save) → atributo Python em PlayerModel
ATTR_KEY_MAP: dict[str, str] = {
    "vitality":    "vitality",
    "maxMana":     "max_mana",
    "strength":    "strength",
    "dexterity":   "dexterity",
    "intellect":   "intellect",
    "hp":          "hp",
    "mana":        "mana",
    "poison":      "poison",
    "hunger":      "hunger",
    "fatigue":     "fatigue",
    "drunkenness": "drunkenness",
    "charLevel":   "level",
    "xp":          "xp",
    "skillPoints": "skill_points",
}

# Atributos de combate/capacidade — coluna Attributes & Vitals
ATTRIBUTES: list[tuple[str, str]] = [
    ("vitality",  "Max HP"),
    ("maxMana",   "Max Mana"),
    ("strength",  "Strength"),
    ("dexterity", "Dexterity"),
    ("intellect", "Intellect"),
]

# Condições de sobrevivência — coluna Status Conditions
STATUS: list[tuple[str, str]] = [
    ("hp",          "Current HP"),
    ("mana",        "Current Mana"),
    ("poison",      "Poison"),
    ("hunger",      "Hunger"),
    ("fatigue",     "Fatigue"),
    ("drunkenness", "Drunkenness"),
]

# Progressão numérica — coluna Progression
PROGRESSION: list[tuple[str, str]] = [
    ("charLevel",   "Character Level"),
    ("xp",          "Experience"),
    ("skillPoints", "Skill Points"),
]

# Estatísticas somente-leitura — coluna Statistics
@dataclass
class StatisticField:
    key:       str
    label:     str
    extractor: Callable[[Any], str]   # recebe um PlayerModel, retorna string

STATISTICS: list[StatisticField] = [
    StatisticField("play_time",        "Play Time",    lambda p: fmt_time(p.play_time)),
    StatisticField("game_time",        "Game Time",    lambda p: fmt_time(p.game_time)),
    StatisticField("books_read",       "Books Read",   lambda p: str(p.books_read)),
    StatisticField("books_burned",     "Books Burned", lambda p: str(p.books_burned)),
    StatisticField("num_fish_caught",  "Fish Caught",  lambda p: str(p.num_fish_caught)),
    StatisticField("num_repairs",      "Repairs Made", lambda p: str(p.num_repairs)),
    StatisticField("water_walk_steps", "Water Steps",  lambda p: str(p.water_walk_steps)),
    StatisticField("lava_walk_steps",  "Lava Steps",   lambda p: str(p.lava_walk_steps)),
]

# Ranges de portrait por género
PORTRAIT_MALE:   list[int] = list(range(5))       # 0–4
PORTRAIT_FEMALE: list[int] = list(range(5, 10))   # 5–9

# Largura do label em colunas de grid
LABEL_WIDTH = 16

# Número de dreams slots
DREAMS_COUNT = 6
