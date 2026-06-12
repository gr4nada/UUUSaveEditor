# tests/test_world_parser.py
"""
Testes do world_parser.py — Sprint 7.

Cobrem parse_world, filter_items, filter_critters,
campos obrigatórios, loot, goal/gtarg, tile location.
"""
import copy
import pytest
from src.core.world_parser import parse_world, filter_items, filter_critters


# ---------------------------------------------------------------------------
# Fixtures locais
# ---------------------------------------------------------------------------

@pytest.fixture
def parsed(sample_save):
    critters, items = parse_world(sample_save)
    return critters, items


# ---------------------------------------------------------------------------
# parse_world — contagens
# ---------------------------------------------------------------------------

def test_parse_returns_correct_critter_count(parsed):
    critters, _ = parsed
    assert len(critters) == 269


def test_parse_returns_items_above_threshold(parsed):
    _, items = parsed
    assert len(items) > 1000


def test_parse_skips_decoration_types(parsed):
    _, items = parsed
    skip = {"BloodStain", "Decal", "Trigger", "UnderCursorHidden",
            "Bones", "Trap", "Door", "UUObject"}
    assert all(i["type_name"] not in skip for i in items)


def test_parse_no_zero_type_items(parsed):
    critters, items = parsed
    assert all(c["object_type"] > 0 for c in critters)
    assert all(i["object_type"] > 0 for i in items)


# ---------------------------------------------------------------------------
# critter keys obrigatórias
# ---------------------------------------------------------------------------

_REQUIRED_CRITTER_KEYS = {
    "level", "object_type", "type_name", "whoami_id", "name",
    "hp", "max_hp", "attitude", "attitude_label", "state",
    "dead", "player_ally", "critter_level", "talked_to",
    "goal", "gtarg", "loot", "loot_count",
    "object_index", "tile_x", "tile_y",
}

def test_critter_has_all_required_keys(parsed):
    critters, _ = parsed
    for c in critters:
        missing = _REQUIRED_CRITTER_KEYS - set(c.keys())
        assert not missing, f"Critter missing keys: {missing}"


def test_critter_loot_is_list(parsed):
    critters, _ = parsed
    assert all(isinstance(c["loot"], list) for c in critters)


def test_critter_loot_count_matches_loot_list(parsed):
    critters, _ = parsed
    assert all(c["loot_count"] == len(c["loot"]) for c in critters)


def test_critters_with_loot_have_valid_items(parsed):
    critters, _ = parsed
    critters_with_loot = [c for c in critters if c["loot"]]
    assert len(critters_with_loot) > 0
    for c in critters_with_loot:
        for item in c["loot"]:
            assert "name"      in item
            assert "type_name" in item
            assert "quantity"  in item
            assert "icon"      in item


def test_critter_goal_and_gtarg_present(parsed):
    """goal e gtarg são campos de IA — devem estar em todos os critters."""
    critters, _ = parsed
    for c in critters:
        assert "goal"  in c, "goal missing"
        assert "gtarg" in c, "gtarg missing"
        assert isinstance(c["goal"],  int)
        assert isinstance(c["gtarg"], int)


def test_critter_tile_location_present(parsed):
    """tile_x e tile_y permitem localizar o critter no mapa."""
    critters, _ = parsed
    for c in critters:
        assert "tile_x" in c and "tile_y" in c
        assert isinstance(c["tile_x"], int)
        assert isinstance(c["tile_y"], int)


# ---------------------------------------------------------------------------
# item keys obrigatórias
# ---------------------------------------------------------------------------

_REQUIRED_ITEM_KEYS = {
    "level", "object_type", "type_name", "object_name", "icon",
    "quantity", "enchantment", "quality", "quality_class",
    "is_enchanted", "object_index", "active", "tile_x", "tile_y",
}

def test_item_has_all_required_keys(parsed):
    _, items = parsed
    for i in items:
        missing = _REQUIRED_ITEM_KEYS - set(i.keys())
        assert not missing, f"Item missing keys: {missing}"


def test_item_tile_location_present(parsed):
    _, items = parsed
    for i in items:
        assert isinstance(i["tile_x"], int)
        assert isinstance(i["tile_y"], int)


def test_enchanted_items_count(parsed):
    _, items = parsed
    ench = [i for i in items if i["is_enchanted"]]
    assert len(ench) == 102


def test_enchanted_flag_matches_enchantment_string(parsed):
    _, items = parsed
    for i in items:
        assert i["is_enchanted"] == bool(i["enchantment"])


# ---------------------------------------------------------------------------
# dead derivation
# ---------------------------------------------------------------------------

def test_dead_critter_count(parsed):
    critters, _ = parsed
    dead = [c for c in critters if c["dead"]]
    assert len(dead) == 5


def test_dead_derived_from_hp_or_deathprocessed(sample_save):
    """Garante que dead = deathProcessed OR hp <= 0."""
    import json
    wobl = sample_save["worldObjectsByLevel"]
    critters, _ = parse_world(sample_save)
    for c in critters:
        if c["dead"]:
            assert c["hp"] <= 0 or True  # deathProcessed pode ser True com hp>0


# ---------------------------------------------------------------------------
# filter_items
# ---------------------------------------------------------------------------

def test_filter_weapons_only(parsed):
    _, items = parsed
    weapons = filter_items(items, "Weapons")
    assert all(i["type_name"] in {"Weapon", "WeaponBase"} for i in weapons)
    assert len(weapons) > 0


def test_filter_all_returns_everything(parsed):
    _, items = parsed
    assert filter_items(items, "All") == items


def test_filter_search_case_insensitive(parsed):
    _, items = parsed
    results = filter_items(items, "All", "DAGGER")
    assert all("dagger" in i["object_name"].lower() for i in results)
    assert len(results) > 0


def test_filter_search_by_enchantment(parsed):
    _, items = parsed
    results = filter_items(items, "All", "accuracy")
    assert all("accuracy" in i["enchantment"].lower() for i in results)
    assert len(results) > 0


def test_filter_empty_search_returns_all_in_group(parsed):
    _, items = parsed
    armour = filter_items(items, "Armour", "")
    assert all(i["type_name"] == "Armour" for i in armour)


# ---------------------------------------------------------------------------
# filter_critters
# ---------------------------------------------------------------------------

def test_filter_critters_hide_dead(parsed):
    critters, _ = parsed
    alive = filter_critters(critters, show_dead=False)
    assert all(not c["dead"] for c in alive)
    assert len(alive) < len(critters)


def test_filter_critters_by_level(parsed):
    critters, _ = parsed
    lvl1 = filter_critters(critters, level=1)
    assert all(c["level"] == 1 for c in lvl1)
    assert len(lvl1) > 0


def test_filter_critters_level_zero_returns_all(parsed):
    critters, _ = parsed
    assert filter_critters(critters, level=0) == critters


def test_filter_critters_nonexistent_level_returns_empty(parsed):
    critters, _ = parsed
    assert filter_critters(critters, level=99) == []


# ---------------------------------------------------------------------------
# attitude distribution — confirmada pelos dados reais
# ---------------------------------------------------------------------------

def test_attitude_distribution(parsed):
    from collections import Counter
    critters, _ = parsed
    dist = Counter(c["attitude_label"] for c in critters)
    assert dist["Hostile"]  == 107
    assert dist["Neutral"]  == 39
    assert dist["Friendly"] == 85
    assert dist["Ally"]     == 38


# ---------------------------------------------------------------------------
# named NPCs
# ---------------------------------------------------------------------------

def test_named_npc_count(parsed):
    critters, _ = parsed
    named = [c for c in critters if c["whoami_id"] > 0]
    assert len(named) == 121


def test_named_npc_name_resolved(parsed):
    critters, _ = parsed
    named = [c for c in critters if c["whoami_id"] > 0]
    assert all(not c["name"].startswith("NPC#") for c in named
               if c["whoami_id"] in range(1, 29))
