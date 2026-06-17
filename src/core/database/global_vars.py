# src/core/database/global_vars.py
"""
Global variables / engine trackers (playerData.globalVars[0..63]).

Single source of truth for:
  - GLOBAL_VAR_NAMES — readable names of known global variables
  - get_global_var_name() / describe_global_var()
"""

GLOBAL_VAR_NAMES: dict[int, str] = {
    0: "Unknown / Reserved",
    1: "Unknown / Reserved",
    # Expand as reverse-engineering progresses (common ones from community/docs)
    # Example placeholders:
    # 10: "Quest Stage - Main Story",
    # 20: "Lizardmen Alliance Level",
    # 42: "Tyball Defeated Flag",
}

def global_var_name(var_id: int) -> str:
    """int → readable name or fallback."""
    return GLOBAL_VAR_NAMES.get(var_id, f"GlobalVar#{var_id}")

def describe_global_var(var_id: int, value: int) -> str:
    """Basic description (expandable)."""
    name = global_var_name(var_id)
    return f"{name} = {value}"