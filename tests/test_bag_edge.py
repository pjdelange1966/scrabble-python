import random

import pytest
from helpers import NL, expected_counts, letter_counts

from scrabble.bag import Bag


def test_contents_match_the_language_distribution() -> None:
    bag = Bag(NL, random.Random(1))
    assert len(bag.contents()) == 102
    assert letter_counts(bag.contents()) == expected_counts()


def test_draw_zero_and_negative() -> None:
    bag = Bag(NL)
    assert bag.draw(0) == []
    assert len(bag) == 102
    with pytest.raises(ValueError):
        bag.draw(-1)


def test_draw_from_empty_bag_and_put_back_nothing() -> None:
    bag = Bag(NL)
    bag.draw(102)
    assert bag.draw(5) == []
    bag.put_back([])
    assert bag.is_empty()


def test_drawn_and_remaining_tiles_add_up() -> None:
    bag = Bag(NL, random.Random(7))
    drawn = bag.draw(30)
    assert letter_counts(drawn) + letter_counts(bag.contents()) == expected_counts()
