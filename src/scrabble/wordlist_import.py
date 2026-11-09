"""Maak een Scrabble-woordenlijst uit de OpenTaal-woordenlijst (wordlist.txt).

Gebruik:
    python -m scrabble.wordlist_import data/opentaal-wordlist.txt
"""

from __future__ import annotations

import argparse
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path

from scrabble.board import BOARD_SIZE
from scrabble.wordlist import normalize


@dataclass
class ImportStats:
    total: int = 0
    kept: int = 0
    skipped_capitalised: int = 0  # eigennamen, afkortingen, woorden met hoofdletters
    skipped_symbols: int = 0  # spaties, koppeltekens, apostrofs, cijfers, enz.
    skipped_length: int = 0  # te kort of te lang voor het bord


def convert_opentaal(
    lines: Iterable[str], max_length: int = BOARD_SIZE
) -> tuple[list[str], ImportStats]:
    """Filter een OpenTaal-lijst tot woorden die in Scrabble gelegd kunnen worden.

    Behouden worden woorden met alleen kleine letters (accenten worden weggehaald),
    van 2 tot ``max_length`` letters. Het resultaat is uniek en gesorteerd.
    """
    stats = ImportStats()
    kept: set[str] = set()
    for raw in lines:
        word = raw.strip()
        if not word:
            continue
        stats.total += 1
        if word != word.lower():
            stats.skipped_capitalised += 1
            continue
        plain = normalize(word)
        if not (plain.isascii() and plain.isalpha()):
            stats.skipped_symbols += 1
            continue
        if not 2 <= len(plain) <= max_length:
            stats.skipped_length += 1
            continue
        kept.add(plain)
    stats.kept = len(kept)
    return sorted(kept), stats


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m scrabble.wordlist_import",
        description="Maak data/woorden.txt uit de OpenTaal-woordenlijst.",
    )
    parser.add_argument("bron", help="pad naar wordlist.txt van OpenTaal")
    parser.add_argument("--uit", default="data/woorden.txt", help="uitvoerbestand")
    parser.add_argument("--max-lengte", type=int, default=BOARD_SIZE, help="langste woord")
    args = parser.parse_args(argv)

    source = Path(args.bron)
    if not source.is_file():
        print(f"Bronbestand niet gevonden: {source}")
        return 2
    words, stats = convert_opentaal(
        source.read_text(encoding="utf-8-sig").splitlines(), args.max_lengte
    )
    target = Path(args.uit)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("\n".join(words) + "\n", encoding="utf-8", newline="\n")

    print(f"Gelezen regels:                   {stats.total}")
    print(f"Overgeslagen (hoofdletters):      {stats.skipped_capitalised}")
    print(f"Overgeslagen (spatie, - ' cijfer): {stats.skipped_symbols}")
    print(f"Overgeslagen (lengte):            {stats.skipped_length}")
    print(f"Unieke woorden bewaard:           {stats.kept}")
    print(f"Geschreven naar: {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
