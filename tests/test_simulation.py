"""Willekeurige hele spellen met een eenvoudige testspeler, met controle van de spelregels.

Na elke actie moet gelden:
- er zijn nog precies 102 stenen (zakje + rekken + bord), met de juiste letterverdeling;
- zolang het zakje niet leeg is, heeft elke speler 7 stenen;
- een zet verandert het bord en het rek niet tijdens de controle;
- de score van een zet klopt en is gelijk als je het bord spiegelt (rij <-> kolom).
"""

import random

from helpers import (
    NL,
    board_tiles,
    expected_counts,
    pick_move,
    total_counts,
    transpose,
)

from scrabble.game import Game
from scrabble.move import Placement
from scrabble.rules import validate_move
from scrabble.wordlist import WordList

BOT_WORDS = [
    "ei", "ui", "oe", "ja", "ik", "is", "om", "op", "of", "er", "te", "de", "en", "zo", "nu",
    "na", "al", "ze", "we", "je", "me", "ons", "oog", "oor", "arm", "been", "neus", "mond",
    "huis", "deur", "raam", "tafel", "stoel", "kind", "hond", "kat", "vis", "boom", "tuin",
    "gras", "water", "vuur", "lucht", "aarde", "zon", "maan", "ster", "dag", "nacht", "tijd",
    "werk", "spel", "boek", "pen", "lamp", "bed", "kast", "brood", "kaas", "melk", "thee",
    "bier", "wijn", "appel", "peer",
]  # fmt: skip
WORDS = WordList.from_words(BOT_WORDS)
MAX_ACTIONS = 120


def check_invariants(game: Game) -> None:
    assert total_counts(game) == expected_counts()
    for player in game.players:
        assert len(player.rack) <= NL.rack_size
        assert all(not t.is_blank or t.is_unassigned_blank for t in player.rack.tiles)
    if not game.bag.is_empty():
        assert all(len(p.rack) == NL.rack_size for p in game.players)
    assert all(not t.is_blank or t.is_unassigned_blank for t in game.bag.contents())
    assert all(not t.is_unassigned_blank for _, _, t in board_tiles(game.board))


def simulate(seed: int) -> int:
    """Speel één spel; geeft het aantal gelegde woorden terug."""
    rng = random.Random(seed)
    names = ["Anna", "Bram", "Cor", "Dirk"][: 2 + seed % 3]
    game = Game(NL, names, random.Random(seed), wordlist=WORDS)
    check_invariants(game)
    sum_of_moves = 0
    plays = 0

    for _ in range(MAX_ACTIONS):
        if game.is_over:
            break
        player = game.current_player
        placements = pick_move(game, BOT_WORDS, rng)
        if placements is not None:
            board_before = board_tiles(game.board)
            rack_before = player.rack.letters()
            scored = validate_move(game.board, player.rack, placements, WORDS, NL)

            mirrored = validate_move(
                transpose(game.board),
                player.rack,
                [Placement(p.col, p.row, p.tile) for p in placements],
                WORDS,
                NL,
            )
            assert mirrored.total == scored.total
            assert sorted(w.score for w in mirrored.words) == sorted(w.score for w in scored.words)
            assert board_tiles(game.board) == board_before
            assert player.rack.letters() == rack_before

            score_before = player.score
            assert game.play(placements) == scored
            sum_of_moves += scored.total
            plays += 1
            if not game.is_over:
                assert player.score == score_before + scored.total
        elif len(game.bag) >= NL.rack_size and rng.random() < 0.5:
            game.exchange(list(player.rack.tiles[: rng.randint(1, 2)]))
        else:
            game.pass_turn()
        check_invariants(game)

    if game.is_over:
        left = sum(t.points for p in game.players for t in p.rack.tiles)
        went_out = any(len(p.rack) == 0 for p in game.players)
        expected = sum_of_moves if went_out else sum_of_moves - left
        assert sum(p.score for p in game.players) == expected
    return plays


def test_random_games_keep_all_invariants() -> None:
    plays = [simulate(seed) for seed in range(6)]
    assert sum(plays) > 10, plays  # de testspeler moet echt woorden leggen
