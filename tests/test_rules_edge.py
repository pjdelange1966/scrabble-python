import pytest
from helpers import NL, put, rack_of, tile, word_placements

from scrabble.board import Board
from scrabble.move import InvalidMoveError, Placement, ScoredMove
from scrabble.rules import validate_move
from scrabble.tiles import Tile
from scrabble.wordlist import WordList

WL = WordList.from_words(["huis", "huisdier", "ui", "oe", "en", "eu", "kuit", "hui", "ik"])


def check(board: Board, letters: str, placements: list[Placement]) -> ScoredMove:
    return validate_move(board, rack_of(letters), placements, WL, NL)


def board_with_huis() -> Board:
    board = Board()
    put(board, 7, 4, "huis")
    return board


# ---------- eerste zet ----------


def test_first_move_vertical_through_center() -> None:
    move = check(Board(), "huis", word_placements(4, 7, "huis", horizontal=False))
    assert move.total == 22  # (4+4+1+2) x 2, s ligt op de middenster


def test_first_move_with_center_in_the_middle_of_the_word() -> None:
    move = check(Board(), "huis", word_placements(7, 6, "huis"))
    assert move.total == 22


def test_blank_on_center_scores_zero_but_doubles_word() -> None:
    placements = word_placements(7, 4, "huis")
    placements[3] = Placement(7, 7, Tile.blank().as_letter("s"))
    assert check(Board(), "hui?", placements).total == 18  # (4+4+1+0) x 2


# ---------- bonusvakken ----------


def test_triple_word_and_double_word_multiply() -> None:
    board = Board()
    board.place(7, 1, tile("u"))
    board.place(7, 2, tile("i"))
    placements = [
        Placement(7, 0, tile("h")),  # driedubbel woord
        Placement(7, 3, tile("s")),  # dubbele letter
        Placement(7, 4, tile("d")),
        Placement(7, 5, tile("i")),
        Placement(7, 6, tile("e")),
        Placement(7, 7, tile("r")),  # dubbel woord
    ]
    move = check(board, "hsdier", placements)
    assert [w.text for w in move.words] == ["huisdier"]
    assert move.bonus == 0  # maar 6 stenen gelegd
    assert move.total == 114  # (4+4+1+2x2+2+1+1+2) x 3 x 2


def test_letter_premium_counts_for_both_words_of_a_tile() -> None:
    board = Board()
    board.place(6, 7, tile("n"))
    board.place(7, 6, tile("u"))
    move = check(board, "e", [Placement(6, 6, tile("e"))])  # (6,6) is dubbele letter
    assert sorted(w.text for w in move.words) == ["en", "eu"]
    assert move.total == 9  # en: 2+1, eu: 2+4


def test_blank_on_triple_letter_scores_zero() -> None:
    placements = [
        Placement(6, 5, tile("k")),
        Placement(8, 5, tile("i")),
        Placement(9, 5, Tile.blank().as_letter("t")),  # driedubbele letter
    ]
    assert check(board_with_huis(), "ki?", placements).total == 8  # 3+4+1+0


# ---- rand van het bord en verlengen ----


def test_word_ending_on_the_right_edge() -> None:
    board = Board()
    board.place(7, 11, tile("h"))
    placements = word_placements(7, 12, "uis")
    move = check(board, "uis", placements)
    assert [w.text for w in move.words] == ["huis"]
    assert move.total == 33  # (4+4+1+2) x 3, de s ligt op driedubbel woord


def test_extending_a_word_on_both_sides_at_once() -> None:
    board = Board()
    board.place(7, 6, tile("u"))
    board.place(7, 7, tile("i"))
    placements = [Placement(7, 5, tile("h")), Placement(7, 8, tile("s"))]
    move = check(board, "hs", placements)
    assert [w.text for w in move.words] == ["huis"]
    assert move.total == 11  # de middenster telt niet opnieuw, i ligt er al


# ---------- ongeldige zetten ----------


def test_parallel_play_with_two_invalid_cross_words() -> None:
    placements = word_placements(8, 4, "oe")  # onder h en u: "ho" en "ue"
    with pytest.raises(InvalidMoveError, match="HO, UE"):
        check(board_with_huis(), "oe", placements)


def test_same_tile_cannot_be_used_twice() -> None:
    placements = [Placement(7, 7, tile("h")), Placement(7, 8, tile("h"))]
    with pytest.raises(InvalidMoveError, match="niet op je rek: H"):
        check(Board(), "h", placements)


def test_tile_with_wrong_points_is_not_the_rack_tile() -> None:
    with pytest.raises(InvalidMoveError, match="niet op je rek"):
        check(Board(), "ab", [Placement(7, 7, Tile("a", 5)), Placement(7, 8, tile("b"))])


def test_letter_that_does_not_exist_in_the_game() -> None:
    with pytest.raises(InvalidMoveError, match="bestaat niet"):
        check(Board(), "ab", [Placement(7, 7, Tile("é", 1)), Placement(7, 8, tile("b"))])


def test_diagonal_contact_is_not_a_connection() -> None:
    board = Board()
    board.place(7, 7, tile("h"))
    with pytest.raises(InvalidMoveError, match="aansluiten"):
        check(board, "oe", word_placements(8, 8, "oe"))


def test_single_tile_without_neighbours_is_rejected() -> None:
    with pytest.raises(InvalidMoveError, match="aansluiten"):
        check(board_with_huis(), "a", [Placement(0, 0, tile("a"))])


def test_single_tile_that_only_extends_to_an_invalid_word() -> None:
    with pytest.raises(InvalidMoveError, match="HUISE"):
        check(board_with_huis(), "e", [Placement(7, 8, tile("e"))])
