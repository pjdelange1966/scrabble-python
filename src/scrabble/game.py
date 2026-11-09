"""Spelstatus: bord, zakje, spelers en beurt. Zetlogica volgt in fase 2."""

from __future__ import annotations

import random
from collections.abc import Sequence

from scrabble.bag import Bag
from scrabble.board import Board
from scrabble.language import Language
from scrabble.player import Player
from scrabble.rack import Rack

MIN_PLAYERS = 2
MAX_PLAYERS = 4


class Game:
    def __init__(
        self,
        language: Language,
        player_names: Sequence[str],
        rng: random.Random | None = None,
    ) -> None:
        if not MIN_PLAYERS <= len(player_names) <= MAX_PLAYERS:
            raise ValueError(f"Een spel heeft {MIN_PLAYERS} tot {MAX_PLAYERS} spelers")
        self.language = language
        self.board = Board()
        self.bag = Bag(language, rng)
        self.players = [Player(name, Rack(language.rack_size)) for name in player_names]
        for player in self.players:
            player.rack.refill(self.bag)
        self.current_index = 0

    @property
    def current_player(self) -> Player:
        return self.players[self.current_index]

    def next_turn(self) -> Player:
        self.current_index = (self.current_index + 1) % len(self.players)
        return self.current_player
