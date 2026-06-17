"""
Filters Module

Contains filtering, searching, and sorting logic for the Critters tab.
Keeps the main tab clean by isolating all business rules related to 
visibility and ordering of critters.
"""

from typing import List, Dict, Any, Optional


def filter_critters(
    critters: List[Dict],
    show_dead: bool = True,
    min_level: int = 0,
    attitude_filter: Optional[int] = None,
    search_term: str = ""
) -> List[Dict]:
    """
    Apply multiple filters to the critters list.

    Args:
        critters: List of raw dicts returned by parse_world()
        show_dead: If False, hide dead critters
        min_level: Minimum level (0 = show all)
        attitude_filter: Filter by specific attitude (0-3)
        search_term: Search term (name, type, state, goal)

    Returns:
        Filtered list of critters
    """
    if not critters:
        return []

    visible = critters.copy()

    # Filter: Dead
    if not show_dead:
        visible = [c for c in visible if not c.get("dead", False)]

    # Filtro: Nível mínimo
    if min_level > 0:
        visible = [c for c in visible if c.get("level", 0) >= min_level]

    # Filtro: Atitude
    if attitude_filter is not None:
        visible = [c for c in visible if c.get("attitude") == attitude_filter]

    # Filtro: Busca textual
    if search_term.strip():
        term = search_term.lower().strip()
        visible = [
            c for c in visible
            if term in str(c.get("name", "")).lower()
            or term in str(c.get("type_name", "")).lower()
            or term in str(c.get("state_label", "")).lower()
            or term in str(c.get("goal_label", "")).lower()
            or term in str(c.get("attitude_label", "")).lower()
        ]

    return visible


def sort_critters(
    critters: List[Dict], 
    column: str = "name", 
    reverse: bool = False
) -> List[Dict]:
    """
    Ordena a lista de critters por uma coluna específica.
    
    Args:
        critters: Lista de critters
        column: Coluna para ordenação ("name", "level", "hp", "attitude", etc.)
        reverse: True para ordem descendente
    
    Returns:
        Lista ordenada
    """
    if not critters:
        return []

    def sort_key(item: Dict) -> Any:
        value = item.get(column)
        
        if isinstance(value, str):
            return value.lower()
        if value is None:
            return -999999 if reverse else 999999  # coloca nulos no final/início
        return value

    return sorted(critters, key=sort_key, reverse=reverse)


# Funções auxiliares úteis

def get_unique_attitudes(critters: List[Dict]) -> List[tuple[int, str]]:
    """Retorna lista de atitudes únicas presentes na lista."""
    from collections import OrderedDict
    attitudes = OrderedDict()
    for c in critters:
        att = c.get("attitude")
        label = c.get("attitude_label", "Unknown")
        if att is not None and att not in attitudes:
            attitudes[att] = label
    return list(attitudes.items())


def get_level_range(critters: List[Dict]) -> tuple[int, int]:
    """Retorna (nível mínimo, nível máximo) presentes na lista."""
    if not critters:
        return 0, 0
    levels = [c.get("level", 0) for c in critters]
    return min(levels), max(levels)