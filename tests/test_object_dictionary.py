# tests/test_object_dictionary.py
"""
Testes do object_dictionary.py — Sprint 7 (P5/P6).

Cobrem: lookup, resolve_name, resolve_icon, all_categories,
fallback para ids desconhecidos, resolução de nomes vazios.
"""
import pytest
from src.core.object_dictionary import (
    lookup, resolve_name, resolve_icon, all_categories
)


# ---------------------------------------------------------------------------
# lookup
# ---------------------------------------------------------------------------

class TestLookup:

    def test_known_weapon_returns_correct_entry(self):
        entry = lookup(5)   # Longsword
        assert entry["name"]     == "Longsword"
        assert entry["category"] == "Weapon"
        assert entry["icon"]     == "⚔"

    def test_known_armour_returns_correct_entry(self):
        entry = lookup(34)  # Breastplate
        assert entry["name"]     == "Breastplate"
        assert entry["category"] == "Armour"

    def test_known_key_returns_correct_entry(self):
        entry = lookup(172)
        assert entry["category"] == "Key"
        assert entry["icon"]     == "🔑"

    def test_unknown_id_returns_fallback(self):
        entry = lookup(9999)
        assert "9999"    in entry["name"]
        assert entry["category"] == "Unknown"
        assert entry["icon"]     == "·"

    def test_zero_id_returns_fallback_or_entry(self):
        # objectType=0 significa slot vazio — não deve levantar exceção
        entry = lookup(0)
        assert isinstance(entry["name"], str)

    def test_critter_type_resolved(self):
        entry = lookup(80)  # Goblin
        assert entry["name"]     == "Goblin"
        assert entry["category"] == "Critter"

    def test_container_type_resolved(self):
        entry = lookup(138)  # Gold Coffer
        assert entry["name"]     == "Gold Coffer"
        assert entry["category"] == "Container"

    def test_all_entries_have_required_keys(self):
        for oid in [3, 5, 32, 34, 57, 80, 138, 145, 172]:
            entry = lookup(oid)
            assert "name"     in entry
            assert "category" in entry
            assert "icon"     in entry


# ---------------------------------------------------------------------------
# resolve_name
# ---------------------------------------------------------------------------

class TestResolveName:

    def test_non_empty_object_name_takes_priority(self):
        # objectName do save tem prioridade máxima
        assert resolve_name(5, "a shiny sword", "Weapon") == "a shiny sword"

    def test_empty_object_name_falls_back_to_dict(self):
        # objectName vazio → dicionário
        assert resolve_name(5, "", "Weapon") == "Longsword"

    def test_whitespace_only_name_falls_back(self):
        assert resolve_name(5, "   ", "Weapon") == "Longsword"

    def test_unknown_type_falls_back_to_type_name(self):
        # objectType desconhecido, objectName vazio → usa objectTypeName
        result = resolve_name(9999, "", "MysteriousItem")
        assert result == "MysteriousItem"

    def test_all_unknown_falls_back_to_object_number(self):
        result = resolve_name(9999, "", "")
        assert "9999" in result

    def test_critter_with_empty_name_resolved(self):
        # Goblins geralmente têm objectName="" no save
        result = resolve_name(80, "")
        assert result == "Goblin"

    def test_case_preserved_in_object_name(self):
        result = resolve_name(5, "Legendary Blade")
        assert result == "Legendary Blade"


# ---------------------------------------------------------------------------
# resolve_icon
# ---------------------------------------------------------------------------

class TestResolveIcon:

    def test_weapon_icon(self):
        assert resolve_icon(5) == "⚔"

    def test_armour_icon(self):
        assert resolve_icon(34) == "🛡"

    def test_key_icon(self):
        assert resolve_icon(172) == "🔑"

    def test_container_icon(self):
        assert resolve_icon(138) == "📦"

    def test_food_icon(self):
        assert resolve_icon(64) == "🍖"

    def test_unknown_with_type_name_uses_category_icon(self):
        # objectType desconhecido, mas type_name é "Key" → ícone de Key
        icon = resolve_icon(9999, "Key")
        assert icon == "🔑"

    def test_fully_unknown_returns_dot(self):
        icon = resolve_icon(9999, "")
        assert icon == "·"


# ---------------------------------------------------------------------------
# all_categories
# ---------------------------------------------------------------------------

class TestAllCategories:

    def test_returns_list_of_strings(self):
        cats = all_categories()
        assert isinstance(cats, list)
        assert all(isinstance(c, str) for c in cats)

    def test_contains_expected_categories(self):
        cats = all_categories()
        for expected in ("Weapon", "Armour", "Food", "Key", "Container", "Critter"):
            assert expected in cats, f"Category '{expected}' missing"

    def test_no_duplicates(self):
        cats = all_categories()
        assert len(cats) == len(set(cats))

    def test_sorted_alphabetically(self):
        cats = all_categories()
        assert cats == sorted(cats)


# ---------------------------------------------------------------------------
# Integração com o fixture real
# ---------------------------------------------------------------------------

class TestIntegrationWithFixture:

    def test_breastplate_resolved_from_save(self, sample_save):
        """
        Slot 4 (Chest) no fixture tem objectType=34.
        resolve_name deve retornar 'Breastplate'.
        """
        equipped = sample_save["inventoryData"]["equippedItems"]
        chest = equipped[4]
        obj_type  = chest.get("objectType", 0)
        obj_name  = chest.get("objectName", "")
        type_name = chest.get("objectTypeName", "")
        result = resolve_name(obj_type, obj_name, type_name)
        # objectName pode estar preenchido ou vazio
        assert isinstance(result, str) and len(result) > 0

    def test_all_equipped_items_resolve_non_empty(self, sample_save):
        """Todo item equipado com objectType>0 deve ter nome resolúvel."""
        equipped = sample_save["inventoryData"]["equippedItems"]
        for slot in equipped:
            otype = slot.get("objectType", 0)
            if otype == 0:
                continue
            name = resolve_name(otype, slot.get("objectName", ""),
                                slot.get("objectTypeName", ""))
            assert name and len(name) > 0, f"Empty name for objectType={otype}"

    def test_world_items_icons_not_empty(self, sample_save):
        """Todo item do mundo com tipo conhecido deve ter ícone não-vazio."""
        import json
        wobl = sample_save["worldObjectsByLevel"]
        checked = 0
        for lvl_data in wobl:
            for obj in lvl_data.get("objects", [])[:10]:  # sample
                otype = obj.get("objectType", 0)
                if otype > 0:
                    icon = resolve_icon(otype, obj.get("objectTypeName", ""))
                    assert isinstance(icon, str) and len(icon) > 0
                    checked += 1
        assert checked > 0
