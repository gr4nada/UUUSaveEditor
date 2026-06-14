# src/core/models/objects.py
"""
GameObject — wrapper sobre nós com jsonData aninhado.

Cobre itens de inventário, world objects, containers e critters.
Garante parse único (cache), commit em cascata para containers aninhados,
e setters com clamp inline para campos críticos (hp, quantity).
"""
from __future__ import annotations
import json
import logging

logger = logging.getLogger("core.models.objects")

class GameObject:
    """
    Wrapper sobre um nó de objeto de jogo (item de inventário, world object, etc.)
    que possui um campo `jsonData` com uma string JSON aninhada.

    Uso:
        obj.parsed_data         # dict — faz parse de jsonData uma vez e cacheia
        obj.quantity            # lê de parsed_data, com fallback para o nó externo
        obj.quantity = 5        # escreve em ambos os níveis e re-serializa jsonData
        obj.commit()            # força a re-serialização de jsonData a partir de parsed_data

    Mutações em `parsed_data` (dict) só são persistidas em `jsonData` quando
    `commit()` é chamado — automaticamente disparado pelos setters desta classe.
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
                logger.warning("Falha ao decodificar jsonData de %r", self._node.get("objectName"))
                self._parsed = {}
        return self._parsed

    def commit(self) -> None:
        """
        Re-serializa parsed_data para jsonData, se já foi carregado.
        Propaga para o GameObject pai (se houver), já que o nó deste
        objeto pode viver dentro de parsed_data["contents"] do pai —
        sem propagar, a mudança ficaria presa no parsed_data em cache
        do pai e nunca chegaria ao jsonData persistido dele.
        """
        if self._parsed is not None:
            self._node["jsonData"] = json.dumps(self._parsed)
        if self._parent is not None:
            self._parent.commit()

    # — Campos comuns —
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
        """Retorna a lista `contents` real (node ou parsed_data), ou None se inexistente."""
        if "contents" in self._node:
            return self._node["contents"]
        if "contents" in self.parsed_data:
            return self.parsed_data["contents"]
        return None

    def delete_content(self, index: int) -> None:
        """Remove o item de índice `index` da lista `contents` deste container."""
        items = self._contents_list()
        if items is None or not (0 <= index < len(items)):
            logger.error("GameObject.delete_content: índice fora de alcance: %d", index)
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
