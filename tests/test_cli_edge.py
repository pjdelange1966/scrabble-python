import random
import tempfile
from pathlib import Path

from helpers import NL, run_cli, scripted, set_rack

from scrabble.cli import main
from scrabble.game import Game
from scrabble.wordlist import WordList

WL = WordList.from_words(["huis", "ui", "oe"])


def new_game(players: int = 2) -> Game:
    names = ["Anna", "Bram", "Cor"][:players]
    return Game(NL, names, random.Random(0), wordlist=WL)


def test_commands_are_case_insensitive() -> None:
    game = new_game()
    set_rack(game, 0, "huiseee")
    run_cli(game, ["LEG h8 H huis"])
    assert game.players[0].score == 22


def test_single_letter_shortcuts() -> None:
    game = new_game()
    set_rack(game, 0, "huiseee")
    run_cli(game, ["l H8 h huis", "p", "r a"])
    assert game.players[0].score == 22
    assert game.scoreless_turns in {1, 2}


def test_spaces_inside_the_word_are_ignored() -> None:
    game = new_game()
    set_rack(game, 0, "huiseee")
    run_cli(game, ["leg H8 h H U I S"])
    assert game.players[0].score == 22


def test_vertical_move_with_blank() -> None:
    game = new_game()
    set_rack(game, 0, "h?isaaa")
    run_cli(game, ["leg H8 v H(U)IS"])
    placed = game.board.get(8, 7)
    assert placed is not None and placed.is_blank and placed.letter == "u"
    assert game.players[0].score == 14


def test_empty_lines_are_ignored() -> None:
    output = run_cli(new_game(), ["", "   ", "stop", "j"])
    assert "Spel gestopt" in output
    assert "Dat kan niet" not in output


def test_stop_accepts_ja() -> None:
    assert "Spel gestopt" in run_cli(new_game(), ["stop", "ja"])


def test_exchange_with_invalid_letter_shows_message() -> None:
    output = run_cli(new_game(), ["ruil a1", "stop", "j"])
    assert "geen geldige letter" in output


def test_pause_screen_for_three_players() -> None:
    output = run_cli(new_game(3), ["pas", "", "pas", "", "stop", "j"], pause=True)
    assert "Geef het toetsenbord aan Bram" in output
    assert "Geef het toetsenbord aan Cor" in output


def test_main_rejects_five_players() -> None:
    out: list[str] = []
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder) / "woorden.txt"
        path.write_text("huis\n", encoding="utf-8")
        argv = ["--spelers", "a", "b", "c", "d", "e", "--woordenlijst", str(path)]
        code = main(argv, scripted([]), out.append)
    assert code == 2
    assert "2 tot 4" in "\n".join(out)
