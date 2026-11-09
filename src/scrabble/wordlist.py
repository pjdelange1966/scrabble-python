"""Woordenlijst: inladen, normaliseren en valideren."""

from __future__ import annotations

import unicodedata
from collections.abc import Iterable
from pathlib import Path


def normalize(word: str) -> str:
    """Kleine letters, zonder accenten (ë -> e), zonder omringende spaties."""
    decomposed = unicodedata.normalize("NFD", word.strip().lower())
    return "".join(c for c in decomposed if unicodedata.category(c) != "Mn")


class WordList:
    """Set van toegestane woorden."""

    def __init__(self, words: set[str]) -> None:
        self._words = words

    @classmethod
    def from_words(cls, words: Iterable[str]) -> WordList:
        """Maak een lijst uit woorden; ongeldige regels (te kort, koppelteken...) vallen af."""
        cleaned: set[str] = set()
        for word in words:
            w = normalize(word)
            if len(w) >= 2 and w.isascii() and w.isalpha():
                cleaned.add(w)
        return cls(cleaned)

    @classmethod
    def from_file(cls, path: str | Path) -> WordList:
        # utf-8-sig: negeert een BOM, die Windows-programma's (zoals Kladblok) soms toevoegen
        return cls.from_words(Path(path).read_text(encoding="utf-8-sig").splitlines())

    def is_valid(self, word: str) -> bool:
        return normalize(word) in self._words

    def __len__(self) -> int:
        return len(self._words)
