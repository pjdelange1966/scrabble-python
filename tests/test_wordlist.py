from pathlib import Path

from scrabble.wordlist import WordList, normalize

SAMPLE = Path(__file__).parent.parent / "data" / "voorbeeld-woorden.txt"


def test_normalize_removes_accents_and_case() -> None:
    assert normalize("  Café ") == "cafe"
    assert normalize("Ruïne") == "ruine"


def test_wordlist_validates_known_and_unknown_words() -> None:
    wl = WordList.from_file(SAMPLE)
    assert wl.is_valid("Huis")
    assert wl.is_valid("gelopen")
    assert not wl.is_valid("qzxv")
