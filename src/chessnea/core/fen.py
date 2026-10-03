import logging

from chessnea.core import position, types

FEN_STARTING_POSITION: str = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
FEN_VALID_PIECE_CHARACTERS: str = "rnbqkpRNBQKP"
FEN_VALID_EMPTY_SQUARE_CHARACTERS: str = "12345678"
FEN_VALID_BOARD_CHARACTERS: str = FEN_VALID_PIECE_CHARACTERS + FEN_VALID_EMPTY_SQUARE_CHARACTERS

logger: logging.Logger = logging.getLogger(__name__)

def parseFENCoordinatesToBoardCoordinates(file: str, rank: str) -> types.Square:
	# Convert FEN coordinates into our internal representation
	if file not in "abcdefgh" or rank not in "12345678":
		raise ValueError(f"FEN: Invalid input FEN square field: {file}{rank}")
	return (8 - int(rank), "abcdefgh".index(file))

def parseBoardCoordinatesToFENCoordinates(row: int, col: int) -> str:
	# Convert our internal representation into FEN coordinates
	if row < 0 or row > 7 or col < 0 or col > 7:
		raise ValueError(f"FEN: Invalid input internal square field: {row} {col}")
	return f"{'abcdefgh'[col]}{8 - row}"

def importFENToPositionObject(fen: str) -> position.Position:
	fenParts: list[str] = fen.split()
	if len(fenParts) != 6:
		raise ValueError(f"FEN: Expected 6 parts, got {len(fenParts)} in {fen}")

	boardFEN: str = fenParts[0]
	sideToMoveFEN: str = fenParts[1]
	castlingRightsFEN: str = fenParts[2]
	enPassantTargetSquareFEN: str = fenParts[3]
	fiftyMoveCounterFEN: str = fenParts[4]
	fullMoveCounterFEN: str = fenParts[5]
 
	# Board FEN
	boardKingCount: int = 0
	boardFENRanks: list[str] = boardFEN.split(sep = "/")
	if len(boardFENRanks) != 8:
		raise ValueError(f"FEN: Expected 8 ranks, got {len(boardFENRanks)} in {fen}")
	parsedBoardList: list[list[tuple[types.Piece, types.PieceColour]]] = []
	for rankFEN in boardFENRanks:
		parsedBoardRanks: list[tuple[types.Piece, types.PieceColour]] = []
		for i in rankFEN:
			if i.lower() in "pnbrqk":
				if i.lower() == "k":
					boardKingCount += 1
				parsedBoardRanks.append((types.FENToPiece.PIECE[i.upper()], types.FENToPiece.COLOUR[i]))
				continue
			if i.isdigit():
				for _ in range(int(i)):
					parsedBoardRanks.append((types.Piece.EMPTY, types.PieceColour.EMPTY))
				continue
			raise ValueError(f"FEN: Expected valid FEN piece character or digit, got {i} in {fen}")
		if len(parsedBoardRanks) != 8:
			raise ValueError(f"FEN: Expected 8 squares in rank, got {len(parsedBoardRanks)} in {fen}")
		parsedBoardList.append(parsedBoardRanks)
	
	if len(parsedBoardList) != 8:
		raise ValueError(f"FEN: Expected 8 ranks in board, got {len(parsedBoardList)} in {fen}")
	
	if boardKingCount != 2:
		raise ValueError(f"FEN: Expected 2 kings, got {boardKingCount} in {fen}")
 
	parsedBoard: tuple[tuple[tuple[types.Piece, types.PieceColour], ...], ...] = tuple(map(tuple, parsedBoardList))
 
	# side to move FEN
	parsedSideToMove: types.PieceColour
	if sideToMoveFEN.lower() == "w":
		parsedSideToMove = types.PieceColour.WHITE
	elif sideToMoveFEN.lower() == "b":
		parsedSideToMove = types.PieceColour.BLACK
	else:
		raise ValueError(f"FEN: Expected valid side to move character, got {sideToMoveFEN} in {fen}")

	# castling rights fen
	unparsedCastlingRights: set[types.CastlingRights] = set[types.CastlingRights]()
	if castlingRightsFEN == "-":
		pass
	else:
		for i in castlingRightsFEN:
			if i == "K":
				unparsedCastlingRights.add(types.CastlingRights.WHITE_KINGSIDE)
			elif i == "Q":
				unparsedCastlingRights.add(types.CastlingRights.WHITE_QUEENSIDE)
			elif i == "k":
				unparsedCastlingRights.add(types.CastlingRights.BLACK_KINGSIDE)
			elif i == "q":
				unparsedCastlingRights.add(types.CastlingRights.BLACK_QUEENSIDE)
			else:
				raise ValueError(f"FEN: Expected valid castling rights character, got {i} in {fen}")
	parsedCastlingRights: frozenset[types.CastlingRights] = frozenset(unparsedCastlingRights)
 
	# en passant target square FEN
	parsedEnPassantTargetSquare: types.Square
	if enPassantTargetSquareFEN == "-":
		parsedEnPassantTargetSquare = (-1, -1)
	else:
		if len(enPassantTargetSquareFEN) != 2:
			raise ValueError(f"FEN: Expected valid en passant target square, got {enPassantTargetSquareFEN} in {fen}")
		parsedEnPassantTargetSquare = parseFENCoordinatesToBoardCoordinates(file = enPassantTargetSquareFEN[0], rank = enPassantTargetSquareFEN[1])
	
		if enPassantTargetSquareFEN[1] not in ("3", "6"):
			raise ValueError(f"FEN: Expected valid en passant target square, got {enPassantTargetSquareFEN} in {fen}")

	# fifty move counter FEN
	if not fiftyMoveCounterFEN.isdigit():
		raise ValueError(f"FEN: Expected valid fifty move counter, got {fiftyMoveCounterFEN} in {fen}")
	parsedFiftyMoveCounter: int = int(fiftyMoveCounterFEN)
 
	# full move counter FEN
	if not fullMoveCounterFEN.isdigit():
		raise ValueError(f"FEN: Expected valid full move counter, got {fullMoveCounterFEN} in {fen}")
	parsedFullMoveCounter: int = int(fullMoveCounterFEN)
 
	positionFilled: position.Position = position.Position(
		board = parsedBoard,
		sideToMove = parsedSideToMove,
		castlingRights = parsedCastlingRights,
		enPassantTargettableSquare = parsedEnPassantTargetSquare,
		fiftyMoveCounter = parsedFiftyMoveCounter,
		fullMoveCounter = parsedFullMoveCounter
	)
	
	return positionFilled
	
 
def exportPositionObjectToFEN(position: position.Position) -> str:
	# encode board FEN
	boardFEN: str = ""
	for rank in position.board:
		tempFEN: str = ""
		emptySquareCount: int = 0
		for i, element in enumerate(rank):
			if element[0] == types.Piece.EMPTY:
				emptySquareCount += 1
			else:
				if emptySquareCount != 0:
					tempFEN += str(emptySquareCount)
					emptySquareCount = 0
				if element[1] == types.PieceColour.BLACK:
					tempFEN += str(types.PieceToFEN.BLACK[element[0]])
				else:
					tempFEN += str(types.PieceToFEN.WHITE[element[0]])
			if i == 7 and emptySquareCount > 0:
				tempFEN += str(emptySquareCount)
		boardFEN += f"{tempFEN}/"
	if boardFEN[len(boardFEN)-1:] == "/":
		boardFEN = boardFEN.rstrip("/")
  
	# encode side to move FEN
	sideToMoveFEN: str
	if position.sideToMove == types.PieceColour.WHITE:
		sideToMoveFEN = "w"
	else:
		sideToMoveFEN = "b"
	
	# encode castling rights FEN
	castlingRightsFEN: str = ""
	if types.CastlingRights.WHITE_KINGSIDE in position.castlingRights:
		castlingRightsFEN += "K"
	if types.CastlingRights.WHITE_QUEENSIDE in position.castlingRights:
		castlingRightsFEN += "Q"
	if types.CastlingRights.BLACK_KINGSIDE in position.castlingRights:
		castlingRightsFEN += "k"
	if types.CastlingRights.BLACK_QUEENSIDE in position.castlingRights:
		castlingRightsFEN += "q"
	if castlingRightsFEN == "":
		castlingRightsFEN = "-"
  
	# encode en passant target square FEN
	enPassantTargetSquareFEN: str
	if position.enPassantTargettableSquare == (-1, -1):
		enPassantTargetSquareFEN = "-"
	else:
		enPassantTargetSquareFEN = parseBoardCoordinatesToFENCoordinates(row = position.enPassantTargettableSquare[0], col = position.enPassantTargettableSquare[1])
  
	# encode fifty move counter FEN
	fiftyMoveCounterFEN: str = str(position.fiftyMoveCounter)
 
	# encode full move counter FEN
	fullMoveCounterFEN: str = str(position.fullMoveCounter)
 
	return f"{boardFEN} {sideToMoveFEN} {castlingRightsFEN} {enPassantTargetSquareFEN} {fiftyMoveCounterFEN} {fullMoveCounterFEN}"
  