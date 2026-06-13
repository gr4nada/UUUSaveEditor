# tests/test_save_model.py
"""
Cobertura para src/core/save_model.py — PlayerModel, GameObject e SaveGame.

Esses wrappers são o ponto único de acesso ao save (Sprint 2). Como eles
fazem leitura/escrita com side-effects sobre o dict original (incluindo
re-serialização de jsonData), cada getter/setter merece teste próprio —
é exatamente onde corrupção silenciosa de save apareceria.
"""
import copy
import json
import logging

import pytest

from src.core.save_model import SaveGame, PlayerModel, GameObject
from src.core.database.skills import SKILL_NAMES
from src.core.database.quests import QUEST_FLAGS
from src.core.save_diff import SaveDiff

logger = logging.getLogger("tests.test_save_model")


# ---------------------------------------------------------------------------
# PlayerModel — atributos simples (getter/setter refletem no dict original)
# ---------------------------------------------------------------------------

def test_player_simple_getters_match_raw_dict(sample_save, player):
    p = sample_save["playerData"]
    assert player.name == p["playerName"]
    assert player.level == p["charLevel"]
    assert player.hp == p["hp"]
    assert player.female == p["female"]
    assert player.left_handed == p["leftHanded"]


@pytest.mark.parametrize("prop,raw_key,value", [
    ("name", "playerName", "New Name"),
    ("level", "charLevel", 42),
    ("hp", "hp", 999),
    ("vitality", "vitality", 250),
    ("mana", "mana", 80),
    ("strength", "strength", 30),
    ("xp", "xp", 123456),
    ("poison", "poison", 5),
])
def test_player_setters_write_through_to_raw_dict(sample_save, player, prop, raw_key, value):
    """Setters do PlayerModel devem refletir imediatamente no dict original (sem cópia)."""
    setattr(player, prop, value)
    assert sample_save["playerData"][raw_key] == value


def test_player_numeric_setters_coerce_to_int(player):
    player.hp = "150"
    assert player.hp == 150
    assert isinstance(player.hp, int)


def test_player_bool_setters_coerce_to_bool(sample_save, player):
    player.female = 1
    assert sample_save["playerData"]["female"] is True

    player.left_handed = 0
    assert sample_save["playerData"]["leftHanded"] is False


def test_player_class_name_known_value(player):
    assert player.player_class_name == "Fighter"


def test_player_class_name_unknown_value_returns_unknown(sample_save, player):
    sample_save["playerData"]["playerClass"] = 9999
    assert player.player_class_name == "Unknown"


# ---------------------------------------------------------------------------
# PlayerModel — skills
# ---------------------------------------------------------------------------

def test_get_all_skills_returns_every_known_skill(player):
    skills = player.get_all_skills()
    assert set(skills.keys()) == set(SKILL_NAMES)
    assert all(isinstance(v, int) for v in skills.values())


def test_get_skill_unknown_name_returns_zero(player):
    assert player.get_skill("NotARealSkill") == 0


def test_set_skill_writes_through_and_get_all_skills_reflects_it(sample_save, player):
    player.set_skill("Sword", 30)
    assert player.get_skill("Sword") == 30
    assert player.get_all_skills()["Sword"] == 30

    idx = SKILL_NAMES.index("Sword")
    assert sample_save["playerData"]["skill"][idx] == 30


def test_set_skill_expands_truncated_skill_array(sample_save, player):
    """Se o array `skill` vier truncado do save, set_skill deve expandi-lo com zeros, não crashar."""
    sample_save["playerData"]["skill"] = sample_save["playerData"]["skill"][:2]
    last_skill = SKILL_NAMES[-1]

    player.set_skill(last_skill, 15)

    assert player.get_skill(last_skill) == 15
    assert len(sample_save["playerData"]["skill"]) == len(SKILL_NAMES)


def test_set_skill_unknown_name_is_noop(sample_save, player):
    before = copy.deepcopy(sample_save["playerData"]["skill"])
    player.set_skill("NotARealSkill", 99)
    assert sample_save["playerData"]["skill"] == before


# ---------------------------------------------------------------------------
# PlayerModel — quest flags
# ---------------------------------------------------------------------------

def test_quest_flags_getter_returns_raw_list(sample_save, player):
    assert player.quest_flags == sample_save["playerData"]["questFlags"]


def test_get_quest_flags_by_name_covers_all_known_flags(player):
    flags = player.get_quest_flags_by_name()
    assert set(flags.keys()) == {q["flag"] for q in QUEST_FLAGS}
    assert all(isinstance(v, bool) for v in flags.values())


def test_quest_flags_setter_overwrites_only_known_ids(sample_save, player):
    """
    O setter deve sobrescrever apenas os IDs declarados em QUEST_FLAGS,
    preservando IDs fora do conhecimento do editor (lista pode ser maior
    do que QUEST_FLAGS).
    """
    original = list(sample_save["playerData"]["questFlags"])
    max_known_id = max(q["id"] for q in QUEST_FLAGS)
    extra_idx = max_known_id + 1
    assert extra_idx < len(original), "fixture deveria ter flags extras além das conhecidas"
    sentinel = original[extra_idx]

    target_flag = QUEST_FLAGS[0]["flag"]
    new_flags = player.get_quest_flags_by_name()
    new_flags[target_flag] = not new_flags[target_flag]

    player.quest_flags = new_flags

    updated = sample_save["playerData"]["questFlags"]
    assert updated[QUEST_FLAGS[0]["id"]] == new_flags[target_flag]
    # Flag fora do escopo do editor não foi tocada
    assert updated[extra_idx] == sentinel


def test_quest_flags_setter_expands_truncated_list(sample_save, player):
    """Lista de questFlags menor que o maior ID conhecido deve ser expandida com False."""
    sample_save["playerData"]["questFlags"] = [True, False]

    target_flag = QUEST_FLAGS[-1]["flag"]  # maior ID conhecido
    flags = {q["flag"]: False for q in QUEST_FLAGS}
    flags[target_flag] = True

    player.quest_flags = flags

    qlist = sample_save["playerData"]["questFlags"]
    max_id = max(q["id"] for q in QUEST_FLAGS)
    assert len(qlist) == max_id + 1
    assert qlist[QUEST_FLAGS[-1]["id"]] is True
    # IDs conhecidos em `flags` mas não setados para True ficam False —
    # mesmo que a posição original (índice 0/1) tivesse outro valor antes
    # da expansão, o dict completo passado sobrescreve todos os IDs conhecidos.
    assert qlist[QUEST_FLAGS[0]["id"]] is False


def test_quest_flags_setter_partial_dict_only_updates_given_keys(sample_save, player):
    """Se o dict passado não contém todos os flags, os ausentes permanecem inalterados."""
    before = list(player.quest_flags)
    first_flag = QUEST_FLAGS[0]["flag"]
    current = player.get_quest_flags_by_name()[first_flag]

    player.quest_flags = {first_flag: not current}

    after = player.quest_flags
    assert after[QUEST_FLAGS[0]["id"]] != before[QUEST_FLAGS[0]["id"]]
    # demais IDs conhecidos não mudaram
    for q in QUEST_FLAGS[1:]:
        assert after[q["id"]] == before[q["id"]]


# ---------------------------------------------------------------------------
# PlayerModel — magic / cast spells
# ---------------------------------------------------------------------------

def test_cast_spells_getter_returns_copy(sample_save, player):
    spells = player.cast_spells
    assert spells == sample_save["playerData"]["magicData"]["castSpells"]

    # Deve ser uma cópia — mutar o retorno não pode afetar o save
    spells[0] = not spells[0]
    assert spells != sample_save["playerData"]["magicData"]["castSpells"]


def test_cast_spells_setter_writes_through(sample_save, player):
    new_spells = [True] * len(player.cast_spells)
    player.cast_spells = new_spells
    assert sample_save["playerData"]["magicData"]["castSpells"] == new_spells


def test_cast_spells_setter_empty_list_is_noop(sample_save, player):
    """Lista vazia significa 'não alterar magicData' — usado pelo SavePayload default."""
    before = copy.deepcopy(sample_save["playerData"]["magicData"])
    player.cast_spells = []
    assert sample_save["playerData"]["magicData"] == before


def test_cast_spells_setter_creates_magic_data_if_missing(sample_save, player):
    del sample_save["playerData"]["magicData"]
    player.cast_spells = [True, False, True]
    assert sample_save["playerData"]["magicData"]["castSpells"] == [True, False, True]


# ---------------------------------------------------------------------------
# GameObject — wrapper sobre nós com jsonData
# ---------------------------------------------------------------------------

def test_game_object_parsed_data_matches_jsondata(sample_save):
    node = sample_save["inventoryData"]["mainInventory"][0]
    obj = GameObject(node)
    assert obj.parsed_data == json.loads(node["jsonData"])


def test_game_object_parsed_data_is_cached(sample_save):
    node = sample_save["inventoryData"]["mainInventory"][0]
    obj = GameObject(node)
    first = obj.parsed_data
    second = obj.parsed_data
    assert first is second  # mesmo objeto — não re-parseia


def test_game_object_handles_missing_jsondata():
    obj = GameObject({"objectName": "Custom", "objectType": 1})
    assert obj.parsed_data == {}
    assert obj.object_name == "Custom"
    assert obj.quantity == 1  # fallback default


def test_game_object_handles_malformed_jsondata(caplog):
    obj = GameObject({"objectName": "Broken", "jsonData": "{not valid json"})
    with caplog.at_level(logging.WARNING, logger="core.save_model"):
        assert obj.parsed_data == {}
    assert obj.object_name == "Broken"


def test_game_object_quantity_getter_prefers_parsed_data(sample_save):
    node = sample_save["inventoryData"]["mainInventory"][0]
    obj = GameObject(node)
    expected = json.loads(node["jsonData"])["quantity"]
    assert obj.quantity == expected


def test_game_object_quantity_setter_updates_jsondata_and_node(sample_save):
    node = sample_save["inventoryData"]["mainInventory"][0]
    obj = GameObject(node)

    obj.quantity = 7

    assert obj.quantity == 7
    assert json.loads(node["jsonData"])["quantity"] == 7


def test_game_object_quantity_setter_clamps_to_minimum_one(sample_save):
    node = sample_save["inventoryData"]["mainInventory"][0]
    obj = GameObject(node)

    obj.quantity = 0
    assert obj.quantity == 1

    obj.quantity = -5
    assert obj.quantity == 1


def test_game_object_quantity_setter_does_not_corrupt_other_jsondata_fields(sample_save):
    """Setar quantity não deve apagar outros campos dentro de jsonData (ex: posição, flags)."""
    node = sample_save["inventoryData"]["mainInventory"][0]
    before = json.loads(node["jsonData"])

    obj = GameObject(node)
    obj.quantity = 5

    after = json.loads(node["jsonData"])
    for key in before:
        if key == "quantity":
            continue
        assert after[key] == before[key], f"campo '{key}' foi alterado inesperadamente"


def test_game_object_commit_without_parsed_data_access_is_noop(sample_save):
    """commit() sem nunca ter acessado parsed_data não deve tocar jsonData."""
    node = sample_save["inventoryData"]["mainInventory"][0]
    before = node["jsonData"]

    obj = GameObject(node)
    obj.commit()

    assert node["jsonData"] == before


def test_game_object_contents_returns_wrapped_children(sample_save):
    # Item 0 do fixture é um container ("a pack") com contents
    node = sample_save["inventoryData"]["mainInventory"][0]
    obj = GameObject(node)

    assert obj.contents_count > 0
    contents = obj.contents
    assert len(contents) == obj.contents_count
    assert all(isinstance(c, GameObject) for c in contents)
    assert contents[0].object_name  # objetos aninhados também são utilizáveis


def test_game_object_contents_count_zero_for_non_container(sample_save):
    items = sample_save["inventoryData"]["mainInventory"]
    leaf = next(GameObject(it) for it in items if not (it.get("contents") or
                json.loads(it.get("jsonData", "{}") or "{}").get("contents")))
    assert leaf.contents_count == 0
    assert leaf.contents == []


# ---------------------------------------------------------------------------
# SaveGame — metadados, main_inventory, equipped_items, world, dungeon_level
# ---------------------------------------------------------------------------

def test_save_game_metadata(sample_save, save_game):
    assert save_game.slot_name == sample_save["slotName"]
    assert save_game.display_name == sample_save["displayName"]
    assert save_game.saved_at == sample_save["savedAtIso"]
    assert save_game.version == str(sample_save["version"])


def test_save_game_dungeon_level(sample_save, save_game):
    assert save_game.dungeon_level == sample_save["currentLevel"]


def test_save_game_raw_is_same_object(sample_save, save_game):
    assert save_game.raw is sample_save


def test_main_inventory_returns_game_objects(sample_save, save_game):
    items = save_game.main_inventory
    assert len(items) == len(sample_save["inventoryData"]["mainInventory"])
    assert all(isinstance(i, GameObject) for i in items)


def test_main_inventory_mutation_reflects_in_raw(sample_save, save_game):
    save_game.main_inventory[0].quantity = 3
    assert json.loads(sample_save["inventoryData"]["mainInventory"][0]["jsonData"])["quantity"] == 3


def test_delete_main_inventory_item_removes_correct_entry(sample_save, save_game):
    target_name = save_game.main_inventory[1].object_name
    before_len = len(sample_save["inventoryData"]["mainInventory"])

    save_game.delete_main_inventory_item(0)

    after = sample_save["inventoryData"]["mainInventory"]
    assert len(after) == before_len - 1
    # O item que era índice 1 agora é índice 0
    assert GameObject(after[0]).object_name == target_name


def test_delete_main_inventory_item_out_of_range_is_noop(sample_save, save_game, caplog):
    before = copy.deepcopy(sample_save["inventoryData"]["mainInventory"])
    with caplog.at_level(logging.ERROR, logger="core.save_model"):
        save_game.delete_main_inventory_item(9999)
    assert sample_save["inventoryData"]["mainInventory"] == before


def test_delete_main_inventory_item_negative_index_is_noop(sample_save, save_game):
    before = copy.deepcopy(sample_save["inventoryData"]["mainInventory"])
    save_game.delete_main_inventory_item(-1)
    assert sample_save["inventoryData"]["mainInventory"] == before


def test_equipped_items_returns_eleven_slots(save_game):
    equipped = save_game.equipped_items
    assert len(equipped) == 11
    assert all(isinstance(i, GameObject) for i in equipped)


def test_equipped_items_object_type_matches_raw(sample_save, save_game):
    raw_equipped = sample_save["inventoryData"]["equippedItems"]
    for obj, raw in zip(save_game.equipped_items, raw_equipped):
        assert obj.object_type == raw.get("objectType", 0)


def test_world_objects_by_level_matches_raw(sample_save, save_game):
    assert save_game.world_objects_by_level == sample_save["worldObjectsByLevel"]


def test_parse_world_returns_critters_and_items(save_game):
    critters, items = save_game.parse_world()
    assert isinstance(critters, list)
    assert isinstance(items, list)
    assert len(critters) > 0
    assert len(items) > 0


# ---------------------------------------------------------------------------
# Isolamento: mutações via SaveGame não afetam blocos não relacionados
# ---------------------------------------------------------------------------

def test_player_mutations_do_not_affect_world_or_inventory(sample_save, save_game):
    world_before = copy.deepcopy(sample_save["worldObjectsByLevel"])
    inventory_before = copy.deepcopy(sample_save["inventoryData"])

    save_game.player.hp = 1
    save_game.player.quest_flags = {QUEST_FLAGS[0]["flag"]: True}
    save_game.player.cast_spells = [True] * len(save_game.player.cast_spells)

    assert sample_save["worldObjectsByLevel"] == world_before
    assert sample_save["inventoryData"] == inventory_before


def test_inventory_mutations_do_not_affect_player_data(sample_save, save_game):
    player_before = copy.deepcopy(sample_save["playerData"])

    save_game.main_inventory[0].quantity = 50
    save_game.delete_main_inventory_item(1)

    assert sample_save["playerData"] == player_before


def test_full_save_remains_json_serializable_after_mutations(sample_save, save_game):
    """Garantia final: depois de várias mutações via SaveGame, o dict ainda serializa."""
    save_game.player.hp = 500
    save_game.player.quest_flags = save_game.player.get_quest_flags_by_name()
    save_game.player.cast_spells = save_game.player.cast_spells
    save_game.main_inventory[0].quantity = 2
    save_game.delete_main_inventory_item(0)

    serialized = json.dumps(sample_save)
    restored = json.loads(serialized)
    assert restored == sample_save


# ---------------------------------------------------------------------------
# GameObject — hp / is_dead / revive / kill (critters em worldObjectsByLevel)
# ---------------------------------------------------------------------------

def _first_alive_critter_node(sample_save):
    """Retorna o jsonData-node de um critter vivo com originalHp > 1, para testes de HP."""
    from src.core.save_model import SaveGame
    sg = SaveGame(sample_save)
    critters, _ = sg.parse_world()
    alive = next(c for c in critters if not c["dead"] and c["max_hp"] > 1)
    return alive["_node"]


def _first_dead_critter_node(sample_save):
    from src.core.save_model import SaveGame
    sg = SaveGame(sample_save)
    critters, _ = sg.parse_world()
    dead = next(c for c in critters if c["dead"])
    return dead["_node"]


def test_game_object_hp_getter_reads_parsed_data(sample_save):
    node = _first_alive_critter_node(sample_save)
    obj = GameObject(node)
    assert obj.hp == obj.parsed_data["hp"]
    assert obj.hp > 0


def test_game_object_hp_setter_writes_through(sample_save):
    node = _first_alive_critter_node(sample_save)
    obj = GameObject(node)

    obj.hp = 10

    assert obj.hp == 10
    assert json.loads(node["jsonData"])["hp"] == 10


def test_game_object_hp_setter_clamps_to_original_hp(sample_save):
    """HP não pode exceder originalHp — evita 'overheal' fora de faixa."""
    node = _first_alive_critter_node(sample_save)
    obj = GameObject(node)
    max_hp = obj.parsed_data["originalHp"]

    obj.hp = max_hp + 9999

    assert obj.hp == max_hp


def test_game_object_hp_setter_clamps_to_zero_minimum(sample_save):
    node = _first_alive_critter_node(sample_save)
    obj = GameObject(node)

    obj.hp = -50

    assert obj.hp == 0


def test_game_object_hp_setter_zero_marks_death_processed(sample_save):
    node = _first_alive_critter_node(sample_save)
    obj = GameObject(node)

    obj.hp = 0

    assert obj.is_dead is True
    assert obj.parsed_data["deathProcessed"] is True


def test_game_object_hp_setter_positive_does_not_force_alive(sample_save):
    """Setar hp > 0 não limpa deathProcessed sozinho — revive() é o caminho explícito."""
    node = _first_alive_critter_node(sample_save)
    obj = GameObject(node)
    obj.parsed_data["deathProcessed"] = True
    obj.commit()

    obj.hp = 20

    assert obj.hp == 20
    assert obj.parsed_data["deathProcessed"] is True


def test_game_object_is_dead_true_when_hp_zero_even_without_flag(sample_save):
    node = _first_alive_critter_node(sample_save)
    obj = GameObject(node)
    obj.parsed_data["hp"] = 0
    obj.parsed_data["deathProcessed"] = False
    obj.commit()

    assert obj.is_dead is True


def test_game_object_is_dead_false_for_alive_critter(sample_save):
    node = _first_alive_critter_node(sample_save)
    obj = GameObject(node)
    assert obj.is_dead is False


def test_game_object_revive_default_restores_original_hp(sample_save):
    node = _first_dead_critter_node(sample_save)
    obj = GameObject(node)
    max_hp = obj.parsed_data.get("originalHp", 1)

    obj.revive()

    assert obj.is_dead is False
    assert obj.hp == max(1, max_hp)
    assert json.loads(node["jsonData"])["deathProcessed"] is False


def test_game_object_revive_with_explicit_hp(sample_save):
    node = _first_dead_critter_node(sample_save)
    obj = GameObject(node)

    obj.revive(hp=33)

    assert obj.hp == 33
    assert obj.is_dead is False


def test_game_object_revive_clamps_to_minimum_one(sample_save):
    node = _first_dead_critter_node(sample_save)
    obj = GameObject(node)

    obj.revive(hp=0)

    assert obj.hp == 1
    assert obj.is_dead is False


def test_game_object_kill_sets_hp_zero_and_death_flag(sample_save):
    node = _first_alive_critter_node(sample_save)
    obj = GameObject(node)

    obj.kill()

    assert obj.hp == 0
    assert obj.is_dead is True
    parsed = json.loads(node["jsonData"])
    assert parsed["hp"] == 0
    assert parsed["deathProcessed"] is True


def test_game_object_kill_then_revive_roundtrip(sample_save):
    node = _first_alive_critter_node(sample_save)
    obj = GameObject(node)
    original_hp = obj.hp

    obj.kill()
    assert obj.is_dead is True

    obj.revive(hp=original_hp)
    assert obj.is_dead is False
    assert obj.hp == original_hp


def test_game_object_hp_methods_do_not_corrupt_other_fields(sample_save):
    """kill/revive/hp não devem apagar outros campos de jsonData (posição, attitude, etc.)."""
    node = _first_alive_critter_node(sample_save)
    before = json.loads(node["jsonData"])

    obj = GameObject(node)
    obj.kill()
    obj.revive()
    obj.hp = 5

    after = json.loads(node["jsonData"])
    for key in before:
        if key in ("hp", "deathProcessed"):
            continue
        assert after[key] == before[key], f"campo '{key}' foi alterado inesperadamente"


def test_game_object_hp_getter_default_zero_when_absent():
    """Item sem campo 'hp' em jsonData (não é critter) retorna 0, não explode."""
    obj = GameObject({"objectName": "Rock", "jsonData": "{}"})
    assert obj.hp == 0
    assert obj.is_dead is True  # hp <= 0


# ---------------------------------------------------------------------------
# GameObject — contents recursivos (containers do Main Inventory)
# ---------------------------------------------------------------------------

def _first_container(save_game):
    """Retorna o primeiro GameObject do main_inventory com contents não vazios."""
    return next(o for o in save_game.main_inventory if o.contents_count > 0)


def test_contents_children_are_game_objects(save_game):
    container = _first_container(save_game)
    children = container.contents
    assert len(children) == container.contents_count
    assert all(isinstance(c, GameObject) for c in children)
    assert all(c.object_name for c in children)


def test_nested_quantity_edit_persists_after_refetch(sample_save, save_game):
    """
    Editar a quantidade de um item dentro de um container deve refletir em
    jsonData do container pai, mesmo quando o pai é re-obtido do zero
    (nova instância de GameObject, sem cache compartilhado).
    """
    container = _first_container(save_game)
    child = container.contents[0]
    new_qty = child.quantity + 3

    child.quantity = new_qty

    # Re-busca tudo do zero — sem reaproveitar instâncias antigas
    container2 = next(o for o in save_game.main_inventory if o.object_name == container.object_name
                       and o.contents_count == container.contents_count)
    child2 = container2.contents[0]
    assert child2.quantity == new_qty

    # E confere diretamente no JSON persistido do container
    parent_json = json.loads(container.raw["jsonData"])
    child_json = json.loads(parent_json["contents"][0]["jsonData"])
    assert child_json["quantity"] == new_qty


def test_nested_quantity_edit_does_not_corrupt_siblings(save_game):
    container = _first_container(save_game)
    if container.contents_count < 2:
        pytest.skip("fixture container precisa de >=2 itens para este teste")

    siblings_before = [c.quantity for c in container.contents]

    container.contents[0].quantity = siblings_before[0] + 5

    siblings_after = [c.quantity for c in container.contents]
    assert siblings_after[0] == siblings_before[0] + 5
    assert siblings_after[1:] == siblings_before[1:]


def test_delete_content_removes_correct_child(save_game):
    container = _first_container(save_game)
    before_count = container.contents_count
    target_name = container.contents[1].object_name if before_count > 1 else None

    container.delete_content(0)

    assert container.contents_count == before_count - 1
    if target_name is not None:
        assert container.contents[0].object_name == target_name


def test_delete_content_persists_to_jsondata(save_game):
    container = _first_container(save_game)
    before_count = container.contents_count

    container.delete_content(0)

    parsed = json.loads(container.raw["jsonData"])
    assert len(parsed["contents"]) == before_count - 1


def test_delete_content_out_of_range_is_noop(save_game, caplog):
    container = _first_container(save_game)
    before = container.contents_count
    with caplog.at_level(logging.ERROR, logger="core.save_model"):
        container.delete_content(9999)
    assert container.contents_count == before


def test_delete_content_negative_index_is_noop(save_game):
    container = _first_container(save_game)
    before = container.contents_count
    container.delete_content(-1)
    assert container.contents_count == before


def test_main_inventory_full_roundtrip_remains_serializable(sample_save, save_game):
    """Mutações aninhadas (edit + delete em containers) preservam serialização do save inteiro."""
    container = _first_container(save_game)
    container.contents[0].quantity = 42
    container.delete_content(1) if container.contents_count > 1 else None

    serialized = json.dumps(sample_save)
    restored = json.loads(serialized)
    assert restored == sample_save


def test_commit_cascades_to_parent_without_explicit_call(save_game):
    """
    Sprint: editar um filho não deve exigir parent.commit() manual — o
    cascading deve acontecer automaticamente via GameObject._parent.
    """
    container = _first_container(save_game)
    child = container.contents[0]

    # Acessa parsed_data do pai ANTES da edição do filho, para garantir cache
    _ = container.parsed_data

    child.quantity = child.quantity + 1

    # jsonData do pai (raw) deve refletir a mudança sem nada além de child.quantity = ...
    parent_json = json.loads(container.raw["jsonData"])
    assert parent_json["contents"][0]["jsonData"] == child.raw["jsonData"]
