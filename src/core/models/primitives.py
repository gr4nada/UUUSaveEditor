# src/core/models/primitives.py
"""
Shared validation primitives for all models.

    ValidationError   — error with field metadata (field, value, lo, hi)
    FIELD_LIMITS      — limits per field (min_inclusive, max_inclusive)
    _clamp            — silently limits (status/survival)
    _validate         — raises ValidationError (progression/combat)
"""
from __future__ import annotations


# ---------------------------------------------------------------------------
# ValidationError
# ---------------------------------------------------------------------------

class ValidationError(ValueError):
    """
    Raised when a value violates game limits.

    Carries metadata sufficient for GUI to display a useful message:
        field   → field name (e.g.: "hp")
        value   → rejected value
        lo / hi → allowed limits (None = no limit on that side)
    """
    def __init__(self, field: str, value, lo=None, hi=None, msg: str = ""):
        self.field = field
        self.value = value
        self.lo    = lo
        self.hi    = hi
        if not msg:
            parts = []
            if lo is not None: parts.append(f">= {lo}")
            if hi is not None: parts.append(f"<= {hi}")
            msg = (f"'{field}' = {value!r} is out of allowed range "
                   f"({' and '.join(parts) or 'unknown'})")
        super().__init__(msg)


# ---------------------------------------------------------------------------
# FIELD_LIMITS
# ---------------------------------------------------------------------------

FIELD_LIMITS: dict[str, tuple] = {
    # — Vitals (validate: erros de digitação claros) —
    "hp":           (0,   9999),
    "vitality":     (1,   9999),
    "mana":         (0,   9999),
    "max_mana":     (0,   9999),

    # — Progressão —
    "level":        (1,    255),
    "xp":           (0, 999_999_999),
    "skill_points": (0,  9999),

    # — Atributos —
    "strength":     (1,    255),
    "intellect":    (1,    255),
    "dexterity":    (1,    255),

    # — Status/sobrevivência (clamp silencioso) —
    "poison":       (0,    255),
    "hunger":       (0,    255),
    "fatigue":      (0,    255),
    "drunkenness":  (0,    255),

    # — Identidade —
    "portrait":     (0,      9),
    "player_class": (0,      7),

    # — Skills —
    "skill":        (0,     30),

    # — Story / Game State (Sprint 10) —
    "dungeon_level":   (0,      9),      # 10 níveis de masmorra (0-9)
    "cup_dream_index": (0,      5),      # índice no array dreamsRemaining[6]
    "dream_count":     (0,     99),      # contador de sonhos restantes por talismã
    "talismans":       (0,     64),      # talismansCollected / talismansDestroyed
    "global_var":      (-32768, 32767),  # Int16 — formato bglobals.dat
    "world_position":  (-2000.0, 2000.0),  # coordenadas x/y/z do mundo
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _clamp(value, lo, hi):
    """Aplica min/max sem levantar exceção — usado em campos de sobrevivência."""
    if lo is not None: value = max(lo, value)
    if hi is not None: value = min(hi, value)
    return value


def _validate(field: str, value, lo, hi):
    """Valida e retorna o valor, ou levanta ValidationError."""
    if lo is not None and value < lo:
        raise ValidationError(field, value, lo=lo, hi=hi)
    if hi is not None and value > hi:
        raise ValidationError(field, value, lo=lo, hi=hi)
    return value
