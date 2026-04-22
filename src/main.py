from enum import IntEnum, Enum
import time
from pygame.surface import Surface
import pygame

class Globals(Enum):
    WIDTH = 600
    HEIGHT = 600
    FPS = 60

class Piece(IntEnum):
    EMPTY = 0
    PAWN = 1
    KNIGHT = 2
    BISHOP = 3
    ROOK = 4
    QUEEN = 5
    KING = 6

class PieceColour(IntEnum):
    WHITE = 0
    BLACK = 1

class RenderingColours(Enum):
    SQUARE_WHITE = (240, 217, 181)
    SQUARE_BLACK = (181, 136, 99)

class BoardHandling():
    def __init__(self)  -> None:
        self.board: list[list[tuple[Piece, PieceColour]]] = [[(Piece.EMPTY, PieceColour.WHITE) for _ in range(8)] for _ in range(8)]
        self.sideToMove: PieceColour = PieceColour.WHITE

class RenderThread():
    def __init__(self) -> None:
        pass

    def drawBoardBackground(self, screen: Surface, Board: BoardHandling) -> None:
        for row in range(len(Board.board)):
            for col in range(len(Board.board[row])):
                if (row + col) % 2 == 0:
                    colour = RenderingColours.SQUARE_WHITE.value
                else:
                    colour = RenderingColours.SQUARE_BLACK.value
                _ = pygame.draw.rect(screen, colour, (col * (Globals.WIDTH.value // 8), row * (Globals.HEIGHT.value // 8), Globals.WIDTH.value // 8, Globals.HEIGHT.value // 8))
        

def main() -> None:
    _ = pygame.init()
    screen: Surface = pygame.display.set_mode(size=(Globals.WIDTH.value, Globals.HEIGHT.value))
    pygame.display.set_caption("Chess")
    Board: BoardHandling = BoardHandling()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        RenderThread().drawBoardBackground(screen, Board)
        pygame.display.flip()
        time.sleep(1 / Globals.FPS.value)

    pygame.quit()
if __name__ == "__main__":
    main()