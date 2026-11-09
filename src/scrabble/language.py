"""Taalconfiguratie: letterverdeling en puntenwaarden per taal (JSON)."""

from __future__ import annotations

import json
from dataclasses import dataclass
from importlib import resources


@dataclass(frozen=True)
class TileSpec:
    count: int
    points: int


@dataclass(frozen=True)
class Language:
    code: str
    name: str
    tiles: dict[str, TileSpec]
    blank_count: int
    rack_size: int = 7
    bingo_bonus: int = 50

    @property
    def total_tiles(self) -> int:
        return sum(spec.count for spec in self.tiles.values()) + self.blank_count

    def points(self, letter: str) -> int:
        return self.tiles[letter].points


def load_language(code: str) -> Language:
    """Laad de configuratie van een taal, bijv. ``load_language("nl")``."""
    path = resources.files("scrabble").joinpath("languages", f"{code}.json")
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise ValueError(f"Onbekende taal: {code!r}") from None

    data = json.loads(text)
    tiles: dict[str, TileSpec] = {}
    for letter, spec in data["tiles"].items():
        if len(letter) != 1 or not letter.isalpha() or not letter.islower():
            raise ValueError(f"Ongeldige letter in taalbestand {code!r}: {letter!r}")
        tiles[letter] = TileSpec(count=int(spec["count"]), points=int(spec["points"]))

    return Language(
        code=str(data["code"]),
        name=str(data["name"]),
        tiles=tiles,
        blank_count=int(data["blank_count"]),
        rack_size=int(data.get("rack_size", 7)),
        bingo_bonus=int(data.get("bingo_bonus", 50)),
    )
