from os import environ
import pygame

import chessnea.config as config
import chessnea.enums as enums
import chessnea.fen as fen
import chessnea.board as boardHandling
import chessnea.render as render

def main() -> None:
    environ["SDL_VSYNC"] = "1" # enable V-Sync
    _ = pygame.init()
    screen: pygame.Surface = pygame.display.set_mode(size = (config.WIDTH, config.HEIGHT))
    pygame.display.set_caption("Chess")
    clock: pygame.time.Clock = pygame.time.Clock()
    print("Init: Pygame initialised")
    board: boardHandling.BoardHandling = boardHandling.BoardHandling()
    renderThreadInstance: render.Rendering = render.Rendering()
    fen.importFEN(board = board, fen = config.FEN_STARTING_POSITION)
    running: bool = True
    print("Init: Started!")
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                square: tuple[int, int] = board.getSquareUnderMousePosition() or (-1, -1)
                if square != (-1, -1):
                    if board.SideToMove == board.Board[square[0]][square[1]][1] and board.Board[square[0]][square[1]][0] != enums.Piece.EMPTY:
                        board.piecePickedUp = square    
            elif event.type == pygame.MOUSEBUTTONUP:
                boardHandling.processMove(board, fromSquare = board.piecePickedUp, toSquare = board.getSquareUnderMousePosition() or (-1, -1))
                board.piecePickedUp = (-1, -1)
        renderThreadInstance.drawBoardBackground(screen, board)
        #renderThreadInstance.debugRenderingMethod(board, screen)
        renderThreadInstance.renderBoard(screen, board)
        pygame.display.flip()
        _ = clock.tick(config.FPS)

    print("Exiting...")
    pygame.quit()

if __name__ == "__main__":
    main()