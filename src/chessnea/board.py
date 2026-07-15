from typing import Literal
import logging
import pygame

import chessnea.assets as assets
import chessnea.config as config
import chessnea.fen as fen

logger: logging.Logger = logging.getLogger(name = __name__)

class BoardHandling():
	def __init__(self)  -> None:
		self.Board: list[list[tuple[config.Piece, config.PieceColour]]] = [
				[
				(config.Piece.EMPTY, config.PieceColour.WHITE) for _ in range(8)
				] for _ in range(8)
			] # Initialise an empty board
		self.SideToMove: config.PieceColour = config.PieceColour.WHITE # White is the default side to move (subject to parsed FEN position)
		self.CastlingRights: list[config.CastlingRights] = [config.CastlingRights.WHITE_KINGSIDE, config.CastlingRights.WHITE_QUEENSIDE, config.CastlingRights.BLACK_KINGSIDE, config.CastlingRights.BLACK_QUEENSIDE]
		self.EnPassantTargettableSquare: tuple[int, int] = (-1, -1) # Defines which square is attackable under en passant
		self.FiftyMoveCounter: int = 0 # Niche rule allowing a draw after 50 moves without a capture
		self.FullMoveCounter: int = 0 # Constant tracking for current move nr.
		self.sprites: list[list[pygame.Surface | None]] = [] # Load sprites from disk
		self.piecePickedUp: tuple[int, int] = (-1, -1) # Current piece picked up by the mouse cursor
		self.piecePickedUpLegalMoves: list[config.MoveData] = [] # Legal moves cache for the currently picked up piece
		self.selectedSquare: tuple[int, int] = (-1, -1)
		self.selectedSquareLegalMoves: list[config.MoveData] = []
		self.pendingPromotion: config.PromotionData | None = None # Hold the intended promotion move in place as we wait for user input
		self.moveHighlighting: config.MoveHighlighting = config.MoveHighlighting() # Store the current and previous move for move highlighting
		self.checkState: config.CheckState = config.CheckState() # Store check state for check highlighting
		self.gameState: config.GameState = config.GameState() # Store game state
		self.PositionHistory: list[config.MoveHistoryData] = [] # Store move history as FEN strings
		self.PositionHistoryAsKeys: list[str] = [] # Store move history as FEN strings when checking for threefold repetition
		self.moveHighlightingWithPositionHistory: list[config.MoveHighlighting] = []
		self.isBoardFlipped: bool = False
		self.isBoardFlippingEnabled: bool = False
		self.hasFirstMoveHappened: bool = False
		
	def resetBoard(self) -> config.ReturnType:
		fen.importFEN(board = self, fen = config.FEN_STARTING_POSITION)
		self.piecePickedUp = (-1, -1)
		self.piecePickedUpLegalMoves = []
		self.selectedSquare = (-1, -1)
		self.selectedSquareLegalMoves = []
		self.pendingPromotion = None
		self.moveHighlighting = config.MoveHighlighting()
		self.checkState = config.CheckState()
		self.gameState = config.GameState()
		self.syncBoardFlipStateToSideToMove()
		fenString: str = fen.exportFEN(board = self)
		self.PositionHistory = [config.MoveHistoryData(fen = fenString, whiteClock = 0.0, blackClock = 0.0)]
		self.PositionHistoryAsKeys = [fen.getFENasKey(fen = fenString)]
		self.moveHighlightingWithPositionHistory = [config.MoveHighlighting()]
		self.hasFirstMoveHappened = False
		return config.ReturnType.NORMAL

	def refreshGameStateAfterFENLoad(self) -> None:
		self.piecePickedUp = (-1, -1)
		self.piecePickedUpLegalMoves = []
		self.selectedSquare = (-1, -1)
		self.selectedSquareLegalMoves = []
		self.pendingPromotion = None
		self.moveHighlighting = config.MoveHighlighting()
		self.checkState = config.CheckState()
		self.gameState = config.GameState()
		enemyColour: config.PieceColour = self.findOpposingColour(colour = self.SideToMove)
		kingPosition: tuple[int, int] = findKing(board = self, sourceColour = self.SideToMove)
		if isSquareAttacked(board = self, targetSquare = kingPosition, attackingColour = enemyColour):
			self.checkState.inCheck = True
			self.checkState.square = kingPosition
			self.checkState.colourInCheck = self.SideToMove
		self.syncBoardFlipStateToSideToMove()
		updateGameStateAfterMove(board = self)
		self.hasFirstMoveHappened = True

	def undoMove(self) -> config.ReturnType:
		if len(self.PositionHistory) <= 1:
			logger.error(msg = "Board: Cannot undo move because position history is empty")
			return config.ReturnType.ERROR

		_ = self.PositionHistory.pop()
		_ = self.PositionHistoryAsKeys.pop()
		if len(self.moveHighlightingWithPositionHistory) > 0:
			_ = self.moveHighlightingWithPositionHistory.pop()
		previousPosition: config.MoveHistoryData = self.PositionHistory[-1]
		fen.importFEN(board = self, fen = previousPosition.fen)
		self.refreshGameStateAfterFENLoad()
		if len(self.PositionHistory) == 1:
			self.hasFirstMoveHappened = False
			self.moveHighlighting = config.MoveHighlighting()
		elif len(self.moveHighlightingWithPositionHistory) > 0:
			self.moveHighlighting = self.moveHighlightingWithPositionHistory[-1]
		else:
			self.moveHighlighting = config.MoveHighlighting()
		logger.info(msg = f"Board: Reverted to the previous move, counter: {self.FullMoveCounter}")
		return config.ReturnType.NORMAL

	def getDisplaySquare(self, square: tuple[int, int]) -> tuple[int, int]:
		if square == (-1, -1): 
			return square
		if self.isBoardFlipped:
			return (7 - square[0], 7 - square[1])
		return square

	def syncBoardFlipStateToSideToMove(self) -> None:
		if self.isBoardFlippingEnabled and self.SideToMove == config.PieceColour.BLACK:
			self.isBoardFlipped = True
		else:
			self.isBoardFlipped = False

	def loadSpritesForBoard(self) -> None:
		self.sprites = assets.loadSprites()

	def getSquareUnderMousePosition(self) -> tuple[int, int] | None:
		# Converts absolute coordinates for the mouse position provided by Pygame into a internal board square
		mouseX, mouseY = pygame.mouse.get_pos()
		mouseY -= config.WindowDefaults.TOP_BAR_HEIGHT.value
		col: int = mouseX // config.WIDTH_PER_SQUARE
		row: int = mouseY // config.HEIGHT_PER_SQUARE
		if 0 <= row < 8 and 0 <= col < 8:
			return self.getDisplaySquare(square = (row, col))
		else:
			return None
	
	def changeSideToMove(self) -> None:
		if self.SideToMove == config.PieceColour.WHITE:
			self.SideToMove = config.PieceColour.BLACK
		else:
			self.SideToMove = config.PieceColour.WHITE

	def findOpposingColour(self, colour: config.PieceColour) -> config.PieceColour:
		if colour == config.PieceColour.WHITE:
			return config.PieceColour.BLACK
		else:
			return config.PieceColour.WHITE

class PseudoLegalMovesForPieceType():
	@staticmethod
	def pawn(board: BoardHandling, row: int, col: int) -> list[config.MoveData]:
		validMoves: list[config.MoveData] = []
		direction: int
		startingRank: int

		if board.Board[row][col][1] == config.PieceColour.WHITE:
			direction = -1
			startingRank = 6
		else:
			direction = 1
			startingRank = 1
		targetSingleRow: int = row + direction
		targetDoubleRow: int = row + (2 * direction)
		if 0 <= targetSingleRow <= 7 and board.Board[targetSingleRow][col][0] == config.Piece.EMPTY: # Standard move
			if targetSingleRow == 0 or targetSingleRow == 7: # A single row push should be a promotion if landing on the final ranks
				for promotionalPiece in config.PromotionalPieces:
					validMoves.append(config.MoveData(fromSquare = (row, col), toSquare = (targetSingleRow, col), moveType = config.MoveType.PROMOTION, promotionPiece = config.Piece(promotionalPiece.value)))
			else:
				validMoves.append(config.MoveData(fromSquare = (row, col), toSquare = (targetSingleRow, col), moveType = config.MoveType.NORMAL))
			if row == startingRank and board.Board[targetDoubleRow][col][0] == config.Piece.EMPTY: # Double move from starting rank
				validMoves.append(config.MoveData(fromSquare = (row, col), toSquare = (targetDoubleRow, col), moveType = config.MoveType.NORMAL))

		for targetDiagonalCol in [col -1, col + 1]: # Captures
			if 0 <= targetDiagonalCol <= 7 and 0 <= targetSingleRow <= 7:
				targetPiece, targetColour = board.Board[targetSingleRow][targetDiagonalCol][0], board.Board[targetSingleRow][targetDiagonalCol][1]
				if targetPiece != config.Piece.EMPTY and targetPiece != config.Piece.KING and targetColour != board.Board[row][col][1]: # Diagonal capture
					if targetSingleRow == 0 or targetSingleRow == 7: # A capture should be a promotion if landing on the final ranks
						for promotionalPiece in config.PromotionalPieces:
							validMoves.append(config.MoveData(fromSquare = (row, col), toSquare = (targetSingleRow, targetDiagonalCol), moveType = config.MoveType.PROMOTION, promotionPiece = config.Piece(promotionalPiece.value)))
					else:
						validMoves.append(config.MoveData(fromSquare = (row, col), toSquare = (targetSingleRow, targetDiagonalCol), moveType = config.MoveType.CAPTURE))
				if (targetSingleRow, targetDiagonalCol) == board.EnPassantTargettableSquare and targetPiece == config.Piece.EMPTY: # En passant capture
					if board.SideToMove == config.PieceColour.WHITE:
						if board.Board[targetSingleRow + 1][targetDiagonalCol][0] == config.Piece.PAWN:
							if board.Board[targetSingleRow + 1][targetDiagonalCol][1] == config.PieceColour.BLACK:
								validMoves.append(config.MoveData(fromSquare = (row, col), toSquare = (targetSingleRow, targetDiagonalCol), moveType = config.MoveType.EN_PASSANT))
					else:
						if board.Board[targetSingleRow - 1][targetDiagonalCol][0] == config.Piece.PAWN:
							if board.Board[targetSingleRow - 1][targetDiagonalCol][1] == config.PieceColour.WHITE:
								validMoves.append(config.MoveData(fromSquare = (row, col), toSquare = (targetSingleRow, targetDiagonalCol), moveType = config.MoveType.EN_PASSANT))
		return validMoves

	@staticmethod
	def bishop(board: BoardHandling, row: int, col: int) -> list[config.MoveData]:
		validMoves: list[config.MoveData] = []
		_, currentColour = board.Board[row][col][0], board.Board[row][col][1]
		directions: list[list[int]] = [[-1, -1], [-1, 1], [1, -1], [1, 1]] # Up Left, Up Right, Down Left, Down Right
		targetRow: int
		targetCol: int

		for i in directions:
			targetRow, targetCol = row + i[0], col + i[1]
			while 0 <= targetRow <= 7 and 0 <= targetCol <= 7:
				targetPiece, targetColour = board.Board[targetRow][targetCol][0], board.Board[targetRow][targetCol][1]
				if targetPiece == config.Piece.EMPTY:
					validMoves.append(config.MoveData(fromSquare = (row, col), toSquare = (targetRow, targetCol), moveType = config.MoveType.NORMAL))
				elif targetColour == currentColour:
					break
				else:
					if targetPiece != config.Piece.KING:
						validMoves.append(config.MoveData(fromSquare = (row, col), toSquare = (targetRow, targetCol), moveType = config.MoveType.CAPTURE))
					break
				targetRow, targetCol = targetRow + i[0], targetCol + i[1]
		return validMoves

	@staticmethod
	def knight(board: BoardHandling, row: int, col: int) -> list[config.MoveData]:
		validMoves: list[config.MoveData] = []
		_, currentColour = board.Board[row][col][0], board.Board[row][col][1]
		# Up 2 Left 1, Up 2 Right 1, Up 1 Left 2, Up 1 Right 2, Down 1 Left 2, Down 1 Right 2, Down 2 Left 1, Down 2 Right 1
		directions: list[list[int]] = [[-2, -1], [-2, 1], [-1, -2], [-1, 2], [1, -2], [1, 2], [2, -1], [2, 1]]
		targetRow: int
		targetCol: int

		for i in directions:
			targetRow, targetCol = row + i[0], col + i[1]
			if 0 <= targetRow <= 7 and 0 <= targetCol <= 7:
				targetPiece, targetColour = board.Board[targetRow][targetCol][0], board.Board[targetRow][targetCol][1]
				if targetPiece == config.Piece.EMPTY:
					validMoves.append(config.MoveData(fromSquare = (row, col), toSquare = (targetRow, targetCol), moveType = config.MoveType.NORMAL))
				elif targetPiece != config.Piece.KING and targetColour != currentColour:
					validMoves.append(config.MoveData(fromSquare = (row, col), toSquare = (targetRow, targetCol), moveType = config.MoveType.CAPTURE))
				targetRow, targetCol = targetRow + i[0], targetCol + i[1]
		return validMoves

	@staticmethod
	def rook(board: BoardHandling, row: int, col: int) -> list[config.MoveData]:
		validMoves: list[config.MoveData] = []
		_, currentColour = board.Board[row][col][0], board.Board[row][col][1]
		directions: list[list[int]] = [[-1, 0], [1, 0], [0, -1], [0, 1]] # Up, Down, Left, Right
		targetRow: int
		targetCol: int

		for i in directions:
			targetRow, targetCol = row + i[0], col + i[1]
			while 0 <= targetRow <= 7 and 0 <= targetCol <= 7:
				targetPiece, targetColour = board.Board[targetRow][targetCol][0], board.Board[targetRow][targetCol][1]
				if targetPiece == config.Piece.EMPTY:
					validMoves.append(config.MoveData(fromSquare = (row, col), toSquare = (targetRow, targetCol), moveType = config.MoveType.NORMAL))
				elif targetColour == currentColour:
					break
				else:
					if targetPiece != config.Piece.KING:
						validMoves.append(config.MoveData(fromSquare = (row, col), toSquare = (targetRow, targetCol), moveType = config.MoveType.CAPTURE))
					break
				targetRow, targetCol = targetRow + i[0], targetCol + i[1]
		return validMoves

	@staticmethod
	def queen(board: BoardHandling, row: int, col: int) -> list[config.MoveData]:
		validMoves: list[config.MoveData] = []
		_, currentColour = board.Board[row][col][0], board.Board[row][col][1]
		# Up Left, Up, Up Right, Left, Right, Down Left, Down, Down Right
		directions: list[list[int]] = [[-1, -1], [-1, 0], [-1, 1], [0, -1], [0, 1], [1, -1], [1, 0], [1, 1]]
		targetRow: int
		targetCol: int

		for i in directions:
			targetRow, targetCol = row + i[0], col + i[1]
			while 0 <= targetRow <= 7 and 0 <= targetCol <= 7:
				targetPiece, targetColour = board.Board[targetRow][targetCol][0], board.Board[targetRow][targetCol][1]
				if targetPiece == config.Piece.EMPTY:
					validMoves.append(config.MoveData(fromSquare = (row, col), toSquare = (targetRow, targetCol), moveType = config.MoveType.NORMAL))
				elif targetColour == currentColour:
					break
				else:
					if targetPiece != config.Piece.KING:
						validMoves.append(config.MoveData(fromSquare = (row, col), toSquare = (targetRow, targetCol), moveType = config.MoveType.CAPTURE))
					break
				targetRow, targetCol = targetRow + i[0], targetCol + i[1]
		return validMoves

	@staticmethod
	def king(board: BoardHandling, row: int, col: int) -> list[config.MoveData]:
		validMoves: list[config.MoveData] = []
		_, currentColour = board.Board[row][col][0], board.Board[row][col][1]
		directions: list[list[int]] = [[-1, -1], [-1, 0], [-1, 1], [0, -1], [0, 1], [1, -1], [1, 0], [1, 1]] # All 8 possible king move directions
		targetRow: int
		targetCol: int

		for i in directions:
			targetRow, targetCol = row + i[0], col + i[1]
			if 0 <= targetRow <= 7 and 0 <= targetCol <= 7:
				targetPiece, targetColour = board.Board[targetRow][targetCol][0], board.Board[targetRow][targetCol][1]
				if targetPiece == config.Piece.EMPTY:
					validMoves.append(config.MoveData(fromSquare = (row, col), toSquare = (targetRow, targetCol), moveType = config.MoveType.NORMAL))
				elif targetPiece != config.Piece.KING and targetColour != currentColour:
					validMoves.append(config.MoveData(fromSquare = (row, col), toSquare = (targetRow, targetCol), moveType = config.MoveType.CAPTURE))
				targetRow, targetCol = targetRow + i[0], targetCol + i[1]

		# Castling moves
		if currentColour == config.PieceColour.WHITE and row == 7 and col == 4:
			if config.CastlingRights.WHITE_KINGSIDE in board.CastlingRights and board.Board[7][7] == (config.Piece.ROOK, config.PieceColour.WHITE):
				if board.Board[7][5][0] == config.Piece.EMPTY and board.Board[7][6][0] == config.Piece.EMPTY:
					validMoves.append(config.MoveData(fromSquare = (row, col), toSquare = (7, 6), moveType = config.MoveType.CASTLING))
			if config.CastlingRights.WHITE_QUEENSIDE in board.CastlingRights and board.Board[7][0] == (config.Piece.ROOK, config.PieceColour.WHITE):
				if board.Board[7][1][0] == config.Piece.EMPTY and board.Board[7][2][0] == config.Piece.EMPTY and board.Board[7][3][0] == config.Piece.EMPTY:
					validMoves.append(config.MoveData(fromSquare = (row, col), toSquare = (7, 2), moveType = config.MoveType.CASTLING))
		elif currentColour == config.PieceColour.BLACK and row == 0 and col == 4:
			if config.CastlingRights.BLACK_KINGSIDE in board.CastlingRights and board.Board[0][7] == (config.Piece.ROOK, config.PieceColour.BLACK):
				if board.Board[0][5][0] == config.Piece.EMPTY and board.Board[0][6][0] == config.Piece.EMPTY:
					validMoves.append(config.MoveData(fromSquare = (row, col), toSquare = (0, 6), moveType = config.MoveType.CASTLING))
			if config.CastlingRights.BLACK_QUEENSIDE in board.CastlingRights and board.Board[0][0] == (config.Piece.ROOK, config.PieceColour.BLACK):
				if board.Board[0][1][0] == config.Piece.EMPTY and board.Board[0][2][0] == config.Piece.EMPTY and board.Board[0][3][0] == config.Piece.EMPTY:
					validMoves.append(config.MoveData(fromSquare = (row, col), toSquare = (0, 2), moveType = config.MoveType.CASTLING))

		return validMoves

def getPseudoLegalMovesForPiece(board: BoardHandling, row: int, col: int) -> list[config.MoveData]:
	# In order to get all legal moves, we get all pseudo-legal moves (ignoring check conditions)
	moves: list[config.MoveData] = []
	if board.Board[row][col][0] == config.Piece.EMPTY:
		return []
	elif board.Board[row][col][0] == config.Piece.PAWN:
		logger.debug(msg = f"Board: Getting pseudo-legal moves for pawn at square {(row, col)}")
		moves =  PseudoLegalMovesForPieceType.pawn(board = board, row = row, col = col)
	elif board.Board[row][col][0] == config.Piece.BISHOP:
		logger.debug(msg = f"Board: Getting pseudo-legal moves for bishop at square {(row, col)}")
		moves = PseudoLegalMovesForPieceType.bishop(board = board, row = row, col = col)
	elif board.Board[row][col][0] == config.Piece.KNIGHT:
		logger.debug(msg = f"Board: Getting pseudo-legal moves for knight at square {(row, col)}")
		moves = PseudoLegalMovesForPieceType.knight(board = board, row = row, col = col)
	elif board.Board[row][col][0] == config.Piece.ROOK:
		logger.debug(msg = f"Board: Getting pseudo-legal moves for rook at square {(row, col)}")
		moves = PseudoLegalMovesForPieceType.rook(board = board, row = row, col = col)
	elif board.Board[row][col][0] == config.Piece.QUEEN:
		logger.debug(msg = f"Board: Getting pseudo-legal moves for queen at square {(row, col)}")
		moves = PseudoLegalMovesForPieceType.queen(board = board, row = row, col = col)
	elif board.Board[row][col][0] == config.Piece.KING:
		logger.debug(msg = f"Board: Getting pseudo-legal moves for king at square {(row, col)}")
		moves = PseudoLegalMovesForPieceType.king(board = board, row = row, col = col)
	else:
		logger.error(msg = f"Board: Invalid piece type {board.Board[row][col][0]} at square {(row, col)}")
	return moves

def findKing(board: BoardHandling, sourceColour: config.PieceColour) -> tuple[int, int]:
	kingPosition: tuple[int, int] = (-1, -1)
	for rankIndex, rank in enumerate[list[tuple[config.Piece, config.PieceColour]]](board.Board):
		for fileIndex, file in enumerate[tuple[config.Piece, config.PieceColour]](rank):
			if file[0] == config.Piece.KING and file[1] == sourceColour:
				kingPosition = (rankIndex, fileIndex)
				return kingPosition
	return kingPosition

class squareAttackChecking():
	@staticmethod
	def pawn(board: BoardHandling, targetSquare: tuple[int, int], attackingColour: config.PieceColour) -> bool:
		targetRow, targetCol = targetSquare
		direction: int
		if attackingColour == config.PieceColour.WHITE:
			direction = 1
		else:
			direction = -1
		for potentialPieceDiagonalCol in [targetCol - 1, targetCol + 1]:
			if 0 <= potentialPieceDiagonalCol <= 7 and 0 <= targetRow + direction <= 7:
				if board.Board[targetRow + direction][potentialPieceDiagonalCol][0] == config.Piece.PAWN and board.Board[targetRow + direction][potentialPieceDiagonalCol][1] == attackingColour:
					return True
		return False

	@staticmethod
	def bishop(board: BoardHandling, targetSquare: tuple[int, int], attackingColour: config.PieceColour) -> bool:
		targetRow, targetCol = targetSquare
		directions: list[list[int]] = [[-1, -1], [-1, 1], [1, -1], [1, 1]] # Up Left, Up Right, Down Left, Down Right
		for i in directions:
			targetRowDirection, targetColDirection = targetRow + i[0], targetCol + i[1]
			while 0 <= targetRowDirection <= 7 and 0 <= targetColDirection <= 7:
				if board.Board[targetRowDirection][targetColDirection][0] == config.Piece.BISHOP and board.Board[targetRowDirection][targetColDirection][1] == attackingColour:
					return True
				if board.Board[targetRowDirection][targetColDirection][0] != config.Piece.EMPTY:
					break
				targetRowDirection, targetColDirection = targetRowDirection + i[0], targetColDirection + i[1]
		return False

	@staticmethod
	def knight(board: BoardHandling, targetSquare: tuple[int, int], attackingColour: config.PieceColour) -> bool:
		targetRow, targetCol = targetSquare
		directions: list[list[int]] = [[-2, -1], [-2, 1], [-1, -2], [-1, 2], [1, -2], [1, 2], [2, -1], [2, 1]] # Up 2 Left 1, Up 2 Right 1, Up 1 Left 2, Up 1 Right 2, Down 1 Left 2, Down 1 Right 2, Down 2 Left 1, Down 2 Right 1
		for i in directions:
			targetRowDirection, targetColDirection = targetRow + i[0], targetCol + i[1]
			if 0 <= targetRowDirection <= 7 and 0 <= targetColDirection <= 7:
				if board.Board[targetRowDirection][targetColDirection][0] == config.Piece.KNIGHT and board.Board[targetRowDirection][targetColDirection][1] == attackingColour:
					return True
		return False

	@staticmethod
	def rook(board: BoardHandling, targetSquare: tuple[int, int], attackingColour: config.PieceColour) -> bool:
		targetRow, targetCol = targetSquare
		directions: list[list[int]] = [[-1, 0], [1, 0], [0, -1], [0, 1]] # Up, Down, Left, Right
		for i in directions:
			targetRowDirection, targetColDirection = targetRow + i[0], targetCol + i[1]
			while 0 <= targetRowDirection <= 7 and 0 <= targetColDirection <= 7:
				if board.Board[targetRowDirection][targetColDirection][0] == config.Piece.ROOK and board.Board[targetRowDirection][targetColDirection][1] == attackingColour:
					return True
				if board.Board[targetRowDirection][targetColDirection][0] != config.Piece.EMPTY:
					break
				targetRowDirection, targetColDirection = targetRowDirection + i[0], targetColDirection + i[1]
		return False

	@staticmethod
	def queen(board: BoardHandling, targetSquare: tuple[int, int], attackingColour: config.PieceColour) -> bool:
		targetRow, targetCol = targetSquare
		directions: list[list[int]] = [[-1, -1], [-1, 0], [-1, 1], [0, -1], [0, 1], [1, -1], [1, 0], [1, 1]] # Up Left, Up, Up Right, Left, Right, Down Left, Down, Down Right
		for i in directions:
			targetRowDirection, targetColDirection = targetRow + i[0], targetCol + i[1]
			while 0 <= targetRowDirection <= 7 and 0 <= targetColDirection <= 7:
				if board.Board[targetRowDirection][targetColDirection][0] == config.Piece.QUEEN and board.Board[targetRowDirection][targetColDirection][1] == attackingColour:
					return True 
				if board.Board[targetRowDirection][targetColDirection][0] != config.Piece.EMPTY:
					break
				targetRowDirection, targetColDirection = targetRowDirection + i[0], targetColDirection + i[1]
		return False

	@staticmethod
	def king(board: BoardHandling, targetSquare: tuple[int, int], attackingColour: config.PieceColour) -> bool:
		targetRow, targetCol = targetSquare
		directions: list[list[int]] = [[-1, -1], [-1, 0], [-1, 1], [0, -1], [0, 1], [1, -1], [1, 0], [1, 1]] # All 8 possible king move directions
		for i in directions:
			targetRowDirection, targetColDirection = targetRow + i[0], targetCol + i[1]
			if 0 <= targetRowDirection <= 7 and 0 <= targetColDirection <= 7:
				if board.Board[targetRowDirection][targetColDirection][0] == config.Piece.KING and board.Board[targetRowDirection][targetColDirection][1] == attackingColour:
					return True
		return False

def isSquareAttacked(board: BoardHandling, targetSquare: tuple[int, int], attackingColour: config.PieceColour) -> bool:
	# Check for attacks
	if squareAttackChecking.pawn(board = board, targetSquare = targetSquare, attackingColour = attackingColour):
		return True
	if squareAttackChecking.bishop(board = board, targetSquare = targetSquare, attackingColour = attackingColour):
		return True
	if squareAttackChecking.knight(board = board, targetSquare = targetSquare, attackingColour = attackingColour):
		return True
	if squareAttackChecking.rook(board = board, targetSquare = targetSquare, attackingColour = attackingColour):
		return True
	if squareAttackChecking.queen(board = board, targetSquare = targetSquare, attackingColour = attackingColour):
		return True
	if squareAttackChecking.king(board = board, targetSquare = targetSquare, attackingColour = attackingColour):
		return True
	return False

def getLegalMovesForPiece(board: BoardHandling, row: int, col: int) -> list[config.MoveData]:
	enemyColour: config.PieceColour
	sourcePiece, sourceColour = board.Board[row][col][0], board.Board[row][col][1]
	if sourcePiece == config.Piece.EMPTY:
		logger.error(msg = f"Board: Attempting to get legal moves for empty square {(row, col)}")
		return []
	if sourceColour != board.SideToMove:
		logger.error(msg = f"Board: Attempting to get legal moves for piece of colour {sourceColour.name} when it is {board.SideToMove.name}'s turn to move")
		return []
	pseudoLegalMoves: list[config.MoveData] = getPseudoLegalMovesForPiece(board = board, row = row, col = col)
	legalMoves: list[config.MoveData] = []
	for pseudoMove in pseudoLegalMoves:
		if pseudoMove.moveType == config.MoveType.CASTLING:
			enemyColour = board.findOpposingColour(colour = sourceColour)
			if isSquareAttacked(board = board, targetSquare = pseudoMove.fromSquare, attackingColour = enemyColour) or isSquareAttacked(board = board, targetSquare = pseudoMove.toSquare, attackingColour = enemyColour):
				continue
			squaresToMove: int
			if pseudoMove.toSquare[1] == 6: # Kingside castling
				squaresToMove = 2
			else: # Queenside castling
				squaresToMove = -2
			attemptedCastleThroughCheck: bool = False
			for i in range(1, abs(squaresToMove) + 1): # Check all squares the king moves through for attacks
				new_i: int
				if squaresToMove > 0:
					new_i = i
				else:
					new_i = -i
				intermediateSquare: tuple[int, int] = (row, col + new_i)
				if isSquareAttacked(board = board, targetSquare = intermediateSquare, attackingColour = enemyColour):
					attemptedCastleThroughCheck = True
					break
			if attemptedCastleThroughCheck:
				continue
			else:
				legalMoves.append(pseudoMove)
				continue

		targetRow, targetCol, moveType = pseudoMove.toSquare[0], pseudoMove.toSquare[1], pseudoMove.moveType
		tempBoardHandling = BoardHandling()
		tempBoard: list[list[tuple[config.Piece, config.PieceColour]]] = []
		# Create the temporary board as a hard copy
		for i in board.Board:
			tempBoard.append(i.copy())
		tempBoardHandling.Board = tempBoard
		# Apply pseudo-legal move to the temporary board
		tempBoard[targetRow][targetCol] = tempBoard[row][col]
		tempBoard[row][col] = (config.Piece.EMPTY, config.PieceColour.WHITE)
		if moveType == config.MoveType.EN_PASSANT:
			if sourceColour == config.PieceColour.WHITE:
				tempBoard[targetRow + 1][targetCol] = (config.Piece.EMPTY, config.PieceColour.WHITE)
			else:
				tempBoard[targetRow - 1][targetCol] = (config.Piece.EMPTY, config.PieceColour.WHITE)
		# Check king check condition
		kingPosition: tuple[int, int] | tuple[Literal[-1], Literal[-1]] = findKing(board = tempBoardHandling, sourceColour = sourceColour)
		
		# Check whether the opponent is attacking the king
		kingInCheck: bool = False
		enemyColour = tempBoardHandling.findOpposingColour(colour = sourceColour)
		kingInCheck = isSquareAttacked(board = tempBoardHandling, targetSquare = kingPosition, attackingColour = enemyColour)
		if not kingInCheck:
			legalMoves.append(pseudoMove)
	return legalMoves

def getAllLegalMovesForSide(board: BoardHandling, colour: config.PieceColour) -> list[config.MoveData]:
	legalMoves: list[config.MoveData] = []
	for rankIndex, rank in enumerate[list[tuple[config.Piece, config.PieceColour]]](board.Board):
		for fileIndex, file in enumerate[tuple[config.Piece, config.PieceColour]](rank):
			if file[0] != config.Piece.EMPTY and file[1] == colour:
				legalMoves.extend(getLegalMovesForPiece(board, row = rankIndex, col = fileIndex))
	return legalMoves

def updateGameStateAfterMove(board: BoardHandling) -> None:
	if checkForInsufficientMaterial(board = board):
		board.gameState.gameOver = True
		board.gameState.winner = None
		board.gameState.reason = config.GameOverReason.INSUFFICIENT_MATERIAL
		logger.info(msg = "Board: Game drawn by insufficient material")
		return
	if checkForThreefoldRepetition(board = board):
		board.gameState.gameOver = True
		board.gameState.winner = None
		board.gameState.reason = config.GameOverReason.THREEFOLD_REPETITION
		logger.info(msg = "Board: Game drawn by threefold repetition")
		return

	legalMoves: list[config.MoveData] = getAllLegalMovesForSide(board = board, colour = board.SideToMove)
	if len(legalMoves) == 0:
		if board.checkState.inCheck and board.checkState.colourInCheck == board.SideToMove:
			board.gameState.gameOver = True
			board.gameState.winner = board.findOpposingColour(colour = board.SideToMove)
			board.gameState.reason = config.GameOverReason.CHECKMATE
			logger.info(msg = f"Board: {board.SideToMove.name} is in checkmate")
			return
		else:
			board.gameState.gameOver = True
			board.gameState.winner = None
			board.gameState.reason = config.GameOverReason.STALEMATE
			logger.info(msg = f"Board: {board.SideToMove.name} is in stalemate")
			return
	
	if board.FiftyMoveCounter >= 100:
		board.gameState.gameOver = True
		board.gameState.winner = None
		board.gameState.reason = config.GameOverReason.FIFTY_MOVE_RULE
		logger.info(msg = "Board: Game drawn by fifty-move rule")
		return

def updateCastlingRightsAfterMove(board: BoardHandling, pieceToMove: config.Piece, colourToMove: config.PieceColour, fromSquare: tuple[int, int], toSquare: tuple[int, int], capturedPiece: config.Piece, capturedColour: config.PieceColour) -> None:
	if pieceToMove == config.Piece.KING:
		if colourToMove == config.PieceColour.WHITE:
			if config.CastlingRights.WHITE_KINGSIDE in board.CastlingRights:
				board.CastlingRights.remove(config.CastlingRights.WHITE_KINGSIDE)
			if config.CastlingRights.WHITE_QUEENSIDE in board.CastlingRights:
				board.CastlingRights.remove(config.CastlingRights.WHITE_QUEENSIDE)
		else:
			if config.CastlingRights.BLACK_KINGSIDE in board.CastlingRights:
				board.CastlingRights.remove(config.CastlingRights.BLACK_KINGSIDE)
			if config.CastlingRights.BLACK_QUEENSIDE in board.CastlingRights:
				board.CastlingRights.remove(config.CastlingRights.BLACK_QUEENSIDE)
	elif pieceToMove == config.Piece.ROOK:
		if colourToMove == config.PieceColour.WHITE:
			if fromSquare == (7, 0) and config.CastlingRights.WHITE_QUEENSIDE in board.CastlingRights:
				board.CastlingRights.remove(config.CastlingRights.WHITE_QUEENSIDE)
			elif fromSquare == (7, 7) and config.CastlingRights.WHITE_KINGSIDE in board.CastlingRights:
				board.CastlingRights.remove(config.CastlingRights.WHITE_KINGSIDE)
		else:
			if fromSquare == (0, 0) and config.CastlingRights.BLACK_QUEENSIDE in board.CastlingRights:
				board.CastlingRights.remove(config.CastlingRights.BLACK_QUEENSIDE)
			elif fromSquare == (0, 7) and config.CastlingRights.BLACK_KINGSIDE in board.CastlingRights:
				board.CastlingRights.remove(config.CastlingRights.BLACK_KINGSIDE)

	if capturedPiece == config.Piece.ROOK:
		if capturedColour == config.PieceColour.WHITE:
			if toSquare == (7, 0) and config.CastlingRights.WHITE_QUEENSIDE in board.CastlingRights:
				board.CastlingRights.remove(config.CastlingRights.WHITE_QUEENSIDE)
			elif toSquare == (7, 7) and config.CastlingRights.WHITE_KINGSIDE in board.CastlingRights:
				board.CastlingRights.remove(config.CastlingRights.WHITE_KINGSIDE)
		else:
			if toSquare == (0, 0) and config.CastlingRights.BLACK_QUEENSIDE in board.CastlingRights:
				board.CastlingRights.remove(config.CastlingRights.BLACK_QUEENSIDE)
			elif toSquare == (0, 7) and config.CastlingRights.BLACK_KINGSIDE in board.CastlingRights:
				board.CastlingRights.remove(config.CastlingRights.BLACK_KINGSIDE)

def completePromotion(board: BoardHandling, promotionPieceType: config.Piece | None) -> None:
	if promotionPieceType is None:
		logger.error(msg = "Board: Attempting to complete promotion with no promotion piece type specified")
		return
	if board.pendingPromotion is None:
		logger.error(msg = "Board: Attempting to complete promotion when there is no pending promotion")
		return
	if promotionPieceType == config.Piece.KING or promotionPieceType == config.Piece.EMPTY:
		logger.error(msg = f"Board: Attempting to promote to invalid piece type {promotionPieceType}")
		return
	toRow, toCol, colour = board.pendingPromotion.toSquare[0], board.pendingPromotion.toSquare[1], board.pendingPromotion.colour
	board.FiftyMoveCounter = 0
	board.Board[toRow][toCol] = (promotionPieceType, colour)
	logger.info(msg = f"Board: Completed promotion to {promotionPieceType.name} {colour.name} at square {(toRow, toCol)}")
	board.EnPassantTargettableSquare = (-1, -1)
	handleCheckStateAfterMove(board = board, colourToMove = colour)
	if colour == config.PieceColour.BLACK:
		board.FullMoveCounter += 1

	board.changeSideToMove()
	fenString: str = fen.exportFEN(board = board)
	board.PositionHistory.append(config.MoveHistoryData(
		fen = fenString,
		move = config.MoveData(
			fromSquare = board.pendingPromotion.fromSquare,
			toSquare = board.pendingPromotion.toSquare,
			moveType = config.MoveType.PROMOTION,
			promotionPiece = promotionPieceType
		),
		piece = config.Piece.PAWN,
		colour = colour,
		capturedPiece = board.pendingPromotion.capturedPiece,
		capturedColour = board.pendingPromotion.capturedColour,
		checkState = config.CheckState(
			inCheck = board.checkState.inCheck,
			square = board.checkState.square,
			colourInCheck = board.checkState.colourInCheck
		),
		gameState = config.GameState(
			gameOver = board.gameState.gameOver,
			winner = board.gameState.winner,
			reason = board.gameState.reason
		),
		whiteClock = 0.0,
		blackClock = 0.0
	))
	board.pendingPromotion = None
	board.PositionHistoryAsKeys.append(fen.getFENasKey(fen = fenString))
	board.moveHighlightingWithPositionHistory.append(config.MoveHighlighting(currentMove = board.moveHighlighting.currentMove, previousMove = board.moveHighlighting.previousMove))
	updateGameStateAfterMove(board = board)

def handleCheckStateAfterMove(board: BoardHandling, colourToMove: config.PieceColour) -> None:
	enemyColour: config.PieceColour = board.findOpposingColour(colour = colourToMove)
	kingPosition: tuple[int, int] = findKing(board = board, sourceColour = enemyColour)
	if isSquareAttacked(board = board, targetSquare = kingPosition, attackingColour = colourToMove):
		board.checkState.inCheck = True
		board.checkState.square = kingPosition
		board.checkState.colourInCheck = enemyColour
		logger.info(msg = f"Board: {enemyColour.name} king is in check at square {kingPosition} after move by {colourToMove.name}")
	else:
		board.checkState.inCheck = False
		board.checkState.square = (-1, -1)
		board.checkState.colourInCheck = None

def checkForThreefoldRepetition(board: BoardHandling) -> bool:
	currentPosition: str = fen.exportFEN(board = board)
	currentPositionKey: str = fen.getFENasKey(fen = currentPosition)
	repetitionCount: int = board.PositionHistoryAsKeys.count(currentPositionKey)
	if repetitionCount >= 3:
		logger.info(msg = f"Board: Detected threefold repetition with position {currentPosition} occurring {repetitionCount} times in the game history")
		return True
	return False

def checkForInsufficientMaterial(board: BoardHandling) -> bool:
	whitePieces: list[config.Piece] = []
	blackPieces: list[config.Piece] = []
	whitePiecesWithPositions: list[tuple[config.Piece, tuple[int, int]]] = []
	blackPiecesWithPositions: list[tuple[config.Piece, tuple[int, int]]] = []
	for rowIndex, row in enumerate[list[tuple[config.Piece, config.PieceColour]]](board.Board):
		for colIndex, (piece, colour) in enumerate[tuple[config.Piece, config.PieceColour]](row):
			if piece != config.Piece.EMPTY:
				if colour == config.PieceColour.WHITE:
					whitePieces.append(piece)
					whitePiecesWithPositions.append((piece, (rowIndex, colIndex)))
				else:
					blackPieces.append(piece)
					blackPiecesWithPositions.append((piece, (rowIndex, colIndex)))
	# king vs king
	if len(whitePieces) == 1 and len(blackPieces) == 1:
		return True

	# king and bishop/ knight vs king
	if (len(whitePieces)) == 2 and len(blackPieces) == 1:
		if config.Piece.BISHOP in whitePieces or config.Piece.KNIGHT in whitePieces:
			return True
	if (len(blackPieces)) == 2 and len(whitePieces) == 1:
		if config.Piece.BISHOP in blackPieces or config.Piece.KNIGHT in blackPieces:
			return True
	
	# king and bishop vs king and bishop (same colour bishops)
	if len(whitePieces) == 2 and len(blackPieces) == 2:
		whiteBishopSquareColour: int = 0
		blackBishopSquareColour: int = 0
		for piece, position in whitePiecesWithPositions:
			if piece == config.Piece.BISHOP:
				whiteBishopSquareColour = (position[0] + position[1]) % 2
		for piece, position in blackPiecesWithPositions:
			if piece == config.Piece.BISHOP:
				blackBishopSquareColour = (position[0] + position[1]) % 2
		if whiteBishopSquareColour == blackBishopSquareColour:
			return True
	return False



def processMove(board: BoardHandling, fromSquare: tuple[int, int], toSquare: tuple[int, int]) -> bool:
	fromRow, fromCol, toRow, toCol = fromSquare[0], fromSquare[1], toSquare[0], toSquare[1]
	if (fromRow, fromCol) == (toRow, toCol) or fromRow == -1 or fromCol == -1 or toRow == -1 or toCol == -1:
		return False # If an empty move; we exit
	moves: list[config.MoveData] = getLegalMovesForPiece(board, row = fromRow, col = fromCol)
	pieceToMove, colourToMove = board.Board[fromRow][fromCol][0], board.Board[fromRow][fromCol][1]

	# Check whether the move to be processed is a pseudo-legal move
	moveType: config.MoveType | None = None
	for move in moves:
		moveRow, moveCol, moveMoveType = move.toSquare[0], move.toSquare[1], move.moveType
		if moveRow == toRow and moveCol == toCol:
			moveType = moveMoveType
			break
	if moveType is None:
		logger.warning(msg = f"Board: Rejecting invalid move from {fromSquare} to {toSquare} for piece {board.Board[fromRow][fromCol][0].name} {board.Board[fromRow][fromCol][1].name}")
		return False
	logger.info(msg = f"Board: Processing move from {fromSquare} to {toSquare} for piece {board.Board[fromRow][fromCol][0].name} {board.Board[fromRow][fromCol][1].name}, Type: {moveType.name}")

	board.moveHighlighting.previousMove = fromSquare
	board.moveHighlighting.currentMove = toSquare
	capturedPiece, capturedColour = board.Board[toRow][toCol][0], board.Board[toRow][toCol][1]
	updateCastlingRightsAfterMove(board = board, pieceToMove = pieceToMove, colourToMove = colourToMove, fromSquare = fromSquare, toSquare = toSquare, capturedPiece = capturedPiece, capturedColour = capturedColour)
	board.Board[toRow][toCol] = board.Board[fromRow][fromCol]
	board.Board[fromRow][fromCol] = (config.Piece.EMPTY, config.PieceColour.WHITE)
	if pieceToMove == config.Piece.PAWN or moveType == config.MoveType.CAPTURE:
		board.FiftyMoveCounter = 0
	else:
		board.FiftyMoveCounter += 1

	if moveType == config.MoveType.PROMOTION:
		board.pendingPromotion = config.PromotionData(
			fromSquare = fromSquare, 
			toSquare = toSquare, 
			moveType = config.MoveType.PROMOTION, 
			colour = colourToMove,
			capturedPiece = capturedPiece,
			capturedColour = capturedColour)
		board.EnPassantTargettableSquare = (-1, -1)
		return True

	# Begin other move type processing
	if moveType == config.MoveType.EN_PASSANT: # Handle en passant
		if colourToMove == config.PieceColour.WHITE:
			board.Board[toRow + 1][toCol] = (config.Piece.EMPTY, config.PieceColour.WHITE)
		else:
			board.Board[toRow - 1][toCol] = (config.Piece.EMPTY, config.PieceColour.WHITE)
	elif moveType == config.MoveType.CASTLING: # Handle castling
		if toCol == 6: # Kingside castling
			board.Board[toRow][5] = board.Board[toRow][7]
			board.Board[toRow][7] = (config.Piece.EMPTY, config.PieceColour.WHITE)
		else: # Queenside castling
			board.Board[toRow][3] = board.Board[toRow][0]
			board.Board[toRow][0] = (config.Piece.EMPTY, config.PieceColour.WHITE)
	board.EnPassantTargettableSquare = (-1, -1) # Reset after every move
	if pieceToMove == config.Piece.PAWN: # Handle pawn logic (setting en passant squares)
		if (fromRow, fromCol) == (toRow + 2, toCol):
			board.EnPassantTargettableSquare = (toRow + 1, toCol)
		elif (fromRow, fromCol) == (toRow - 2, toCol):
			board.EnPassantTargettableSquare = (toRow - 1, toCol)
		else:
			board.EnPassantTargettableSquare = (-1, -1)

	handleCheckStateAfterMove(board = board, colourToMove = colourToMove)
	if colourToMove == config.PieceColour.BLACK:
		board.FullMoveCounter += 1
	board.changeSideToMove()
	fenString: str = fen.exportFEN(board = board)
	data: config.MoveHistoryData = config.MoveHistoryData(
		fen = fenString,
		move = config.MoveData(
			fromSquare = fromSquare,
			toSquare = toSquare,
			moveType = moveType
		),
		piece = pieceToMove,
		colour = colourToMove,
		capturedPiece = capturedPiece,
		capturedColour = capturedColour,
		checkState = config.CheckState(
			inCheck = board.checkState.inCheck,
			square = board.checkState.square,
			colourInCheck = board.checkState.colourInCheck
		),
		gameState = config.GameState(
			gameOver = board.gameState.gameOver,
			winner = board.gameState.winner,
			reason = board.gameState.reason
		),
		whiteClock = 0.0,
		blackClock = 0.0
	)
	updateGameStateAfterMove(board = board)
	board.PositionHistory.append(data)
	board.PositionHistoryAsKeys.append(fen.getFENasKey(fen = fenString))
	board.moveHighlightingWithPositionHistory.append(config.MoveHighlighting(currentMove = board.moveHighlighting.currentMove, previousMove = board.moveHighlighting.previousMove))
	return True
