"""Defines functions for generating legal moves."""

from chessnea.core import types


class PseudoLegalMoves:
	"""Class for methods that revolve around generating pseudo-legal moves for pieces."""

	@staticmethod
	def __checkBounds(num: int) -> bool:
		return not (num < 0 or num > 7)

	@staticmethod
	def pawn(position: types.Position, square: types.Square, boardSquare: types.BoardSquare) -> list[types.Move]:
		"""Returns a tuple of pseudo-legal moves for a pawn at the given square."""
		direction: int
		moves: list[types.Move] = []
		colour: types.PieceColour = boardSquare[1]

		# Case 1: 1 square forward
		direction = -1 if colour == types.PieceColour.WHITE else 1
		targetSquare: types.Square = (square[0] + direction, square[1])
		if PseudoLegalMoves.__checkBounds(num = targetSquare[0]) and position.board[targetSquare[0]][targetSquare[1]][0] == types.Piece.EMPTY:
			moves.append(types.Move(fromSquare = square, toSquare = targetSquare))

		# Case 2: 2 squares forward from starting position
		startingRow: int = 6 if colour == types.PieceColour.WHITE else 1
		if square[0] == startingRow:
			targetSquare = (square[0] + 2 * direction, square[1])
			if position.board[targetSquare[0]][targetSquare[1]][0] == types.Piece.EMPTY and \
				position.board[square[0] + direction][square[1]][0] == types.Piece.EMPTY:
				moves.append(types.Move(fromSquare = square, toSquare = targetSquare))

		# Case 3: Captures
		# White Pawn - 1 up the board, diagonal left and right
		if colour == types.PieceColour.WHITE and PseudoLegalMoves.__checkBounds(num = square[0] - 1):
			if (PseudoLegalMoves.__checkBounds(num = square[1] - 1)) and \
				(position.board[square[0] - 1][square[1] - 1][0] != types.Piece.EMPTY) and \
				(position.board[square[0] - 1][square[1] - 1][1] != colour):
					moves.append(types.Move(fromSquare = square, toSquare = types.Square((square[0] - 1, square[1] - 1))))
			if (PseudoLegalMoves.__checkBounds(num = square[1] + 1)) and \
				(position.board[square[0] - 1][square[1] + 1][0] != types.Piece.EMPTY) and \
				(position.board[square[0] - 1][square[1] + 1][1] != colour):
					moves.append(types.Move(fromSquare = square, toSquare = types.Square((square[0] - 1, square[1] + 1))))
		# Black Pawn - 1 down the board, diagonal left and right
		if colour == types.PieceColour.BLACK and PseudoLegalMoves.__checkBounds(num = square[0] + 1):
			if (PseudoLegalMoves.__checkBounds(num = square[1] - 1)) and \
				(position.board[square[0] + 1][square[1] - 1][0] != types.Piece.EMPTY) and \
				(position.board[square[0] + 1][square[1] - 1][1] != colour):
					moves.append(types.Move(fromSquare = square, toSquare = types.Square((square[0] + 1, square[1] - 1))))
			if (PseudoLegalMoves.__checkBounds(num = square[1] + 1)) and \
				(position.board[square[0] + 1][square[1] + 1][0] != types.Piece.EMPTY) and \
				(position.board[square[0] + 1][square[1] + 1][1] != colour):
					moves.append(types.Move(fromSquare = square, toSquare = types.Square((square[0] + 1, square[1] + 1))))

		# Case 4: En passant
		if position.enPassantTargettableSquare and \
			square[0] + direction == position.enPassantTargettableSquare[0]:
			if square[1] + 1 == position.enPassantTargettableSquare[1]:
				moves.append(types.Move(fromSquare = square, toSquare = types.Square((square[0] + direction, square[1] + 1))))
			elif square[1] - 1 == position.enPassantTargettableSquare[1]:
				moves.append(types.Move(fromSquare = square, toSquare = types.Square((square[0] + direction, square[1] - 1))))
		return moves

	@staticmethod
	def bishop(position: types.Position, square: types.Square, boardSquare: types.BoardSquare) -> list[types.Move]:
		"""Returns a tuple of pseudo-legal moves for a bishop at the given square."""
		diagonals: list[tuple[int, int]] = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
		moves: list[types.Move] = []
		colour: types.PieceColour = boardSquare[1]
		for diagonal in diagonals:
			row, col = diagonal
			newRow, newCol = square
			while (PseudoLegalMoves.__checkBounds(num = newRow + row)) and (PseudoLegalMoves.__checkBounds(num = newCol + col)):
				newRow += row
				newCol += col
				if position.board[newRow][newCol][1] == colour:
					break
				if position.board[newRow][newCol][0] != types.Piece.EMPTY:
					moves.append(types.Move(fromSquare = square, toSquare = types.Square((newRow, newCol))))
					break
				moves.append(types.Move(fromSquare = square, toSquare = types.Square((newRow, newCol))))
		return moves

	@staticmethod
	def rook(position: types.Position, square: types.Square, boardSquare: types.BoardSquare) -> list[types.Move]:
		"""Returns a tuple of pseudo-legal moves for a rook at the given square."""
		moves: list[types.Move] = []
		colour: types.PieceColour = boardSquare[1]
		directions: list[tuple[int, int]] = [(-1, 0), (1, 0), (0, -1), (0, 1)]
		for direction in directions:
			row, col = direction
			newRow, newCol = square
			while (PseudoLegalMoves.__checkBounds(num = newRow + row)) and (PseudoLegalMoves.__checkBounds(num = newCol + col)):
				newRow += row
				newCol += col
				if position.board[newRow][newCol][1] == colour:
					break
				if position.board[newRow][newCol][0] != types.Piece.EMPTY:
					moves.append(types.Move(fromSquare = square, toSquare = types.Square((newRow, newCol))))
					break
				moves.append(types.Move(fromSquare = square, toSquare = types.Square((newRow, newCol))))
		return moves

	@staticmethod
	def knight(position: types.Position, square: types.Square, boardSquare: types.BoardSquare) -> list[types.Move]:
		"""Returns a tuple of pseudo-legal moves for a knight at the given square."""
		moves: list[types.Move] = []
		colour: types.PieceColour = boardSquare[1]
		knightMoves: list[tuple[int, int]] = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]
		for knightMove in knightMoves:
			row, col = knightMove
			newRow: int = square[0] + row
			newCol: int = square[1] + col
			if (PseudoLegalMoves.__checkBounds(num = newRow) and PseudoLegalMoves.__checkBounds(num = newCol)) and position.board[newRow][newCol][1] != colour:
					moves.append(types.Move(fromSquare = square, toSquare = types.Square((newRow, newCol))))
		return moves

	@staticmethod
	def queen(position: types.Position, square: types.Square, boardSquare: types.BoardSquare) -> list[types.Move]:
		"""Returns a tuple of pseudo-legal moves for a queen at the given square."""
		return PseudoLegalMoves.bishop(position = position, square = square, boardSquare = boardSquare) + \
			PseudoLegalMoves.rook(position = position, square = square, boardSquare = boardSquare)
   
	@staticmethod
	def king(position: types.Position, square: types.Square, boardSquare: types.BoardSquare) -> list[types.Move]:
		"""Returns a tuple of pseudo-legal moves for a king at the given square."""
		moves: list[types.Move] = []
		colour: types.PieceColour = boardSquare[1]
		kingMoves: list[tuple[int, int]] = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
		for kingMove in kingMoves:
			row, col = kingMove
			newRow: int = square[0] + row
			newCol: int = square[1] + col
			if (PseudoLegalMoves.__checkBounds(num = newRow) and PseudoLegalMoves.__checkBounds(num = newCol)) and position.board[newRow][newCol][1] != colour:
					moves.append(types.Move(fromSquare = square, toSquare = types.Square((newRow, newCol))))
		return moves

	@staticmethod
	def movesForPiece(position: types.Position, square: types.Square) -> list[types.Move]:
		"""Returns a list of pseudo-legal moves for the piece at the given square."""
		boardSquare: types.BoardSquare = position.board[square[0]][square[1]]
		if boardSquare[0] == types.Piece.EMPTY:
			return []
		if boardSquare[0] == types.Piece.PAWN:
			return PseudoLegalMoves.pawn(position = position, square = square, boardSquare = boardSquare)
		if boardSquare[0] == types.Piece.BISHOP:
			return PseudoLegalMoves.bishop(position = position, square = square, boardSquare = boardSquare)
		if boardSquare[0] == types.Piece.ROOK:
			return PseudoLegalMoves.rook(position = position, square = square, boardSquare = boardSquare)
		if boardSquare[0] == types.Piece.KNIGHT:
			return PseudoLegalMoves.knight(position = position, square = square, boardSquare = boardSquare)
		if boardSquare[0] == types.Piece.QUEEN:
			return PseudoLegalMoves.queen(position = position, square = square, boardSquare = boardSquare)
		if boardSquare[0] == types.Piece.KING:
			return PseudoLegalMoves.king(position = position, square = square, boardSquare = boardSquare)
		return []

def handleMoveSquareChanges(position: types.Position, boardRows: types.BoardRows, move: types.Move) -> tuple[frozenset[types.CastlingRights], types.BoardRows]:
	fromRow, fromCol = move.fromSquare
	toRow, toCol = move.toSquare
	pieceFrom, colourFrom = position.board[fromRow][fromCol]

	# Promotion
	if pieceFrom == types.Piece.PAWN and move.promotionPiece is not None and (toRow == 0 or toRow == 7):
		boardRows[toRow][toCol] = (move.promotionPiece, colourFrom)
		boardRows[fromRow][fromCol] = (types.Piece.EMPTY, types.PieceColour.EMPTY)
		return position.castlingRights, boardRows
  
	# Castling - White Kingside
	if (types.CastlingRights.WHITE_KINGSIDE in position.castlingRights) and \
		(pieceFrom == types.Piece.KING and colourFrom == types.PieceColour.WHITE and move.fromSquare == (7, 4) and move.toSquare == (7, 6)):
			boardRows[7][4] = (types.Piece.EMPTY, types.PieceColour.EMPTY)
			boardRows[7][6] = (types.Piece.KING, types.PieceColour.WHITE)
			boardRows[7][7] = (types.Piece.EMPTY, types.PieceColour.EMPTY)
			boardRows[7][5] = (types.Piece.ROOK, types.PieceColour.WHITE)
			return position.castlingRights - {types.CastlingRights.WHITE_KINGSIDE, types.CastlingRights.WHITE_QUEENSIDE}, boardRows
	
	# Castling - White Queenside
	if (types.CastlingRights.WHITE_QUEENSIDE in position.castlingRights) and \
		(pieceFrom == types.Piece.KING and colourFrom == types.PieceColour.WHITE and move.fromSquare == (7, 4) and move.toSquare == (7, 2)):
			boardRows[7][4] = (types.Piece.EMPTY, types.PieceColour.EMPTY)
			boardRows[7][2] = (types.Piece.KING, types.PieceColour.WHITE)
			boardRows[7][0] = (types.Piece.EMPTY, types.PieceColour.EMPTY)
			boardRows[7][3] = (types.Piece.ROOK, types.PieceColour.WHITE)
			return position.castlingRights - {types.CastlingRights.WHITE_KINGSIDE, types.CastlingRights.WHITE_QUEENSIDE}, boardRows

	# Castling - Black Kingside
	if (types.CastlingRights.BLACK_KINGSIDE in position.castlingRights) and \
		(pieceFrom == types.Piece.KING and colourFrom == types.PieceColour.BLACK and move.fromSquare == (0, 4) and move.toSquare == (0, 6)):
			boardRows[0][4] = (types.Piece.EMPTY, types.PieceColour.EMPTY)
			boardRows[0][6] = (types.Piece.KING, types.PieceColour.BLACK)
			boardRows[0][7] = (types.Piece.EMPTY, types.PieceColour.EMPTY)
			boardRows[0][5] = (types.Piece.ROOK, types.PieceColour.BLACK)
			return position.castlingRights - {types.CastlingRights.BLACK_KINGSIDE, types.CastlingRights.BLACK_QUEENSIDE}, boardRows

	# Castling - Black Queenside
	if (types.CastlingRights.BLACK_QUEENSIDE in position.castlingRights) and \
		(pieceFrom == types.Piece.KING and colourFrom == types.PieceColour.BLACK and move.fromSquare == (0, 4) and move.toSquare == (0, 2)):
			boardRows[0][4] = (types.Piece.EMPTY, types.PieceColour.EMPTY)
			boardRows[0][2] = (types.Piece.KING, types.PieceColour.BLACK)
			boardRows[0][0] = (types.Piece.EMPTY, types.PieceColour.EMPTY)
			boardRows[0][3] = (types.Piece.ROOK, types.PieceColour.BLACK)
			return position.castlingRights - {types.CastlingRights.BLACK_KINGSIDE, types.CastlingRights.BLACK_QUEENSIDE}, boardRows
	
	# En passant
	if pieceFrom == types.Piece.PAWN and position.enPassantTargettableSquare is not None and move.toSquare == position.enPassantTargettableSquare:
		boardRows[toRow][toCol] = (pieceFrom, colourFrom)
		boardRows[fromRow][fromCol] = (types.Piece.EMPTY, types.PieceColour.EMPTY)
		direction: int = -1 if colourFrom == types.PieceColour.WHITE else 1
		capturedPawnRow: int = toRow - direction
		boardRows[capturedPawnRow][toCol] = (types.Piece.EMPTY, types.PieceColour.EMPTY)
		return position.castlingRights, boardRows

	# Standard capture or move
	boardRows[toRow][toCol] = (pieceFrom, colourFrom)
	boardRows[fromRow][fromCol] = (types.Piece.EMPTY, types.PieceColour.EMPTY)
	
	# Handle changes to castling rights
	if pieceFrom == types.Piece.KING:
		if colourFrom == types.PieceColour.WHITE:
			return position.castlingRights - {types.CastlingRights.WHITE_KINGSIDE, types.CastlingRights.WHITE_QUEENSIDE}, boardRows
		else:
			return position.castlingRights - {types.CastlingRights.BLACK_KINGSIDE, types.CastlingRights.BLACK_QUEENSIDE}, boardRows
	elif pieceFrom == types.Piece.ROOK:
		if colourFrom == types.PieceColour.WHITE:
			if move.fromSquare == (7, 0):
				return position.castlingRights - {types.CastlingRights.WHITE_QUEENSIDE}, boardRows
			elif move.fromSquare == (7, 7):
				return position.castlingRights - {types.CastlingRights.WHITE_KINGSIDE}, boardRows
		else:
			if move.fromSquare == (0, 0):
				return position.castlingRights - {types.CastlingRights.BLACK_QUEENSIDE}, boardRows
			elif move.fromSquare == (0, 7):
				return position.castlingRights - {types.CastlingRights.BLACK_KINGSIDE}, boardRows
	return position.castlingRights, boardRows
	

def applyMove(position: types.Position, move: types.Move) -> types.Position:
	"""Applies a move to the given position and returns the new position."""
	# Convert immutable tuple to mutable list
	boardRows: types.BoardRows = list[list[types.BoardSquare]](map(list, position.board))
	fromRow, fromCol = move.fromSquare
	toRow, toCol = move.toSquare
	pieceFrom, colourFrom = position.board[fromRow][fromCol]

	# Handle square changes
	castlingRights, boardRows = handleMoveSquareChanges(position = position, boardRows = boardRows, move = move)

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
		castlingRights = castlingRights,
		enPassantTargettableSquare = enPassantTargettableSquare,
		fiftyMoveCounter = fiftyMoveCounter,
		fullMoveCounter = position.fullMoveCounter + (1 if position.sideToMove == types.PieceColour.BLACK else 0),
	)