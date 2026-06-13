# tests/test_validation.py
"""
Testes de validação de ranges — PlayerModel setters e regras cruzadas.

Cobre:
  - Setters que levantam ValidationError fora dos limites
  - Setters que aceitam valores nos limites exatos (boundary)
  - Campos de status que clampeiam silenciosamente (sem exceção)
  - Regras cruzadas: hp <= vitality, mana <= max_mana
  - Validação de skill individual
  - Metadados de ValidationError (field, lo, hi)
"""
import pytest
from src.core.save_model import PlayerModel, ValidationError, FIELD_LIMITS


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def player(sample_save):
    return PlayerModel(sample_save["playerData"])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _set(player, attr, value):
    """Atalho para setar via atributo ou set_skill."""
    setattr(player, attr, value)


# ---------------------------------------------------------------------------
# ValidationError — metadados
# ---------------------------------------------------------------------------

class TestValidationErrorMetadata:
    def test_carries_field_name(self, player):
        with pytest.raises(ValidationError) as exc:
            player.hp = -1
        assert exc.value.field == "hp"

    def test_carries_rejected_value(self, player):
        with pytest.raises(ValidationError) as exc:
            player.level = 0
        assert exc.value.value == 0

    def test_carries_lo_hi_limits(self, player):
        with pytest.raises(ValidationError) as exc:
            player.hp = -5
        lo, hi = FIELD_LIMITS["hp"]
        assert exc.value.lo == lo
        assert exc.value.hi == hi

    def test_is_subclass_of_value_error(self, player):
        with pytest.raises(ValueError):
            player.hp = -1

    def test_message_mentions_field_and_value(self, player):
        with pytest.raises(ValidationError) as exc:
            player.strength = 300
        msg = str(exc.value)
        assert "strength" in msg
        assert "300" in msg


# ---------------------------------------------------------------------------
# HP / Vitality
# ---------------------------------------------------------------------------

class TestHP:
    def test_negative_hp_raises(self, player):
        with pytest.raises(ValidationError):
            player.hp = -1

    def test_zero_hp_accepted(self, player):
        player.hp = 0
        assert player.hp == 0

    def test_max_hp_accepted(self, player):
        lo, hi = FIELD_LIMITS["hp"]
        player.hp = hi
        assert player.hp == hi

    def test_over_max_hp_raises(self, player):
        _, hi = FIELD_LIMITS["hp"]
        with pytest.raises(ValidationError):
            player.hp = hi + 1

    def test_valid_hp_persists(self, player):
        player.hp = 50
        assert player.hp == 50


class TestVitality:
    def test_zero_vitality_raises(self, player):
        with pytest.raises(ValidationError):
            player.vitality = 0

    def test_minimum_vitality_accepted(self, player):
        player.vitality = 1
        assert player.vitality == 1

    def test_negative_vitality_raises(self, player):
        with pytest.raises(ValidationError):
            player.vitality = -10


# ---------------------------------------------------------------------------
# Mana / MaxMana
# ---------------------------------------------------------------------------

class TestMana:
    def test_negative_mana_raises(self, player):
        with pytest.raises(ValidationError):
            player.mana = -1

    def test_zero_mana_accepted(self, player):
        player.mana = 0
        assert player.mana == 0

    def test_negative_max_mana_raises(self, player):
        with pytest.raises(ValidationError):
            player.max_mana = -1

    def test_valid_mana_persists(self, player):
        player.mana = 25
        player.max_mana = 100
        assert player.mana == 25
        assert player.max_mana == 100


# ---------------------------------------------------------------------------
# Level / XP / Skill Points
# ---------------------------------------------------------------------------

class TestProgression:
    def test_level_zero_raises(self, player):
        with pytest.raises(ValidationError):
            player.level = 0

    def test_level_one_accepted(self, player):
        player.level = 1
        assert player.level == 1

    def test_level_max_accepted(self, player):
        _, hi = FIELD_LIMITS["level"]
        player.level = hi
        assert player.level == hi

    def test_level_over_max_raises(self, player):
        _, hi = FIELD_LIMITS["level"]
        with pytest.raises(ValidationError):
            player.level = hi + 1

    def test_negative_xp_raises(self, player):
        with pytest.raises(ValidationError):
            player.xp = -1

    def test_zero_xp_accepted(self, player):
        player.xp = 0
        assert player.xp == 0

    def test_large_xp_accepted(self, player):
        player.xp = 500_000
        assert player.xp == 500_000

    def test_negative_skill_points_raises(self, player):
        with pytest.raises(ValidationError):
            player.skill_points = -1

    def test_zero_skill_points_accepted(self, player):
        player.skill_points = 0
        assert player.skill_points == 0


# ---------------------------------------------------------------------------
# Atributos primários (STR / INT / DEX)
# ---------------------------------------------------------------------------

class TestPrimaryAttributes:
    @pytest.mark.parametrize("attr", ["strength", "intellect", "dexterity"])
    def test_zero_raises(self, player, attr):
        with pytest.raises(ValidationError):
            setattr(player, attr, 0)

    @pytest.mark.parametrize("attr", ["strength", "intellect", "dexterity"])
    def test_negative_raises(self, player, attr):
        with pytest.raises(ValidationError):
            setattr(player, attr, -5)

    @pytest.mark.parametrize("attr", ["strength", "intellect", "dexterity"])
    def test_minimum_accepted(self, player, attr):
        setattr(player, attr, 1)
        assert getattr(player, attr) == 1

    @pytest.mark.parametrize("attr", ["strength", "intellect", "dexterity"])
    def test_maximum_accepted(self, player, attr):
        _, hi = FIELD_LIMITS[attr]
        setattr(player, attr, hi)
        assert getattr(player, attr) == hi

    @pytest.mark.parametrize("attr", ["strength", "intellect", "dexterity"])
    def test_over_maximum_raises(self, player, attr):
        _, hi = FIELD_LIMITS[attr]
        with pytest.raises(ValidationError):
            setattr(player, attr, hi + 1)


# ---------------------------------------------------------------------------
# Portrait / Player Class
# ---------------------------------------------------------------------------

class TestIdentity:
    def test_portrait_negative_raises(self, player):
        with pytest.raises(ValidationError):
            player.portrait = -1

    def test_portrait_valid_range(self, player):
        for v in range(0, 10):
            player.portrait = v
            assert player.portrait == v

    def test_portrait_over_max_raises(self, player):
        _, hi = FIELD_LIMITS["portrait"]
        with pytest.raises(ValidationError):
            player.portrait = hi + 1

    def test_player_class_negative_raises(self, player):
        with pytest.raises(ValidationError):
            player.player_class = -1

    def test_player_class_valid_range(self, player):
        for v in range(0, 8):
            player.player_class = v
            assert player.player_class == v

    def test_player_class_over_max_raises(self, player):
        _, hi = FIELD_LIMITS["player_class"]
        with pytest.raises(ValidationError):
            player.player_class = hi + 1


# ---------------------------------------------------------------------------
# Status / Survival — clamp silencioso (sem ValidationError)
# ---------------------------------------------------------------------------

class TestSurvivalClamp:
    @pytest.mark.parametrize("attr", ["poison", "hunger", "fatigue", "drunkenness"])
    def test_negative_clamped_to_zero(self, player, attr):
        setattr(player, attr, -999)
        assert getattr(player, attr) == 0

    @pytest.mark.parametrize("attr", ["poison", "hunger", "fatigue", "drunkenness"])
    def test_over_max_clamped(self, player, attr):
        _, hi = FIELD_LIMITS[attr]
        setattr(player, attr, hi + 999)
        assert getattr(player, attr) == hi

    @pytest.mark.parametrize("attr", ["poison", "hunger", "fatigue", "drunkenness"])
    def test_valid_value_accepted(self, player, attr):
        setattr(player, attr, 10)
        assert getattr(player, attr) == 10

    @pytest.mark.parametrize("attr", ["poison", "hunger", "fatigue", "drunkenness"])
    def test_no_exception_on_extremes(self, player, attr):
        """Status fields must never raise — just clamp."""
        setattr(player, attr, -9999)
        setattr(player, attr, 9999)


# ---------------------------------------------------------------------------
# Skills individuais
# ---------------------------------------------------------------------------

class TestSkillValidation:
    def test_skill_negative_raises(self, player):
        with pytest.raises(ValidationError):
            player.set_skill("Attack", -1)

    def test_skill_zero_accepted(self, player):
        player.set_skill("Attack", 0)
        assert player.get_skill("Attack") == 0

    def test_skill_max_accepted(self, player):
        _, hi = FIELD_LIMITS["skill"]
        player.set_skill("Attack", hi)
        assert player.get_skill("Attack") == hi

    def test_skill_over_max_raises(self, player):
        _, hi = FIELD_LIMITS["skill"]
        with pytest.raises(ValidationError):
            player.set_skill("Defense", hi + 1)

    def test_unknown_skill_ignored(self, player):
        """set_skill com nome inválido não deve levantar exceção."""
        player.set_skill("NonExistentSkill", 99)

    def test_validation_error_mentions_skill_name(self, player):
        with pytest.raises(ValidationError) as exc:
            player.set_skill("Sword", -5)
        assert "Sword" in str(exc.value)


# ---------------------------------------------------------------------------
# Regras cruzadas hp <= vitality, mana <= max_mana
# (testadas via SaveController para garantir que o controller também protege)
# ---------------------------------------------------------------------------

class TestCrossFieldRules:
    def test_hp_above_vitality_raises_in_controller(self, sample_save):
        """SaveController.save() deve rejeitar hp > vitality."""
        from src.core.save_model import SaveGame, ValidationError
        from src.core.save_controller import SaveController, SavePayload

        sg = SaveGame(sample_save)
        ctrl = SaveController()
        ctrl.raw_save  = sample_save
        ctrl.save_game = sg

        # vitality do fixture = 82; tentamos salvar hp = 999
        payload = SavePayload(
            attrs={"hp": 999, "vitality": 82},
            skills={},
            flags={},
        )
        with pytest.raises(ValidationError) as exc:
            ctrl.save(payload)
        assert exc.value.field == "hp"

    def test_mana_above_max_mana_raises_in_controller(self, sample_save):
        """SaveController.save() deve rejeitar mana > maxMana."""
        from src.core.save_model import SaveGame, ValidationError
        from src.core.save_controller import SaveController, SavePayload

        sg = SaveGame(sample_save)
        ctrl = SaveController()
        ctrl.raw_save  = sample_save
        ctrl.save_game = sg

        payload = SavePayload(
            attrs={"mana": 500, "maxMana": 39},
            skills={},
            flags={},
        )
        with pytest.raises(ValidationError) as exc:
            ctrl.save(payload)
        assert exc.value.field == "mana"

    def test_hp_equal_vitality_accepted_in_controller(self, sample_save):
        """hp == vitality é válido (personagem em HP máximo)."""
        from src.core.save_model import SaveGame, ValidationError
        from src.core.save_controller import SaveController, SavePayload
        from unittest.mock import patch

        sg = SaveGame(sample_save)
        ctrl = SaveController()
        ctrl.raw_save  = sample_save
        ctrl.save_game = sg
        ctrl.selected_slot = 0

        payload = SavePayload(
            attrs={"hp": 82, "vitality": 82, "mana": 39, "maxMana": 39},
            skills={},
            flags={},
        )
        # Mocka o I/O de disco — só queremos testar a validação
        with patch("src.core.save_controller.save_game_data"):
            with patch("src.core.save_controller.update_character"):
                ctrl.save(payload)   # não deve levantar

    def test_mana_zero_with_any_max_mana_accepted(self, sample_save):
        """mana = 0 sempre é válido independente de maxMana."""
        from src.core.save_model import SaveGame
        from src.core.save_controller import SaveController, SavePayload
        from unittest.mock import patch

        sg = SaveGame(sample_save)
        ctrl = SaveController()
        ctrl.raw_save  = sample_save
        ctrl.save_game = sg
        ctrl.selected_slot = 0

        payload = SavePayload(
            attrs={"mana": 0, "maxMana": 100},
            skills={},
            flags={},
        )
        with patch("src.core.save_controller.save_game_data"):
            with patch("src.core.save_controller.update_character"):
                ctrl.save(payload)   # não deve levantar


# ---------------------------------------------------------------------------
# Boundary: limites exatos nunca devem levantar
# ---------------------------------------------------------------------------

class TestBoundaryExact:
    @pytest.mark.parametrize("field, attr, key", [
        ("hp",           "hp",           "hp"),
        ("vitality",     "vitality",     "vitality"),
        ("mana",         "mana",         "mana"),
        ("max_mana",     "max_mana",     "max_mana"),
        ("skill_points", "skill_points", "skill_points"),
    ])
    def test_lower_bound_accepted(self, player, field, attr, key):
        lo, _ = FIELD_LIMITS[key]
        setattr(player, attr, lo)
        assert getattr(player, attr) == lo

    @pytest.mark.parametrize("field, attr, key", [
        ("hp",           "hp",           "hp"),
        ("vitality",     "vitality",     "vitality"),
        ("mana",         "mana",         "mana"),
        ("max_mana",     "max_mana",     "max_mana"),
        ("level",        "level",        "level"),
    ])
    def test_upper_bound_accepted(self, player, field, attr, key):
        _, hi = FIELD_LIMITS[key]
        setattr(player, attr, hi)
        assert getattr(player, attr) == hi
