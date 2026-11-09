import random
import tempfile
from collections.abc import Callable
from pathlib import Path

import pytest

from scrabble.board import Board
from scrabble.cli import (
    CommandError,
    main,
    parse_exchange,
    parse_play,
    parse_square,
    render_board,
    render_rack,
    run_game,
)
from scrabble.game import Game
from scrabble.language import load_language
from scrabble.tiles import Tile
from scrabble.wordlist import WordList

NL = load_language("nl")
WORDS = WordList.from_words(["huis", "ui", "oe", "oh", "eu", "kuit"])


def tile(ch: str) -> Tile:
    return Tile.blank() if ch == "?" else Tile(ch, NL.points(ch))


def scripted(lines: list[str]) -> Callable[[str], str]:
    remaining = iter(lines)

    def read(prompt: str = "") -> str:
        try:
            return next(remaining)
        except StopIteration:
            raise EOFError from None

    return read


def new_game() -> Game:
    return Game(NL, ["Anna", "Bram"], random.Random(0), wordlist=WORDS)


def set_rack(game: Game, index: int, letters: str) -> None:
    rack = game.players[index].rack
    for t in rack.tiles:
        rack.remove(t)
    rack.add([tile(c) for c in letters])


def run(game: Game, lines: list[str], pause: bool = False) -> str:
    out: list[str] = []
    run_game(game, scripted(lines), out.append, pause=pause)
    return "\n".join(out)


def board_with_huis() -> Board:
    board = Board()
    for i, ch in enumerate("huis"):
        board.place(7, 4 + i, tile(ch))
    return board


# ---------- weergave ----------


def test_render_empty_board_has_header_premiums_and_center() -> None:
    lines = render_board(Board()).splitlines()
    assert len(lines) == 16
    assert lines[0].split() == list("ABCDEFGHIJKLMNO")
    assert lines[1].split()[:2] == ["1", "3W"]
    assert "**" in lines[8].split()


def test_render_board_shows_letters_and_lowercase_blanks() -> None:
    board = Board()
    board.place(7, 7, tile("h"))
    board.place(7, 8, Tile.blank().as_letter("u"))
    tokens = render_board(board).splitlines()[8].split()
    assert "H" in tokens
    assert "u" in tokens
    assert "**" not in tokens


def test_render_rack_shows_letters_with_points() -> None:
    game = new_game()
    set_rack(game, 0, "hu?")
    assert render_rack(game.players[0]).endswith("H4  U4  ?0")


# ---------- invoer lezen ----------


def test_parse_square() -> None:
    assert parse_square("H8") == (7, 7)
    assert parse_square("a1") == (0, 0)
    assert parse_square("o15") == (14, 14)


def test_parse_square_rejects_bad_input() -> None:
    for bad in ["P1", "H16", "8H", "H0", "", "HH"]:
        with pytest.raises(CommandError):
            parse_square(bad)


def test_parse_play_horizontal_and_vertical() -> None:
    horizontal = parse_play(["H8", "h", "HUIS"], Board(), NL)
    assert [(p.row, p.col, p.tile.letter) for p in horizontal] == [
        (7, 7, "h"),
        (7, 8, "u"),
        (7, 9, "i"),
        (7, 10, "s"),
    ]
    vertical = parse_play(["H8", "v", "ui"], Board(), NL)
    assert [(p.row, p.col) for p in vertical] == [(7, 7), (8, 7)]


def test_parse_play_skips_letters_already_on_board() -> None:
    placements = parse_play(["F7", "v", "kuit"], board_with_huis(), NL)
    assert [(p.row, p.col, p.tile.letter) for p in placements] == [
        (6, 5, "k"),
        (8, 5, "i"),
        (9, 5, "t"),
    ]


def test_parse_play_detects_mismatch_with_board() -> None:
    with pytest.raises(CommandError, match="ligt al een U"):
        parse_play(["F7", "v", "kait"], board_with_huis(), NL)


def test_parse_play_word_must_fit_on_board() -> None:
    with pytest.raises(CommandError, match="past niet"):
        parse_play(["M8", "h", "HUIS"], Board(), NL)


def test_parse_play_blank_in_parentheses() -> None:
    placements = parse_play(["H8", "h", "H(U)IS"], Board(), NL)
    assert placements[1].tile.is_blank
    assert placements[1].tile.letter == "u"
    assert not placements[0].tile.is_blank


def test_parse_play_rejects_bad_syntax() -> None:
    for args in (["H8", "h"], ["H8", "x", "huis"], ["H8", "h", "H(UU)IS"], ["H8", "h", "h1"]):
        with pytest.raises(CommandError):
            parse_play(args, Board(), NL)


def test_parse_exchange() -> None:
    tiles = parse_exchange(["ae?"], NL)
    assert [t.letter for t in tiles] == ["a", "e", "?"]
    assert tiles[2].is_unassigned_blank
    with pytest.raises(CommandError):
        parse_exchange(["a1"], NL)
    with pytest.raises(CommandError):
        parse_exchange([], NL)


# ---------- spelverloop ----------


def test_play_then_pass_then_quit() -> None:
    game = new_game()
    set_rack(game, 0, "huiseee")
    output = run(game, ["leg H8 h huis", "pas", "stop", "j"])
    assert "22 punten" in output
    assert "Je past." in output
    assert "Spel gestopt" in output
    assert game.players[0].score == 22
    assert game.current_player.name == "Anna"


def test_invalid_move_shows_reason_and_keeps_turn() -> None:
    game = new_game()
    set_rack(game, 0, "aaaaaaa")
    output = run(game, ["leg H8 h huis", "stop", "j"])
    assert "Dat kan niet" in output
    assert "niet op je rek" in output
    assert game.current_player.name == "Anna"
    assert game.board.is_empty()


def test_syntax_error_shows_message() -> None:
    output = run(new_game(), ["leg H8", "stop", "j"])
    assert "Dat kan niet" in output
    assert "Gebruik: leg" in output


def test_unknown_command_and_help() -> None:
    output = run(new_game(), ["foo", "hulp", "stop", "j"])
    assert "Onbekend commando 'foo'" in output
    assert "ruil <letters>" in output


def test_rack_board_and_score_commands() -> None:
    game = new_game()
    set_rack(game, 0, "huiseee")
    output = run(game, ["rek", "bord", "score", "stop", "j"])
    assert "H4" in output
    assert "Score: Anna: 0 | Bram: 0" in output


def test_stop_can_be_cancelled() -> None:
    game = new_game()
    output = run(game, ["stop", "n", "pas", "stop", "j"])
    assert "Je past." in output


def test_exchange_command() -> None:
    game = new_game()
    set_rack(game, 0, "aaaaaaa")
    output = run(game, ["ruil aa", "stop", "j"])
    assert "geruild" in output
    assert game.scoreless_turns == 1


def test_pause_screen_between_players() -> None:
    game = new_game()
    set_rack(game, 0, "huiseee")
    output = run(game, ["leg H8 h huis", "", "stop", "j"], pause=True)
    assert "Geef het toetsenbord aan Bram" in output
    assert "Laatste actie: Anna" in output


def test_game_over_shows_result() -> None:
    game = new_game()
    game.bag.draw(len(game.bag))
    set_rack(game, 0, "huis")
    set_rack(game, 1, "qz")
    output = run(game, ["leg H8 h huis"])
    assert "Einde van het spel" in output
    assert "Winnaar: Anna" in output


def test_end_of_input_stops_gracefully() -> None:
    assert "Spel afgebroken" in run(new_game(), [])


# ---------- opstarten ----------


def run_main(argv: list[str], lines: list[str]) -> tuple[int, str]:
    out: list[str] = []
    code = main(argv, scripted(lines), out.append)
    return code, "\n".join(out)


def test_main_starts_game_with_given_wordlist_and_players() -> None:
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder) / "woorden.txt"
        path.write_text("huis\nui\n", encoding="utf-8")
        code, output = run_main(
            ["--spelers", "Anna", "Bram", "--woordenlijst", str(path), "--seed", "1"],
            ["stop", "j"],
        )
    assert code == 0
    assert "Welkom bij Scrabble" in output
    assert "Aan de beurt: Anna" in output


def test_main_asks_for_players_when_not_given() -> None:
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder) / "woorden.txt"
        path.write_text("huis\n", encoding="utf-8")
        code, output = run_main(
            ["--woordenlijst", str(path)], ["x", "3", "Anna", "", "Cor", "stop", "j"]
        )
    assert code == 0
    assert "Kies een getal van 2 tot 4" in output
    assert "Speler 2" in output


def test_main_reports_missing_wordlist() -> None:
    code, output = run_main(["--woordenlijst", "bestaat-niet.txt"], [])
    assert code == 2
    assert "Geen woordenlijst gevonden" in output


def test_main_rejects_wrong_number_of_players() -> None:
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder) / "woorden.txt"
        path.write_text("huis\n", encoding="utf-8")
        code, _ = run_main(["--spelers", "Alleen", "--woordenlijst", str(path)], [])
    assert code == 2
