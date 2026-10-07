"""Defines functions for generating legal moves."""

from chessnea.core import types


class PseudoLegalMoves:
	"""Class for methods that revolve around generating pseudo-legal moves for pieces."""

	@staticmethod
	def pawn(position: types.Position, square: types.Square, boardSquare: types.BoardSquare) -> list[types.Move]:
		"""Returns a tuple of pseudo-legal moves for a pawn at the given square."""
		direction: int
		moves: list[types.Move] = []
		colour: types.PieceColour = boardSquare[1]

		# Case 1: 1 square forward
		direction = -1 if colour == types.PieceColour.WHITE else 1
		targetSquare: types.Square = (square[0] + direction, square[1])
		if 0 <= targetSquare[0] < 8 and position.board[targetSquare[0]][targetSquare[1]][0] == types.Piece.EMPTY:
			moves.append(types.Move(fromSquare = square, toSquare = targetSquare))

		# Case 2: 2 squares forward from starting position
		startingRow: int = 6 if colour == types.PieceColour.WHITE else 1
		if square[0] == startingRow:
			targetSquare = (square[0] + 2 * direction, square[1])
			if position.board[targetSquare[0]][targetSquare[1]][0] == types.Piece.EMPTY:
				moves.append(types.Move(fromSquare = square, toSquare = targetSquare))
		return moves

	@staticmethod
	def movesForPiece(position: types.Position, square: types.Square) -> list[types.Move]:
		"""Returns a list of pseudo-legal moves for the piece at the given square."""
		boardSquare: types.BoardSquare = position.board[square[0]][square[1]]
		if boardSquare[0] == types.Piece.EMPTY:
			return []
		if boardSquare[0] == types.Piece.PAWN:
			return PseudoLegalMoves.pawn(position = position, square = square, boardSquare = boardSquare)
		return []

def applyMove(position: types.Position, move: types.Move) -> types.Position:
	"""Applies a move to the given position and returns the new position."""
	# Convert immutable tupleto mutable list
	boardRows: list[list[types.BoardSquare]] = list(map(list, position.board))
	fromRow, fromCol = move.fromSquare
	toRow, toCol = move.toSquare
	pieceFrom, colourFrom = position.board[fromRow][fromCol]

	# Set the from square to empty
	boardRows[fromRow][fromCol] = (types.Piece.EMPTY, types.PieceColour.EMPTY)

	# Set the to square to the piece being moved
	boardRows[toRow][toCol] = (pieceFrom, colourFrom)

	# Convert back to tuple
	newBoard: types.Board = tuple[tuple[types.BoardSquare, ...], ...](map(tuple, boardRows))

	# Reset en passant target square if the move is a pawn double move else set it to None
	enPassantTargettableSquare: types.Square | None = None
	if pieceFrom == types.Piece.PAWN and abs(fromRow - toRow) == 2:
		direction: int = -1 if colourFrom == types.PieceColour.WHITE else 1
		enPassantTargettableSquare = (fromRow + direction, fromCol)

	# Reset the fifty move counter if the move is a pawn move or a capture
	fiftyMoveCounter: int = position.fiftyMoveCounter + 1 if pieceFrom != types.Piece.PAWN and position.board[toRow][toCol][0] == types.Piece.EMPTY else 0
	
	return types.Position(
		board = newBoard,
		sideToMove = types.PieceColour.BLACK if position.sideToMove == types.PieceColour.WHITE else types.PieceColour.WHITE,
		castlingRights = position.castlingRights,
		enPassantTargettableSquare = enPassantTargettableSquare,
		fiftyMoveCounter = fiftyMoveCounter,
		fullMoveCounter = position.fullMoveCounter + (1 if position.sideToMove == types.PieceColour.BLACK else 0),
	)