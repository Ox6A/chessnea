import math
import logging
import pygame

import chessnea.config as config
import chessnea.board as boardHandling

logger: logging.Logger = logging.getLogger(name = __name__)

class Rendering():
    # Handle all board rendering functions
    def __init__(self) -> None:
        self.font: pygame.font.Font = pygame.font.Font(filename = None, size = 18) # Initialise the font used for debugging methods at object init
        self.promotionBackgroundSurface: pygame.Surface = self.createGradient(
            size = (config.WIDTH_PER_SQUARE, config.HEIGHT_PER_SQUARE),
            centreColour = config.RenderingGradientColours.PROMOTION_CHOICE_BACKGROUND_CENTRE.value,
            edgeColour = config.RenderingGradientColours.PROMOTION_CHOICE_BACKGROUND_EDGE.value)

    def drawBoardBackground(self, screen: pygame.Surface, board: boardHandling.BoardHandling) -> None:
        # Draw the coloured squares for the chess board
        for row in range(len(board.Board)):
            for col in range(len(board.Board[row])):
                colour: tuple[int, int, int]
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
        for row, rank in enumerate[list[tuple[config.Piece, config.PieceColour]]](board.Board):
            for col, square in enumerate[tuple[config.Piece, config.PieceColour]](rank):
                piece, colour = square
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
                    spriteRect = sprite.get_rect(center = squareRect.center)
                    _ = screen.blit(source = sprite, dest = spriteRect)
                elif board.piecePickedUp == (row, col):
                    pickedUpSprite = board.sprites[colour.value][piece.value]

        if board.piecePickedUpLegalMoves != []:
            for move in board.piecePickedUpLegalMoves:
                if move.moveType == config.MoveType.CAPTURE or move.moveType == config.MoveType.EN_PASSANT:
                    captureHighlightSurface: pygame.Surface = pygame.Surface((config.WIDTH_PER_SQUARE, config.HEIGHT_PER_SQUARE), pygame.SRCALPHA)
                    _ = pygame.draw.circle(
                        surface = captureHighlightSurface, 
                        color = config.RenderingColours.PIECE_LEGAL_MOVE_BACKGROUND.value, 
                        center = (config.WIDTH_PER_SQUARE // 2, config.HEIGHT_PER_SQUARE // 2), 
                        radius = config.WIDTH_PER_SQUARE / 2 + config.WIDTH_PER_SQUARE // 4,
                        width = config.WIDTH_PER_SQUARE // 4)
                    _ = screen.blit(source = captureHighlightSurface, dest = (move.toSquare[1] * config.WIDTH_PER_SQUARE, move.toSquare[0] * config.HEIGHT_PER_SQUARE))
                # legal move circle
                else:
                    _ = pygame.draw.circle(
                        surface = screen, 
                        color = config.RenderingColours.PIECE_LEGAL_MOVE_BACKGROUND.value, 
                        center = (move.toSquare[1] * config.WIDTH_PER_SQUARE + config.WIDTH_PER_SQUARE // 2, move.toSquare[0] * config.HEIGHT_PER_SQUARE + config.HEIGHT_PER_SQUARE // 2), 
                        radius = config.WIDTH_PER_SQUARE // 8)

        # moving piece square highlight
        pieceBackgroundSurface: pygame.Surface = pygame.Surface((config.WIDTH_PER_SQUARE, config.HEIGHT_PER_SQUARE), pygame.SRCALPHA)
        _ = pieceBackgroundSurface.fill(config.RenderingColours.PIECE_PICKED_UP_BACKGROUND.value)
        _ = screen.blit(source = pieceBackgroundSurface, dest = (board.piecePickedUp[1] * config.WIDTH_PER_SQUARE, board.piecePickedUp[0] * config.HEIGHT_PER_SQUARE))

        # picked up piece render
        if board.piecePickedUp != (-1, -1) and pickedUpSprite is not None:
            mouseX, mouseY = pygame.mouse.get_pos()
            spriteRect = pickedUpSprite.get_rect(center=(mouseX, mouseY))
            _ = screen.blit(source = pickedUpSprite, dest = spriteRect)

    def renderPromotionChoice(self, screen: pygame.Surface, board: boardHandling.BoardHandling) -> list[tuple[pygame.Rect, config.Piece]]:
        if board.pendingPromotion is None:
            return []
        promotionOverlaySurface: pygame.Surface = pygame.Surface((config.WIDTH, config.HEIGHT), pygame.SRCALPHA)
        _ = promotionOverlaySurface.fill(color = config.RenderingColours.PROMOTION_CHOICE_BOARD_OVERLAY.value)
        _ = screen.blit(source = promotionOverlaySurface, dest = (0, 0))
        toSquare: tuple[int, int] = board.pendingPromotion.toSquare
        colour: config.PieceColour = board.pendingPromotion.colour
        direction: int
        if colour == config.PieceColour.BLACK:
            direction = -1
        else:
            direction = 1

        uiRects: list[tuple[pygame.Rect, config.Piece]] = []
        for i, v in enumerate[config.PromotionalPieces](config.PromotionalPieces):
            piece: config.Piece = config.Piece(v.value)
            row: int = toSquare[0] + (direction * i)
            col: int = toSquare[1]
            if row < 0 or row > 7:
                logger.error(msg = f"Render: Attempted to render promotion choice with out of bounds row {row}")
                raise ValueError(f"Attempted to render promotion choice with out of bounds row {row}")
            rect: pygame.Rect = pygame.Rect(
                col * config.WIDTH_PER_SQUARE,
                row * config.HEIGHT_PER_SQUARE,
                config.WIDTH_PER_SQUARE,
                config.HEIGHT_PER_SQUARE,
            )

            _= screen.blit(source = self.promotionBackgroundSurface, dest = rect)

            sprite: pygame.Surface | None = board.sprites[colour.value][piece.value]
            if sprite is None:
                logger.error(msg = f"Render: Sprite for {colour.name} {piece.name} is None")
                raise ValueError(f"Sprite for {colour.name} {piece.name} is None")
            spriteRect: pygame.Rect = sprite.get_rect(center = rect.center)
            _ = screen.blit(source = sprite, dest = spriteRect)
            uiRects.append((rect, piece))
        return uiRects

    def createGradient(self, size: tuple[int, int], centreColour: tuple[int, int, int, int], edgeColour: tuple[int, int, int, int]) -> pygame.Surface:
        gradientSurface: pygame.Surface = pygame.Surface(size, pygame.SRCALPHA)
        width, height = size[0], size[1]
        for y in range(height):
            for x in range(width):
                distanceToCentre: float = math.sqrt(((x - width / 2) ** 2 + (y - height / 2) ** 2))
                if distanceToCentre > min(width, height) / 2:
                    gradientSurface.set_at((x, y), (0, 0, 0, 0))
                    continue
                amount: float = min(distanceToCentre / ((min(width, height) / 2)), 1)
                red: int = int(centreColour[0] * (1 - amount) + edgeColour[0] * amount)
                green: int = int(centreColour[1] * (1 - amount) + edgeColour[1] * amount)
                blue: int = int(centreColour[2] * (1 - amount) + edgeColour[2] * amount)
                alpha: int = int(centreColour[3] * (1 - amount) + edgeColour[3] * amount)
                if distanceToCentre > (min(width, height) / 2) - 3:
                    alpha = int(alpha * ((((min(width, height) / 2) - distanceToCentre) / 3)))
                gradientSurface.set_at((x, y), (red, green, blue, alpha))
        return gradientSurface