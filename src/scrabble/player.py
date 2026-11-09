"""Speler."""

from __future__ import annotations

from dataclasses import dataclass

from scrabble.rack import Rack


@dataclass
class Player:
    name: str
    rack: Rack
    score: int = 0
