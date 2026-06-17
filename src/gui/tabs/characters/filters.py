# src/gui/tabs/characters/filters.py
"""
Helpers de coerção e validação de input para os painéis de personagem.

Mantém fora da GUI a lógica de "como converter string de Entry → valor Python".
Testável sem display.
"""
from __future__ import annotations


def coerce_int(value: str | None, default: int = 0) -> int:
    """Converte string de Entry para int com fallback."""
    try:
        return int(value or default)
    except (ValueError, TypeError):
        return default


def coerce_float(value: str | None, default: float = 0.0) -> float:
    """Converte string de Entry para float com fallback."""
    try:
        return float(value or default)
    except (ValueError, TypeError):
        return default


def coerce_bool_from_str(value: str, true_str: str) -> bool:
    """Converte string de Combobox para bool. Ex: coerce_bool_from_str("Female", "Female") → True."""
    return value == true_str


def build_attrs_payload(vars_: dict) -> dict:
    """
    Monta o dict de atributos a partir dos StringVars do CharacterTab.
    `vars_` deve ter as mesmas chaves de ATTR_KEY_MAP mais as de identidade.
    """
    from src.gui.tabs.characters.character_model import ATTR_KEY_MAP
    attrs: dict = {
        "playerName":  vars_["playerName"].get(),
        "playerClass": vars_["playerClass"].get(),
        "female":      coerce_bool_from_str(vars_["female"].get(),     "Female"),
        "leftHanded":  coerce_bool_from_str(vars_["leftHanded"].get(), "Left-Handed"),
        "portrait":    coerce_int(vars_["portrait"].get()),
    }
    for key in ATTR_KEY_MAP:
        attrs[key] = coerce_int(vars_[key].get())
    return attrs


def build_story_overrides(easy_var, pos_x, pos_y, pos_z, dream_vars) -> dict:
    """
    Monta as sobreposições de story (easy, position, dreams_remaining)
    para serem mescladas em SavePayload.story.
    """
    return {
        "easy": bool(easy_var.get()),
        "position": {
            "x": coerce_float(pos_x.get()),
            "y": coerce_float(pos_y.get()),
            "z": coerce_float(pos_z.get()),
        },
        "dreams_remaining": [coerce_int(v.get()) for v in dream_vars],
    }
