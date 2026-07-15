from __future__ import annotations # Fix import cycling
from typing import Protocol

import logging
import chessnea.config as config

class BoardHandlingProtocolForFEN(Protocol):                                                                                                                                                                                      
	Board: list[list[tuple[config.Piece, config.PieceColour]]]                                                                                                                                                    
	SideToMove: config.PieceColour                                                                                                                                                                                
	CastlingRights: list[config.CastlingRights]                                                                                                                                                                   
	EnPassantTargettableSquare: tuple[int, int]                                                                                                                                                                   
	FiftyMoveCounter: int                                                                                                                                                                                         
	FullMoveCounter: int

logger: logging.Logger = logging.getLogger(__name__)

def parseFENCoordinatesToBoardCoordinates(file: str, rank: str) -> tuple[int, int]:
	# Convert FEN coordinates into our internal representation
	if file not in "abcdefgh" or rank not in "12345678":
		raise ValueError(f"BoardHandling: Invalid FEN: Invalid input square field: {file}{rank}")
	return (8 - int(rank), "abcdefgh".index(file))

def parseBoardCoordinatesToFENCoordinates(row: int, col: int) -> str:
	# Convert our internal board coordinates into FEN coordinates
	if row < 0 or row > 7 or col < 0 or col > 7:
		raise ValueError(f"BoardHandling: Invalid FEN: Invalid input square field: {row} {col}")
	return f"{'abcdefgh'[col]}{8 - row}"

def exportFEN(board: BoardHandlingProtocolForFEN) -> str:
	positionFEN: str = ""
	for row in board.Board:
		emptySquareCounter: int = 0
		for piece, colour in row:
			# We want it to end up in the format : nr of squares / piece / nr of squares etc. etc.
			if piece == config.Piece.EMPTY: 
				emptySquareCounter += 1
			else:
				if emptySquareCounter != 0:
					positionFEN += str(emptySquareCounter)
					emptySquareCounter = 0
				if colour == config.PieceColour.WHITE:
					positionFEN += config.PieceToFEN.WHITE[piece]
				else:
					positionFEN += config.PieceToFEN.BLACK[piece]
		if emptySquareCounter != 0:
			positionFEN += str(emptySquareCounter)
		positionFEN += "/"
	positionFEN = positionFEN[:-1] # Remove the last "/"

	sideToMoveFEN: str
	if board.SideToMove == config.PieceColour.WHITE: # Encode side to move
		sideToMoveFEN = "w"
	else:
		sideToMoveFEN= "b"
	
	castlingRightsFEN: str = "" # Encode castling rights
	if config.CastlingRights.WHITE_KINGSIDE in board.CastlingRights:
		castlingRightsFEN += "K"
	if config.CastlingRights.WHITE_QUEENSIDE in board.CastlingRights:
		castlingRightsFEN += "Q"
	if config.CastlingRights.BLACK_KINGSIDE in board.CastlingRights:
		castlingRightsFEN += "k"
	if config.CastlingRights.BLACK_QUEENSIDE in board.CastlingRights:
		castlingRightsFEN += "q"
	if castlingRightsFEN == "": # Empty
		castlingRightsFEN = "-"

	if board.EnPassantTargettableSquare == (-1, -1): # Encode en passant target square
		enPassantTargetSquareFEN: str = "-"
	else:
		enPassantTargetSquareFEN = parseBoardCoordinatesToFENCoordinates(row = board.EnPassantTargettableSquare[0], col = board.EnPassantTargettableSquare[1])

	fiftyMoveCounterFEN: str = str(board.FiftyMoveCounter) # Encode move counters
	fullMoveCounterFEN: str = str(board.FullMoveCounter)

	FEN: str = f"{positionFEN} {sideToMoveFEN} {castlingRightsFEN} {enPassantTargetSquareFEN} {fiftyMoveCounterFEN} {fullMoveCounterFEN}"
	logger.debug(msg = f"FEN: Exported FEN string: {FEN}")
	return FEN

def getFENasKey(fen: str) -> str:
	splitFEN: list[str] = fen.split(sep = " ")
	return splitFEN[0] + " " + splitFEN[1] + " " + splitFEN[2] + " " + splitFEN[3] # We only want the position, side to move, castling rights and en passant target square for our key, as this uniquely identifies a position for repetition detection

def importFEN(board: BoardHandlingProtocolForFEN, fen: str) -> None:
	# Parse a position given in FEN into our internal representation, as well as assigning values to necessary flags for game flow
	logger.debug(msg = f"FEN: Importing FEN string: {fen}")
	splitFEN: list[str] = fen.split(sep = " ")
	if len(splitFEN) != 6: 
		raise ValueError(f"Invalid FEN: Expected 6 fields, got {len(splitFEN)}") # FEN field nr. check (erroneous data)

	# Assigning the different parts of the FEN string into separate variables.
	sideToMoveFEN, castlingRightsFEN, enPassantTargetSquareFEN, fiftyMoveCounterFEN, fullMoveCounterFEN = splitFEN[1], splitFEN[2], splitFEN[3], splitFEN[4], splitFEN[5]

	# Set side to move flag
	if sideToMoveFEN == "w":
		board.SideToMove = config.PieceColour.WHITE
	elif sideToMoveFEN == "b":
		board.SideToMove = config.PieceColour.BLACK
	else:
		raise ValueError(f"Invalid FEN: Invalid side to move field: {sideToMoveFEN}")
	
	# Set castling rights flag
	tempCastlingRights: list[config.CastlingRights] = []
	if castlingRightsFEN != "-":
		for char in castlingRightsFEN:
			if char == "K":
				tempCastlingRights.append(config.CastlingRights.WHITE_KINGSIDE)
			elif char == "Q":
				tempCastlingRights.append(config.CastlingRights.WHITE_QUEENSIDE)
			elif char == "k":
				tempCastlingRights.append(config.CastlingRights.BLACK_KINGSIDE)
			elif char == "q":
				tempCastlingRights.append(config.CastlingRights.BLACK_QUEENSIDE)
			else:
				raise ValueError(f"Invalid FEN: Invalid castling rights field: {castlingRightsFEN}")
	board.CastlingRights = tempCastlingRights
	
	# Set en passant target flag
	if enPassantTargetSquareFEN == "-":
		board.EnPassantTargettableSquare = (-1, -1)
	else:
		file: str = enPassantTargetSquareFEN[0]
		rank: str = enPassantTargetSquareFEN[1]
		board.EnPassantTargettableSquare = parseFENCoordinatesToBoardCoordinates(file = file, rank = rank)
	try:
		board.FiftyMoveCounter = int(fiftyMoveCounterFEN)
		board.FullMoveCounter = int(fullMoveCounterFEN)
	except ValueError:
		raise ValueError(f"Invalid FEN: Invalid move counter(s): {fiftyMoveCounterFEN} {fullMoveCounterFEN}")
	
	# Parse FEN board position
	splitFENRanks: list[str] = splitFEN[0].split(sep = "/")
	if len(splitFENRanks) != 8: 
		raise ValueError(f"Invalid FEN: Expected 8 ranks, got {len(splitFENRanks)}") # FEN position rank nr. check (erroneous data)

	emptyBoard: list[list[tuple[config.Piece, config.PieceColour]]] = [[(config.Piece.EMPTY, config.PieceColour.WHITE) for _ in range(8)] for _ in range(8)] # Initialise an empty board for us to populate
	for rankIndex, ranks in enumerate(splitFENRanks):
		fileIndex: int = 0
		for piece in ranks:
			if piece not in config.FEN_VALID_BOARD_CHARACTERS:
				raise ValueError(f"Invalid FEN: Invalid character for piece: {piece}")
			if piece in "12345678":
				if fileIndex + int(piece) > 8:
					raise ValueError(f"Invalid FEN: Too many squares in rank {rankIndex + 1}")
				for i in range(int(piece)):
					emptyBoard[rankIndex][fileIndex + i] = (config.Piece.EMPTY, config.PieceColour.WHITE)
				fileIndex += int(piece)
			else:
				if fileIndex >= 8:
					raise ValueError(f"Invalid FEN: Too many squares in rank {rankIndex + 1}")
				colour: config.PieceColour = config.PieceColour.WHITE
				if piece.isupper(): # Check char capitalisation before checking for equivalence with internal representation (invalid data)
					colour = config.PieceColour.WHITE
				else:
					colour = config.PieceColour.BLACK
				pieceUpper: str = piece.upper()
				pieceType: config.Piece = config.Piece.EMPTY
				match pieceUpper: # Needs a recent version of Python (>Python 3.7?)
					case "P":
						pieceType = config.Piece.PAWN
					case "N":
						pieceType = config.Piece.KNIGHT
					case "B":
						pieceType = config.Piece.BISHOP
					case "R":
						pieceType = config.Piece.ROOK
					case "Q":
						pieceType = config.Piece.QUEEN
					case "K":
						pieceType = config.Piece.KING
					case _:
						raise ValueError(f"Invalid FEN: Invalid character for piece: {piece}")
				emptyBoard[rankIndex][fileIndex] = (pieceType, colour)
				fileIndex += 1
	board.Board = emptyBoard
	# Check if the imported position has legal castling positions
	if config.CastlingRights.WHITE_KINGSIDE in board.CastlingRights:
		if board.Board[7][4] != (config.Piece.KING, config.PieceColour.WHITE) or board.Board[7][7] != (config.Piece.ROOK, config.PieceColour.WHITE):
			logger.error(msg = "FEN: Castling rights for white kingside castling given in FEN, but no king and/or rook in the correct position")
			board.CastlingRights.remove(config.CastlingRights.WHITE_KINGSIDE)
	if config.CastlingRights.WHITE_QUEENSIDE in board.CastlingRights:
		if board.Board[7][4] != (config.Piece.KING, config.PieceColour.WHITE) or board.Board[7][0] != (config.Piece.ROOK, config.PieceColour.WHITE):
			logger.error(msg = "FEN: Castling rights for white queenside castling given in FEN, but no king and/or rook in the correct position")
			board.CastlingRights.remove(config.CastlingRights.WHITE_QUEENSIDE)
	if config.CastlingRights.BLACK_KINGSIDE in board.CastlingRights:
		if board.Board[0][4] != (config.Piece.KING, config.PieceColour.BLACK) or board.Board[0][7] != (config.Piece.ROOK, config.PieceColour.BLACK):
			logger.error(msg = "FEN: Castling rights for black kingside castling given in FEN, but no king and/or rook in the correct position")
			board.CastlingRights.remove(config.CastlingRights.BLACK_KINGSIDE)
	if config.CastlingRights.BLACK_QUEENSIDE in board.CastlingRights:
		if board.Board[0][4] != (config.Piece.KING, config.PieceColour.BLACK) or board.Board[0][0] != (config.Piece.ROOK, config.PieceColour.BLACK):
			logger.error(msg = "FEN: Castling rights for black queenside castling given in FEN, but no king and/or rook in the correct position")
			board.CastlingRights.remove(config.CastlingRights.BLACK_QUEENSIDE)

	# Check if both kings exist
	whiteKingExists: bool = False
	blackKingExists: bool = False
	for row in board.Board:
		for piece, colour in row:
			if piece == config.Piece.KING and colour == config.PieceColour.WHITE:
				whiteKingExists = True
			elif piece == config.Piece.KING and colour == config.PieceColour.BLACK:
				blackKingExists = True
	if not whiteKingExists:
		logger.error(msg = "FEN: No white king found in the imported position")
		raise ValueError("No white king found in the imported position")
	if not blackKingExists:
		logger.error(msg = "FEN: No black king found in the imported position")
		raise ValueError("No black king found in the imported position")
	logger.debug(msg = f"FEN: Successfully parsed FEN string, side to move: {board.SideToMove.name}, full-move counter: {board.FullMoveCounter}")