"""Defines functions to check if a move is legal or not."""

from chessnea.core import types
from chessnea.rules import moves

KNIGHT_OFFSETS: list[tuple[int, int]] = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]
KING_OFFSETS: list[tuple[int, int]] = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
DIAGONAL_OFFSETS: list[tuple[int, int]] = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
STRAIGHT_OFFSETS: list[tuple[int, int]] = [(-1, 0), (1, 0), (0, -1), (0, 1)]

def checkBounds(row: int, col: int) -> bool:
	"""Checks if a given row and column are within the bounds of the chess board."""
	return 0 <= row < 8 and 0 <= col < 8

def getOpposingColour(colour: types.PieceColour) -> types.PieceColour:
	"""Returns the opposing colour of the given colour."""
	if colour == types.PieceColour.WHITE:
		return types.PieceColour.BLACK
	else: 
		return types.PieceColour.WHITE

def isSquareAttacked(board: types.Board, square: types.Square, attackingColour: types.PieceColour) -> bool:
	"""Checks if a given square is attacked by any piece of the attacking colour."""
	row, col = square
	# Pawns
	pawnRow: int = row + 1 if attackingColour == types.PieceColour.WHITE else row - 1
	for pawnCol in [col - 1, col + 1]:
		if checkBounds(row = pawnRow, col = pawnCol):
			piece, colour = board[pawnRow][pawnCol]
			if piece == types.Piece.PAWN and colour == attackingColour:
				return True

	# Knights
	for offset in KNIGHT_OFFSETS:
		knightRow, knightCol = row + offset[0], col + offset[1]
		if checkBounds(row = knightRow, col = knightCol):
			piece, colour = board[knightRow][knightCol]
			if piece == types.Piece.KNIGHT and colour == attackingColour:
				return True

	# Kings
	for offset in KING_OFFSETS:
		kingRow, kingCol = row + offset[0], col + offset[1]
		if checkBounds(row = kingRow, col = kingCol):
			piece, colour = board[kingRow][kingCol]
			if piece == types.Piece.KING and colour == attackingColour:
				return True
	# Diagonals: Bishop/Queen
	for offset in DIAGONAL_OFFSETS:
		rowOffset, colOffset = row + offset[0], col + offset[1]
		while checkBounds(row = rowOffset, col = colOffset):
			piece, colour = board[rowOffset][colOffset]
			if piece != types.Piece.EMPTY:
				if colour == attackingColour and (piece == types.Piece.BISHOP or piece == types.Piece.QUEEN):
					return True
				break
			rowOffset += offset[0]
			colOffset += offset[1]
	# Straights: Rook/Queen
	for offset in STRAIGHT_OFFSETS:
		rowOffset, colOffset = row + offset[0], col + offset[1]
		while checkBounds(row = rowOffset, col = colOffset):
			piece, colour = board[rowOffset][colOffset]
			if piece != types.Piece.EMPTY:
				if colour == attackingColour and (piece == types.Piece.ROOK or piece == types.Piece.QUEEN):
					return True
				break
			rowOffset += offset[0]
			colOffset += offset[1]
	return False

def findKing(board: types.Board, colour: types.PieceColour) -> types.Square | None:
	"""Finds the square of the king of the given colour on the board."""
	for row in range(8):
		for col in range(8):
			piece, pieceColour = board[row][col]
			if piece == types.Piece.KING and pieceColour == colour:
				return (row, col)
	return None

def isKingInCheck(board: types.Board, colour: types.PieceColour) -> bool:
	"""Checks if the king of the given colour is in check."""
	kingSquare: types.Square | None = findKing(board = board, colour = colour)
	if kingSquare is None:
		raise ValueError(f"Board: No king found for colour {colour.name}")
	return isSquareAttacked(
		board = board,
		square = kingSquare, 
		attackingColour = getOpposingColour(colour = colour))

def getCastlingMoves(position: types.Position, square: types.Square) -> list[types.Move]:
	"""Returns a list of castling moves to the king on the given square"""
	moves: list[types.Move] = []
	board: types.Board = position.board
	kingColour: types.PieceColour = board[square[0]][square[1]][1]
	opposingColour: types.PieceColour = getOpposingColour(colour = kingColour)
	tempRights: set[types.CastlingRights] = set(position.castlingRights)
	row: int = 7 if kingColour == types.PieceColour.WHITE else 0
	
	# Check that the king is on its original row and is not in check
	if square != (row, 4) or isSquareAttacked(board = board, square = square, attackingColour = opposingColour):
		return moves
	
	'''
	1. We go through each castling right and check if it corresponds with the kingColour
	2. We check if the squares between the king and the rook are empty
	3. We check if the squares the king would move through are not attacked by the opposing color
	4. If all conditions are met, we add the castling move to the list
 	'''
	for right in tempRights:
		if right == types.CastlingRights.WHITE_KINGSIDE and kingColour == types.PieceColour.WHITE and \
  				(board[7][5][0] == types.Piece.EMPTY and board[7][6][0] == types.Piece.EMPTY and
				not isSquareAttacked(board = board, square = (7, 5), attackingColour = opposingColour) and
				not isSquareAttacked(board = board, square = (7, 6), attackingColour = opposingColour)):
				moves.append(types.Move(fromSquare=(7, 4), toSquare=(7, 6)))
		elif right == types.CastlingRights.WHITE_QUEENSIDE and kingColour == types.PieceColour.WHITE and \
  				(board[7][1][0] == types.Piece.EMPTY and board[7][2][0] == types.Piece.EMPTY and board[7][3][0] == types.Piece.EMPTY and
				not isSquareAttacked(board = board, square = (7, 2), attackingColour = opposingColour) and
				not isSquareAttacked(board = board, square = (7, 3), attackingColour = opposingColour)):
				moves.append(types.Move(fromSquare=(7, 4), toSquare=(7, 2)))
		elif right == types.CastlingRights.BLACK_KINGSIDE and kingColour == types.PieceColour.BLACK and \
  				(board[0][5][0] == types.Piece.EMPTY and board[0][6][0] == types.Piece.EMPTY and
				not isSquareAttacked(board = board, square = (0, 5), attackingColour = opposingColour) and
				not isSquareAttacked(board = board, square = (0, 6), attackingColour = opposingColour)):
				moves.append(types.Move(fromSquare=(0, 4), toSquare=(0, 6)))
		elif right == types.CastlingRights.BLACK_QUEENSIDE and kingColour == types.PieceColour.BLACK and \
  				(board[0][1][0] == types.Piece.EMPTY and board[0][2][0] == types.Piece.EMPTY and board[0][3][0] == types.Piece.EMPTY and
				not isSquareAttacked(board = board, square = (0, 2), attackingColour = opposingColour) and
				not isSquareAttacked(board = board, square = (0, 3), attackingColour = opposingColour)):
				moves.append(types.Move(fromSquare=(0, 4), toSquare=(0, 2)))
	return moves

def filterPseudoLegalMovesToLegalMoves(position: types.Position, pseudoLegalMoves: list[types.Move]) -> list[types.Move]:
	"""Filters a list of pseudo-legal moves to only include legal moves."""
	legalMoves: list[types.Move] = []
	for move in pseudoLegalMoves:
		newPosition: types.Position = moves.applyMove(position = position, move = move)
		if not isKingInCheck(board = newPosition.board, colour = position.sideToMove):
			legalMoves.append(move)
	return legalMoves

def getLegalMovesForPiece(position: types.Position, square: types.Square) -> list[types.Move]:
	"""Returns a list of legal moves for the piece on the given square."""
	piece: types.Piece = position.board[square[0]][square[1]][0]
	pseudoLegalMoves: list[types.Move] = moves.PseudoLegalMoves.movesForPiece(position = position, square = square)
	if piece == types.Piece.KING:
		pseudoLegalMoves.extend(getCastlingMoves(position = position, square = square))
	if piece == types.Piece.PAWN:
		promotionMoves: list[types.Move] = []
		for move in pseudoLegalMoves:
			if move.toSquare[0] == 0 or move.toSquare[0] == 7:
				for promotionPiece in [types.Piece.QUEEN, types.Piece.ROOK, types.Piece.BISHOP, types.Piece.KNIGHT]:
					promotionMoves.append(types.Move(fromSquare = move.fromSquare, toSquare = move.toSquare, promotionPiece = promotionPiece))
			else:
				promotionMoves.append(move)
		pseudoLegalMoves = promotionMoves
	legalMoves: list[types.Move] = filterPseudoLegalMovesToLegalMoves(position = position, pseudoLegalMoves = pseudoLegalMoves)
	return legalMoves

def getAllLegalMoves(position: types.Position) -> list[types.Move]:
	"""Returns a list of all legal moves for the current position."""
	legalMoves: list[types.Move] = []
	for row in range(8):
		for col in range(8):
			if position.board[row][col][1] == position.sideToMove:
				square: types.Square = (row, col)
				legalMoves.extend(getLegalMovesForPiece(position = position, square = square))
	return legalMoves
