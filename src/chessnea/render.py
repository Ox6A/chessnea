import logging
import pygame

import chessnea.config as config
import chessnea.board as boardHandling

logger: logging.Logger = logging.getLogger(__name__)

class Rendering():
    # Handle all board rendering functions
    def __init__(self) -> None:
        self.font: pygame.font.Font = pygame.font.Font(filename = None, size = 18) # Initialise the font used for debugging methods at object init

    def drawBoardBackground(self, screen: pygame.Surface, board: boardHandling.BoardHandling) -> None:
        # Draw the coloured squares for the chess board
        for row in range(len(board.Board)):
            for col in range(len(board.Board[row])):
                if (row + col) % 2 == 0:
                    colour = config.RenderingColours.SQUARE_WHITE.value
                else:
                    colour = config.RenderingColours.SQUARE_BLACK.value
                _ = pygame.draw.rect(surface = screen, color = colour, rect = pygame.Rect(col * config.WIDTH_PER_SQUARE, row * config.HEIGHT_PER_SQUARE, config.WIDTH_PER_SQUARE, config.HEIGHT_PER_SQUARE))
    
    def debugRenderingMethod(self, board: boardHandling.BoardHandling, screen: pygame.Surface) -> None:
        for row in range(len(board.Board)):
            for col in range(len(board.Board[row])):
                coordinates: tuple[int, int] = (col * (config.WIDTH_PER_SQUARE), row * (config.HEIGHT_PER_SQUARE))
                label: str = f"{row}{col}"
                textSurface: pygame.Surface = self.font.render(text = label, antialias = True, color = (0, 0, 0))
                _ = screen.blit(source = textSurface, dest = (coordinates[0], coordinates[1]))

    def renderBoard(self, screen: pygame.Surface, board: boardHandling.BoardHandling) -> None:
        sprite: pygame.Surface | None
        spriteRect: pygame.Rect
        pickedUpSprite: pygame.Surface | None = None
        pickedUpMoves: list[tuple[int, int, config.MoveType]] = []
        for row in range(len(board.Board)):
            for col in range(len(board.Board[row])):
                piece, colour = board.Board[row][col]
                if piece != config.Piece.EMPTY and board.piecePickedUp != (row, col):
                    sprite = board.sprites[colour.value][piece.value]
                    if sprite is None:
                        logger.error(msg = f"ERROR at Render: Sprite for {colour.name} {piece.name} is None")
                        raise ValueError(f"Sprite for {colour.name} {piece.name} is None")
                    squareRect: pygame.Rect = pygame.Rect(
                        col * config.WIDTH_PER_SQUARE,
                        row * config.HEIGHT_PER_SQUARE,
                        config.WIDTH_PER_SQUARE,
                        config.HEIGHT_PER_SQUARE,
                    )
                    spriteRect = sprite.get_rect(center=squareRect.center)
                    _ = screen.blit(source=sprite, dest=spriteRect)
                elif board.piecePickedUp == (row, col):
                    pickedUpSprite = board.sprites[colour.value][piece.value]
                    pickedUpMoves = boardHandling.getPseudoLegalMovesForPiece(board, row, col)

        if pickedUpMoves != []:
            for moveRow, moveCol, _ in pickedUpMoves:
                # legal move circle
                _ = pygame.draw.circle(surface = screen, color = config.RenderingColours.PIECE_LEGAL_MOVE_BACKGROUND.value, center = (moveCol * config.WIDTH_PER_SQUARE + config.WIDTH_PER_SQUARE // 2, moveRow * config.HEIGHT_PER_SQUARE + config.HEIGHT_PER_SQUARE // 2), radius = config.WIDTH_PER_SQUARE // 8)

        # moving piece square highlight
        pieceBackgroundSurface: pygame.Surface = pygame.Surface((config.WIDTH_PER_SQUARE, config.HEIGHT_PER_SQUARE), pygame.SRCALPHA)
        _ = pieceBackgroundSurface.fill(config.RenderingColours.PIECE_PICKED_UP_BACKGROUND.value)
        _ = screen.blit(source = pieceBackgroundSurface, dest = (board.piecePickedUp[1] * config.WIDTH_PER_SQUARE, board.piecePickedUp[0] * config.HEIGHT_PER_SQUARE))

        # picked up piece render
        if board.piecePickedUp != (-1, -1) and pickedUpSprite is not None:
            mouseX, mouseY = pygame.mouse.get_pos()
            spriteRect = pickedUpSprite.get_rect(center=(mouseX, mouseY))
            _ = screen.blit(source = pickedUpSprite, dest = spriteRect)