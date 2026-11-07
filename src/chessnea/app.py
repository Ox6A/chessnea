"""Acts as the entry point for Chessnea."""
import argparse
import logging
import sys
import typing
from os import environ

import pygame

logger: logging.Logger = logging.getLogger(name = __name__)

from chessnea import __version__
from chessnea.core import clock, fen, types
from chessnea.rules import legal, moves
from chessnea.ui import bar, board, overlay
from chessnea.ui.selection import Selection

FPS: int = 60

def scaleBoard(widthPx: int, heightPx: int) -> int:
	return int(min(widthPx, heightPx) * board.BOARD_TO_RESOLUTION_FACTOR)

def checkPositiveIntFromArgument(text: str) -> int:
	try:
		value: int = int(text)
	except ValueError as error:
		raise argparse.ArgumentTypeError(f"expected a positive integer - got {text!r}") from error
	if value <= 0:
		raise argparse.ArgumentTypeError(f"expected a positive integer - got {text!r}")
	return value


class App:
	def __init__(self, boardSize: int | None = None) -> None:
		# Enable V-Sync
		environ["SDL_VSYNC"] = "1"

		# Initialise pygame window
		_ = pygame.init()
		pygameclock: pygame.Clock = pygame.Clock()

		# Derive board size from command-line argument if passed, or auto-scale to display resolution
		boardPx: int
		if boardSize is None:
			boardPx = scaleBoard(widthPx = pygame.display.Info().current_w, heightPx = pygame.display.Info().current_h)
			logger.info(msg = f"Init: No board size given, auto-scaled to {boardPx}px board using screen resolution {pygame.display.Info().current_w}x{pygame.display.Info().current_h}px")
		else:
			boardPx = boardSize
			logger.info(msg = f"Init: Using board size {boardPx}px from command-line argument")
		self.layout: board.Layout = board.Layout.fromBoardPx(boardPx = boardPx)
		self.screen: pygame.Surface = pygame.display.set_mode(size = self.layout.window)
		self.selection: Selection = Selection()
		logger.info(msg = f"Init: Display created with configuration: {self.layout.boardPx}x{self.layout.boardPx + self.layout.topBarPx}px window, with {self.layout.squarePx}px squares")
		pygame.display.set_caption("Chessnea")
		self.history: list[types.HistoryEntry] = [types.HistoryEntry(position = fen.importFENToPositionObject(fen = fen.FEN_STARTING_POSITION))]
		self.viewport: board.BoardViewport = board.BoardViewport(layout = self.layout)
		self.gameOverReason: types.GameOverReason | None = None
		self.gameOverOverlay: overlay.GameOverOverlay | None = None
		self.clock: clock.Clock = clock.Clock()
		self.topBar: bar.Bar = bar.Bar(layout = self.layout, padLeftLabels = ["Menu"], padRightLabels = ["Exit", "Undo"])
		logger.debug(msg = "Init: Starting main loop")
		mouseDownPosition: tuple[int, int] | None = None
		running: bool = True

		pos: tuple[int, int]
		key: int
		modifiers: int
		button: int
		while running:
			mousePosition: tuple[int, int] = pygame.mouse.get_pos()
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					running = False
				elif event.type == pygame.MOUSEBUTTONDOWN:
					button = typing.cast(int, event.button)
					pos = typing.cast(tuple[int, int], event.pos)
					if button == 1 and self.topBar.rect.collidepoint(pos):
						box = self.topBar.getButtonAtPos(mousePosition = pos)
						running = self.handleTopBarClick(label = box.label if box is not None else None)
					elif button == 1:
						self.handleMouseEvent(mousePosition = pos, event = event)
						if self.selection.selectedSquare is not None:
							mouseDownPosition = pos
				elif event.type == pygame.MOUSEMOTION:
					pos = typing.cast(tuple[int, int], event.pos)
					buttonsHeld: tuple[int, int, int] = typing.cast(tuple[int, int, int], event.buttons)
					if buttonsHeld[0] and mouseDownPosition is not None and self.selection.state == types.SelectionState.SELECTED:
						distanceFromSquare: tuple[int, int] = (pos[0] - mouseDownPosition[0], pos[1] - mouseDownPosition[1])
						modulusFromSquare: float = typing.cast(float, (distanceFromSquare[0] ** 2 + distanceFromSquare[1] ** 2) ** 0.5)
						if modulusFromSquare > self.layout.squarePx * 0.25:
							self.selection.state = types.SelectionState.DRAGGING
							logger.debug(msg = "Input: Switching selection state from SELECTED to DRAGGING")
				elif event.type == pygame.MOUSEBUTTONUP:
					button = typing.cast(int, event.button)
					pos = typing.cast(tuple[int, int], event.pos)
					if button == 1:
						self.handleMouseEvent(mousePosition = pos, event = event)
						mouseDownPosition = None
				elif event.type == pygame.KEYDOWN:
					key = typing.cast(int, event.key)
					modifiers = typing.cast(int, event.mod)
					if key == pygame.K_z and (modifiers & pygame.KMOD_CTRL):
						self.undoMove(plies = 1)
			if self.gameOverReason is None and self.clock.updateClock(sideToMove = self.boardPosition.sideToMove):
				self.checkGameOver(timeOut = True)
			_ = self.screen.fill(color = (255, 255, 255))
			_ = self.viewport.renderBoard(screen = self.screen, boardPosition = self.boardPosition, selectionState = self.selection, mousePosition = mousePosition, lastMove = self.lastMove)
			if self.gameOverOverlay is not None:
				_ = self.gameOverOverlay.draw(screen = self.screen, mousePosition = mousePosition)
			self.topBar.draw(screen = self.screen, mousePosition = mousePosition, clock = self.clock, sideToMove = self.boardPosition.sideToMove, clockEnabled = self.gameOverReason is None)
			pygame.display.flip()
			_ = pygameclock.tick(FPS)

	@property
	def boardPosition(self) -> types.Position:
		"""Returns the current board position."""
		return self.history[-1].position

	@property
	def lastMove(self) -> types.Move | None:
		"""Returns the last move played, or None if no moves have been played."""
		if len(self.history) < 2:
			return None
		return self.history[-1].move
	
	def handleMouseEvent(self, mousePosition: tuple[int, int], event: pygame.event.Event) -> None:
		"""Handles mouse clicks within the UI.

		Args:
			mousePosition: Mouse coordinates in pixels (x, y).
			event: Pygame event.
		"""
		square: types.Square | None = self.viewport.getSquareAt(mousePosition = mousePosition)
		matchedMoveToSquare: types.Move | None
		possibleMoves: list[types.Move]
  
		if self.gameOverOverlay is not None:
			if (event.type == pygame.MOUSEBUTTONDOWN) and (self.gameOverOverlay.newGameButtonRect.collidepoint(mousePosition)):
					logger.debug(msg = f"Input: Mouse click at {mousePosition} on new game button, starting new game")
					self.startNewGame()
			return
		if event.type == pygame.MOUSEBUTTONDOWN:
			if square is None:
				logger.debug(msg = f"Input: Mouse click outside of board at {mousePosition}, clearing selection state")
				self.selection.clear()
				return
			# Put down a piece
			if self.selection.selectedSquare is not None:
				if square == self.selection.selectedSquare:
					logger.debug(msg = f"Input: Putting down piece on the same square {square}")
					# Delay deselection until release so this press can transition to selection.state.DRAGGING
					self.selection.deselectPieceOnMouseUp = True
					self.selection.mouseDown = True
					return
				elif self.viewport.getBoardSquareAtSquare(square = square, boardPosition = self.boardPosition)[1] != self.boardPosition.sideToMove:
					logger.debug(msg = f"Input: Putting down piece from {self.selection.selectedSquare} on a different square {square}")
					matchedMoveToSquare= self.findMatchingMoveWithSquare(fromSquare = self.selection.selectedSquare, toSquare = square, possibleMoves = self.selection.possibleMoves or [])
					if matchedMoveToSquare is not None:
						logger.debug(msg = f"Input: Attempting move from {self.selection.selectedSquare} to {square}")
						self.playMove(move = matchedMoveToSquare, animate = True)
					self.selection.clear()
					return

			# Pickup a piece
			piece, colour = self.boardPosition.board[square[0]][square[1]]
			if self.boardPosition.sideToMove != colour:
				return
			if piece == types.Piece.EMPTY:
				logger.debug(msg = f"Input: Mouse click at empty square {square}, no piece to pick up")
				return
			logger.debug(msg = f"Input: Picking up {colour.name} {piece.name} at square {square}")
			possibleMoves = legal.getLegalMovesForPiece(position = self.boardPosition, square = square)
			self.selection.select(square = square, possibleMoves = possibleMoves, state = types.SelectionState.SELECTED)
		elif event.type == pygame.MOUSEBUTTONUP:
			if self.selection.state == types.SelectionState.DRAGGING:
				matchedMoveToSquare= self.findMatchingMoveWithSquare(fromSquare = typing.cast(types.Square, self.selection.selectedSquare), toSquare = typing.cast(types.Square, square), possibleMoves = self.selection.possibleMoves or [])
				if matchedMoveToSquare is not None:
					logger.debug(msg = f"Input: Attempting move from {self.selection.selectedSquare} to {square}")
					self.playMove(move = matchedMoveToSquare)
				self.selection.clear()
			elif self.selection.deselectPieceOnMouseUp:
				# No drag started so treat the second click as deselect
				logger.debug(msg = f"Input: Deselecting piece at square {self.selection.selectedSquare}")
				self.selection.clear()
			self.selection.mouseDown = False
		else:
			return

	def handleTopBarClick(self, label: str | None) -> bool:
		"""Handles clicks on the top bar buttons.

		Args:
			label: The label of the button that was clicked.

		Returns:
			True if the application should continue running, False if it should exit.
		"""
		if label is None:
			return True
		logger.debug(msg = f"Input: Top bar button '{label}' clicked")
		if label == "Exit":
			logger.info(msg = "Input: Exiting application")
			return False
		elif label == "Undo":
			self.undoMove(plies = 1)
		elif label == "Menu":
			logger.info(msg = "Input: Menu button clicked")
		return True

	def findMatchingMoveWithSquare(self, fromSquare: types.Square, toSquare: types.Square, possibleMoves: list[types.Move], promotionPiece: types.Piece = types.Piece.QUEEN) -> types.Move | None:
		"""Finds a move in the list of possible moves that matches the given from and to squares.

		Args:
			fromSquare: The starting square of the move.
			toSquare: The ending square of the move.
			possibleMoves: List of possible moves.
			promotionPiece: The piece to promote to.
   
		Returns:
			The matching move if found, otherwise None.
		"""
		for move in possibleMoves:
			if (move.fromSquare == fromSquare and move.toSquare == toSquare) and (move.promotionPiece is None or move.promotionPiece == promotionPiece):
				return move
		return None

	def playMove(self, move: types.Move, animate: bool = False) -> None:
		"""Plays a move on the board.

		Args:
			move: The move to play.
			animate: Whether to animate the move.
		"""
		moveColour: types.PieceColour = self.boardPosition.sideToMove
		if self.clock.updateClock(sideToMove = moveColour):
			self.checkGameOver(timeOut = True)
			return
		newPosition: types.Position = moves.applyMove(position = self.boardPosition, move = move)
		self.clock.applyClockIncrement(sideToMove = moveColour)
		if not self.clock.isRunning:
			self.clock.setClockState(isRunning = True)
		self.history.append(types.HistoryEntry(position = newPosition, move = move, clockTimes = self.clock.timeRemaining.copy()))
		if animate:
			self.viewport.BoardAnimations.startMoveAnimation(board = self.viewport, move = move, boardPosition = self.boardPosition)
		self.checkGameOver()

	def undoMove(self, plies: int = 1) -> None:
		"""Undoes the last move(s) played.

		Args:
			plies: The number of plies (half-moves) to undo.
		"""
		totalMoves: int = len(self.history) - 1
		if totalMoves < plies:
			logger.warning(msg = f"Board: Attempted to undo {plies} plies, but only {totalMoves} moves have been played")
			return 
		for _ in range(plies):
			_ = self.history.pop()
		logger.info(msg = f"Board: Undid {plies} plies")

		# Resync UI state with the new board position
		self.viewport.moveAnimations = []
		self.selection.clear()
		self.gameOverOverlay = None
		self.gameOverReason = None
		_ = pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
		previousEntry: types.HistoryEntry = self.history[-1]
		if previousEntry.clockTimes is None:
			self.clock.resetClock()
		else:
			self.clock.timeRemaining = previousEntry.clockTimes.copy()
			if not self.clock.isRunning:
				self.clock.setClockState(isRunning = True)

	def checkGameOver(self, timeOut: bool = False) -> None:
		"""Checks if the game is over and updates the game over state."""
		if timeOut:
			self.gameOverReason = types.GameOverReason.TIMEOUT
		else:
			positionHistory: list[types.PositionIdentifier] = [legal.returnPositionIdentifierFromPosition(position = entry.position) for entry in self.history]
			self.gameOverReason = legal.getGameOverState(position = self.boardPosition, positionHistory = positionHistory)
		if self.gameOverReason is None:
			return
		self.clock.setClockState(isRunning = False)
		winner: types.PieceColour | None = None
		if self.gameOverReason in (types.GameOverReason.CHECKMATE, types.GameOverReason.TIMEOUT):
			winner = legal.getOpposingColour(colour = self.boardPosition.sideToMove)
		logger.info(msg = f"Board: Game Over by {self.gameOverReason.name}, winner: {winner.name if winner is not None else 'None'}")
		icon: pygame.Surface | None = self.viewport.getSprite(colour = winner, piece = types.Piece.KING) if winner is not None else None
		self.gameOverOverlay = overlay.GameOverOverlay(layout = self.layout, reason = self.gameOverReason, winner = winner, icon = icon)
  
	def startNewGame(self) -> None:
		"""Starts a new game.."""
		logger.info(msg = "Board: Starting new game")
		_ = pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
		self.history = [types.HistoryEntry(position = fen.importFENToPositionObject(fen = fen.FEN_STARTING_POSITION))]
		self.viewport.moveAnimations = []
		self.selection.clear()
		self.gameOverReason = None
		self.gameOverOverlay = None
		self.clock.resetClock()
			

def main() -> None:
	parser: argparse.ArgumentParser = argparse.ArgumentParser(description = "Chessnea", suggest_on_error = True)
	_ = parser.add_argument("--version", action = "version", version = __version__)
	_ = parser.add_argument("--board-size", type = checkPositiveIntFromArgument, default = None, metavar = "PX", help = "Board size in pixels, e.g. 800 [default: auto-scale]")
	_ = parser.add_argument("--debug", action = "store_true", help="Enable debug logging")
	args: argparse.Namespace = parser.parse_args()
	if args.debug:  # pyright: ignore[reportAny]
		logging.basicConfig(level = logging.DEBUG, format = "[%(asctime)s] [%(levelname)s] %(message)s", datefmt = "%H:%M:%S")
	else:
		logging.basicConfig(level = logging.INFO, format = "[%(asctime)s] [%(levelname)s] %(message)s", datefmt = "%H:%M:%S")
	logger.info(msg = "Init: Chessnea version " + __version__)
	logger.debug(msg = "Init: Checking for command-line arguments...")
	if len(sys.argv) > 1:
		logger.debug(msg = f"Init: Command-line arguments: {sys.argv[1:]}")
	else:
		logger.debug(msg = "Init: No command-line arguments given!")
	logger.debug(msg = "Init: Running initialisation...")
	_ = App(boardSize = args.board_size)  # pyright: ignore[reportAny]
