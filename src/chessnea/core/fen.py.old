from __future__ import annotations

import logging

from chessnea.core import position, types

FEN_STARTING_POSITION: str = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
FEN_VALID_PIECE_CHARACTERS: str = "rnbqkpRNBQKP"
FEN_VALID_EMPTY_SQUARE_CHARACTERS: str = "12345678"
FEN_VALID_BOARD_CHARACTERS: str = FEN_VALID_PIECE_CHARACTERS + FEN_VALID_EMPTY_SQUARE_CHARACTERS

logger: logging.Logger = logging.getLogger(__name__)

def parseFENCoordinatesToBoardCoordinates(file: str, rank: str) -> tuple[int, int]:
    # Convert FEN coordinates into our internal representation
    if file not in "abcdefgh" or rank not in "12345678":
        raise ValueError(f"Invalid FEN: Invalid input FEN square field: {file}{rank}")
    return (8 - int(rank), "abcdefgh".index(file))

def parseBoardCoordinatesToFENCoordinates(row: int, col: int) -> str:
    # Convert our internal representation into FEN coordinates
    if row < 0 or row > 7 or col < 0 or col > 7:
        raise ValueError(f"Invalid FEN: Invalid input internal square field: {row} {col}")
    return f"{'abcdefgh'[col]}{8 - row}"

def exportFEN(position: position.Position) -> str:
	positionFEN: str = ""
	for row in position.Board:
		emptySquareCounter: int = 0
		for piece, colour in row:
			# We want it to end up in the format : nr of squares / piece / nr of squares etc. etc.
			if piece == types.Piece.EMPTY: 
				emptySquareCounter += 1
			else:
				if emptySquareCounter != 0:
					positionFEN += str(emptySquareCounter)
					emptySquareCounter = 0
				if colour == types.PieceColour.WHITE:
					positionFEN += types.PieceToFEN.WHITE[piece]
				else:
					positionFEN += types.PieceToFEN.BLACK[piece]
		if emptySquareCounter != 0:
			positionFEN += str(emptySquareCounter)
		positionFEN += "/"
	positionFEN = positionFEN[:-1] # Remove the last "/"

	sideToMoveFEN: str
	if position.SideToMove == types.PieceColour.WHITE: # Encode side to move
		sideToMoveFEN = "w"
	else:
		sideToMoveFEN= "b"
	
	castlingRightsFEN: str = "" # Encode castling rights
	if types.CastlingRights.WHITE_KINGSIDE in position.CastlingRights:
		castlingRightsFEN += "K"
	if types.CastlingRights.WHITE_QUEENSIDE in position.CastlingRights:
		castlingRightsFEN += "Q"
	if types.CastlingRights.BLACK_KINGSIDE in position.CastlingRights:
		castlingRightsFEN += "k"
	if types.CastlingRights.BLACK_QUEENSIDE in position.CastlingRights:
		castlingRightsFEN += "q"
	if castlingRightsFEN == "": # Empty
		castlingRightsFEN = "-"

	if position.EnPassantTargettableSquare == (-1, -1): # Encode en passant target square
		enPassantTargetSquareFEN: str = "-"
	else:
		enPassantTargetSquareFEN = parseBoardCoordinatesToFENCoordinates(row = position.EnPassantTargettableSquare[0], col = position.EnPassantTargettableSquare[1])

	fiftyMoveCounterFEN: str = str(position.FiftyMoveCounter) # Encode move counters
	fullMoveCounterFEN: str = str(position.FullMoveCounter)

	FEN: str = f"{positionFEN} {sideToMoveFEN} {castlingRightsFEN} {enPassantTargetSquareFEN} {fiftyMoveCounterFEN} {fullMoveCounterFEN}"
	logger.debug(msg = f"FEN: Exported FEN string: {FEN}")
	return FEN

def importFENToPositionObject(fen: str) -> position.Position:
	# Parse a position given in FEN into our internal representation, as well as assigning values to necessary flags for game flow
	logger.debug(msg = f"FEN: Importing FEN string: {fen}")
	splitFEN: list[str] = fen.split()
	if len(splitFEN) != 6: 
		raise ValueError(f"Invalid FEN: Expected 6 fields, got {len(splitFEN)}") # FEN field nr. check (erroneous data)

	# Assigning the different parts of the FEN string into separate variables.
	sideToMoveFEN, castlingRightsFEN, enPassantTargetSquareFEN, fiftyMoveCounterFEN, fullMoveCounterFEN = splitFEN[1], splitFEN[2], splitFEN[3], splitFEN[4], splitFEN[5]

	# Set side to move flag
	SideToMove: types.PieceColour
	if sideToMoveFEN == "w":
		SideToMove = types.PieceColour.WHITE
	elif sideToMoveFEN == "b":
		SideToMove = types.PieceColour.BLACK
	else:
		raise ValueError(f"Invalid FEN: Invalid side to move field: {sideToMoveFEN}")
	
	# Set castling rights flag
	CastlingRights: set[types.CastlingRights] = set()
	if castlingRightsFEN != "-":
		for char in castlingRightsFEN:
			if char == "K":
				CastlingRights.add(types.CastlingRights.WHITE_KINGSIDE)
			elif char == "Q":
				CastlingRights.add(types.CastlingRights.WHITE_QUEENSIDE)
			elif char == "k":
				CastlingRights.add(types.CastlingRights.BLACK_KINGSIDE)	
			elif char == "q":
				CastlingRights.add(types.CastlingRights.BLACK_QUEENSIDE)
			else:
				raise ValueError(f"Invalid FEN: Invalid castling rights field: {castlingRightsFEN}")
	
	EnPassantTargettableSquare: tuple[int, int]
	FiftyMoveCounter: int
	FullMoveCounter: int

	# Set en passant target flag
	if enPassantTargetSquareFEN == "-":
		EnPassantTargettableSquare = (-1, -1)
	else:
		file: str = enPassantTargetSquareFEN[0]
		rank: str = enPassantTargetSquareFEN[1]
		EnPassantTargettableSquare = parseFENCoordinatesToBoardCoordinates(file = file, rank = rank)
	try:
		FiftyMoveCounter = int(fiftyMoveCounterFEN)
		FullMoveCounter = int(fullMoveCounterFEN)
	except ValueError:
		raise ValueError(f"Invalid FEN: Invalid move counter(s): {fiftyMoveCounterFEN} {fullMoveCounterFEN}")
	
	# Parse FEN board position
	splitFENRanks: list[str] = splitFEN[0].split(sep = "/")
	if len(splitFENRanks) != 8: 
		raise ValueError(f"Invalid FEN: Expected 8 ranks, got {len(splitFENRanks)}") # FEN position rank nr. check (erroneous data)

	emptyBoard: list[list[tuple[types.Piece, types.PieceColour]]] = [[(types.Piece.EMPTY, types.PieceColour.WHITE) for _ in range(8)] for _ in range(8)] # Initialise an empty board for us to populate
	for rankIndex, ranks in enumerate(splitFENRanks):
		fileIndex: int = 0
		for piece in ranks:
			if piece not in FEN_VALID_BOARD_CHARACTERS:
				raise ValueError(f"Invalid FEN: Invalid character for piece: {piece}")
			if piece in "12345678":
				if fileIndex + int(piece) > 8:
					raise ValueError(f"Invalid FEN: Too many squares in rank {rankIndex + 1}")
				for i in range(int(piece)):
					emptyBoard[rankIndex][fileIndex + i] = (types.Piece.EMPTY, types.PieceColour.WHITE)
				fileIndex += int(piece)
			else:
				if fileIndex >= 8:
					raise ValueError(f"Invalid FEN: Too many squares in rank {rankIndex + 1}")
				colour: types.PieceColour = types.PieceColour.WHITE
				if piece.isupper(): # Check char capitalisation before checking for equivalence with internal representation (invalid data)
					colour = types.PieceColour.WHITE
				else:
					colour = types.PieceColour.BLACK
				pieceUpper: str = piece.upper()
				pieceType: types.Piece = types.Piece.EMPTY
				match pieceUpper: # Needs a recent version of Python (>Python 3.7?)
					case "P":
						pieceType = types.Piece.PAWN
					case "N":
						pieceType = types.Piece.KNIGHT
					case "B":
						pieceType = types.Piece.BISHOP
					case "R":
						pieceType = types.Piece.ROOK
					case "Q":
						pieceType = types.Piece.QUEEN
					case "K":
						pieceType = types.Piece.KING
					case _:
						raise ValueError(f"Invalid FEN: Invalid character for piece: {piece}")
				emptyBoard[rankIndex][fileIndex] = (pieceType, colour)
				fileIndex += 1
	# Check if the imported position has legal castling positions
	if types.CastlingRights.WHITE_KINGSIDE in CastlingRights and (emptyBoard[7][4] != (types.Piece.KING, types.PieceColour.WHITE) or emptyBoard[7][7] != (types.Piece.ROOK, types.PieceColour.WHITE)):
			logger.error(msg = "FEN: Castling rights for white kingside castling given in FEN, but no king and/or rook in the correct position")
			CastlingRights.discard(types.CastlingRights.WHITE_KINGSIDE)
	if types.CastlingRights.WHITE_QUEENSIDE in CastlingRights and (emptyBoard[7][4] != (types.Piece.KING, types.PieceColour.WHITE) or emptyBoard[7][0] != (types.Piece.ROOK, types.PieceColour.WHITE)):
			logger.error(msg = "FEN: Castling rights for white queenside castling given in FEN, but no king and/or rook in the correct position")
			CastlingRights.discard(types.CastlingRights.WHITE_QUEENSIDE)
	if types.CastlingRights.BLACK_KINGSIDE in CastlingRights and (emptyBoard[0][4] != (types.Piece.KING, types.PieceColour.BLACK) or emptyBoard[0][7] != (types.Piece.ROOK, types.PieceColour.BLACK)):
			logger.error(msg = "FEN: Castling rights for black kingside castling given in FEN, but no king and/or rook in the correct position")
			CastlingRights.discard(types.CastlingRights.BLACK_KINGSIDE)
	if types.CastlingRights.BLACK_QUEENSIDE in CastlingRights and (emptyBoard[0][4] != (types.Piece.KING, types.PieceColour.BLACK) or emptyBoard[0][0] != (types.Piece.ROOK, types.PieceColour.BLACK)):
			logger.error(msg = "FEN: Castling rights for black queenside castling given in FEN, but no king and/or rook in the correct position")
			CastlingRights.discard(types.CastlingRights.BLACK_QUEENSIDE)

	# Check if both kings exist
	whiteKingExists: bool = False
	blackKingExists: bool = False
	for row in emptyBoard:
		for piece, colour in row:
			if piece == types.Piece.KING and colour == types.PieceColour.WHITE:
				whiteKingExists = True
			elif piece == types.Piece.KING and colour == types.PieceColour.BLACK:
				blackKingExists = True
	if not whiteKingExists:
		logger.error(msg = "FEN: No white king found in the imported position")
		raise ValueError("No white king found in the imported position")
	if not blackKingExists:
		logger.error(msg = "FEN: No black king found in the imported position")
		raise ValueError("No black king found in the imported position")
	positionObject: position.Position = position.Position(
		Board = tuple(tuple(row) for row in emptyBoard),
		SideToMove = SideToMove,
		CastlingRights = frozenset(CastlingRights),
		EnPassantTargettableSquare = EnPassantTargettableSquare,
		FiftyMoveCounter = FiftyMoveCounter,
		FullMoveCounter = FullMoveCounter
	)
	logger.debug(msg = f"FEN: Successfully parsed FEN string, side to move: {SideToMove.name}, full-move counter: {FullMoveCounter}")
	return positionObject