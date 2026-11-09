"""Het letterzakje."""

from __future__ import annotations

import random
from collections.abc import Iterable

from scrabble.language import Language
from scrabble.tiles import Tile


class Bag:
    def __init__(self, language: Language, rng: random.Random | None = None) -> None:
        self._rng = rng or random.Random()
        self._tiles: list[Tile] = [
            Tile(letter, spec.points)
            for letter, spec in language.tiles.items()
            for _ in range(spec.count)
        ]
        self._tiles += [Tile.blank() for _ in range(language.blank_count)]
        self._rng.shuffle(self._tiles)

    def __len__(self) -> int:
        return len(self._tiles)

    def is_empty(self) -> bool:
        return not self._tiles

    def contents(self) -> tuple[Tile, ...]:
        """Alle stenen in het zakje. Alleen bedoeld voor tests en analyse, niet voor spelers."""
        return tuple(self._tiles)

    def draw(self, count: int) -> list[Tile]:
        """Trek maximaal ``count`` stenen (minder als het zakje bijna leeg is)."""
        if count < 0:
            raise ValueError("count mag niet negatief zijn")
        count = min(count, len(self._tiles))
        drawn = self._tiles[len(self._tiles) - count :]
        del self._tiles[len(self._tiles) - count :]
        return drawn

    def put_back(self, tiles: Iterable[Tile]) -> None:
        """Stop stenen terug (bijv. bij ruilen). Een blanco wordt weer onbepaald."""
        for tile in tiles:
            self._tiles.append(Tile.blank() if tile.is_blank else tile)
        self._rng.shuffle(self._tiles)
