from importlib import resources

from scrabble.language import load_language


def language_codes() -> list[str]:
    folder = resources.files("scrabble").joinpath("languages")
    names = [p.name for p in folder.iterdir() if p.name.endswith(".json")]
    return sorted(name.removesuffix(".json") for name in names)


def test_there_is_at_least_dutch() -> None:
    assert "nl" in language_codes()


def test_every_language_file_is_consistent() -> None:
    for code in language_codes():
        language = load_language(code)
        assert language.code == code
        assert language.rack_size > 0
        assert language.bingo_bonus >= 0
        assert language.blank_count >= 0
        assert language.total_tiles == sum(s.count for s in language.tiles.values()) + (
            language.blank_count
        )
        for letter, spec in language.tiles.items():
            assert len(letter) == 1 and letter.isalpha() and letter.islower(), (code, letter)
            assert spec.count >= 1, (code, letter)
            assert spec.points >= 1, (code, letter)


# Controleer deze tabel tegen de officiële Nederlandse Scrabble-regels. Deze test is een
# vangnet: hij laat zien als iemand per ongeluk een waarde in nl.json wijzigt.
DUTCH = {
    "a": (6, 1), "b": (2, 3), "c": (2, 5), "d": (5, 2), "e": (18, 1), "f": (2, 4),
    "g": (3, 3), "h": (2, 4), "i": (4, 1), "j": (2, 4), "k": (3, 3), "l": (3, 3),
    "m": (3, 3), "n": (10, 1), "o": (6, 1), "p": (2, 3), "q": (1, 10), "r": (5, 2),
    "s": (5, 2), "t": (5, 2), "u": (3, 4), "v": (2, 4), "w": (2, 5), "x": (1, 8),
    "y": (1, 8), "z": (2, 4),
}  # fmt: skip


def test_dutch_distribution_table() -> None:
    nl = load_language("nl")
    assert {k: (v.count, v.points) for k, v in nl.tiles.items()} == DUTCH
    assert nl.blank_count == 2
    assert nl.total_tiles == 102
    assert nl.rack_size == 7
    assert nl.bingo_bonus == 50
