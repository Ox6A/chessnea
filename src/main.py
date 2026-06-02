from os import environ
import pygame

import chessnea.config as config
import chessnea.enums as enums
import chessnea.assets as assets
import chessnea.fen as fen
import chessnea.moves as moveHandling
import chessnea.render as render

class BoardHandling():
    def __init__(self)  -> None:
        self.Board: list[list[tuple[enums.Piece, enums.PieceColour]]] = [[(enums.Piece.EMPTY, enums.PieceColour.WHITE) for _ in range(8)] for _ in range(8)] # Initialise an empty board
        self.SideToMove: enums.PieceColour = enums.PieceColour.WHITE # White is the default side to move (subject to parsed FEN position)
        self.CastlingRights: list[enums.CastlingRights] = [enums.CastlingRights.WHITE_KINGSIDE, enums.CastlingRights.WHITE_QUEENSIDE, enums.CastlingRights.BLACK_KINGSIDE, enums.CastlingRights.BLACK_QUEENSIDE]
        self.EnPassantTargettableSquare: tuple[int, int] = (-1, -1) # Defines which square is attackable under en passant
        self.FiftyMoveCounter: int = 0 # Niche rule allowing a draw after 50 moves without a capture
        self.FullMoveCounter: int = 0 # Constant tracking for current move nr.
        self.sprites: list[list[pygame.Surface | None]] = assets.loadSprites() # Load sprites from disk
        self.piecePickedUp: tuple[int, int] = (-1, -1) # Current piece picked up by the mouse cursor

    def getSquareUnderMousePosition(self) -> tuple[int, int] | None:
        # Converts absolute coordinates for the mouse position provided by Pygame into a internal board square
        mouseX, mouseY = pygame.mouse.get_pos()
        col: int = mouseX // config.WIDTH_PER_SQUARE
        row: int = mouseY // config.HEIGHT_PER_SQUARE
        if 0 <= row < 8 and 0 <= col < 8:
            return (row, col)
        else:
            return None

def main() -> None:
    environ["SDL_VSYNC"] = "1" # enable V-Sync
    _ = pygame.init()
    screen: pygame.Surface = pygame.display.set_mode(size = (config.WIDTH, config.HEIGHT))
    pygame.display.set_caption("Chess")
    clock: pygame.time.Clock = pygame.time.Clock()
    print("Init: Pygame initialised")
    board: BoardHandling = BoardHandling()
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
                moveHandling.processMove(board, fromSquare = board.piecePickedUp, toSquare = board.getSquareUnderMousePosition() or (-1, -1))
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