import logging
from multiprocessing import Value

from chessnea.core import types

FEN_STARTING_POSITION: str = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
FEN_VALID_PIECE_CHARACTERS: str = "rnbqkpRNBQKP"
FEN_VALID_EMPTY_SQUARE_CHARACTERS: str = "12345678"
FEN_VALID_BOARD_CHARACTERS: str = FEN_VALID_PIECE_CHARACTERS + FEN_VALID_EMPTY_SQUARE_CHARACTERS

logger: logging.Logger = logging.getLogger(__name__)

def parseFENCoordinatesToBoardCoordinates(file: str, rank: str) -> tuple[int, int]:
	# Convert FEN coordinates into our internal representation
	if file not in "abcdefgh" or rank not in "12345678":
		raise ValueError(f"FEN: Invalid input FEN square field: {file}{rank}")
	return (8 - int(rank), "abcdefgh".index(file))

def parseBoardCoordinatesToFENCoordinates(row: int, col: int) -> str:
	# Convert our internal representation into FEN coordinates
	if row < 0 or row > 7 or col < 0 or col > 7:
		raise ValueError(f"FEN: Invalid input internal square field: {row} {col}")
	return f"{'abcdefgh'[col]}{8 - row}"

def importFENToPositionObject(fen: str) -> None:
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
	boardFENRanks: list[str] = boardFEN.split(sep = "/")
	if len(boardFENRanks) != 8:
		raise ValueError(f"FEN: Expected 8 ranks, got {len(boardFENRanks)} in {fen}")
	parsedBoard: list[list[tuple[types.Piece, types.PieceColour]]] = []
	for rankFEN in boardFENRanks:
		parsedBoardRanks: list[tuple[types.Piece, types.PieceColour]] = []
		for i in rankFEN:
			if i.lower() in "pnbrqk":
				parsedBoardRanks.append((types.FENToPiece.PIECE[i.upper()], types.FENToPiece.COLOUR[i]))
				continue
			if i.isdigit():
				for _ in range(int(i)):
					parsedBoardRanks.append((types.Piece.EMPTY, types.PieceColour.WHITE))
				continue
			raise ValueError(f"FEN: Expected valid FEN piece character or digit, got {i} in {fen}")
		parsedBoard.append(parsedBoardRanks)
	
	# side to move FEN
	parsedSideToMove: types.PieceColour
	if sideToMoveFEN.lower() == "w":
		parsedSideToMove = types.PieceColour.WHITE
	elif sideToMoveFEN.lower() == "b":
		parsedSideToMove = types.PieceColour.BLACK
	else:
		raise ValueError(f"FEN: Expected valid side to move character, got {sideToMoveFEN} in {fen}")

	# castling rights fen
	parsedCastlingRights: set[types.CastlingRights] = set[types.CastlingRights]()
	
 
	