"""Converts our internal moves to UCI format and vice versa."""

from chessnea.core import fen, types

PROMOTION_PIECE_TO_UCI: dict[types.Piece, str] = {
	types.Piece.QUEEN: "q",
	types.Piece.ROOK: "r",
	types.Piece.BISHOP: "b",
	types.Piece.KNIGHT: "n",
}

UCI_TO_PROMOTION_PIECE: dict[str, types.Piece] = {
	"q": types.Piece.QUEEN,
	"r": types.Piece.ROOK,
	"b": types.Piece.BISHOP,
	"n": types.Piece.KNIGHT,
}

def moveToUCI(move: types.Move) -> str:
	"""Converts an internal move representation to UCI format.

	Args:
		move (types.Move): The internal move representation.

	Returns:
		str: The UCI formatted move.
	"""
	fromStr: str = fen.parseBoardCoordinatesToFENCoordinates(row = move.fromSquare[0], col = move.fromSquare[1])
	toStr: str = fen.parseBoardCoordinatesToFENCoordinates(row = move.toSquare[0], col = move.toSquare[1])
	uciMove: str = fromStr + toStr
	if move.promotionPiece is not None:
		uciMove += PROMOTION_PIECE_TO_UCI[move.promotionPiece]
	return uciMove

def UCIToMove(uciMove: str) -> types.Move:
	"""Converts a UCI formatted move to an internal move representation.

	Args:
		uciMove (str): The UCI formatted move.

	Returns:
		types.Move: The internal move representation.
	"""
	fromSquare: tuple[int, int] = fen.parseFENCoordinatesToBoardCoordinates(file = uciMove[0], rank = uciMove[1])
	toSquare: tuple[int, int] = fen.parseFENCoordinatesToBoardCoordinates(file = uciMove[2], rank = uciMove[3])
	promotionPiece: types.Piece | None = None
	if len(uciMove) == 5:
		promotionPiece = UCI_TO_PROMOTION_PIECE[uciMove[4]]
	return types.Move(fromSquare = fromSquare, toSquare = toSquare, promotionPiece = promotionPiece)