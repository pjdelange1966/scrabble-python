"""Het rek van een speler."""

from __future__ import annotations

from collections.abc import Iterable

from scrabble.bag import Bag
from scrabble.tiles import Tile


class Rack:
    def __init__(self, size: int = 7) -> None:
        self.size = size
        self._tiles: list[Tile] = []

    @property
    def tiles(self) -> tuple[Tile, ...]:
        return tuple(self._tiles)

    def __len__(self) -> int:
        return len(self._tiles)

    def letters(self) -> str:
        """Letters op het rek als tekst (blanco = '?')."""
        return "".join(t.letter for t in self._tiles)

    def add(self, tiles: Iterable[Tile]) -> None:
        new = list(tiles)
        if len(self._tiles) + len(new) > self.size:
            raise ValueError(f"Een rek bevat maximaal {self.size} stenen")
        self._tiles.extend(new)

    def remove(self, tile: Tile) -> None:
        try:
            self._tiles.remove(tile)
        except ValueError:
            raise ValueError(f"Steen {tile.letter!r} ligt niet op het rek") from None

    def refill(self, bag: Bag) -> None:
        """Vul het rek aan tot ``size`` stenen (of tot het zakje leeg is)."""
        self.add(bag.draw(self.size - len(self._tiles)))
