import random

import pytest

from scrabble.game import Game
from scrabble.language import load_language

NL = load_language("nl")


def test_new_game_deals_seven_tiles_each() -> None:
    game = Game(NL, ["Anna", "Bram"], random.Random(5))
    assert all(len(p.rack) == 7 for p in game.players)
    assert len(game.bag) == 102 - 14
    assert game.board.is_empty()
    assert all(p.score == 0 for p in game.players)


def test_player_count_limits() -> None:
    with pytest.raises(ValueError):
        Game(NL, ["Alleen"])
    with pytest.raises(ValueError):
        Game(NL, ["a", "b", "c", "d", "e"])


def test_turns_cycle_through_players() -> None:
    game = Game(NL, ["Anna", "Bram", "Cor"])
    assert game.current_player.name == "Anna"
    assert game.next_turn().name == "Bram"
    assert game.next_turn().name == "Cor"
    assert game.next_turn().name == "Anna"
