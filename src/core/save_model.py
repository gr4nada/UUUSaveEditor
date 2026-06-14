# src/core/save_model.py
"""
Re-exportador de compatibilidade.

Todos os imports externos continuam funcionando sem modificação:
    from src.core.save_model import PlayerModel, GameObject, SaveGame
    from src.core.save_model import ValidationError, FIELD_LIMITS

Os módulos reais vivem em src/core/models/.
"""
from src.core.models.primitives import ValidationError, FIELD_LIMITS, _clamp, _validate  # noqa: F401
from src.core.models.player     import PlayerModel   # noqa: F401
from src.core.models.objects    import GameObject    # noqa: F401
from src.core.models.game       import SaveGame      # noqa: F401
from src.core.models.world      import CritterModel  # noqa: F401

__all__ = [
    "ValidationError", "FIELD_LIMITS",
    "PlayerModel", "GameObject", "SaveGame", "CritterModel",
]
