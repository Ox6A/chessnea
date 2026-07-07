import math
import logging
import pygame

import chessnea.config as config
import chessnea.board as boardHandling
import chessnea.ui as ui

logger: logging.Logger = logging.getLogger(name = __name__)

class Rendering():
    # Handle all board rendering functions
    def __init__(self) -> None:
        self.font: pygame.font.Font = pygame.font.Font(filename = None, size = 18) # Initialise the font used for debugging methods at object init
        self.gameOverFontLarge: pygame.font.Font = pygame.font.Font(filename = str(config.FONT_MEDIUM), size = 48)
        self.gameOverFontSmall: pygame.font.Font = pygame.font.Font(filename = str(config.FONT_REGULAR), size = 24)
        self.gameOverFontButton: pygame.font.Font = pygame.font.Font(filename = str(config.FONT_MEDIUM), size = 28)
        self.colourState: list[tuple[int, int, int]] = [config.RenderingColours.SQUARE_BLACK.value, config.RenderingColours.SQUARE_WHITE.value]
        self.boardBackgroundSurface: pygame.Surface = self.createBoardBackgroundSurface() # cache board background surface
        self.flippedBoardBackgroundSurface: pygame.Surface = self.boardBackgroundSurface.copy()
        self.promotionOverlaySurface: pygame.Surface = pygame.Surface((config.WindowDefaults.BOARD_WIDTH.value, config.WindowDefaults.BOARD_HEIGHT.value), pygame.SRCALPHA) # cache promotion overlay surface
        self.promotionBackgroundSurface: pygame.Surface = self.createGradient(
            size = (config.WIDTH_PER_SQUARE, config.HEIGHT_PER_SQUARE),
            centreColour = config.RenderingGradientColours.PROMOTION_CHOICE_BACKGROUND_CENTRE.value,
            edgeColour = config.RenderingGradientColours.PROMOTION_CHOICE_BACKGROUND_EDGE.value) # cache promotion UI
        self.currentMoveBackgroundSurface: pygame.Surface = pygame.Surface((config.WIDTH_PER_SQUARE, config.HEIGHT_PER_SQUARE), pygame.SRCALPHA) # cache move highlight surface
        self.checkHighlightBackgroundSurface: pygame.Surface = pygame.Surface((config.WIDTH_PER_SQUARE, config.HEIGHT_PER_SQUARE), pygame.SRCALPHA) # cache check highlight surface
        self.gameOverMenuSurface: pygame.Surface = pygame.Surface((config.WindowDefaults.BOARD_WIDTH.value, config.WindowDefaults.BOARD_HEIGHT.value), pygame.SRCALPHA)

    def createBoardBackgroundSurface(self) -> pygame.Surface:
        boardBackgroundSurface: pygame.Surface = pygame.Surface((config.WindowDefaults.BOARD_WIDTH.value, config.WindowDefaults.BOARD_HEIGHT.value))
        for row in range(config.WindowDefaults.BOARD_SIZE.value):
            for col in range(config.WindowDefaults.BOARD_SIZE.value):
                colour: tuple[int, int, int]
                if (row + col) % 2 == 0:
                    colour = config.RenderingColours.SQUARE_WHITE.value
                else:
                    colour = config.RenderingColours.SQUARE_BLACK.value
                _ = pygame.draw.rect(surface = boardBackgroundSurface, color = colour, rect = pygame.Rect(col * config.WIDTH_PER_SQUARE, row * config.HEIGHT_PER_SQUARE, config.WIDTH_PER_SQUARE, config.HEIGHT_PER_SQUARE))
        return boardBackgroundSurface
    
    def drawBoardBackground(self, screen: pygame.Surface, board: boardHandling.BoardHandling) -> None:
        # Draw the coloured squares for the chess board
        if board.isBoardFlipped:
            _ = screen.blit(source = self.flippedBoardBackgroundSurface, dest = (0, config.WindowDefaults.TOP_BAR_HEIGHT.value))
        else:
            _ = screen.blit(source = self.boardBackgroundSurface, dest = (0, config.WindowDefaults.TOP_BAR_HEIGHT.value))

    def debugRenderingMethod(self, board: boardHandling.BoardHandling, screen: pygame.Surface) -> None:
        for row in range(len(board.Board)):
            for col in range(len(board.Board[row])):
                coordinates: tuple[int, int] = (col * (config.WIDTH_PER_SQUARE), row * (config.HEIGHT_PER_SQUARE))
                label: str = f"{row}{col}"
                textSurface: pygame.Surface = self.font.render(text = label, antialias = True, color = (0, 0, 0))
                _ = screen.blit(source = textSurface, dest = (coordinates[0], coordinates[1]))

    def renderBoard(self, screen: pygame.Surface, board: boardHandling.BoardHandling) -> None:
        self.renderMoveHighlighting(screen = screen, board = board)
        self.renderCheckHighlight(screen = screen, board = board)
        sprite: pygame.Surface | None
        spriteRect: pygame.Rect
        pickedUpSprite: pygame.Surface | None = None
        for row, rank in enumerate[list[tuple[config.Piece, config.PieceColour]]](board.Board):
            for col, square in enumerate[tuple[config.Piece, config.PieceColour]](rank):
                piece, colour = square
                if piece != config.Piece.EMPTY and board.piecePickedUp != (row, col):
                    sprite = board.sprites[colour.value][piece.value]
                    if sprite is None:
                        logger.error(msg = f"Render: Sprite for {colour.name} {piece.name} is None")
                        raise ValueError(f"Render: Sprite for {colour.name} {piece.name} is None")
                    displayRow, displayCol = board.getDisplaySquare(square = (row, col))
                    squareRect: pygame.Rect = pygame.Rect(
                        displayCol * config.WIDTH_PER_SQUARE,
                        displayRow * config.HEIGHT_PER_SQUARE + config.WindowDefaults.TOP_BAR_HEIGHT.value,
                        config.WIDTH_PER_SQUARE,
                        config.HEIGHT_PER_SQUARE,
                    )
                    spriteRect = sprite.get_rect(center = squareRect.center)
                    _ = screen.blit(source = sprite, dest = spriteRect)
                elif board.piecePickedUp == (row, col):
                    pickedUpSprite = board.sprites[colour.value][piece.value]

        if board.piecePickedUpLegalMoves != []:
            drawnSquares: list[tuple[int, int]] = []
            for move in board.piecePickedUpLegalMoves:
                if move.toSquare in drawnSquares:
                    continue
                drawnSquares.append(move.toSquare)
                if move.moveType == config.MoveType.CAPTURE or move.moveType == config.MoveType.EN_PASSANT:
                    captureHighlightSurface: pygame.Surface = pygame.Surface((config.WIDTH_PER_SQUARE, config.HEIGHT_PER_SQUARE), pygame.SRCALPHA)
                    _ = pygame.draw.circle(
                        surface = captureHighlightSurface, 
                        color = config.RenderingColours.PIECE_LEGAL_MOVE_BACKGROUND.value, 
                        center = (config.WIDTH_PER_SQUARE // 2, config.HEIGHT_PER_SQUARE // 2), 
                        radius = config.WIDTH_PER_SQUARE / 2 + config.WIDTH_PER_SQUARE // 4,
                        width = config.WIDTH_PER_SQUARE // 4)
                    displayRow, displayCol = board.getDisplaySquare(square = move.toSquare)
                    _ = screen.blit(source = captureHighlightSurface, dest = (displayCol * config.WIDTH_PER_SQUARE, displayRow * config.HEIGHT_PER_SQUARE + config.WindowDefaults.TOP_BAR_HEIGHT.value))
                # legal move circle
                else:
                    displayRow, displayCol = board.getDisplaySquare(square = move.toSquare)
                    _ = pygame.draw.circle(
                        surface = screen, 
                        color = config.RenderingColours.PIECE_LEGAL_MOVE_BACKGROUND.value, 
                        center = (displayCol * config.WIDTH_PER_SQUARE + config.WIDTH_PER_SQUARE // 2, displayRow * config.HEIGHT_PER_SQUARE + config.HEIGHT_PER_SQUARE // 2 + config.WindowDefaults.TOP_BAR_HEIGHT.value),
                        radius = config.WIDTH_PER_SQUARE // 8)

        # moving piece square highlight
        if board.piecePickedUp != (-1, -1):
            displayRow, displayCol = board.getDisplaySquare(square = (board.piecePickedUp[0], board.piecePickedUp[1]))
            _ = self.currentMoveBackgroundSurface.fill(color = config.RenderingColours.PIECE_PICKED_UP_BACKGROUND.value)
            _ = screen.blit(source = self.currentMoveBackgroundSurface, dest = (displayCol * config.WIDTH_PER_SQUARE, displayRow * config.HEIGHT_PER_SQUARE + config.WindowDefaults.TOP_BAR_HEIGHT.value))

        # picked up piece render
        if board.piecePickedUp != (-1, -1) and pickedUpSprite is not None:
            mouseX, mouseY = pygame.mouse.get_pos()
            spriteRect = pickedUpSprite.get_rect(center=(mouseX, mouseY))
            _ = screen.blit(source = pickedUpSprite, dest = spriteRect)

    def renderCheckHighlight(self, screen: pygame.Surface, board: boardHandling.BoardHandling) -> None:
        if board.checkState.inCheck and board.checkState.square != (-1, -1):
            _ = self.checkHighlightBackgroundSurface.fill(config.RenderingColours.CHECK_HIGHLIGHT_BACKGROUND.value)
            displayRow, displayCol = board.getDisplaySquare(square = board.checkState.square)
            _ = screen.blit(source = self.checkHighlightBackgroundSurface, dest = (displayCol * config.WIDTH_PER_SQUARE, displayRow * config.HEIGHT_PER_SQUARE + config.WindowDefaults.TOP_BAR_HEIGHT.value))

    def renderMoveHighlighting(self, screen: pygame.Surface, board: boardHandling.BoardHandling) -> None:
        for square in [board.moveHighlighting.currentMove, board.moveHighlighting.previousMove]:
            if square != (-1, -1):
                _ = self.currentMoveBackgroundSurface.fill(color = config.RenderingColours.PIECE_PREVIOUS_MOVE_BACKGROUND.value)
                displayRow, displayCol = board.getDisplaySquare(square = square)
                _ = screen.blit(source = self.currentMoveBackgroundSurface, dest = (displayCol * config.WIDTH_PER_SQUARE, displayRow * config.HEIGHT_PER_SQUARE + config.WindowDefaults.TOP_BAR_HEIGHT.value))

    def renderPromotionChoice(self, screen: pygame.Surface, board: boardHandling.BoardHandling) -> list[tuple[pygame.Rect, config.Piece]]:
        if board.pendingPromotion is None:
            return []
        _ = self.promotionOverlaySurface.fill(color = config.RenderingColours.DIMMED_BOARD_OVERLAY.value)
        _ = screen.blit(source = self.promotionOverlaySurface, dest = (0, config.WindowDefaults.TOP_BAR_HEIGHT.value))
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
            displayRow, displayCol = board.getDisplaySquare(square = (row, col))
            rect: pygame.Rect = pygame.Rect(
                displayCol * config.WIDTH_PER_SQUARE,
                displayRow * config.HEIGHT_PER_SQUARE + config.WindowDefaults.TOP_BAR_HEIGHT.value,
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

    def renderGameOver(self, screen: pygame.Surface, board: boardHandling.BoardHandling) -> list[tuple[pygame.Rect, str]]:
        if not board.gameState.gameOver:
            return []
        _ = self.gameOverMenuSurface.fill(color = config.RenderingColours.DIMMED_BOARD_OVERLAY.value)
        _ = screen.blit(source = self.gameOverMenuSurface, dest = (0, config.WindowDefaults.TOP_BAR_HEIGHT.value))
        title, subtitle = getGameOverMessage(gameState = board.gameState)

        titlePanelWidth: int = config.WindowDefaults.BOARD_WIDTH.value // 2
        titlePanelHeight: int = config.WindowDefaults.BOARD_HEIGHT.value // 4
        titlePanelX: int = (config.WindowDefaults.BOARD_WIDTH.value - titlePanelWidth) // 2
        titlePanelY: int = (config.WindowDefaults.BOARD_HEIGHT.value - titlePanelHeight) // 2
        titlePanelRect: pygame.Rect = pygame.Rect(titlePanelX, titlePanelY, titlePanelWidth, titlePanelHeight)
        _ = ui.drawSmoothRoundedRect(surface = screen, colour = config.UIColours.SURFACE.value, rect = titlePanelRect, radius = 16)

        titleSurface: pygame.Surface = self.gameOverFontLarge.render(text = title, antialias = True, color = config.UIColours.TEXT_PRIMARY.value)
        titleRect: pygame.Rect = titleSurface.get_rect(centerx = titlePanelRect.centerx, centery = titlePanelRect.centery - config.WindowDefaults.BOARD_HEIGHT.value // 16)
        _ = screen.blit(source=titleSurface, dest=titleRect)

        if subtitle:
            subtitleSurface: pygame.Surface = self.gameOverFontSmall.render(text = subtitle, antialias = True, color = config.UIColours.TEXT_SECONDARY.value)
            subtitleRect: pygame.Rect = subtitleSurface.get_rect(centerx = titlePanelRect.centerx, centery = titlePanelRect.centery - config.WindowDefaults.BOARD_HEIGHT.value // 160)
            _ = screen.blit(source = subtitleSurface, dest = subtitleRect)

        newGameButtonWidth: int = config.WindowDefaults.BOARD_WIDTH.value // 4
        newGameButtonHeight: int = config.WindowDefaults.BOARD_HEIGHT.value // 16
        newGameButtonX: int = titlePanelRect.centerx - newGameButtonWidth // 2
        newGameButtonY: int = titlePanelRect.bottom - config.WindowDefaults.BOARD_HEIGHT.value // 10
        newGameButtonRect: pygame.Rect = pygame.Rect(newGameButtonX, newGameButtonY, newGameButtonWidth, newGameButtonHeight)

        mouseX, mouseY = pygame.mouse.get_pos()
        newGameButtonHovered: bool = newGameButtonRect.collidepoint(mouseX, mouseY)
        newGameButtonColour: tuple[int, int, int, int] = config.UIColours.ACTION_HOVER.value if newGameButtonHovered else config.UIColours.SURFACE.value
        _ = ui.drawSmoothRoundedRect(surface = screen, colour = newGameButtonColour, rect = newGameButtonRect, radius = 8)
        _ = ui.drawSmoothRoundedRect(surface = screen, colour = config.UIColours.OUTLINE.value, rect = newGameButtonRect, radius = 8, width = 2)

        newGameButtonText = self.gameOverFontButton.render(text = "New Game", antialias = True, color = config.UIColours.TEXT_PRIMARY.value)
        newGameButtonTextRect: pygame.Rect = newGameButtonText.get_rect(center = newGameButtonRect.center)
        _ = screen.blit(source = newGameButtonText, dest = newGameButtonTextRect)
        return [(newGameButtonRect, "newGame")]

        
def getGameOverMessage(gameState: config.GameState) -> tuple[str, str]:
    reason: config.GameOverReason | None = gameState.reason
    winner: config.PieceColour | None = gameState.winner
    title: str
    subtitle: str = ""
    if reason == config.GameOverReason.CHECKMATE:
        winnerName: str
        if winner == config.PieceColour.WHITE:
            winnerName = "White"
        else:
            winnerName = "Black"
        title = "Checkmate"
        subtitle = f"{winnerName} wins!"
    elif reason == config.GameOverReason.STALEMATE:
        title = "Draw by Stalemate"
        subtitle = "The game is a draw as no further moves can be made!"
    elif reason == config.GameOverReason.FIFTY_MOVE_RULE:
        title = "Draw by threefold repetition"
        subtitle = "The same position has occurred 3 times!"
    elif reason == config.GameOverReason.INSUFFICIENT_MATERIAL:
        title = "Draw by insufficient material"
        subtitle = "There isn't sufficient material to continue the game!"
    else:
        raise ValueError("GameOverReason was not in expected list!")
    return (title, subtitle)