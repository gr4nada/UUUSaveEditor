# src/core/database/__init__.py
"""
Knowledge Base do UUU Save Editor — fonte única de verdade sobre o jogo.

Importação conveniente:

    from src.core.database import objects, critters, whoami, quests, skills

Ou direto:

    from src.core.database.objects  import object_name, object_icon
    from src.core.database.critters import state_label, goal_label
    from src.core.database.whoami   import npc_name
    from src.core.database.quests   import QUEST_FLAGS
    from src.core.database.skills   import SKILL_NAMES
"""

from src.core.database import objects, critters, whoami, quests, skills

__all__ = ["objects", "critters", "whoami", "quests", "skills"]
