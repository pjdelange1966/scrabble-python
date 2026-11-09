"""Bord: 15x15 raster met bonusvakken. Geen GUI-code in deze module."""

from __future__ import annotations

from enum import Enum

from scrabble.tiles import Tile

BOARD_SIZE = 15
CENTER = (BOARD_SIZE // 2, BOARD_SIZE // 2)


class Premium(Enum):
    NONE = "none"
    DOUBLE_LETTER = "dl"
    TRIPLE_LETTER = "tl"
    DOUBLE_WORD = "dw"
    TRIPLE_WORD = "tw"


# Linkerbovenkwadrant (rij en kolom 0..7). De rest volgt door spiegelen.
_QUADRANT: dict[Premium, list[tuple[int, int]]] = {
    Premium.TRIPLE_WORD: [(0, 0), (0, 7), (7, 0)],
    Premium.DOUBLE_WORD: [(1, 1), (2, 2), (3, 3), (4, 4), (7, 7)],
    Premium.TRIPLE_LETTER: [(1, 5), (5, 1), (5, 5)],
    Premium.DOUBLE_LETTER: [(0, 3), (3, 0), (2, 6), (6, 2), (3, 7), (7, 3), (6, 6)],
}


def _build_premium_map() -> dict[tuple[int, int], Premium]:
    last = BOARD_SIZE - 1
    result: dict[tuple[int, int], Premium] = {}
    for premium, squares in _QUADRANT.items():
        for r, c in squares:
            for rr, cc in {(r, c), (r, last - c), (last - r, c), (last - r, last - c)}:
                result[(rr, cc)] = premium
    return result


PREMIUMS: dict[tuple[int, int], Premium] = _build_premium_map()


class Board:
    def __init__(self) -> None:
        self._grid: list[list[Tile | None]] = [[None] * BOARD_SIZE for _ in range(BOARD_SIZE)]

    @staticmethod
    def in_bounds(row: int, col: int) -> bool:
        return 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE

    def _check(self, row: int, col: int) -> None:
        if not self.in_bounds(row, col):
            raise IndexError(f"Vak ({row}, {col}) ligt buiten het bord")

    def get(self, row: int, col: int) -> Tile | None:
        self._check(row, col)
        return self._grid[row][col]

    def place(self, row: int, col: int, tile: Tile) -> None:
        self._check(row, col)
        if tile.is_unassigned_blank:
            raise ValueError("Geef de blanco eerst een letter (Tile.as_letter)")
        if self._grid[row][col] is not None:
            raise ValueError(f"Vak ({row}, {col}) is al bezet")
        self._grid[row][col] = tile

    def premium_at(self, row: int, col: int) -> Premium:
        self._check(row, col)
        return PREMIUMS.get((row, col), Premium.NONE)

    def is_empty(self) -> bool:
        return all(cell is None for row in self._grid for cell in row)
