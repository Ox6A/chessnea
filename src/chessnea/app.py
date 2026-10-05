"""Acts as the entry point for Chessnea."""
import argparse
import logging
import sys
from os import environ

import pygame

logger: logging.Logger = logging.getLogger(name = __name__)

from chessnea import __version__
from chessnea.core import fen, types
from chessnea.ui import board
from chessnea.ui.selection import SelectionState

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
        print(self.layout.window)
        self.selectionState: SelectionState = SelectionState()
        logger.info(msg = f"Init: Display created with configuration: {self.layout.boardPx}x{self.layout.boardPx + self.layout.topBarPx}px window, with {self.layout.squarePx}px squares")
        pygame.display.set_caption("Chessnea")
        boardPosition: types.Position = fen.importFENToPositionObject(fen = fen.FEN_STARTING_POSITION)
        self.viewport: board.BoardViewport = board.BoardViewport(layout = self.layout)
        logger.debug(msg = "Init: Starting main loop")
        running: bool = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handleMouseClickEvent(mousePosition = pygame.mouse.get_pos())
            _ = self.screen.fill(color = (255, 255, 255))
            _ = self.viewport.renderBoard(screen = self.screen, boardPosition = boardPosition)
            _ = clock.tick(FPS)
            pygame.display.flip()

    def handleMouseClickEvent(self, mousePosition: tuple[int, int]) -> None:
        square: types.Square | None = self.viewport.getSquareAt(mousePosition = mousePosition)
        if square is not None:
            logger.debug(msg = f"Input: Mouse click at square {square}, setting selection state: selectedSquare={square}, possibleMoves=[{square}], dragging=True")
            testTuple: tuple[types.Move, ...] = (types.Move(fromSquare = square, toSquare = (square)), )
            self.selectionState.select(square, possibleMoves = testTuple, dragging = True)
        else:
            logger.debug(msg = f"Input: Mouse click outside of board at {mousePosition}, clearing selection state")
            self.selectionState.clear()

def main() -> None:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(description = "Chessnea", suggest_on_error = True)
    _ = parser.add_argument("--version", action = "version", version = __version__)
    _ = parser.add_argument("--board-size", type = checkPositiveIntFromArgument, default = None, metavar = "PX", help="Board size in pixels, e.g. 800 [default: auto-scale]")
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
