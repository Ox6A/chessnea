from os import environ
import logging
import typing
import pygame

import chessnea.config as config
import chessnea.fen as fen
import chessnea.board as boardHandling
import chessnea.render as render
import chessnea.ui as ui

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
    logger.info(msg = "Init: Starting main UI...")
    menuBarInstance: ui.MenuBar = ui.MenuBar()
    ui.addStandardUIItems(menuBarInstance = menuBarInstance)
    logger.info(msg = "Init: Started UI initialisation")
    fen.handleStartingPositionFEN(board = board)
    running: bool = True
    promotionUIRects: list[tuple[pygame.Rect, config.Piece]] = []
    logger.info(msg = "Init: Initialisation finished")
    logger.info(msg = "Init: Started main game loop")
    currentCursor:int = pygame.SYSTEM_CURSOR_ARROW
    while running:
        mouseX, mouseY = pygame.mouse.get_pos()
        hoveringOverButton: config.MenuItem | None = menuBarInstance.checkIfHoveringOverMenuItem(mouseX = mouseX, mouseY = mouseY)
        for event in pygame.event.get():
            targetSquare: tuple[int, int] | tuple[typing.Literal[-1], typing.Literal[-1]]
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:  
                if event.key == pygame.K_TAB:
                    menuBarInstance.hidden = not menuBarInstance.hidden
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
                if hoveringOverButton:
                    if hoveringOverButton.children and menuBarInstance.openItem == hoveringOverButton:
                        menuBarInstance.openItem = None
                    elif hoveringOverButton.children:
                        menuBarInstance.openItem = hoveringOverButton
                    else:
                        menuBarInstance.runConnectorFunction(item = hoveringOverButton)
                        menuBarInstance.openItem = None
                    continue
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

        cursorToUse: int = pygame.SYSTEM_CURSOR_ARROW
        if hoveringOverButton:
            cursorToUse = pygame.SYSTEM_CURSOR_HAND
        elif board.pendingPromotion:
            for uiRect, _ in promotionUIRects:
                if uiRect.collidepoint(mouseX, mouseY):
                    cursorToUse = pygame.SYSTEM_CURSOR_HAND
                    break
        elif board.piecePickedUp != (-1, -1):
            cursorToUse = pygame.SYSTEM_CURSOR_HAND
        elif not board.gameState.gameOver:
            targetSquareTemp = board.getSquareUnderMousePosition()
            if targetSquareTemp is not None:
                row, col = targetSquareTemp
                piece, colour = board.Board[row][col]
                if piece != config.Piece.EMPTY and colour == board.SideToMove:
                    cursorToUse = pygame.SYSTEM_CURSOR_CROSSHAIR
        if cursorToUse != currentCursor:
            pygame.mouse.set_cursor(cursorToUse)
            currentCursor = cursorToUse
        menuBarInstance.drawMenuBar(screen = screen)
        pygame.display.flip()
        _ = clock.tick(config.FPS)

    logger.info(msg = "Init: Exiting...")
    pygame.quit()

if __name__ == "__main__":
    main()