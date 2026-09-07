import typing
from dataclasses import dataclass
from enum import IntEnum


class Piece(IntEnum):
	EMPTY = 0
	PAWN = 1
	KNIGHT = 2 
	BISHOP = 3
	ROOK = 4
	QUEEN = 5
	KING = 6

class PieceColour(IntEnum):
	WHITE = 0
	BLACK = 1

class PieceToDisplayName:
	PIECE: typing.ClassVar[dict[Piece, str]] = {
		Piece.EMPTY: "Empty",
		Piece.PAWN: "Pawn",
		Piece.KNIGHT: "Knight",
		Piece.BISHOP: "Bishop",
		Piece.ROOK: "Rook",
		Piece.QUEEN: "Queen",
		Piece.KING: "King",
	}
	COLOUR: typing.ClassVar[dict[PieceColour, str]] = {
		PieceColour.WHITE: "White",
		PieceColour.BLACK: "Black",
	}

class CastlingRights(IntEnum):
	WHITE_KINGSIDE = 0
	WHITE_QUEENSIDE = 1
	BLACK_KINGSIDE = 2
	BLACK_QUEENSIDE = 3

class PieceToFEN:
	WHITE: typing.ClassVar[dict[Piece, str]] = {
		Piece.PAWN: "P",
		Piece.KNIGHT: "N",
		Piece.BISHOP: "B",
		Piece.ROOK: "R",
		Piece.QUEEN: "Q",
		Piece.KING: "K",
	}

	BLACK: typing.ClassVar[dict[Piece, str]] = {
		Piece.PAWN: "p",
		Piece.KNIGHT: "n",
		Piece.BISHOP: "b",
		Piece.ROOK: "r",
		Piece.QUEEN: "q",
		Piece.KING: "k",
	}

class FENToPiece:
	PIECE: typing.ClassVar[dict[str, Piece]] = {
		"P": Piece.PAWN,
		"N": Piece.KNIGHT,
		"B": Piece.BISHOP,
		"R": Piece.ROOK,
		"Q": Piece.QUEEN,
		"K": Piece.KING,
	}
	COLOUR: typing.ClassVar[dict[str, PieceColour]] = {
		"P": PieceColour.WHITE,
		"N": PieceColour.WHITE,
		"B": PieceColour.WHITE,
		"R": PieceColour.WHITE,
		"Q": PieceColour.WHITE,
		"K": PieceColour.WHITE,
		"p": PieceColour.BLACK,
		"n": PieceColour.BLACK,
		"b": PieceColour.BLACK,
		"r": PieceColour.BLACK,
		"q": PieceColour.BLACK,
		"k": PieceColour.BLACK,
	}

class MoveType(IntEnum): # LUT for integer equivalence of possible chess move types
	NORMAL = 0
	CAPTURE = 1
	EN_PASSANT = 2
	CASTLING = 3
	PROMOTION = 4

# move to a simpler system to make UCI moves and board moves analagous
@dataclass(frozen = True, slots = True)
class Move:
	fromSquare: tuple[int, int]
	toSquare: tuple[int, int]
	promotionPiece: Piece | None = None

""" @dataclass(frozen = True)
class MoveData:
	fromSquare: tuple[int, int]
	toSquare: tuple[int, int]
	moveType: MoveType
	promotionPiece: Piece | None = None

@dataclass(frozen = True)
class CheckState:
	inCheck: bool = False
	square: tuple[int, int] = (-1, -1)
	colourInCheck: PieceColour | None = None """