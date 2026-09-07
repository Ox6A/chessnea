import argparse
import logging
import sys
from dataclasses import dataclass
from os import environ

import pygame

logger: logging.Logger = logging.getLogger(name = __name__)

from chessnea import __version__
from chessnea.core import fen, position
from chessnea.ui import board

FPS: int = 60

@dataclass
class SelectionState:
    piecePickedUp: tuple[int, int] = (-1, -1)

    def setPickedUpPiece(self, row: int, col: int) -> None:
        self.piecePickedUp = (row, col)

    def clearPickedUpPiece(self) -> None:
        self.piecePickedUp = (-1, -1)

def scaleBoard(widthPx: int, heightPx: int) -> int:
    currentWidth: int = int(widthPx)
    currentHeight: int = int(heightPx)
    resolutionPx: int = min(currentWidth, currentHeight)
    availableScreenPx: int = int(resolutionPx * board.BOARD_TO_RESOLUTION_FACTOR)
    board_px = availableScreenPx // 8 * 8 # round to square size
    return max(board.MIN_BOARD_PX, board_px)


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
        if boardSize is None:
            boardPx: int = scaleBoard(widthPx = pygame.display.Info().current_w, heightPx = pygame.display.Info().current_h)
            logger.info(msg = f"Init: No board size given, auto-scaled to {boardPx}px board using screen resolution {pygame.display.Info().current_w}x{pygame.display.Info().current_h}px")
        else:
            boardPx = boardSize
            logger.info(msg = f"Init: Using board size {boardPx}px from command-line argument")
        self.layout: board.Layout = board.Layout.fromBoardPx(boardPx = boardPx)
        self.screen: pygame.Surface = pygame.display.set_mode(size = self.layout.window)
        self.selectionState: SelectionState = SelectionState()
        logger.info(msg = f"Init: Display created with configuration: {self.layout.boardPx}x{self.layout.boardPx + self.layout.topBarPx}px window, with {self.layout.squarePx}px squares")
        pygame.display.set_caption("Chessnea")
        boardPosition: position.Position = fen.importFENToPositionObject(fen = fen.FEN_STARTING_POSITION)
        viewport: board.BoardViewport = board.BoardViewport(layout = self.layout)
        logger.info(msg = "Init: Starting main loop")
        running: bool = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            _ = self.screen.fill((255, 255, 255))
            _ = viewport.renderBoard(screen = self.screen, boardPosition = boardPosition)
            _ = clock.tick(FPS)
            pygame.display.flip()


def main() -> None:
    logging.basicConfig(level = logging.INFO, format = "[%(asctime)s] [%(levelname)s] %(message)s", datefmt = "%H:%M:%S")
    logger.info(msg = "Init: Chessnea version " + __version__)

    logger.info(msg = "Init: Checking for command-line arguments...")
    parser: argparse.ArgumentParser = argparse.ArgumentParser(description = "Chessnea", suggest_on_error = True)
    _ = parser.add_argument("--version", action = "version", version = __version__)
    _ = parser.add_argument("--board-size", type = checkPositiveIntFromArgument, default = None, metavar = "PX", help="Board size in pixels, e.g. 800 [default: auto-scale]")
    args: argparse.Namespace = parser.parse_args()
    if len(sys.argv) > 1:
        logger.info(msg = f"Init: Command-line arguments: {sys.argv[1:]}")
    else:
        logger.info(msg = "Init: No command-line arguments given!")
    logger.info(msg = "Init: Running initialisation...")
    _ = App(boardSize = args.board_size)  # pyright: ignore[reportAny]
