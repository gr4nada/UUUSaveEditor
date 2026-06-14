# tests/test_story_tab.py
"""
Sprint 10 — Aba "Story": testes de PlayerModel/SaveGame setters e
roundtrip end-to-end via SaveController.

Não usa Tkinter — StoryTab.get_story_data() é testada indiretamente
através do formato de dict que SaveController._apply_story() consome
(ambos descritos no docstring de _apply_story).

Cobre:
  - PlayerModel: easy, position (set/clamp/partial update),
    plot flags booleanos, cup_dream_index, sapling/moonstone level,
    talismans_collected/destroyed (validação), dreams_remaining,
    global_vars (set/clamp/partial/OOB)
  - SaveGame.current_level (teleporte entre níveis, clamp)
  - SaveController.save() com payload.story:
      roundtrip completo, partial update, story=None,
      interação com validação cruzada hp<=vitality
"""
from __future__ import annotations

import copy
import gzip
import json
import os

import pytest

import src.core.save_manager as sm
from src.core.save_controller import SaveController, SavePayload
from src.core.save_model import SaveGame, PlayerModel, ValidationError, FIELD_LIMITS
from src.core.database.skills import SKILL_NAMES


# ---------------------------------------------------------------------------
# Fixtures locais
# ---------------------------------------------------------------------------

@pytest.fixture
def player(sample_save) -> PlayerModel:
    return PlayerModel(sample_save["playerData"])


@pytest.fixture
def saves_dir(tmp_path, monkeypatch):
    d = tmp_path / "saves"
    d.mkdir()
    monkeypatch.setattr(sm, "SAVES_DIR", str(d))
    return str(d)


def _write_slot(saves_dir: str, slot: int, data: dict) -> str:
    path = os.path.join(saves_dir, f"slot{slot}.json.gz")
    with gzip.open(path, "wb") as f:
        f.write(json.dumps(data).encode("utf-8"))
    return path


@pytest.fixture
def controller_with_save(saves_dir, sample_save):
    _write_slot(saves_dir, 0, sample_save)
    ctrl = SaveController()
    ctrl.load(0)
    return ctrl, saves_dir


def _full_payload(ctrl: SaveController, story: dict | None = None, **overrides) -> SavePayload:
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
    return SavePayload(attrs=attrs, skills=skills, flags=flags, story=story)


# ---------------------------------------------------------------------------
# PlayerModel — easy
# ---------------------------------------------------------------------------

class TestEasy:
    def test_set_true(self, player):
        player.easy = True
        assert player.easy is True

    def test_set_false(self, player):
        player.easy = False
        assert player.easy is False

    def test_roundtrip_persists_in_dict(self, player, sample_save):
        player.easy = not player.easy
        new_val = player.easy
        assert sample_save["playerData"]["easy"] == new_val


# ---------------------------------------------------------------------------
# PlayerModel — position (teleporte)
# ---------------------------------------------------------------------------

class TestPosition:
    def test_get_returns_xyz(self, player):
        pos = player.position
        assert set(pos.keys()) == {"x", "y", "z"}

    def test_set_full(self, player):
        player.position = {"x": 1.0, "y": 2.0, "z": 3.0}
        assert player.position == {"x": 1.0, "y": 2.0, "z": 3.0}

    def test_partial_update_preserves_other_axes(self, player):
        player.position = {"x": 10.0, "y": 20.0, "z": 30.0}
        player.position = {"y": 99.0}
        pos = player.position
        assert pos == {"x": 10.0, "y": 99.0, "z": 30.0}

    def test_clamp_upper(self, player):
        player.position = {"x": 99999.0}
        assert player.position["x"] == 2000.0

    def test_clamp_lower(self, player):
        player.position = {"z": -99999.0}
        assert player.position["z"] == -2000.0

    def test_unknown_keys_ignored(self, player):
        player.position = {"x": 5.0, "w": 999.0}  # 'w' não é eixo válido
        pos = player.position
        assert "w" not in pos
        assert pos["x"] == 5.0

    def test_float_precision_preserved(self, player):
        player.position = {"x": 12.3456789}
        assert abs(player.position["x"] - 12.3456789) < 1e-9


# ---------------------------------------------------------------------------
# PlayerModel — Plot Flags booleanos
# ---------------------------------------------------------------------------

class TestPlotFlagsBoolean:
    @pytest.mark.parametrize("attr", [
        "cup_found", "sapling_planted", "moonstone_dropped",
        "garamon_at_rest", "entered_green_moongate", "said_fanlo",
    ])
    def test_set_true_false(self, player, attr):
        setattr(player, attr, True)
        assert getattr(player, attr) is True
        setattr(player, attr, False)
        assert getattr(player, attr) is False

    @pytest.mark.parametrize("attr", [
        "cup_found", "sapling_planted", "moonstone_dropped",
        "garamon_at_rest", "entered_green_moongate", "said_fanlo",
    ])
    def test_truthy_value_coerced_to_bool(self, player, attr):
        setattr(player, attr, 1)
        assert getattr(player, attr) is True
        assert isinstance(getattr(player, attr), bool)


# ---------------------------------------------------------------------------
# PlayerModel — cup_dream_index, sapling/moonstone level
# ---------------------------------------------------------------------------

class TestPlotFlagsClampedInts:
    def test_cup_dream_index_in_range(self, player):
        player.cup_dream_index = 3
        assert player.cup_dream_index == 3

    def test_cup_dream_index_clamped_high(self, player):
        player.cup_dream_index = 99
        _, hi = FIELD_LIMITS["cup_dream_index"]
        assert player.cup_dream_index == hi

    def test_cup_dream_index_clamped_low(self, player):
        player.cup_dream_index = -5
        lo, _ = FIELD_LIMITS["cup_dream_index"]
        assert player.cup_dream_index == lo

    def test_sapling_level_in_range(self, player):
        player.sapling_planted_level = 5
        assert player.sapling_planted_level == 5

    def test_sapling_level_clamped_high(self, player):
        player.sapling_planted_level = 999
        _, hi = FIELD_LIMITS["dungeon_level"]
        assert player.sapling_planted_level == hi

    def test_moonstone_level_clamped_low(self, player):
        player.moonstone_dropped_level = -10
        lo, _ = FIELD_LIMITS["dungeon_level"]
        assert player.moonstone_dropped_level == lo


# ---------------------------------------------------------------------------
# PlayerModel — talismans (validados, não clampados)
# ---------------------------------------------------------------------------

class TestTalismans:
    def test_collected_in_range(self, player):
        player.talismans_collected = 30
        assert player.talismans_collected == 30

    def test_collected_max_accepted(self, player):
        _, hi = FIELD_LIMITS["talismans"]
        player.talismans_collected = hi
        assert player.talismans_collected == hi

    def test_collected_over_max_raises(self, player):
        _, hi = FIELD_LIMITS["talismans"]
        with pytest.raises(ValidationError):
            player.talismans_collected = hi + 1

    def test_destroyed_negative_raises(self, player):
        with pytest.raises(ValidationError):
            player.talismans_destroyed = -1

    def test_destroyed_zero_accepted(self, player):
        player.talismans_destroyed = 0
        assert player.talismans_destroyed == 0


# ---------------------------------------------------------------------------
# PlayerModel — dreams_remaining
# ---------------------------------------------------------------------------

class TestDreamsRemaining:
    def test_fixture_has_six_entries(self, player):
        assert len(player.dreams_remaining) == 6

    def test_set_all_six(self, player):
        player.dreams_remaining = [10, 20, 30, 40, 50, 60]
        assert player.dreams_remaining == [10, 20, 30, 40, 50, 60]

    def test_partial_update_first_index_only(self, player):
        before = list(player.dreams_remaining)
        player.dreams_remaining = [99]
        after = player.dreams_remaining
        assert after[0] == 99
        assert after[1:] == before[1:]

    def test_clamp_to_max(self, player):
        _, hi = FIELD_LIMITS["dream_count"]
        player.dreams_remaining = [hi + 100]
        assert player.dreams_remaining[0] == hi

    def test_clamp_to_min(self, player):
        lo, _ = FIELD_LIMITS["dream_count"]
        player.dreams_remaining = [-50]
        assert player.dreams_remaining[0] == lo

    def test_length_preserved(self, player):
        before_len = len(player.dreams_remaining)
        player.dreams_remaining = [1, 2]
        assert len(player.dreams_remaining) == before_len


# ---------------------------------------------------------------------------
# PlayerModel — global_vars
# ---------------------------------------------------------------------------

class TestGlobalVars:
    def test_fixture_has_64_entries(self, player):
        assert len(player.global_vars) == 64

    def test_set_single_index(self, player):
        player.global_vars = {0: 1234}
        assert player.global_vars[0] == 1234

    def test_set_multiple_indices(self, player):
        player.global_vars = {0: 100, 5: -50, 63: 32767}
        gv = player.global_vars
        assert gv[0] == 100
        assert gv[5] == -50
        assert gv[63] == 32767

    def test_other_indices_unchanged(self, player):
        before = list(player.global_vars)
        player.global_vars = {10: 999}
        after = player.global_vars
        for i in range(64):
            if i != 10:
                assert after[i] == before[i]

    def test_clamp_upper(self, player):
        player.global_vars = {0: 99999}
        _, hi = FIELD_LIMITS["global_var"]
        assert player.global_vars[0] == hi

    def test_clamp_lower(self, player):
        player.global_vars = {1: -99999}
        lo, _ = FIELD_LIMITS["global_var"]
        assert player.global_vars[1] == lo

    def test_out_of_range_index_ignored(self, player):
        before = list(player.global_vars)
        player.global_vars = {999: 1}  # índice fora do range — ignorado
        after = player.global_vars
        assert after == before

    def test_negative_index_ignored(self, player):
        before = list(player.global_vars)
        player.global_vars = {-1: 1}
        assert player.global_vars == before

    def test_get_global_var_in_range(self, player):
        player.global_vars = {7: 555}
        assert player.get_global_var(7) == 555

    def test_get_global_var_out_of_range_returns_zero(self, player):
        assert player.get_global_var(999) == 0

    def test_string_keys_work_via_apply_story(self, sample_save):
        """
        SaveController._apply_story converte chaves str→int (vindas de
        StoryTab/JSON). Verifica esse contrato diretamente.
        """
        sg = SaveGame(sample_save)
        ctrl = SaveController()
        ctrl.raw_save  = sample_save
        ctrl.save_game = sg
        ctrl._apply_story({"global_vars": {"3": 777, "4": 888}})
        gv = sg.player.global_vars
        assert gv[3] == 777
        assert gv[4] == 888


# ---------------------------------------------------------------------------
# SaveGame.current_level (teleporte entre níveis)
# ---------------------------------------------------------------------------

class TestCurrentLevel:
    def test_initial_value_from_fixture(self, save_game, sample_save):
        assert save_game.current_level == sample_save["currentLevel"]

    def test_set_in_range(self, save_game):
        save_game.current_level = 3
        assert save_game.current_level == 3

    def test_clamp_lower(self, save_game):
        save_game.current_level = -5
        assert save_game.current_level == 0

    def test_clamp_upper_respects_world_objects_by_level(self, save_game, sample_save):
        num_levels = len(sample_save["worldObjectsByLevel"])
        _, hi = FIELD_LIMITS["dungeon_level"]
        expected_max = min(hi, num_levels - 1)
        save_game.current_level = 999
        assert save_game.current_level == expected_max

    def test_raw_dict_updated(self, save_game, sample_save):
        save_game.current_level = 7
        assert sample_save["currentLevel"] == 7


# ---------------------------------------------------------------------------
# SaveController._apply_story — formato e comportamento
# ---------------------------------------------------------------------------

class TestApplyStory:
    def _ctrl(self, sample_save):
        sg = SaveGame(sample_save)
        ctrl = SaveController()
        ctrl.raw_save  = sample_save
        ctrl.save_game = sg
        return ctrl

    def test_empty_dict_changes_nothing(self, sample_save):
        ctrl = self._ctrl(sample_save)
        before = copy.deepcopy(sample_save["playerData"])
        ctrl._apply_story({})
        assert sample_save["playerData"] == before

    def test_partial_dict_only_touches_mentioned_fields(self, sample_save):
        ctrl = self._ctrl(sample_save)
        original_easy = ctrl.save_game.player.easy
        ctrl._apply_story({"cup_found": True})
        assert ctrl.save_game.player.cup_found is True
        assert ctrl.save_game.player.easy == original_easy

    def test_all_boolean_fields(self, sample_save):
        ctrl = self._ctrl(sample_save)
        story = {
            "easy": True, "cup_found": True, "sapling_planted": True,
            "moonstone_dropped": True, "garamon_at_rest": True,
            "entered_green_moongate": True, "said_fanlo": True,
        }
        ctrl._apply_story(story)
        p = ctrl.save_game.player
        assert all([p.easy, p.cup_found, p.sapling_planted, p.moonstone_dropped,
                     p.garamon_at_rest, p.entered_green_moongate, p.said_fanlo])

    def test_position_and_current_level(self, sample_save):
        ctrl = self._ctrl(sample_save)
        ctrl._apply_story({"position": {"x": 1.0, "y": 2.0, "z": 3.0}, "current_level": 4})
        assert ctrl.save_game.player.position == {"x": 1.0, "y": 2.0, "z": 3.0}
        assert ctrl.save_game.current_level == 4

    def test_dreams_remaining(self, sample_save):
        ctrl = self._ctrl(sample_save)
        ctrl._apply_story({"dreams_remaining": [1, 2, 3, 4, 5, 6]})
        assert ctrl.save_game.player.dreams_remaining == [1, 2, 3, 4, 5, 6]


# ---------------------------------------------------------------------------
# End-to-end: load -> story edit -> save -> reload
# ---------------------------------------------------------------------------

class TestStoryEndToEnd:
    def test_full_story_roundtrip(self, controller_with_save):
        ctrl, saves_dir = controller_with_save

        story = {
            "easy": True,
            "position": {"x": 100.0, "y": 5.0, "z": 200.0},
            "current_level": 3,
            "cup_found": True,
            "cup_dream_index": 2,
            "sapling_planted": True,
            "sapling_planted_level": 4,
            "moonstone_dropped": True,
            "moonstone_dropped_level": 7,
            "garamon_at_rest": True,
            "entered_green_moongate": True,
            "said_fanlo": True,
            "talismans_collected": 50,
            "talismans_destroyed": 10,
            "dreams_remaining": [1, 2, 3, 4, 5, 6],
            "global_vars": {0: 1000, 1: -500, 63: 42},
        }
        ctrl.save(_full_payload(ctrl, story=story))

        ctrl2 = SaveController()
        ctrl2.load(0)
        p2  = ctrl2.save_game.player
        sg2 = ctrl2.save_game

        assert p2.easy is True
        assert p2.position == {"x": 100.0, "y": 5.0, "z": 200.0}
        assert sg2.current_level == 3
        assert p2.cup_found is True
        assert p2.cup_dream_index == 2
        assert p2.sapling_planted is True
        assert p2.sapling_planted_level == 4
        assert p2.moonstone_dropped is True
        assert p2.moonstone_dropped_level == 7
        assert p2.garamon_at_rest is True
        assert p2.entered_green_moongate is True
        assert p2.said_fanlo is True
        assert p2.talismans_collected == 50
        assert p2.talismans_destroyed == 10
        assert p2.dreams_remaining == [1, 2, 3, 4, 5, 6]

        gv = p2.global_vars
        assert gv[0] == 1000
        assert gv[1] == -500
        assert gv[63] == 42

    def test_story_none_does_not_break_save(self, controller_with_save):
        ctrl, saves_dir = controller_with_save
        ctrl.save(_full_payload(ctrl, story=None, hp=50))

        ctrl2 = SaveController()
        ctrl2.load(0)
        assert ctrl2.save_game.player.hp == 50

    def test_partial_story_preserves_other_fields(self, controller_with_save):
        ctrl, saves_dir = controller_with_save
        original_easy = ctrl.save_game.player.easy
        original_pos  = ctrl.save_game.player.position

        ctrl.save(_full_payload(ctrl, story={"cup_found": True}))

        ctrl2 = SaveController()
        ctrl2.load(0)
        assert ctrl2.save_game.player.cup_found is True
        assert ctrl2.save_game.player.easy == original_easy
        assert ctrl2.save_game.player.position == original_pos

    def test_hp_validation_still_enforced_with_story(self, controller_with_save):
        """
        payload.story não deve contornar a validação cruzada hp<=vitality:
        o save inteiro é rejeitado, incluindo as mudanças de story.
        """
        ctrl, saves_dir = controller_with_save
        path = os.path.join(saves_dir, "slot0.json.gz")
        with gzip.open(path, "rb") as f:
            before = json.loads(f.read().decode("utf-8"))

        with pytest.raises(ValidationError):
            ctrl.save(_full_payload(ctrl, hp=999, story={"easy": True, "cup_found": True}))

        with gzip.open(path, "rb") as f:
            after = json.loads(f.read().decode("utf-8"))
        assert after == before

    def test_position_float_precision_through_gzip(self, controller_with_save):
        ctrl, saves_dir = controller_with_save
        ctrl.save(_full_payload(ctrl, story={
            "position": {"x": 12.3456789, "y": -0.0001, "z": 1999.999}
        }))

        ctrl2 = SaveController()
        ctrl2.load(0)
        pos = ctrl2.save_game.player.position
        assert abs(pos["x"] - 12.3456789) < 1e-6
        assert abs(pos["y"] - (-0.0001)) < 1e-6
        assert abs(pos["z"] - 1999.999) < 1e-6

    def test_teleport_to_different_level_persists(self, controller_with_save):
        ctrl, saves_dir = controller_with_save
        original_level = ctrl.save_game.current_level
        target_level = 0 if original_level != 0 else 1

        ctrl.save(_full_payload(ctrl, story={"current_level": target_level}))

        ctrl2 = SaveController()
        ctrl2.load(0)
        assert ctrl2.save_game.current_level == target_level

    def test_global_vars_partial_update_through_full_cycle(self, controller_with_save):
        ctrl, saves_dir = controller_with_save
        before_gv = list(ctrl.save_game.player.global_vars)

        ctrl.save(_full_payload(ctrl, story={"global_vars": {2: -1234}}))

        ctrl2 = SaveController()
        ctrl2.load(0)
        after_gv = ctrl2.save_game.player.global_vars
        assert after_gv[2] == -1234
        for i in range(64):
            if i != 2:
                assert after_gv[i] == before_gv[i]
