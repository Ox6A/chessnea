from os import environ
import logging
import typing
import pygame

import chessnea.config as config
import chessnea.fen as fen
import chessnea.board as boardHandling
import chessnea.render as render

logger: logging.Logger = logging.getLogger(name = __name__)

def main() -> None:
    logging.basicConfig(level=logging.INFO, format="[%(asctime)s] [%(levelname)s] %(message)s", datefmt="%H:%M:%S")
    logger.info(msg = "Init: Chessnea version " + config.VERSION)
    logger.info(msg = "Init: Running initialisation...")
    environ["SDL_VSYNC"] = "1" # enable V-Sync
    _ = pygame.init()
    logger.info(msg = "Init: Pygame initialised!")
    screen: pygame.Surface = pygame.display.set_mode(size = (config.WIDTH, config.HEIGHT))
    logger.info(msg = f"Init: Display created with configuration: {config.WIDTH}x{config.HEIGHT} at {config.FPS} FPS")
    pygame.display.set_caption("Chess")
    clock: pygame.time.Clock = pygame.time.Clock()
    board: boardHandling.BoardHandling = boardHandling.BoardHandling()
    _ = board.loadSpritesForBoard()
    renderThreadInstance: render.Rendering = render.Rendering()
    fen.handleStartingPositionFEN(board = board)
    running: bool = True
    promotionUIRects: list[tuple[pygame.Rect, config.Piece]] = []
    logger.info(msg = "Init: Initialisation finished")
    logger.info(msg = "Main: Started main game loop")
    cursorChanged: bool = False
    while running:
        for event in pygame.event.get():
            targetSquare: tuple[int, int] | tuple[typing.Literal[-1], typing.Literal[-1]]
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if not board.gameState.gameOver:
                    if board.pendingPromotion:
                        mouseX, mouseY = pygame.mouse.get_pos()
                        for uiRect, piece in promotionUIRects:
                            if uiRect.collidepoint(mouseX, mouseY):
                                boardHandling.completePromotion(board = board, promotionPieceType = piece)
                                promotionUIRects = []
                                logger.debug(msg = f"Main: Processed promotion to {piece.name}")
                                break
                        continue
                    targetSquare = board.getSquareUnderMousePosition() or (-1, -1)
                    if targetSquare != (-1, -1):
                        piece, colour = board.Board[targetSquare[0]][targetSquare[1]][0], board.Board[targetSquare[0]][targetSquare[1]][1]
                        if board.SideToMove == colour and piece != config.Piece.EMPTY:
                            board.piecePickedUp = targetSquare   
                            row, col = targetSquare
                            board.piecePickedUpLegalMoves = boardHandling.getLegalMovesForPiece(board = board, row = row, col = col)
                            logger.debug(msg = f"Main: Picked up piece at square {targetSquare} of type {board.Board[targetSquare[0]][targetSquare[1]][0]} and colour {board.Board[targetSquare[0]][targetSquare[1]][1]}")
            elif event.type == pygame.MOUSEBUTTONUP:
                if not board.gameState.gameOver:
                    if board.pendingPromotion:
                        continue
                    targetSquare = board.getSquareUnderMousePosition() or (-1, -1)
                    boardHandling.processMove(board = board, fromSquare = board.piecePickedUp, toSquare = targetSquare)
                    logger.debug(msg = f"Main: Attempted move from {board.piecePickedUp} to {targetSquare}")
                    board.piecePickedUp = (-1, -1)
                    board.piecePickedUpLegalMoves = []
        renderThreadInstance.drawBoardBackground(screen = screen)
        #renderThreadInstance.debugRenderingMethod(board, screen)
        renderThreadInstance.renderBoard(screen = screen, board = board)
        promotionUIRects = renderThreadInstance.renderPromotionChoice(screen = screen, board = board)
        mouseX, mouseY = pygame.mouse.get_pos()
        if board.pendingPromotion and not cursorChanged:
            for uiRect, _ in promotionUIRects:
                if uiRect.collidepoint(mouseX, mouseY):
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                    cursorChanged = True
                    break
        elif not board.pendingPromotion and cursorChanged:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

        pygame.display.flip()
        _ = clock.tick(config.FPS)

    logger.info(msg = "Init: Exiting...")
    pygame.quit()

if __name__ == "__main__":
    main()