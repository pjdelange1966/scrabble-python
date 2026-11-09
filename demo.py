"""Demo voor fase 1: start een spel en toon de rekken.

Uitvoeren vanuit de projectmap (met geactiveerde omgeving):
    python demo.py
"""

from scrabble.board import CENTER
from scrabble.game import Game
from scrabble.language import load_language


def main() -> None:
    language = load_language("nl")
    game = Game(language, ["Anna", "Bram"])

    print(f"Taal: {language.name} ({language.total_tiles} stenen)")
    print()

    for player in game.players:
        letters = " ".join(t.letter.upper() for t in player.rack.tiles)
        points = sum(t.points for t in player.rack.tiles)
        print(f"{player.name}: {letters}   (waarde: {points} punten)")

    print()
    print(f"Stenen in het zakje: {len(game.bag)}")
    print(f"Middenster: rij {CENTER[0]}, kolom {CENTER[1]} ({game.board.premium_at(*CENTER).name})")
    print(f"Aan de beurt: {game.current_player.name}")
    print()
    print("(? = blanco)")


if __name__ == "__main__":
    main()
