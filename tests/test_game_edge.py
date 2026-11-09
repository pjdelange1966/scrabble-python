import random

import pytest
from helpers import NL, letter_counts, set_rack, tile, word_placements

from scrabble.game import Game, GameOverError
from scrabble.move import InvalidMoveError, Placement
from scrabble.tiles import Tile
from scrabble.wordlist import WordList

WL = WordList.from_words(["huis", "ui", "oe"])


def new_game(players: int = 2, **kwargs: int) -> Game:
    names = ["Anna", "Bram", "Cor", "Dirk"][:players]
    return Game(NL, names, random.Random(0), wordlist=WL, **kwargs)


def huis() -> list[Placement]:
    return word_placements(7, 4, "huis")


def test_going_out_with_three_players_collects_from_both_others() -> None:
    game = new_game(3)
    game.bag.draw(len(game.bag))
    set_rack(game, 0, "huis")
    set_rack(game, 1, "qz")  # 10 + 4
    set_rack(game, 2, "x")  # 8
    game.play(huis())
    assert game.is_over
    assert [p.score for p in game.players] == [22 + 22, -14, -8]
    assert [p.name for p in game.winners] == ["Anna"]


def test_tie_gives_multiple_winners() -> None:
    game = new_game()
    set_rack(game, 0, "a")
    set_rack(game, 1, "e")
    for _ in range(6):
        game.pass_turn()
    assert game.is_over
    assert [p.score for p in game.players] == [-1, -1]
    assert [p.name for p in game.winners] == ["Anna", "Bram"]


def test_custom_scoreless_limit() -> None:
    game = new_game(scoreless_limit=2)
    game.pass_turn()
    assert not game.is_over
    game.pass_turn()
    assert game.is_over


def test_exchanging_a_blank_returns_it_unassigned() -> None:
    game = new_game()
    set_rack(game, 0, "?aaaaaa")
    game.exchange([Tile.blank()])
    assert len(game.bag) == 88
    assert len(game.players[0].rack) == 7
    assert all(not t.is_blank or t.is_unassigned_blank for t in game.bag.contents())


def test_partial_refill_when_bag_is_nearly_empty() -> None:
    game = new_game()
    game.bag.draw(len(game.bag) - 2)
    set_rack(game, 0, "huiseee")
    game.play(huis())
    assert len(game.players[0].rack) == 5  # 3 over + 2 getrokken
    assert game.bag.is_empty()
    assert not game.is_over
    assert game.current_player.name == "Bram"


def test_invalid_play_changes_nothing_at_all() -> None:
    game = new_game()
    set_rack(game, 0, "aaaaaaa")
    bag_before = len(game.bag)
    with pytest.raises(InvalidMoveError):
        game.play(huis())
    assert len(game.bag) == bag_before
    assert game.players[0].rack.letters() == "aaaaaaa"
    assert game.current_player.name == "Anna"
    assert game.scoreless_turns == 0
    assert game.board.is_empty()


def test_playing_a_blank_removes_it_from_the_rack_and_scores_zero_for_it() -> None:
    game = new_game()
    set_rack(game, 0, "h?isaaa")
    placements = huis()
    placements[1] = Placement(7, 5, Tile.blank().as_letter("u"))
    scored = game.play(placements)
    assert scored.total == 14  # (4+0+1+2) x 2
    assert "?" not in game.players[0].rack.letters()


def test_every_action_is_refused_after_the_game_is_over() -> None:
    game = new_game(scoreless_limit=1)
    game.pass_turn()
    assert game.is_over
    with pytest.raises(GameOverError):
        game.pass_turn()
    with pytest.raises(GameOverError):
        game.exchange([tile("a")])
    with pytest.raises(GameOverError):
        game.play(huis())


def test_turn_order_with_four_players() -> None:
    game = new_game(4)
    names = []
    for _ in range(5):
        names.append(game.current_player.name)
        game.pass_turn()
    assert names == ["Anna", "Bram", "Cor", "Dirk", "Anna"]


def test_first_move_that_misses_the_center_is_rejected_and_keeps_turn() -> None:
    game = new_game()
    set_rack(game, 0, "huiseee")
    with pytest.raises(InvalidMoveError, match="middenster"):
        game.play(word_placements(2, 2, "huis"))
    assert game.current_player.name == "Anna"


def test_exchange_draws_before_returning_your_own_tiles() -> None:
    game = new_game()
    game.bag.draw(len(game.bag) - NL.rack_size)  # precies het minimum om te mogen ruilen
    in_bag = letter_counts(game.bag.contents())
    set_rack(game, 0, "aaaaaaa")
    game.exchange(list(game.players[0].rack.tiles))
    # alle 7 nieuwe stenen komen uit het zakje van daarvoor, niet uit je eigen teruggestopte stenen
    assert letter_counts(game.players[0].rack.tiles) == in_bag
    assert len(game.bag) == NL.rack_size
