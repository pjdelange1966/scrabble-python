import pytest

from scrabble.language import load_language


def test_dutch_has_102_tiles() -> None:
    nl = load_language("nl")
    assert nl.total_tiles == 102
    assert nl.blank_count == 2
    assert nl.rack_size == 7


def test_dutch_letter_values() -> None:
    nl = load_language("nl")
    assert nl.points("e") == 1
    assert nl.points("i") == 1
    assert nl.points("q") == 10
    assert nl.points("x") == 8
    assert nl.tiles["e"].count == 18
    assert nl.tiles["n"].count == 10


def test_unknown_language_raises() -> None:
    with pytest.raises(ValueError):
        load_language("xx")
