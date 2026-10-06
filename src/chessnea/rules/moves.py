"""Defines functions for generating legal moves."""
from chessnea.core import types


class PseudoLegalMoves:
	"""Class for methods that revolve around generating pseudo-legal moves for pieces."""

	@staticmethod
	def Pawn(position: types.Position, square: types.Square, boardSquare: types.BoardSquare) -> tuple[types.Move, ...]:
		"""Returns a tuple of pseudo-legal moves for a pawn at the given square."""
		# Case 1: 1 square forward
		if boardSquare[1] == types.PieceColour.WHITE:
			distance: int = -1

	@staticmethod
	def MovesForPiece(position: types.Position, square: types.Square) -> tuple[types.Move, ...]:
		"""Returns a tuple of pseudo-legal moves for the piece at the given square."""
		boardSquare: types.BoardSquare = position.board[square[0]][square[1]]
		if boardSquare[0] == types.Piece.EMPTY:
			return ()
		if boardSquare[0] == types.Piece.PAWN:
			return PseudoLegalMoves.Pawn(position = position, square = square, boardSquare = boardSquare)