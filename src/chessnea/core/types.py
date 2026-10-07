"""Defines types used throughout the project."""

import typing
from dataclasses import dataclass
from enum import IntEnum

import pygame

Square: typing.TypeAlias = tuple[int, int] 
"""Represents a square on the chessboard as (row, col) with (0, 0) at a8 and (7, 7) at h1."""

class Piece(IntEnum):
	"""Represents the type of a chess piece."""
	EMPTY = -1
	PAWN = 0
	KNIGHT = 1
	BISHOP = 2
	ROOK = 3
	QUEEN = 4
	KING = 5

class PieceColour(IntEnum):
	"""Represents the colour of a chess piece."""
	EMPTY = -1
	WHITE = 0
	BLACK = 1


BoardSquare: typing.TypeAlias = tuple[Piece, PieceColour]
"""Represents a square on the chessboard as a (piece, colour) tuple."""

Board: typing.TypeAlias = tuple[tuple[BoardSquare, ...], ...]
"""Represents the entire chessboard as a 2-dimensional array of BoardSquares."""

class PieceToDisplayName:
	"""Converts a types.Piece type to a human-readable string.

	Examples:
		PieceToDisplayName.PIECE[Piece.PAWN] -> "Pawn"
		PieceToDisplayName.COLOUR[PieceColour.WHITE] -> "White"
	"""
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
	"""Represents the castling rights for both players."""
	WHITE_KINGSIDE = 0
	WHITE_QUEENSIDE = 1
	BLACK_KINGSIDE = 2
	BLACK_QUEENSIDE = 3

@dataclass(frozen = True, slots = True)
class Position:
	"""A snapshot of the board state.

	Attributes:
		board (tuple[tuple[BoardSquare, ...], ...]): Rows of (piece, colour) cells.
		sideToMove (PieceColour): The player whose turn it is.
		castlingRights (frozenset[CastlingRights]): Remaining castling rights.
		enPassantTargettableSquare (Square | None): En passant target.
		fiftyMoveCounter (int): Half-moves since the last pawn move or capture.
		fullMoveCounter (int): Full-move number.
	"""

	board: Board
	sideToMove: PieceColour
	castlingRights: frozenset[CastlingRights]  # Corresponds to types.CastlingRights LUT
	enPassantTargettableSquare: Square | None
	fiftyMoveCounter: int
	fullMoveCounter: int

class PieceToFEN:
	"""Converts a types.Piece type to a FEN compatible string.

	Examples:
		PieceToFEN.WHITE[Piece.PAWN] -> 'P'
		PieceToFEN.BLACK[Piece.PAWN] -> 'p'
	"""
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
	"""Converts a FEN compatible string to a types.Piece type.

	Examples:
		FENToPiece.PIECE['P'] -> returns types.Piece.
		FENToPiece.COLOUR['p'] -> returns types.PieceColour.
	"""
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

# move to a simpler system to make UCI moves and board moves analagous
@dataclass(frozen = True, slots = True)
class Move:
	"""Represents a move in the game.
	
	Attributes:
		fromSquare: The starting square of the move.
		toSquare: The ending square of the move.
		promotionPiece: The piece to promote to.
	"""
	fromSquare: Square
	toSquare: Square
	promotionPiece: Piece | None = None

class SelectionState(IntEnum):
	NONE = 0
	DRAGGING = 1
	SELECTED = 2

@dataclass(frozen = True, slots = True)
class StationaryBoardCache:
	"""Cache for the stationary board: background, static pieces minus selected piece if present.

	Rebuilt when static pieces change on the board.

	Attributes:
		surface: Surface for the entire board.
		selectedSquare: Selection square, or None.
		boardState: Board state used for the current cached board.
	"""

	surface: pygame.Surface
	selectedSquare: Square | None
	boardState: Board

@dataclass(frozen = True, slots = True)
class HighlightedBoardCache:
	"""Cache for the entire board: copy of stationaryBoardCache + selection square/move highlighting.

	Rebuilt when selection highlighting changes (piece selected/deselected)
	or stationaryBoardCache is rebuilt.

	Attributes:
		surface: Surface for the entire board.
		selectedSquare: Selection square, or None.
		possibleMoves: Possible moves used for move highlighting.
	"""
	surface: pygame.Surface
	selectedSquare: Square | None
	possibleMoves: tuple[Move, ...]

class CacheLevel(IntEnum):
	"""Represents the level of board cache."""
	STATIONARY = 0
	HIGHLIGHTED = 1