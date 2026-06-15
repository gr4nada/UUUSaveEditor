# src/core/database/char_globals.py
"""
Character-specific globals (booksRead, numFishCaught, etc.).

Centralized access for progression counters.
"""

CHAR_GLOBALS: list[str] = [
    "booksRead",
    "numFishCaught",
    "numRepairs",
    "booksBurned",
    "waterWalkSteps",
    "lavaWalkSteps",
    "gateTravelDistance",
    # Add more as needed
]

def char_global_label(key: str) -> str:
    """Human-readable label for character globals."""
    labels = {
        "booksRead": "Books Read",
        "numFishCaught": "Fish Caught",
        "numRepairs": "Items Repaired",
        "booksBurned": "Books Burned",
        "waterWalkSteps": "Water Walk Steps",
        "lavaWalkSteps": "Lava Walk Steps",
        "gateTravelDistance": "Gate Travel Distance",
    }
    return labels.get(key, key)