# src/core/models/objects.py
"""
GameObject — wrapper over nodes with nested jsonData.

Covers inventory items, world objects, containers, and critters.
Ensures single parse (cached), cascade commit for nested containers,
and setters with inline clamp for critical fields (hp, quantity).
"""
from __future__ import annotations
import json
import logging

logger = logging.getLogger("core.models.objects")

class GameObject:
    """
    Wrapper over a game object node (inventory item, world object, etc.)
    that has a `jsonData` field with nested JSON string.

    Usage:
        obj.parsed_data         # dict — parses jsonData once and caches
        obj.quantity            # reads from parsed_data, with fallback to external node
        obj.quantity = 5        # writes to both levels and re-serializes jsonData
        obj.commit()            # forces re-serialization of jsonData from parsed_data

    Mutations to `parsed_data` (dict) are only persisted to `jsonData` when
    `commit()` is called — automatically triggered by setters in this class.
    """

    def __init__(self, node: dict, _parent: "GameObject | None" = None) -> None:
        self._node = node
        self._parsed: dict | None = None
        self._parent = _parent

    @property
    def raw(self) -> dict:
        return self._node

    @property
    def parsed_data(self) -> dict:
        if self._parsed is None:
            raw = self._node.get("jsonData", "")
            try:
                self._parsed = json.loads(raw) if raw else {}
            except Exception:
                logger.warning("Failed to decode jsonData from %r", self._node.get("objectName"))
                self._parsed = {}
        return self._parsed

    def commit(self) -> None:
        """
        Re-serializes parsed_data to jsonData, if already loaded.
        Propagates to parent GameObject (if any), since this object's node
        may live inside the parent's parsed_data["contents"] — without
        propagating, the change would be stuck in the parent's cached
        parsed_data and never reach its persisted jsonData.
        """
        if self._parsed is not None:
            self._node["jsonData"] = json.dumps(self._parsed)
        if self._parent is not None:
            self._parent.commit()

    # — Common fields —
    @property
    def object_name(self) -> str:
        return self._node.get("objectName") or self.parsed_data.get("objectName", "") or ""

    @property
    def object_type_name(self) -> str:
        return self._node.get("objectTypeName", "")

    @property
    def object_type(self) -> int:
        return int(self._node.get("objectType", self.parsed_data.get("objectType", 0)))

    @property
    def quantity(self) -> int:
        return int(self.parsed_data.get("quantity", self._node.get("quantity", 1)))

    @quantity.setter
    def quantity(self, value: int) -> None:
        value = max(1, int(value))
        if "quantity" in self._node:
            self._node["quantity"] = value
        self.parsed_data["quantity"] = value
        self.commit()

    @property
    def enchantment(self) -> str:
        return self.parsed_data.get("enchantmentName", "") or ""

    @property
    def contents(self) -> list[GameObject]:
        items = self._node.get("contents") or self.parsed_data.get("contents") or []
        return [GameObject(it, _parent=self) for it in items]

    @property
    def contents_count(self) -> int:
        items = self._node.get("contents") or self.parsed_data.get("contents") or []
        return len(items)

    def _contents_list(self) -> list | None:
        """Returns the real `contents` list (node or parsed_data), or None if nonexistent."""
        if "contents" in self._node:
            return self._node["contents"]
        if "contents" in self.parsed_data:
            return self.parsed_data["contents"]
        return None

    def delete_content(self, index: int) -> None:
        """Removes item at index `index` from this container's `contents` list."""
        items = self._contents_list()
        if items is None or not (0 <= index < len(items)):
            logger.error("GameObject.delete_content: index out of range: %d", index)
            return
        removed = items.pop(index)
        self.commit()
        logger.info("Content #%d removed from %r: %r", index, self.object_name, removed.get("objectName"))

    # — Critters (campos lidos/escritos em parsed_data) —
    @property
    def hp(self) -> int:
        return int(self.parsed_data.get("hp", 0))

    @hp.setter
    def hp(self, value: int) -> None:
        """
        Ajusta o HP da criatura. Clampa em [0, originalHp] quando originalHp
        é conhecido, para evitar valores fora de faixa (overheal silencioso).
        Setar para 0 também marca deathProcessed, igual ao comportamento do jogo.
        """
        value = int(value)
        max_hp = self.parsed_data.get("originalHp", value)
        value = max(0, min(value, max_hp) if max_hp else value)
        self.parsed_data["hp"] = value
        if value <= 0:
            self.parsed_data["deathProcessed"] = True
        self.commit()

    @property
    def is_dead(self) -> bool:
        return bool(self.parsed_data.get("deathProcessed", False)) or self.hp <= 0

    def revive(self, hp: int | None = None) -> None:
        """Marca a criatura como viva, restaurando HP (default: originalHp ou 1)."""
        restored = hp if hp is not None else self.parsed_data.get("originalHp", 1)
        self.parsed_data["deathProcessed"] = False
        self.parsed_data["hp"] = max(1, int(restored))
        self.commit()

    def kill(self) -> None:
        """Marca a criatura como morta (hp=0, deathProcessed=True)."""
        self.parsed_data["hp"] = 0
        self.parsed_data["deathProcessed"] = True
        self.commit()


# ---------------------------------------------------------------------------
# SaveGame — ponto de entrada único
# ---------------------------------------------------------------------------
