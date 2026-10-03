import logging
from dataclasses import dataclass

import pygame

from chessnea.core import position, types
from chessnea.ui import assets, theme

logger: logging.Logger = logging.getLogger(name = __name__)

MIN_BOARD_PX: int = 480
BOARD_TO_RESOLUTION_FACTOR: float = 0.8 # 80% of screen width/height is used

@dataclass(frozen = True)
class Layout:
    boardPx: int
    squarePx: int
    topBarPx: int
    window: tuple[int, int]

    @classmethod
    def fromBoardPx(cls, boardPx: int) -> "Layout":
        boardPx = max(MIN_BOARD_PX, boardPx) # Enforce minimum board size
        boardPx -= boardPx % 8 # Remove excess pixels after setting the 8 square division factor
        return cls(
            boardPx = boardPx,
            squarePx = boardPx // 8,
            topBarPx = boardPx // 16,
            window = (boardPx, boardPx + boardPx // 16),
        )

class BoardViewport:
    def __init__(self, layout: Layout) -> None:
        self.layout: Layout = layout
        self.sprites: dict[tuple[types.PieceColour, types.Piece], pygame.Surface]= assets.loadSprites(squarePx = self.layout.squarePx)
        self.backgroundSurface: pygame.Surface = self.createBoardBackgroundSurface()

    def createBoardBackgroundSurface(self) -> pygame.Surface:
        surface: pygame.Surface = pygame.Surface((self.layout.boardPx, self.layout.boardPx))
        for row in range(8):
            for col in range(8):
                colour : tuple[int, int, int]
                if (row + col) % 2 == 0:
                    colour = theme.SQUARE_WHITE
                else:
                    colour = theme.SQUARE_BLACK
                _ = pygame.draw.rect(surface = surface, color = colour, rect = (col * self.layout.squarePx, row * self.layout.squarePx, self.layout.squarePx, self.layout.squarePx))
        return surface

    def drawBoardBackgroundSurface(self, screen: pygame.Surface) -> None:
        _ = screen.blit(source = self.backgroundSurface, dest = (0, self.layout.topBarPx))

    def getSprite(self, colour: types.PieceColour, piece: types.Piece) -> pygame.Surface:
        try:
            return self.sprites[(colour, piece)]
        except KeyError as e:
            logger.error(msg = f"Render: Sprite for {colour.name} {piece.name} not found in loaded sprites")
            raise ValueError(f"Render: Sprite for {colour.name} {piece.name} not found in loaded sprites") from e
    
    def getSquareAt(self, mousePosition: tuple[int, int]) -> types.Square | None:
        mouseX, mouseY = mousePosition
        mouseY -= self.layout.topBarPx
        row: int = mouseY // self.layout.squarePx
        col: int = mouseX // self.layout.squarePx
        if 0 <= row < 8 and 0 <= col < 8:
            return (row, col)
        return None
    
    def getSquareRectAtGamePosition(self, square: types.Square) -> pygame.Rect:
        row, col = square
        size = self.layout.squarePx
        return pygame.Rect(
			col * size,
			self.layout.topBarPx + (row * size),
			size,
			size
		)


    def renderBoard(self, screen: pygame.Surface, boardPosition: position.Position) -> None:
        self.drawBoardBackgroundSurface(screen = screen)
        for row, rank in enumerate(boardPosition.board):
            for col, (piece, colour) in enumerate(rank):
                if piece == types.Piece.EMPTY:
                    continue
                sprite: pygame.Surface = self.getSprite(colour = colour, piece = piece)
                rect: pygame.Rect = self.getSquareRectAtGamePosition(square = (row, col))
                _ = screen.blit(source = sprite, dest = sprite.get_rect(center = rect.center))