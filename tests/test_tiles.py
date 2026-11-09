import pytest

from scrabble.tiles import BLANK, Tile


def test_blank_is_unassigned_and_zero_points() -> None:
    blank = Tile.blank()
    assert blank.letter == BLANK
    assert blank.points == 0
    assert blank.is_unassigned_blank


def test_blank_assignment_keeps_zero_points() -> None:
    tile = Tile.blank().as_letter("Q")
    assert tile.letter == "q"
    assert tile.points == 0
    assert tile.is_blank
    assert not tile.is_unassigned_blank


def test_normal_tile_cannot_become_other_letter() -> None:
    with pytest.raises(ValueError):
        Tile("a", 1).as_letter("b")
