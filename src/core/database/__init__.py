# src/core/database/__init__.py
"""
Knowledge Base do UUU Save Editor — fonte única de verdade sobre o jogo.
"""

from src.core.database import objects, critters, whoami, quests, skills
# New modules:
from src.core.database import global_vars, conversations, char_globals

__all__ = [
    "objects", "critters", "whoami", "quests", "skills",
    "global_vars", "conversations", "char_globals"
]