# tests/test_roundtrip.py
import json

def test_roundtrip_identity(sample_save): # type: ignore
    """Validates full data transformations compliance cycles avoiding structural type mutations."""
    original = sample_save

    # Emulate disk pipeline operational bounds
    serialized = json.dumps(original)
    restored = json.loads(serialized)

    assert restored == original, "Data stream structures diverged across data compression boundary lines!"
    assert restored["playerData"]["playerName"] == "TEST_AVATAR"

def test_roundtrip_identity(sample_save):
    """Valida que a transformação completa de dados preserva a integridade exata do ficheiro."""
    original = sample_save

    # Simular ciclo de escrita em disco e leitura
    serialized = json.dumps(original, indent=4)
    restored = json.loads(serialized)

    # Asserções de Identidade Estrutural
    assert restored == original, "A estrutura de dados divergiu durante o ciclo de serialização!"
    assert restored["version"] == 1
    assert restored["slotName"] == "Slot0"
    assert restored["displayName"] == "test"