from dataclasses import dataclass
import pygame
from pathlib import Path
import sys
from enum import IntEnum, Enum
import typing
import logging

logger: logging.Logger = logging.getLogger(__name__)

VERSION: str = "0.0.1"
FPS: int = 60
WIDTH: int = 900
HEIGHT: int = 900
BOARD_SIZE: int = 8
PIECE_SET = "alpha"

HEIGHT_PER_SQUARE: int = HEIGHT // BOARD_SIZE
WIDTH_PER_SQUARE: int = WIDTH // BOARD_SIZE

FEN_STARTING_POSITION: str = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
FEN_VALID_PIECE_CHARACTERS: str = "rnbqkpRNBQKP"
FEN_VALID_EMPTY_SQUARE_CHARACTERS: str = "12345678"
FEN_VALID_BOARD_CHARACTERS: str = FEN_VALID_PIECE_CHARACTERS + FEN_VALID_EMPTY_SQUARE_CHARACTERS

def getRelativePathToAssets(assetsDir: str) -> Path:
    basePath = getattr(sys, "_MEIPASS", None)
    if basePath is not None:
        return Path(basePath) / assetsDir
    return Path(__file__).parent.parent.parent / assetsDir

ASSETS_DIRECTORY: Path = getRelativePathToAssets(assetsDir = "assets")
ASSETS_PIECES_DIRECTORY: Path = getRelativePathToAssets(assetsDir = "assets/pieces")
FONT_FAMILY: str = "Roboto"    
FONT_DIRECTORY: Path = getRelativePathToAssets(assetsDir = f"assets/fonts/{FONT_FAMILY}")

def getFontPath(fontName: str, dir: Path) -> Path:
    for file in dir.iterdir():
        if file.is_file() and file.name == fontName:
            return file
    logging.error(msg = f"Init: Font file not found: {fontName} in directory {dir}")
    raise FileNotFoundError(f"Font file not found: {fontName}")

FONT_REGULAR: Path = getFontPath(fontName = f"{FONT_FAMILY}-Regular.ttf", dir = FONT_DIRECTORY)
FONT_MEDIUM: Path = getFontPath(fontName = f"{FONT_FAMILY}-Medium.ttf", dir = FONT_DIRECTORY)

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


# UI colours from Material Design: https://mui.com/material-ui/customization/dark-mode/ (Accessed 10/06/2026)
# (https://raw.githubusercontent.com/mui/material-ui/master/packages/mui-material/src/styles/createPalette.js)
# class UIColours(Enum):
#     PRIMARY = (0, 121, 107, 255)           # teal 700 #00796b
#     PRIMARY_HOVER = (0, 105, 92, 255)      # teal 800 #00695c
#     PRIMARY_LIGHT = (77, 182, 172, 255)    # teal 300 #4db6ac

#     BACKGROUND = (250, 250, 250, 255)      # grey 50 #fafafa
#     SURFACE = (255, 255, 255, 255)         # white
#     OUTLINE = (224, 224, 224, 255)         # grey 300 #e0e0e0

#     TEXT_PRIMARY = (33, 33, 33, 255)       # grey 900 #212121
#     TEXT_SECONDARY = (97, 97, 97, 255)     # grey 700 #616161
#     TEXT_ON_PRIMARY = (255, 255, 255, 255)

#     SHADOW = (0, 0, 0, 35)

#     ERROR = (211, 47, 47, 255)             # red 700 #d32f2f
#     WARNING = (251, 192, 45, 255)          # yellow 700 #fbc02d
#     SUCCESS = (56, 142, 60, 255)           # green 700 #388e3c

class UIColours(Enum):
    PRIMARY = (144, 202, 249, 255)          # blue 200 #90caf9
    PRIMARY_HOVER = (66, 165, 245, 255)     # blue 400 #42a5f5
    PRIMARY_LIGHT = (227, 242, 253, 255)    # blue 50 #e3f2fd

    BACKGROUND = (18, 18, 18, 255)          # #121212
    SURFACE = (18, 18, 18, 255)             # #121212
    OUTLINE = (180, 180, 180, 255)           # rgba(255, 255, 255, 0.12) changed

    TEXT_PRIMARY = (255, 255, 255, 255)     # #FFFFFF
    TEXT_SECONDARY = (255, 255, 255, 179)   # rgba(255, 255, 255, 0.7)
    TEXT_DISABLED = (255, 255, 255, 128)    # rgba(255, 255, 255, 0.5)
    TEXT_ON_PRIMARY = (0, 0, 0, 222)        # rgba(0, 0, 0, 0.87)

    ACTION_ACTIVE = (255, 255, 255, 255)    # #FFFFFF
    ACTION_HOVER = (37, 37, 37, 255)      # rgba(255, 255, 255, 0.08) changed
    ACTION_SELECTED = (56, 56, 56, 255)   # rgba(255, 255, 255, 0.16) changed

    SHADOW = (0, 0, 0, 80)

    ERROR = (244, 67, 54, 255)              # red 500 #f44336
    WARNING = (255, 167, 38, 255)           # orange 400 #ffa726
    SUCCESS = (102, 187, 106, 255)          # green 400 #66bb6a

class ItemType(IntEnum):
    BUTTON = 1
    DROPDOWN = 2
    TOGGLE = 3

@dataclass
class MenuItem():
    name: str
    itemType: ItemType
    connector: typing.Callable[[], bool]
    children: list["MenuItem"] | None
    rect: pygame.Rect | None = None
    pressed: bool = False
    paddedRight: bool = False