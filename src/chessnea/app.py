"""Acts as the entry point for Chessnea."""
import argparse
import logging
import sys
import typing
from os import environ

import pygame

logger: logging.Logger = logging.getLogger(name = __name__)

from chessnea import __version__
from chessnea.core import fen, types
from chessnea.ui import board
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
		clock: pygame.Clock = pygame.Clock()

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
		self.boardPosition: types.Position = fen.importFENToPositionObject(fen = fen.FEN_STARTING_POSITION)
		self.viewport: board.BoardViewport = board.BoardViewport(layout = self.layout)
		logger.debug(msg = "Init: Starting main loop")
		mouseDownPosition: tuple[int, int] | None = None
		running: bool = True

		pos: tuple[int, int]
		button: int
		while running:
			mousePosition: tuple[int, int] = pygame.mouse.get_pos()
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					running = False
				elif event.type == pygame.MOUSEBUTTONDOWN:
					button = typing.cast(int, event.button)
					pos = typing.cast(tuple[int, int], event.pos)
					if button == 1:
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
			_ = self.screen.fill(color = (255, 255, 255))
			_ = self.viewport.renderBoard(screen = self.screen, boardPosition = self.boardPosition, selectionState = self.selection, mousePosition = mousePosition)
			pygame.display.flip()
			_ = clock.tick(FPS)

	def handleMouseEvent(self, mousePosition: tuple[int, int], event: pygame.event.Event) -> None:
		"""Handles mouse clicks within the UI"""
		square: types.Square | None = self.viewport.getSquareAt(mousePosition = mousePosition)
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
				else:
					logger.debug(msg = f"Input: Putting down piece from {self.selection.selectedSquare} on a different square {square}")
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
			self.selection.select(square = square, possibleMoves = (), state = types.SelectionState.SELECTED)
		elif event.type == pygame.MOUSEBUTTONUP:
			if self.selection.state == types.SelectionState.DRAGGING:
				logger.debug(msg = f"Input: Dropping piece at square {square}")
				self.selection.clear()
			elif self.selection.deselectPieceOnMouseUp:
				# No drag started so treat the second click as deselect
				logger.debug(msg = f"Input: Deselecting piece at square {self.selection.selectedSquare}")
				self.selection.clear()
			self.selection.mouseDown = False
		else:
			return

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