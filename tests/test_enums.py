# tests/test_enums.py
"""
Testes de EWhoAmI, EAttitude e helpers — Sprint 7.
"""
import pytest
from src.core.enums import EWhoAmI, EAttitude, whoami_name, attitude_label


class TestEWhoAmI:
    def test_generic_is_zero(self):
        assert EWhoAmI(0).name == "Generic"

    def test_named_npcs_key_values(self):
        cases = {1: "Corby", 2: "Shak", 14: "DrOwl", 27: "Garamon",
                 28: "Zak", 64: "Jaacar", 88: "Brawnclan", 110: "Gazer",
                 112: "Bandit", 136: "Oradinar", 184: "Delanrey",
                 207: "Warren", 231: "Tyball", 232: "Carasso", 233: "Count"}
        for wid, name in cases.items():
            assert EWhoAmI(wid).name == name, f"whoami={wid}"

    def test_non_sequential_values_correctly_mapped(self):
        """Jaacar=64 e Brawnclan=88 não são sequenciais — devem ser explícitos."""
        assert EWhoAmI(64).name == "Jaacar"
        assert EWhoAmI(65).name == "Eb"
        assert EWhoAmI(88).name == "Brawnclan"

    def test_unknown_id_raises_value_error(self):
        with pytest.raises(ValueError):
            EWhoAmI(9999)

    def test_whoami_name_known(self):
        assert whoami_name(27)  == "Garamon"
        assert whoami_name(28)  == "Zak"
        assert whoami_name(231) == "Tyball"
        assert whoami_name(0)   == "Generic"

    def test_whoami_name_unknown_fallback(self):
        assert whoami_name(9999)  == "NPC#9999"
        assert whoami_name(-1)    == "NPC#-1"
        assert whoami_name(10000) == "NPC#10000"

    def test_all_enum_members_have_non_empty_names(self):
        for member in EWhoAmI:
            assert member.name and len(member.name) > 0


class TestEAttitude:
    def test_all_four_values_present(self):
        assert EAttitude(0).name == "HOSTILE"
        assert EAttitude(1).name == "NEUTRAL"
        assert EAttitude(2).name == "FRIENDLY"
        assert EAttitude(3).name == "ALLY"

    def test_attitude_label_capitalized(self):
        assert attitude_label(0) == "Hostile"
        assert attitude_label(1) == "Neutral"
        assert attitude_label(2) == "Friendly"
        assert attitude_label(3) == "Ally"

    def test_attitude_label_unknown_fallback(self):
        assert attitude_label(99) == "Att99"
        assert attitude_label(-1) == "Att-1"

    def test_unknown_int_raises_value_error(self):
        with pytest.raises(ValueError):
            EAttitude(99)

    def test_ally_value_confirmed_by_fixture(self, sample_save):
        """Confirma que o valor 3=ALLY existe no save fixture (38 critters)."""
        import json
        from collections import Counter
        wobl = sample_save["worldObjectsByLevel"]
        attitudes = []
        for lvl in wobl:
            for obj in lvl.get("objects", []) + lvl.get("inactiveObjects", []):
                jd = json.loads(obj.get("jsonData", "{}")) if obj.get("jsonData") else {}
                if "whoami" in jd and "attitude" in jd:
                    attitudes.append(jd["attitude"])
        dist = Counter(attitudes)
        assert dist[3] == 38, f"Esperado 38 critters com attitude=3, encontrado {dist[3]}"
