from pathlib import Path
from enum import IntEnum, Enum

FPS: int = 60
WIDTH: int = 600
HEIGHT: int = 600
BOARD_SIZE: int = 8
PIECE_SET = "alpha"

HEIGHT_PER_SQUARE: int = HEIGHT // BOARD_SIZE
WIDTH_PER_SQUARE: int = WIDTH // BOARD_SIZE

FEN_STARTING_POSITION: str = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
FEN_VALID_PIECE_CHARACTERS: str = "rnbqkpRNBQKP"
FEN_VALID_EMPTY_SQUARE_CHARACTERS: str = "12345678"
FEN_VALID_BOARD_CHARACTERS: str = FEN_VALID_PIECE_CHARACTERS + FEN_VALID_EMPTY_SQUARE_CHARACTERS

ASSETS_DIRECTORY: Path = Path(__file__).parent.parent.parent / "assets"
ASSETS_PIECES_DIRECTORY: Path = ASSETS_DIRECTORY / "pieces"

class Piece(IntEnum): # LUT for integer equivalence for chess pieces
    PAWN = 0
    KNIGHT = 1
    BISHOP = 2
    ROOK = 3
    QUEEN = 4
    KING = 5
    EMPTY = 6 # Default piece type

class MoveType(IntEnum): # LUT for integer equivalence of possible chess move types
    NORMAL = 0
    CAPTURE = 1
    EN_PASSANT = 2
    CASTLING = 3
    PROMOTION = 4

class CastlingRights(IntEnum): # LUT for integer equivalence of side castling rights when parsing FEN strings
    WHITE_KINGSIDE = 0
    WHITE_QUEENSIDE = 1
    BLACK_KINGSIDE = 2
    BLACK_QUEENSIDE = 3

class PieceColour(IntEnum): # LUT for integer equivalence of chess piece colours
    WHITE = 0
    BLACK = 1

class RenderingColours(Enum): # Lichess (lichess.org) default colour scheme
    SQUARE_WHITE = (240, 217, 181)
    SQUARE_BLACK = (181, 136, 99)
    PIECE_PICKED_UP_BACKGROUND = (60, 200, 60, 128)
    PIECE_LEGAL_MOVE_BACKGROUND = (60, 200, 60, 128)