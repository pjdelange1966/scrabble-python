import pytest

from scrabble.board import BOARD_SIZE, CENTER, PREMIUMS, Board, Premium
from scrabble.tiles import Tile


def count(premium: Premium) -> int:
    return sum(1 for p in PREMIUMS.values() if p is premium)


def test_premium_square_counts() -> None:
    assert count(Premium.TRIPLE_WORD) == 8
    assert count(Premium.DOUBLE_WORD) == 17  # incl. middenster
    assert count(Premium.TRIPLE_LETTER) == 12
    assert count(Premium.DOUBLE_LETTER) == 24


def test_center_is_double_word() -> None:
    assert Board().premium_at(*CENTER) is Premium.DOUBLE_WORD


def test_corners_are_triple_word() -> None:
    board = Board()
    last = BOARD_SIZE - 1
    for r, c in [(0, 0), (0, last), (last, 0), (last, last)]:
        assert board.premium_at(r, c) is Premium.TRIPLE_WORD


def test_premium_map_is_symmetric() -> None:
    board = Board()
    last = BOARD_SIZE - 1
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            p = board.premium_at(r, c)
            assert p is board.premium_at(r, last - c)
            assert p is board.premium_at(last - r, c)
            assert p is board.premium_at(c, r)


def test_new_board_is_empty() -> None:
    assert Board().is_empty()


def test_place_and_get() -> None:
    board = Board()
    tile = Tile("a", 1)
    board.place(7, 7, tile)
    assert board.get(7, 7) == tile
    assert not board.is_empty()


def test_cannot_place_on_occupied_square() -> None:
    board = Board()
    board.place(7, 7, Tile("a", 1))
    with pytest.raises(ValueError):
        board.place(7, 7, Tile("b", 3))


def test_out_of_bounds_raises() -> None:
    board = Board()
    with pytest.raises(IndexError):
        board.get(-1, 0)
    with pytest.raises(IndexError):
        board.place(0, BOARD_SIZE, Tile("a", 1))


def test_unassigned_blank_cannot_be_placed() -> None:
    with pytest.raises(ValueError):
        Board().place(7, 7, Tile.blank())


def test_assigned_blank_can_be_placed_and_scores_zero() -> None:
    board = Board()
    board.place(7, 7, Tile.blank().as_letter("E"))
    placed = board.get(7, 7)
    assert placed is not None
    assert placed.letter == "e"
    assert placed.points == 0
