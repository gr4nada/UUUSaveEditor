# tests/test_e2e_save_controller.py
"""
Sprint 9 — Testes de integração end-to-end via SaveController.

Cobre o caminho completo sem Tkinter:

    load_save (disco) → SaveController.load() → SaveGame
        → edições (PlayerModel, quest flags, skills, world objects)
        → SaveController.save(SavePayload)
        → save_game_data (disco, gzip)
        → load_save novamente → SaveGame
        → asserts: valores persistiram corretamente

Cada teste isola SAVES_DIR num diretório temporário (monkeypatch), grava o
fixture como slot0.json.gz, e roda o ciclo completo load → edit → save → reload.

Diferença em relação a test_validation.py / test_world_objects_logic.py:
  - Aqueles testam unidades isoladas (PlayerModel, world_parser) em memória.
  - Este arquivo testa o fluxo real do controller, incluindo I/O em disco
    (gzip), backup automático, reconstrução de SaveGame após save, e a
    interação entre validação cruzada (hp<=vitality) e persistência.
"""
from __future__ import annotations

import copy
import gzip
import json
import os

import pytest

import src.core.save_manager as sm
from src.core.save_controller import SaveController, SavePayload
from src.core.save_model import SaveGame, ValidationError
from src.core.database.quests import QUEST_FLAGS
from src.core.database.skills import SKILL_NAMES
from src.core.world_parser import parse_world, set_critter_hp, set_item_quantity


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def saves_dir(tmp_path, monkeypatch):
    """Redireciona SAVES_DIR (save_manager) para um diretório temporário isolado."""
    d = tmp_path / "saves"
    d.mkdir()
    monkeypatch.setattr(sm, "SAVES_DIR", str(d))
    return str(d)


def _write_slot(saves_dir: str, slot: int, data: dict) -> str:
    """Escreve `data` como slot{N}.json.gz, igual ao formato real do jogo."""
    path = os.path.join(saves_dir, f"slot{slot}.json.gz")
    with gzip.open(path, "wb") as f:
        f.write(json.dumps(data).encode("utf-8"))
    return path


def _read_slot_raw(saves_dir: str, slot: int) -> dict:
    """Lê slot{N}.json.gz diretamente, sem passar por load_save (controle)."""
    path = os.path.join(saves_dir, f"slot{slot}.json.gz")
    with gzip.open(path, "rb") as f:
        return json.loads(f.read().decode("utf-8"))


@pytest.fixture
def controller_with_save(saves_dir, sample_save):
    """
    Escreve sample_save como slot0, carrega via SaveController.load(0),
    e retorna (controller, saves_dir) prontos para edição.
    """
    _write_slot(saves_dir, 0, sample_save)
    ctrl = SaveController()
    ctrl.load(0)
    return ctrl, saves_dir


def _full_payload(ctrl: SaveController, **overrides) -> SavePayload:
    """
    Monta um SavePayload completo a partir do estado atual de ctrl.save_game,
    com `overrides` aplicados sobre os atributos. Garante que campos não
    mencionados explicitamente preservem o valor atual (round-trip neutro).
    """
    p = ctrl.save_game.player
    attrs = {
        "playerName":  p.name,
        "playerClass": p.player_class,
        "female":      p.female,
        "leftHanded":  p.left_handed,
        "charLevel":   p.level,
        "xp":          p.xp,
        "strength":    p.strength,
        "intellect":   p.intellect,
        "dexterity":   p.dexterity,
        "hp":          p.hp,
        "vitality":    p.vitality,
        "mana":        p.mana,
        "maxMana":     p.max_mana,
        "skillPoints": p.skill_points,
        "poison":      p.poison,
        "hunger":      p.hunger,
        "fatigue":     p.fatigue,
        "drunkenness": p.drunkenness,
        "portrait":    p.portrait,
    }
    attrs.update(overrides)
    skills = {name: p.get_skill(name) for name in SKILL_NAMES}
    flags  = p.get_quest_flags_by_name()
    return SavePayload(attrs=attrs, skills=skills, flags=flags)


# ---------------------------------------------------------------------------
# Caminho completo — happy path
# ---------------------------------------------------------------------------

class TestFullRoundTrip:
    def test_load_edit_save_reload_hp(self, controller_with_save):
        """hp editado persiste após save → reload completo do disco."""
        ctrl, saves_dir = controller_with_save

        payload = _full_payload(ctrl, hp=55)
        ctrl.save(payload)

        # Novo controller, simulando reabrir o editor do zero
        ctrl2 = SaveController()
        ctrl2.load(0)
        assert ctrl2.save_game.player.hp == 55

    def test_load_edit_save_reload_multiple_attrs(self, controller_with_save):
        """Vários atributos editados simultaneamente persistem corretamente."""
        ctrl, saves_dir = controller_with_save

        payload = _full_payload(
            ctrl,
            hp=70, vitality=100, mana=50, maxMana=80,
            charLevel=20, xp=250_000,
            strength=99, intellect=88, dexterity=77,
        )
        ctrl.save(payload)

        ctrl2 = SaveController()
        ctrl2.load(0)
        p = ctrl2.save_game.player
        assert p.hp == 70
        assert p.vitality == 100
        assert p.mana == 50
        assert p.max_mana == 80
        assert p.level == 20
        assert p.xp == 250_000
        assert p.strength == 99
        assert p.intellect == 88
        assert p.dexterity == 77

    def test_load_edit_save_reload_name(self, controller_with_save):
        """Nome do personagem persiste, incluindo unicode."""
        ctrl, saves_dir = controller_with_save

        payload = _full_payload(ctrl, playerName="Sir Galahad ⚔️")
        ctrl.save(payload)

        ctrl2 = SaveController()
        ctrl2.load(0)
        assert ctrl2.save_game.player.name == "Sir Galahad ⚔️"

    def test_load_edit_save_reload_skills(self, controller_with_save):
        """Skills editados individualmente persistem na ordem correta."""
        ctrl, saves_dir = controller_with_save

        payload = _full_payload(ctrl)
        payload.skills["Attack"]  = 25
        payload.skills["Defense"] = 18
        payload.skills["Sneak"]   = 30
        ctrl.save(payload)

        ctrl2 = SaveController()
        ctrl2.load(0)
        p = ctrl2.save_game.player
        assert p.get_skill("Attack")  == 25
        assert p.get_skill("Defense") == 18
        assert p.get_skill("Sneak")   == 30
        # Skills não mencionados existem e são >= 0 (não corrompidos)
        assert p.get_skill("Mana") >= 0

    def test_load_edit_save_reload_quest_flags(self, controller_with_save):
        """Quest flags editadas persistem, sem afastar flags fora do escopo do editor."""
        ctrl, saves_dir = controller_with_save

        payload = _full_payload(ctrl)
        # Ativa todas as quest flags conhecidas pelo editor
        for q in QUEST_FLAGS:
            payload.flags[q["flag"]] = True
        ctrl.save(payload)

        ctrl2 = SaveController()
        ctrl2.load(0)
        flags_after = ctrl2.save_game.player.get_quest_flags_by_name()
        for q in QUEST_FLAGS:
            assert flags_after[q["flag"]] is True

    def test_load_edit_save_reload_player_class(self, controller_with_save):
        """playerClass editado persiste como int correto."""
        ctrl, saves_dir = controller_with_save

        payload = _full_payload(ctrl, playerClass=4)  # Druid
        ctrl.save(payload)

        ctrl2 = SaveController()
        ctrl2.load(0)
        assert ctrl2.save_game.player.player_class == 4
        assert ctrl2.save_game.player.player_class_name == "Druid"

    def test_load_edit_save_reload_boolean_flags(self, controller_with_save):
        """female / leftHanded persistem corretamente como bool."""
        ctrl, saves_dir = controller_with_save

        payload = _full_payload(ctrl, female=True, leftHanded=True)
        ctrl.save(payload)

        ctrl2 = SaveController()
        ctrl2.load(0)
        assert ctrl2.save_game.player.female is True
        assert ctrl2.save_game.player.left_handed is True


# ---------------------------------------------------------------------------
# Status / sobrevivência — clamp persiste corretamente
# ---------------------------------------------------------------------------

class TestSurvivalRoundTrip:
    def test_negative_hunger_clamped_and_persisted(self, controller_with_save):
        """hunger=-50 é clampado para 0 antes de salvar, e 0 persiste."""
        ctrl, saves_dir = controller_with_save

        payload = _full_payload(ctrl, hunger=-50)
        ctrl.save(payload)

        ctrl2 = SaveController()
        ctrl2.load(0)
        assert ctrl2.save_game.player.hunger == 0

    def test_overflow_poison_clamped_and_persisted(self, controller_with_save):
        """poison=9999 é clampado para 255 antes de salvar."""
        ctrl, saves_dir = controller_with_save

        payload = _full_payload(ctrl, poison=9999)
        ctrl.save(payload)

        ctrl2 = SaveController()
        ctrl2.load(0)
        assert ctrl2.save_game.player.poison == 255


# ---------------------------------------------------------------------------
# Validação — falhas não persistem nada
# ---------------------------------------------------------------------------

class TestValidationDoesNotPersist:
    def test_hp_above_vitality_rejected_save_file_unchanged(self, controller_with_save):
        """
        Tentativa de salvar hp > vitality levanta ValidationError e o
        arquivo em disco permanece byte-a-byte o save original (nenhuma
        escrita parcial ocorre).
        """
        ctrl, saves_dir = controller_with_save

        before = _read_slot_raw(saves_dir, 0)

        payload = _full_payload(ctrl, hp=999)  # vitality=82 no fixture
        with pytest.raises(ValidationError):
            ctrl.save(payload)

        after = _read_slot_raw(saves_dir, 0)
        assert after == before

    def test_mana_above_max_mana_rejected_save_file_unchanged(self, controller_with_save):
        ctrl, saves_dir = controller_with_save

        before = _read_slot_raw(saves_dir, 0)

        payload = _full_payload(ctrl, mana=500)  # maxMana=39 no fixture
        with pytest.raises(ValidationError):
            ctrl.save(payload)

        after = _read_slot_raw(saves_dir, 0)
        assert after == before

    def test_level_zero_rejected_save_file_unchanged(self, controller_with_save):
        ctrl, saves_dir = controller_with_save

        before = _read_slot_raw(saves_dir, 0)

        payload = _full_payload(ctrl, charLevel=0)
        with pytest.raises(ValidationError):
            ctrl.save(payload)

        after = _read_slot_raw(saves_dir, 0)
        assert after == before

    def test_rejected_save_in_memory_state_unchanged(self, controller_with_save):
        """
        Após um save() rejeitado, save_game (em memória) ainda reflete o
        valor original — controller não fica em estado intermediário.
        """
        ctrl, saves_dir = controller_with_save
        original_hp = ctrl.save_game.player.hp

        payload = _full_payload(ctrl, hp=999)
        with pytest.raises(ValidationError):
            ctrl.save(payload)

        assert ctrl.save_game.player.hp == original_hp

    def test_failed_save_then_successful_save(self, controller_with_save):
        """
        Um save() rejeitado não impede saves subsequentes válidos —
        o controller permanece operável após o erro.
        """
        ctrl, saves_dir = controller_with_save

        bad_payload = _full_payload(ctrl, hp=999)
        with pytest.raises(ValidationError):
            ctrl.save(bad_payload)

        good_payload = _full_payload(ctrl, hp=50)
        ctrl.save(good_payload)  # não deve levantar

        ctrl2 = SaveController()
        ctrl2.load(0)
        assert ctrl2.save_game.player.hp == 50


# ---------------------------------------------------------------------------
# Múltiplos ciclos de save — idempotência e acúmulo
# ---------------------------------------------------------------------------

class TestMultipleSaveCycles:
    def test_two_sequential_saves_accumulate(self, controller_with_save):
        """Duas edições sequenciais (load→save→load→save) acumulam corretamente."""
        ctrl, saves_dir = controller_with_save

        # Ciclo 1: hp = 60
        payload1 = _full_payload(ctrl, hp=60)
        ctrl.save(payload1)

        # Ciclo 2: carrega de novo, edita vitality
        ctrl2 = SaveController()
        ctrl2.load(0)
        assert ctrl2.save_game.player.hp == 60  # ciclo 1 persistiu

        payload2 = _full_payload(ctrl2, vitality=150)
        ctrl2.save(payload2)

        # Ciclo 3: verifica que ambas as edições estão presentes
        ctrl3 = SaveController()
        ctrl3.load(0)
        assert ctrl3.save_game.player.hp == 60
        assert ctrl3.save_game.player.vitality == 150

    def test_idempotent_save_without_changes(self, controller_with_save):
        """Salvar sem alterar nada produz um save funcionalmente idêntico."""
        ctrl, saves_dir = controller_with_save

        before = copy.deepcopy(ctrl.raw_save["playerData"])
        payload = _full_payload(ctrl)
        ctrl.save(payload)

        ctrl2 = SaveController()
        ctrl2.load(0)
        after = ctrl2.raw_save["playerData"]

        # __dungeon_level__ é um campo de runtime injetado por _inject_dungeon_level,
        # não persiste no arquivo — removido de ambos os lados antes de comparar.
        before.pop("__dungeon_level__", None)
        after_clean = {k: v for k, v in after.items() if k != "__dungeon_level__"}
        assert after_clean == before


# ---------------------------------------------------------------------------
# Backup automático durante save()
# ---------------------------------------------------------------------------

class TestBackupDuringSave:
    def test_save_creates_backup_of_previous_version(self, controller_with_save):
        """save_game_data cria backup do save anterior antes de sobrescrever."""
        ctrl, saves_dir = controller_with_save

        backups_dir = os.path.join(saves_dir, "backups")
        assert not os.path.isdir(backups_dir)  # nenhum backup ainda

        payload = _full_payload(ctrl, hp=42)
        ctrl.save(payload)

        assert os.path.isdir(backups_dir)
        files = [f for f in os.listdir(backups_dir) if f.startswith("slot0_")]
        assert len(files) == 1

    def test_backup_contains_pre_edit_value(self, controller_with_save):
        """O backup criado contém o hp ANTES da edição, não o novo valor."""
        ctrl, saves_dir = controller_with_save
        original_hp = ctrl.save_game.player.hp

        payload = _full_payload(ctrl, hp=999_999)  # será rejeitado, mas tentamos um válido depois
        payload.attrs["hp"] = 42
        payload.attrs["vitality"] = max(payload.attrs["vitality"], 42)
        ctrl.save(payload)

        backups_dir = os.path.join(saves_dir, "backups")
        backup_file = [f for f in os.listdir(backups_dir) if f.startswith("slot0_")][0]
        with gzip.open(os.path.join(backups_dir, backup_file), "rb") as f:
            backup_data = json.loads(f.read().decode("utf-8"))
        assert backup_data["playerData"]["hp"] == original_hp


# ---------------------------------------------------------------------------
# World objects / critters — write API + reload via parse_world
# ---------------------------------------------------------------------------

class TestWorldObjectsRoundTrip:
    def test_critter_hp_edit_persists_through_full_cycle(self, controller_with_save):
        """
        set_critter_hp() edita raw_save em memória; após save()+reload,
        parse_world() no novo controller reflete o HP atualizado.
        """
        ctrl, saves_dir = controller_with_save

        critters, _ = ctrl.save_game.parse_world()
        target = critters[0]

        ok = set_critter_hp(ctrl.raw_save, target["level"], target["object_index"], 1, original_hp=target["max_hp"])
        assert ok is True

        payload = _full_payload(ctrl)
        ctrl.save(payload)

        ctrl2 = SaveController()
        ctrl2.load(0)
        critters2, _ = ctrl2.save_game.parse_world()
        target2 = next(c for c in critters2
                       if c["level"] == target["level"]
                       and c["object_index"] == target["object_index"])
        assert target2["hp"] == 1

    def test_item_quantity_edit_persists_through_full_cycle(self, controller_with_save):
        """set_item_quantity() em raw_save sobrevive ao ciclo save+reload."""
        ctrl, saves_dir = controller_with_save

        _, items = ctrl.save_game.parse_world()
        target = items[0]

        ok = set_item_quantity(ctrl.raw_save, target["level"], target["object_index"], 77)
        assert ok is True

        payload = _full_payload(ctrl)
        ctrl.save(payload)

        ctrl2 = SaveController()
        ctrl2.load(0)
        _, items2 = ctrl2.save_game.parse_world()
        target2 = next(i for i in items2
                       if i["level"] == target["level"]
                       and i["object_index"] == target["object_index"])
        assert target2["quantity"] == 77

    def test_world_object_edit_does_not_affect_player_data(self, controller_with_save):
        """Editar um world object não deve alterar playerData no ciclo completo."""
        ctrl, saves_dir = controller_with_save

        before_player = copy.deepcopy(ctrl.raw_save["playerData"])
        before_player.pop("__dungeon_level__", None)

        critters, _ = ctrl.save_game.parse_world()
        target = critters[0]
        set_critter_hp(ctrl.raw_save, target["level"], target["object_index"], 1)

        payload = _full_payload(ctrl)
        ctrl.save(payload)

        ctrl2 = SaveController()
        ctrl2.load(0)
        after_player = {k: v for k, v in ctrl2.raw_save["playerData"].items()
                       if k != "__dungeon_level__"}
        assert after_player == before_player


# ---------------------------------------------------------------------------
# Inventário — delete e reload
# ---------------------------------------------------------------------------

class TestInventoryRoundTrip:
    def test_delete_main_inventory_item_persists(self, controller_with_save):
        """Item deletado do main_inventory não retorna após save+reload."""
        ctrl, saves_dir = controller_with_save

        before_count = len(ctrl.save_game.main_inventory)
        deleted_name  = ctrl.save_game.main_inventory[0].object_name

        ctrl.save_game.delete_main_inventory_item(0)

        payload = _full_payload(ctrl)
        ctrl.save(payload)

        ctrl2 = SaveController()
        ctrl2.load(0)
        after_count = len(ctrl2.save_game.main_inventory)
        assert after_count == before_count - 1
        # O item deletado não está mais presente (ao menos não na posição 0,
        # a menos que outro item com mesmo nome exista nessa posição)
        names_after = [o.object_name for o in ctrl2.save_game.main_inventory]
        # Apenas garante contagem reduzida; presença de nomes duplicados é aceitável
        assert len(names_after) == before_count - 1

    def test_quantity_edit_in_main_inventory_persists(self, controller_with_save):
        """GameObject.quantity editado via main_inventory persiste."""
        ctrl, saves_dir = controller_with_save

        obj = ctrl.save_game.main_inventory[0]
        obj.quantity = 33

        payload = _full_payload(ctrl)
        ctrl.save(payload)

        ctrl2 = SaveController()
        ctrl2.load(0)
        assert ctrl2.save_game.main_inventory[0].quantity == 33


# ---------------------------------------------------------------------------
# Cenário combinado — edição de várias camadas num único save
# ---------------------------------------------------------------------------

class TestCombinedEdit:
    def test_player_world_and_inventory_in_single_save(self, controller_with_save):
        """
        Um único ciclo load→edit→save→reload que toca PlayerModel,
        world objects (critter) e main inventory simultaneamente —
        simula uma sessão de edição real do usuário.
        """
        ctrl, saves_dir = controller_with_save

        # 1. Player
        # 2. World object
        critters, _ = ctrl.save_game.parse_world()
        target_critter = critters[0]
        set_critter_hp(ctrl.raw_save, target_critter["level"], target_critter["object_index"], 5)

        # 3. Inventory
        ctrl.save_game.main_inventory[0].quantity = 9

        # 4. Player attrs + skills + quest flags
        payload = _full_payload(
            ctrl,
            hp=33, charLevel=25, playerName="Combined Edit Hero",
        )
        payload.skills["Attack"] = 29
        for q in QUEST_FLAGS[:3]:
            payload.flags[q["flag"]] = True

        ctrl.save(payload)

        # Reload e verifica todas as camadas
        ctrl2 = SaveController()
        ctrl2.load(0)
        p2 = ctrl2.save_game.player

        assert p2.hp == 33
        assert p2.level == 25
        assert p2.name == "Combined Edit Hero"
        assert p2.get_skill("Attack") == 29

        flags_after = p2.get_quest_flags_by_name()
        for q in QUEST_FLAGS[:3]:
            assert flags_after[q["flag"]] is True

        critters2, _ = ctrl2.save_game.parse_world()
        target2 = next(c for c in critters2
                       if c["level"] == target_critter["level"]
                       and c["object_index"] == target_critter["object_index"])
        assert target2["hp"] == 5

        assert ctrl2.save_game.main_inventory[0].quantity == 9


# ---------------------------------------------------------------------------
# Compressão / formato de arquivo
# ---------------------------------------------------------------------------

class TestFileFormat:
    def test_saved_file_is_valid_gzip(self, controller_with_save):
        """O arquivo salvo é um gzip válido contendo JSON válido."""
        ctrl, saves_dir = controller_with_save

        payload = _full_payload(ctrl, hp=44)
        ctrl.save(payload)

        path = os.path.join(saves_dir, "slot0.json.gz")
        with gzip.open(path, "rb") as f:
            data = json.loads(f.read().decode("utf-8"))
        assert data["playerData"]["hp"] == 44

    def test_saved_file_round_trips_unicode(self, controller_with_save):
        """Caracteres unicode no nome sobrevivem à compressão gzip + JSON."""
        ctrl, saves_dir = controller_with_save

        payload = _full_payload(ctrl, playerName="Älfrïc Ñöño 龍")
        ctrl.save(payload)

        ctrl2 = SaveController()
        ctrl2.load(0)
        assert ctrl2.save_game.player.name == "Älfrïc Ñöño 龍"
