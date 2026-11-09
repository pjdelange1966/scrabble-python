"""Speelstenen."""

from __future__ import annotations

from dataclasses import dataclass

BLANK = "?"


@dataclass(frozen=True)
class Tile:
    """Een steen. Een blanco heeft altijd 0 punten, ook als hij een letter voorstelt."""

    letter: str
    points: int
    is_blank: bool = False

    @classmethod
    def blank(cls) -> Tile:
        return cls(BLANK, 0, True)

    @property
    def is_unassigned_blank(self) -> bool:
        return self.is_blank and self.letter == BLANK

    def as_letter(self, letter: str) -> Tile:
        """Geef een blanco een letter (alleen voor blanco's)."""
        if not self.is_blank:
            raise ValueError("Alleen een blanco kan een letter krijgen")
        if len(letter) != 1 or not letter.isalpha():
            raise ValueError(f"Ongeldige letter: {letter!r}")
        return Tile(letter.lower(), 0, True)
