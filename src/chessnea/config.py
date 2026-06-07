from dataclasses import dataclass
from pathlib import Path
from enum import IntEnum, Enum
import typing

VERSION: str = "0.0.1"
FPS: int = 60
WIDTH: int = 1200
HEIGHT: int = 1200
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

@dataclass(frozen = True)
class MoveData:
    fromSquare: tuple[int, int]
    toSquare: tuple[int, int]
    moveType: MoveType
    promotionPiece: Piece | None = None

class CastlingRights(IntEnum): # LUT for integer equivalence of side castling rights when parsing FEN strings
    WHITE_KINGSIDE = 0
    WHITE_QUEENSIDE = 1
    BLACK_KINGSIDE = 2
    BLACK_QUEENSIDE = 3

class PieceColour(IntEnum): # LUT for integer equivalence of chess piece colours
    WHITE = 0
    BLACK = 1

@dataclass(frozen = True)
class PromotionData(MoveData):
    move: MoveData = MoveData(fromSquare = (-1, -1), toSquare = (-1, -1), moveType = MoveType.PROMOTION)
    colour: PieceColour = PieceColour.WHITE

class PromotionalPieces(IntEnum): # LUT for integer equivalence of pieces that a pawn can promote to
    KNIGHT = 1
    BISHOP = 2
    ROOK = 3
    QUEEN = 4

@dataclass
class MoveHighlighting():
    currentMove: tuple[int, int] = (-1, -1)
    previousMove: tuple[int, int] = (-1, -1)

@dataclass
class CheckState():
    inCheck: bool = False
    square: tuple[int, int] = (-1, -1)
    colourInCheck: PieceColour | None = None

class GameOverReason(IntEnum): # LUT for integer equivalence of possible game over reasons
    CHECKMATE = 0
    STALEMATE = 1
    INSUFFICIENT_MATERIAL = 2
    THREEFOLD_REPETITION = 3
    FIFTY_MOVE_RULE = 4

@dataclass
class GameState():
    gameOver: bool = False
    winner: PieceColour | None = None
    reason: GameOverReason | None = None

@dataclass(frozen = True)
class PieceToFen(): # LUT for character equivalence of chess pieces when exporting FEN strings
    WHITE: typing.ClassVar[dict[Piece, str]] = {
        Piece.PAWN: "P",
        Piece.KNIGHT: "N",
        Piece.BISHOP: "B",
        Piece.ROOK: "R",
        Piece.QUEEN: "Q",
        Piece.KING: "K"}
    BLACK: typing.ClassVar[dict[Piece, str]] = {
        Piece.PAWN: "p",
        Piece.KNIGHT: "n",
        Piece.BISHOP: "b",
        Piece.ROOK: "r",
        Piece.QUEEN: "q",
        Piece.KING: "k"}

class RenderingColours(Enum): # Lichess (lichess.org) default colour scheme
    SQUARE_WHITE = (240, 217, 181)
    SQUARE_BLACK = (181, 136, 99)
    PIECE_PICKED_UP_BACKGROUND = (60, 200, 60, 128)
    PIECE_LEGAL_MOVE_BACKGROUND = (60, 200, 60, 128)
    PIECE_PREVIOUS_MOVE_BACKGROUND = (210, 210, 0, 128)
    PROMOTION_CHOICE_BOARD_OVERLAY = (0, 0, 0, 90)
    CHECK_HIGHLIGHT_BACKGROUND = (255, 30, 20, 128)

class RenderingGradientColours(Enum):
    PROMOTION_CHOICE_BACKGROUND_CENTRE = (226, 226, 226, 255)
    PROMOTION_CHOICE_BACKGROUND_EDGE = (170, 170, 170, 255)
    PROMOTION_CHOICE_BACKGROUND_BORDER = (100, 100, 100, 255)
    CHECK_BACKGROUND_CENTRE = (255, 30, 20, 255)
    CHECK_BACKGROUND_EDGE = (120, 45, 35, 40)