"""Gedeelde hulpfuncties voor de tests (bevat zelf geen tests)."""

from __future__ import annotations

import random
from collections import Counter
from collections.abc import Callable, Iterable, Sequence

from scrabble.board import BOARD_SIZE, Board
from scrabble.cli import run_game
from scrabble.game import Game
from scrabble.language import load_language
from scrabble.move import InvalidMoveError, Placement
from scrabble.rack import Rack
from scrabble.rules import validate_move
from scrabble.tiles import BLANK, Tile

NL = load_language("nl")


def tile(ch: str) -> Tile:
    """Een steen met de Nederlandse puntenwaarde; '?' is een blanco."""
    return Tile.blank() if ch == "?" else Tile(ch, NL.points(ch))


def rack_of(letters: str) -> Rack:
    rack = Rack(NL.rack_size)
    rack.add([tile(c) for c in letters])
    return rack


def set_rack(game: Game, index: int, letters: str) -> None:
    """Geef een speler precies deze stenen (de oude stenen verdwijnen uit het spel)."""
    rack = game.players[index].rack
    for t in rack.tiles:
        rack.remove(t)
    rack.add([tile(c) for c in letters])


def word_placements(row: int, col: int, text: str, horizontal: bool = True) -> list[Placement]:
    result = []
    for i, ch in enumerate(text):
        r, c = (row, col + i) if horizontal else (row + i, col)
        result.append(Placement(r, c, tile(ch)))
    return result


def put(board: Board, row: int, col: int, text: str, horizontal: bool = True) -> None:
    for p in word_placements(row, col, text, horizontal):
        board.place(p.row, p.col, p.tile)


def board_tiles(board: Board) -> list[tuple[int, int, Tile]]:
    found = []
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            t = board.get(r, c)
            if t is not None:
                found.append((r, c, t))
    return found


def transpose(board: Board) -> Board:
    """Spiegel het bord over de diagonaal (rij en kolom wisselen)."""
    mirrored = Board()
    for r, c, t in board_tiles(board):
        mirrored.place(c, r, t)
    return mirrored


def scripted(lines: list[str]) -> Callable[[str], str]:
    remaining = iter(lines)

    def read(prompt: str = "") -> str:
        try:
            return next(remaining)
        except StopIteration:
            raise EOFError from None

    return read


def run_cli(game: Game, lines: list[str], pause: bool = False) -> str:
    out: list[str] = []
    run_game(game, scripted(lines), out.append, pause=pause)
    return "\n".join(out)


# ---------- telling van stenen ----------


def letter_counts(tiles: Iterable[Tile]) -> Counter[str]:
    """Tel stenen per letter; elke blanco telt als '?', ook als hij een letter voorstelt."""
    return Counter(BLANK if t.is_blank else t.letter for t in tiles)


def expected_counts() -> Counter[str]:
    counts: Counter[str] = Counter({letter: spec.count for letter, spec in NL.tiles.items()})
    counts[BLANK] += NL.blank_count
    return counts


def total_counts(game: Game) -> Counter[str]:
    """Alle stenen in het spel: zakje, rekken en bord samen."""
    tiles = list(game.bag.contents())
    for player in game.players:
        tiles += player.rack.tiles
    tiles += [t for _, _, t in board_tiles(game.board)]
    return letter_counts(tiles)


# ---------- eenvoudige testspeler (brute force, alleen voor tests) ----------


def placements_for(
    board: Board,
    text: str,
    row: int,
    col: int,
    horizontal: bool,
    rack_counts: Counter[str],
) -> list[Placement] | None:
    """Stenen om ``text`` hier te leggen met dit rek, of None als dat niet kan."""
    remaining = Counter(rack_counts)
    placements: list[Placement] = []
    for i, ch in enumerate(text):
        r, c = (row, col + i) if horizontal else (row + i, col)
        if not board.in_bounds(r, c):
            return None
        existing = board.get(r, c)
        if existing is not None:
            if existing.letter != ch:
                return None
            continue
        if remaining[ch] > 0:
            remaining[ch] -= 1
            placements.append(Placement(r, c, tile(ch)))
        elif remaining[BLANK] > 0:
            remaining[BLANK] -= 1
            placements.append(Placement(r, c, Tile.blank().as_letter(ch)))
        else:
            return None
    return placements or None


def start_squares(board: Board, length: int, horizontal: bool) -> list[tuple[int, int]]:
    """Beginvakken waar een woord van deze lengte het bord kan raken."""
    center = BOARD_SIZE // 2
    last_start = BOARD_SIZE - length
    tiles = board_tiles(board)
    if not tiles:
        span = range(max(0, center - length + 1), min(center, last_start) + 1)
        return [(center, c) for c in span] if horizontal else [(r, center) for r in span]
    rows = [r for r, _, _ in tiles]
    cols = [c for _, c, _ in tiles]
    r_lo, r_hi = min(rows) - 1, max(rows) + 1
    c_lo, c_hi = min(cols) - 1, max(cols) + 1
    if horizontal:
        return [
            (r, c)
            for r in range(max(0, r_lo), min(BOARD_SIZE - 1, r_hi) + 1)
            for c in range(max(0, c_lo - length + 1), min(last_start, c_hi) + 1)
        ]
    return [
        (r, c)
        for r in range(max(0, r_lo - length + 1), min(last_start, r_hi) + 1)
        for c in range(max(0, c_lo), min(BOARD_SIZE - 1, c_hi) + 1)
    ]


def pick_move(game: Game, words: Sequence[str], rng: random.Random) -> list[Placement] | None:
    """Zoek een geldige zet voor de speler aan de beurt, of None als er geen is."""
    assert game.wordlist is not None
    rack = game.current_player.rack
    rack_counts = Counter(t.letter for t in rack.tiles)
    board_letters = Counter(t.letter for _, _, t in board_tiles(game.board))
    candidates = list(words)
    rng.shuffle(candidates)
    for text in candidates:
        missing = Counter(text) - rack_counts
        if sum((missing - board_letters).values()) > rack_counts[BLANK]:
            continue  # kan nooit: letters ontbreken op rek en bord
        for horizontal in (True, False):
            for row, col in start_squares(game.board, len(text), horizontal):
                placements = placements_for(game.board, text, row, col, horizontal, rack_counts)
                if placements is None:
                    continue
                try:
                    validate_move(game.board, rack, placements, game.wordlist, game.language)
                except InvalidMoveError:
                    continue
                return placements
    return None
