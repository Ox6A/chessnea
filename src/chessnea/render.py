from typing import Protocol

import pygame

import chessnea.config as config
import chessnea.enums as enums
import chessnea.moves as moveHandling

class BoardTypes(Protocol):
    Board: list[list[tuple[enums.Piece, enums.PieceColour]]]
    SideToMove: enums.PieceColour
    CastlingRights: list[enums.CastlingRights]
    EnPassantTargettableSquare: tuple[int, int]
    FiftyMoveCounter: int
    FullMoveCounter: int
    sprites: list[list[pygame.Surface | None]]
    piecePickedUp: tuple[int, int]

class Rendering():
    # Handle all board rendering functions
    def __init__(self) -> None:
        self.font: pygame.font.Font = pygame.font.Font(filename = None, size = 18) # Initialise the font used for debugging methods at object init

    def drawBoardBackground(self, screen: pygame.Surface, board: BoardTypes) -> None:
        # Draw the coloured squares for the chess board
        for row in range(len(board.Board)):
            for col in range(len(board.Board[row])):
                if (row + col) % 2 == 0:
                    colour = enums.RenderingColours.SQUARE_WHITE.value
                else:
                    colour = enums.RenderingColours.SQUARE_BLACK.value
                _ = pygame.draw.rect(surface = screen, color = colour, rect = pygame.Rect(col * config.WIDTH_PER_SQUARE, row * config.HEIGHT_PER_SQUARE, config.WIDTH_PER_SQUARE, config.HEIGHT_PER_SQUARE))
    
    def debugRenderingMethod(self, board: BoardTypes, screen: pygame.Surface) -> None:
        for row in range(len(board.Board)):
            for col in range(len(board.Board[row])):
                coordinates: tuple[int, int] = (col * (config.WIDTH_PER_SQUARE), row * (config.HEIGHT_PER_SQUARE))
                label: str = f"{row}{col}"
                textSurface: pygame.Surface = self.font.render(text = label, antialias = True, color = (0, 0, 0))
                _ = screen.blit(source = textSurface, dest = (coordinates[0], coordinates[1]))

    def renderBoard(self, screen: pygame.Surface, board: BoardTypes) -> None:
        sprite: pygame.Surface | None
        spriteRect: pygame.Rect
        pickedUpSprite: pygame.Surface | None = None
        for row in range(len(board.Board)):
            for col in range(len(board.Board[row])):
                piece, colour = board.Board[row][col]
                if piece != enums.Piece.EMPTY and board.piecePickedUp != (row, col):
                    sprite = board.sprites[colour.value][piece.value]
                    if sprite is None:
                        print(f"ERROR at Render: Sprite for {colour.name} {piece.name} is None")
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
                    mouseX, mouseY = pygame.mouse.get_pos()
                    if piece == enums.Piece.EMPTY:
                        continue
                    pickedUpSprite = board.sprites[colour.value][piece.value]
                    if pickedUpSprite is None:
                        print(f"ERROR at Render: Sprite for {colour.name} {piece.name} is None")
                        raise ValueError(f"Sprite for {colour.name} {piece.name} is None")
                    pieceBackgroundSurface: pygame.Surface = pygame.Surface((config.WIDTH_PER_SQUARE, config.HEIGHT_PER_SQUARE), pygame.SRCALPHA)
                    _ = pieceBackgroundSurface.fill(enums.RenderingColours.PIECE_PICKED_UP_BACKGROUND.value)
                    _ = screen.blit(source = pieceBackgroundSurface, dest = (col * config.WIDTH_PER_SQUARE, row * config.HEIGHT_PER_SQUARE))
                    moveBackgroundSurface: pygame.Surface = pygame.Surface((config.WIDTH_PER_SQUARE, config.HEIGHT_PER_SQUARE), pygame.SRCALPHA)
                    _ = moveBackgroundSurface.fill(enums.RenderingColours.PIECE_LEGAL_MOVE_BACKGROUND.value)
                    moves: list[tuple[int, int, enums.MoveType]] = moveHandling.getPseudoLegalMovesForPiece(board, row, col)
                    for move in moves:
                        moveRow, moveCol, _ = move
                        if moveRow == -1 and moveCol == -1: continue
                        _ = pygame.draw.circle(surface = screen, color = enums.RenderingColours.PIECE_LEGAL_MOVE_BACKGROUND.value, center = (moveCol * config.WIDTH_PER_SQUARE + config.WIDTH_PER_SQUARE // 2, moveRow * config.HEIGHT_PER_SQUARE + config.HEIGHT_PER_SQUARE // 2), radius = config.WIDTH_PER_SQUARE // 8)
        if board.piecePickedUp != (-1, -1) and pickedUpSprite is not None:
            mouseX, mouseY = pygame.mouse.get_pos()
            spriteRect = pickedUpSprite.get_rect(center=(mouseX, mouseY))
            _ = screen.blit(source = pickedUpSprite, dest = spriteRect)