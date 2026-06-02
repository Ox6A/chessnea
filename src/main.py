from os import environ
import logging
import pygame

import chessnea.config as config
import chessnea.fen as fen
import chessnea.board as boardHandling
import chessnea.render as render

logger: logging.Logger = logging.getLogger(__name__)

def main() -> None:
    logging.basicConfig(level=logging.INFO, format="[%(asctime)s] [%(levelname)s] %(message)s", datefmt="%H:%M:%S")
    logger.info(msg = "Init: Running initialisation...")
    environ["SDL_VSYNC"] = "1" # enable V-Sync
    _ = pygame.init()
    logger.info(msg = "Init: Pygame initialised!")
    screen: pygame.Surface = pygame.display.set_mode(size = (config.WIDTH, config.HEIGHT))
    pygame.display.set_caption("Chess")
    clock: pygame.time.Clock = pygame.time.Clock()
    board: boardHandling.BoardHandling = boardHandling.BoardHandling()
    renderThreadInstance: render.Rendering = render.Rendering()
    fen.importFEN(board = board, fen = config.FEN_STARTING_POSITION)
    running: bool = True
    logger.info(msg = "Init: Initialisation finished")
    logger.info(msg = "Init: Started main game loop")
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                square: tuple[int, int] = board.getSquareUnderMousePosition() or (-1, -1)
                if square != (-1, -1):
                    if board.SideToMove == board.Board[square[0]][square[1]][1] and board.Board[square[0]][square[1]][0] != config.Piece.EMPTY:
                        board.piecePickedUp = square    
            elif event.type == pygame.MOUSEBUTTONUP:
                boardHandling.processMove(board, fromSquare = board.piecePickedUp, toSquare = board.getSquareUnderMousePosition() or (-1, -1))
                board.piecePickedUp = (-1, -1)
        renderThreadInstance.drawBoardBackground(screen, board)
        #renderThreadInstance.debugRenderingMethod(board, screen)
        renderThreadInstance.renderBoard(screen, board)
        pygame.display.flip()
        _ = clock.tick(config.FPS)

    logger.info(msg = "Init: Exiting...")
    pygame.quit()

if __name__ == "__main__":
    main()