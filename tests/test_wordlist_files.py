import tempfile
from pathlib import Path

from scrabble.wordlist import WordList, normalize
from scrabble.wordlist_import import main


def test_from_file_handles_bom_and_windows_line_endings() -> None:
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder) / "woorden.txt"
        path.write_bytes(b"\xef\xbb\xbfhuis\r\nui\r\n\r\n")
        words = WordList.from_file(path)
    assert words.is_valid("huis")
    assert words.is_valid("ui")
    assert len(words) == 2


def test_import_tool_handles_bom() -> None:
    with tempfile.TemporaryDirectory() as folder:
        source = Path(folder) / "wordlist.txt"
        target = Path(folder) / "woorden.txt"
        source.write_bytes(b"\xef\xbb\xbfhuis\r\nAmsterdam\r\nui\r\n")
        assert main([str(source), "--uit", str(target)]) == 0
        assert target.read_text(encoding="utf-8").splitlines() == ["huis", "ui"]


def test_from_words_drops_unusable_lines() -> None:
    words = WordList.from_words(["huis", "a", "", "auto-bus", "zo'n", "a4", "zo even", "Ui"])
    assert len(words) == 2
    assert words.is_valid("ui")


def test_is_valid_ignores_case_spaces_and_accents() -> None:
    words = WordList.from_words(["cafe", "huis"])
    assert words.is_valid("  HUIS ")
    assert words.is_valid("Café")
    assert not words.is_valid("")
    assert not words.is_valid("h")
    assert not words.is_valid("huizen")


def test_normalize_is_idempotent() -> None:
    for word in ["café", "Ruïne", "ÉÉN", "naïef", "huis"]:
        once = normalize(word)
        assert normalize(once) == once
