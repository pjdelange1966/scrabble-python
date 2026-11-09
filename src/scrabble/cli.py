"""Tekstversie van Scrabble voor in de terminal (PowerShell).

De invoer en uitvoer zijn losgekoppeld (``read`` en ``write``), zodat dit te testen is.
"""

from __future__ import annotations

import argparse
import random
import re
from collections.abc import Callable, Sequence
from pathlib import Path

from scrabble.board import BOARD_SIZE, CENTER, Board, Premium, square_name
from scrabble.game import MAX_PLAYERS, MIN_PLAYERS, Game
from scrabble.language import Language, load_language
from scrabble.move import InvalidMoveError, Placement, ScoredMove
from scrabble.player import Player
from scrabble.tiles import Tile
from scrabble.wordlist import WordList

ReadFn = Callable[[str], str]
WriteFn = Callable[[str], None]

PROJECT_ROOT = Path(__file__).resolve().parents[2]

HELP = """Commando's:
  leg <vak> <h|v> <woord>   Leg een woord, bijv.  leg H8 h HUIS
                            Letters die al op het bord liggen typ je gewoon mee.
                            Een blanco schrijf je tussen haakjes, bijv.  H(U)IS
  pas                       Sla je beurt over
  ruil <letters>            Ruil stenen met het zakje, bijv.  ruil AEI  (blanco = ?)
  rek                       Toon je rek opnieuw
  bord                      Toon het bord
  score                     Toon de tussenstand
  hulp                      Toon deze hulp
  stop                      Stop het spel

Bonusvakken: 3W = woord x3, 2W = woord x2, 3L = letter x3, 2L = letter x2,
** = midden (woord x2). Kleine letters op het bord zijn blanco's."""

NO_WORDLIST = (
    "Geen woordenlijst gevonden.\n"
    "Zet een woordenlijst (één woord per regel, UTF-8) in data/woorden.txt of geef het pad op "
    "met --woordenlijst PAD.\nZie data/README.md."
)

_PREMIUM_LABEL = {
    Premium.TRIPLE_WORD: "3W",
    Premium.DOUBLE_WORD: "2W",
    Premium.TRIPLE_LETTER: "3L",
    Premium.DOUBLE_LETTER: "2L",
}
_SQUARE = re.compile(r"^([A-Oa-o])(\d{1,2})$")
_WORD = re.compile(r"(?:\([A-Za-z]\)|[A-Za-z])+")
_WORD_TOKEN = re.compile(r"\(([A-Za-z])\)|([A-Za-z])")


class CommandError(Exception):
    """De invoer van de speler is niet te begrijpen."""


# ---------- weergave ----------


def render_board(board: Board) -> str:
    header = "    " + "".join(f" {chr(ord('A') + c)} " for c in range(BOARD_SIZE))
    lines = [header]
    for r in range(BOARD_SIZE):
        cells = []
        for c in range(BOARD_SIZE):
            tile = board.get(r, c)
            if tile is not None:
                text = tile.letter.lower() if tile.is_blank else tile.letter.upper()
            elif (r, c) == CENTER:
                text = "**"
            else:
                text = _PREMIUM_LABEL.get(board.premium_at(r, c), ".")
            cells.append(f" {text:<2}")
        lines.append(f"{r + 1:>2}  " + "".join(cells))
    return "\n".join(lines)


def render_rack(player: Player) -> str:
    tiles = "  ".join(f"{t.letter.upper()}{t.points}" for t in player.rack.tiles)
    return f"Rek van {player.name}:  {tiles}"


def render_status(game: Game) -> str:
    scores = " | ".join(f"{p.name}: {p.score}" for p in game.players)
    return f"Score: {scores}   Zakje: {len(game.bag)} stenen"


def render_turn(game: Game, last: str | None = None) -> str:
    parts = [f"\n=== Aan de beurt: {game.current_player.name} ==="]
    if last:
        parts.append(f"Laatste actie: {last}")
    parts += [
        render_status(game),
        "",
        render_board(game.board),
        "",
        render_rack(game.current_player),
    ]
    return "\n".join(parts)


def describe_move(move: ScoredMove) -> str:
    words = ", ".join(f"{w.text.upper()} ({w.score})" for w in move.words)
    text = f"Gelegd: {words}."
    if move.bonus:
        text += f" Bingo! +{move.bonus} punten."
    return f"{text} Totaal: {move.total} punten."


def render_result(game: Game) -> str:
    ranking = sorted(game.players, key=lambda p: p.score, reverse=True)
    lines = ["", "=== Einde van het spel ==="]
    lines += [f"{i}. {p.name}: {p.score}" for i, p in enumerate(ranking, start=1)]
    winners = game.winners
    if len(winners) == 1:
        lines.append(f"Winnaar: {winners[0].name}!")
    else:
        lines.append("Gelijkspel tussen: " + ", ".join(p.name for p in winners))
    return "\n".join(lines)


# ---------- invoer lezen ----------


def parse_square(text: str) -> tuple[int, int]:
    """'H8' -> (rij 7, kolom 7)."""
    match = _SQUARE.match(text)
    row = int(match.group(2)) - 1 if match else -1
    if match is None or not 0 <= row < BOARD_SIZE:
        raise CommandError(
            f"'{text}' is geen geldig vak. Gebruik een letter A-O en een getal 1-15, bijv. H8."
        )
    return row, ord(match.group(1).upper()) - ord("A")


def parse_direction(text: str) -> bool:
    """True = horizontaal, False = verticaal."""
    lowered = text.lower()
    if lowered in {"h", "horizontaal"}:
        return True
    if lowered in {"v", "verticaal"}:
        return False
    raise CommandError("Kies de richting 'h' (horizontaal) of 'v' (verticaal).")


def parse_play(args: Sequence[str], board: Board, language: Language) -> list[Placement]:
    """Vertaal 'H8 h HUIS' naar stenen. Letters die al op het bord liggen worden overgeslagen."""
    if len(args) < 3:
        raise CommandError("Gebruik: leg <vak> <h|v> <woord>, bijv.  leg H8 h HUIS")
    row, col = parse_square(args[0])
    horizontal = parse_direction(args[1])
    word = "".join(args[2:])
    if not _WORD.fullmatch(word):
        raise CommandError("Gebruik alleen letters. Een blanco schrijf je tussen haakjes: H(U)IS.")

    placements: list[Placement] = []
    for i, token in enumerate(_WORD_TOKEN.finditer(word)):
        is_blank = token.group(1) is not None
        letter = (token.group(1) or token.group(2)).lower()
        r, c = (row, col + i) if horizontal else (row + i, col)
        if not board.in_bounds(r, c):
            raise CommandError("Het woord past niet op het bord.")
        if letter not in language.tiles:
            raise CommandError(f"De letter {letter.upper()} bestaat niet in dit spel.")
        existing = board.get(r, c)
        if existing is not None:
            if existing.letter != letter:
                raise CommandError(
                    f"Op {square_name(r, c)} ligt al een {existing.letter.upper()}, "
                    f"geen {letter.upper()}."
                )
            continue
        tile = Tile.blank().as_letter(letter) if is_blank else Tile(letter, language.points(letter))
        placements.append(Placement(r, c, tile))
    return placements


def parse_exchange(args: Sequence[str], language: Language) -> list[Tile]:
    text = "".join(args).lower()
    if not text:
        raise CommandError("Gebruik: ruil <letters>, bijv.  ruil AEI  (een blanco is ?)")
    tiles: list[Tile] = []
    for ch in text:
        if ch == "?":
            tiles.append(Tile.blank())
        elif ch in language.tiles:
            tiles.append(Tile(ch, language.points(ch)))
        else:
            raise CommandError(f"'{ch}' is geen geldige letter.")
    return tiles


# ---------- het spel spelen ----------


def run_game(
    game: Game,
    read: ReadFn = input,
    write: WriteFn = print,
    pause: bool = True,
) -> None:
    """Speel het spel in de terminal tot het afgelopen is of de spelers stoppen."""
    write(f"Welkom bij Scrabble ({game.language.name}).\n\n{HELP}")
    try:
        _loop(game, read, write, pause)
    except (EOFError, KeyboardInterrupt):
        write("\nSpel afgebroken.")
        return
    if game.is_over:
        write(render_result(game))


def _loop(game: Game, read: ReadFn, write: WriteFn, pause: bool) -> None:
    last: str | None = None
    show = True
    while not game.is_over:
        if show:
            write(render_turn(game, last))
        show = False
        player = game.current_player
        line = read(f"{player.name}> ").strip()
        if not line:
            continue
        verb, *args = line.split()
        verb = verb.lower()

        advanced = False
        try:
            if verb in {"leg", "l"}:
                move = game.play(parse_play(args, game.board, game.language))
                write(describe_move(move))
                last, advanced = f"{player.name}: {describe_move(move)}", True
            elif verb in {"pas", "p"}:
                game.pass_turn()
                write("Je past.")
                last, advanced = f"{player.name} paste.", True
            elif verb in {"ruil", "r"}:
                game.exchange(parse_exchange(args, game.language))
                write("Je hebt stenen geruild.")
                last, advanced = f"{player.name} ruilde stenen.", True
            elif verb == "rek":
                write(render_rack(player))
            elif verb == "bord":
                write(render_board(game.board))
            elif verb == "score":
                write(render_status(game))
            elif verb in {"hulp", "help", "?"}:
                write(HELP)
            elif verb == "stop":
                answer = read("Weet je zeker dat je wilt stoppen? (j/n) ").strip().lower()
                if answer in {"j", "ja"}:
                    write("Spel gestopt. Tot ziens!")
                    return
            else:
                write(f"Onbekend commando '{verb}'. Typ 'hulp' voor de commando's.")
        except (CommandError, InvalidMoveError) as error:
            write(f"Dat kan niet: {error}")

        if advanced and not game.is_over:
            show = True
            if pause:
                write("\n" * 40)
                write(f"Geef het toetsenbord aan {game.current_player.name} en druk op Enter...")
                read("")


# ---------- opstarten ----------


def find_wordlist(explicit: str | None) -> tuple[Path, bool] | None:
    """Zoek de woordenlijst. De boolean is True als het alleen de kleine voorbeeldlijst is."""
    if explicit is not None:
        path = Path(explicit)
        return (path, False) if path.is_file() else None
    for name, is_sample in (("woorden.txt", False), ("voorbeeld-woorden.txt", True)):
        for base in (Path.cwd(), PROJECT_ROOT):
            path = base / "data" / name
            if path.is_file():
                return path, is_sample
    return None


def ask_players(read: ReadFn, write: WriteFn) -> list[str]:
    while True:
        answer = read(f"Aantal spelers ({MIN_PLAYERS}-{MAX_PLAYERS}) [2]: ").strip() or "2"
        if answer.isdigit() and MIN_PLAYERS <= int(answer) <= MAX_PLAYERS:
            break
        write(f"Kies een getal van {MIN_PLAYERS} tot {MAX_PLAYERS}.")
    return [
        read(f"Naam speler {i}: ").strip() or f"Speler {i}" for i in range(1, int(answer) + 1)
    ]


def main(
    argv: Sequence[str] | None = None,
    read: ReadFn = input,
    write: WriteFn = print,
) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m scrabble", description="Scrabble in de terminal (Nederlands)."
    )
    parser.add_argument("--spelers", nargs="+", metavar="NAAM", help="namen van 2 tot 4 spelers")
    parser.add_argument("--woordenlijst", metavar="PAD", help="pad naar de woordenlijst (.txt)")
    parser.add_argument("--seed", type=int, help="vaste seed (voor een herhaalbaar spel)")
    args = parser.parse_args(argv)

    located = find_wordlist(args.woordenlijst)
    if located is None:
        write(NO_WORDLIST)
        return 2
    path, is_sample = located
    wordlist = WordList.from_file(path)
    if is_sample:
        write(
            f"LET OP: je gebruikt de kleine voorbeeldlijst ({len(wordlist)} woorden). "
            "Zet een echte woordenlijst in data/woorden.txt om echt te spelen."
        )

    try:
        names: list[str] = args.spelers or ask_players(read, write)
        rng = random.Random(args.seed) if args.seed is not None else None
        game = Game(load_language("nl"), names, rng, wordlist=wordlist)
    except (EOFError, KeyboardInterrupt):
        return 1
    except ValueError as error:
        write(str(error))
        return 2

    run_game(game, read, write)
    return 0
