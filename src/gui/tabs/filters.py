"""
Filters Module

Contains all filtering, searching, and sorting logic for the Critters tab.
This module is responsible for applying user-defined filters (dead, level,
attitude, search) and sorting the critter list.
"""

from typing import List, Dict, Any, Callable
from .critter_model import Critter


def filter_critters(
    critters: List[Dict],
    show_dead: bool = True,
    min_level: int = 0,
    attitude_filter: int | None = None,
    search_term: str = ""
) -> List[Dict]:
    """
    Filter critters based on multiple criteria.
    
    Args:
        critters: List of raw critter dictionaries
        show_dead: Whether to include dead critters
        min_level: Minimum level to show (0 = all)
        attitude_filter: Specific attitude value to filter by
        search_term: Text to search in name, type, state or goal
    
    Returns:
        Filtered list of critters
    """
    visible = critters.copy()

    if not show_dead:
        visible = [c for c in visible if not c.get("dead", False)]

    if min_level > 0:
        visible = [c for c in visible if c.get("level", 0) >= min_level]

    if attitude_filter is not None:
        visible = [c for c in visible if c.get("attitude") == attitude_filter]

    if search_term:
        term = search_term.lower()
        visible = [
            c for c in visible
            if (
                term in c.get("name", "").lower()
                or term in c.get("type_name", "").lower()
                or term in c.get("state_label", "").lower()
                or term in c.get("goal_label", "").lower()
            )
        ]

    return visible


def sort_critters(critters: List[Dict], column: str, reverse: bool = False) -> List[Dict]:
    """
    Sort critters by a specific column.
    
    Args:
        critters: List of critter dictionaries
        column: Column name to sort by
        reverse: Sort in descending order
    
    Returns:
        Sorted list
    """
    def sort_key(item: Dict) -> Any:
        value = item.get(column)
        if isinstance(value, str):
            return value.lower()
        return value if value is not None else 0

    return sorted(critters, key=sort_key, reverse=reverse)