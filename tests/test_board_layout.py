from helpers import board_tiles, put, transpose

from scrabble.board import BOARD_SIZE, Board, Premium, square_name

# Bovenste helft van het standaardbord (rij 1 t/m 8). De onderste helft is het spiegelbeeld.
# T = driedubbel woord, W = dubbel woord, t = driedubbele letter, d = dubbele letter.
TOP_HALF = [
    "T..d...T...d..T",
    ".W...t...t...W.",
    "..W...d.d...W..",
    "d..W...d...W..d",
    "....W.....W....",
    ".t...t...t...t.",
    "..d...d.d...d..",
    "T..d...W...d..T",
]
SYMBOLS = {
    "T": Premium.TRIPLE_WORD,
    "W": Premium.DOUBLE_WORD,
    "t": Premium.TRIPLE_LETTER,
    "d": Premium.DOUBLE_LETTER,
    ".": Premium.NONE,
}


def test_all_225_squares_match_the_standard_layout() -> None:
    layout = TOP_HALF + TOP_HALF[-2::-1]
    assert len(layout) == BOARD_SIZE
    board = Board()
    for row, line in enumerate(layout):
        assert len(line) == BOARD_SIZE
        for col, symbol in enumerate(line):
            assert board.premium_at(row, col) is SYMBOLS[symbol], square_name(row, col)


def test_square_names() -> None:
    assert square_name(0, 0) == "A1"
    assert square_name(7, 7) == "H8"
    assert square_name(14, 14) == "O15"
    assert square_name(0, 14) == "O1"


def test_transpose_moves_tiles_and_keeps_board_unchanged() -> None:
    board = Board()
    put(board, 7, 4, "huis")
    mirrored = transpose(board)
    assert [(r, c, t.letter) for r, c, t in board_tiles(mirrored)] == [
        (4, 7, "h"),
        (5, 7, "u"),
        (6, 7, "i"),
        (7, 7, "s"),
    ]
    assert len(board_tiles(board)) == 4
