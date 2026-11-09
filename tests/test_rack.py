import random

import pytest

from scrabble.bag import Bag
from scrabble.language import load_language
from scrabble.rack import Rack
from scrabble.tiles import Tile

NL = load_language("nl")


def test_refill_fills_to_seven() -> None:
    bag = Bag(NL, random.Random(3))
    rack = Rack()
    rack.refill(bag)
    assert len(rack) == 7
    assert len(bag) == 95


def test_refill_after_play_tops_up() -> None:
    bag = Bag(NL, random.Random(3))
    rack = Rack()
    rack.refill(bag)
    rack.remove(rack.tiles[0])
    rack.remove(rack.tiles[0])
    rack.refill(bag)
    assert len(rack) == 7


def test_refill_with_nearly_empty_bag() -> None:
    bag = Bag(NL)
    bag.draw(100)
    rack = Rack()
    rack.refill(bag)
    assert len(rack) == 2


def test_too_many_tiles_raises() -> None:
    rack = Rack()
    with pytest.raises(ValueError):
        rack.add([Tile("a", 1)] * 8)


def test_remove_missing_tile_raises() -> None:
    with pytest.raises(ValueError):
        Rack().remove(Tile("a", 1))
