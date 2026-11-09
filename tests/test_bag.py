import random

from scrabble.bag import Bag
from scrabble.language import load_language
from scrabble.tiles import Tile

NL = load_language("nl")


def test_full_bag_has_102_tiles() -> None:
    assert len(Bag(NL)) == 102


def test_draw_reduces_bag() -> None:
    bag = Bag(NL)
    drawn = bag.draw(7)
    assert len(drawn) == 7
    assert len(bag) == 95


def test_draw_more_than_available_returns_rest() -> None:
    bag = Bag(NL)
    bag.draw(100)
    assert len(bag.draw(10)) == 2
    assert bag.is_empty()


def test_same_seed_gives_same_order() -> None:
    a = Bag(NL, random.Random(42)).draw(20)
    b = Bag(NL, random.Random(42)).draw(20)
    assert a == b


def test_put_back_restores_count_and_resets_blank() -> None:
    bag = Bag(NL, random.Random(1))
    tiles = bag.draw(102)
    assert len(bag) == 0
    tiles = [t.as_letter("a") if t.is_blank else t for t in tiles]
    bag.put_back(tiles)
    assert len(bag) == 102
    assert all(t.is_unassigned_blank for t in bag.draw(102) if t.is_blank)


def test_bag_contains_two_blanks() -> None:
    tiles = Bag(NL).draw(102)
    assert sum(1 for t in tiles if t == Tile.blank()) == 2
